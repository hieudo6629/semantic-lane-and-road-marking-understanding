"""
Wrapper cho model Ultra-Fast-Lane-Detection-v2, chuyển output thô của model
thành danh sách làn dạng [(x, y), ...] mà toàn bộ pipeline phía sau
(analysis/lane_analyzer.py, ...) sử dụng.

Đây là file MỚI HOÀN TOÀN - trước đây repo này CHƯA CÓ wrapper thật nào gọi
Ultra-Fast-Lane-Detection-v2; `src/main.py --live` chỉ đọc lane có sẵn từ
annotation của dataset CULane (src/dataset.py), KHÔNG hề chạy model qua ảnh
thật. Wrapper này lấp đúng khoảng trống đó.

Nguyên tắc khi viết file này (theo yêu cầu của dự án): KHÔNG thay đổi logic
lõi của Ultra-Fast-Lane-Detection-v2 (kiến trúc model, cách decode output) -
chỉ đóng gói lại thành class dễ dùng, có kiểm tra lỗi và log rõ ràng. Phần
decode `pred2coords()` được port gần như nguyên vẹn từ
Ultra-Fast-Lane-Detection-v2/demo.py, chỉ đổi tên biến cho rõ nghĩa và thêm
giải thích tiếng Việt.

CẢI TIẾN so với demo.py gốc: demo.py hardcode kích thước ảnh gốc CULane
(1640x590) khi quy đổi tọa độ dự đoán về pixel thật - đúng với CULane
nhưng SẼ SAI nếu dùng ảnh dashcam kích thước khác (ví dụ 1920x1080 như dự
án này hướng tới). Wrapper này dùng ĐÚNG kích thước ảnh gốc thật sự truyền
vào detect(), không hardcode.

HỖ TRỢ NHIỀU BIẾN THỂ (dataset x backbone): CULane/Tusimple đều dùng CHUNG
kiến trúc `model/model_culane.py:parsingNet` (đã xác nhận bằng cách đọc
Ultra-Fast-Lane-Detection-v2/model/model_tusimple.py - file đó chỉ import
lại đúng class parsingNet của model_culane.py), chỉ khác nhau ở vài tham số
cấu hình (số hàng/cột anchor, kích thước train, crop_ratio, fc_norm, công
thức row_anchor). Vì vậy chỉ cần tham số hóa các con số này (bảng
_DATASET_PRESETS bên dưới, chép trực tiếp từ file cấu hình gốc
Ultra-Fast-Lane-Detection-v2/configs/{dataset}_res{backbone}.py) là dùng
được cho cả 2 dataset x 2 backbone (18/34) = 4 tổ hợp, KHÔNG cần sửa logic
decode.

CHƯA HỖ TRỢ CurveLanes: dataset này dùng một KIẾN TRÚC MẠNG KHÁC HẲN
(model/model_curvelanes.py - có thêm nhánh cls_distribute/lane_token, tách
riêng cls_row/cls_col, không có forward_tta) và một thuật toán hậu xử lý
phức tạp hơn nhiều để gộp dự đoán row+col cho từng lane
(evaluation/eval_wrapper.py: generate_lines_local_curve_combine,
generate_lines_col_local_curve_combine, revise_lines_curve_combine) - việc
port đúng phần này nằm ngoài phạm vi thay đổi nhỏ gọn hiện tại, để lại cho
một tác vụ riêng nếu cần.

LƯU Ý QUAN TRỌNG: KHÔNG dùng cơ chế `Config.fromfile()` của chính
Ultra-Fast-Lane-Detection-v2 (utils/config.py) để tự động đọc các file cấu
hình .py gốc, dù cách đó tránh được rủi ro chép nhầm số. Lý do: repo đó có
package tên "utils" TRÙNG TÊN với package utils/ của chính dự án này. Một
khi package utils/ của DỰ ÁN đã được import (ví dụ dòng `from utils.logger
import get_logger` ngay bên dưới), Python cache sẵn "utils" trong
sys.modules - mọi `import utils.xxx` sau đó (kể cả sau khi đã thêm đường
dẫn Ultra-Fast-Lane-Detection-v2 vào sys.path) đều bị resolve NHẦM sang
package utils/ của dự án này chứ không phải của UFLD-v2, gây lỗi
ModuleNotFoundError khó hiểu. Vì vậy bảng cấu hình dưới đây được chép trực
tiếp (giá trị ổn định, ít khi đổi vì đây là cấu hình tái tạo kết quả bài
báo gốc), không phụ thuộc code nào của UFLD-v2 ngoài chính kiến trúc model.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

from utils.logger import get_logger
from utils.preprocessing import bgr_to_normalized_tensor, resize_keep_ratio_then_crop, validate_image

logger = get_logger(__name__)

Point = Tuple[float, float]
Lane = List[Point]

SUPPORTED_BACKBONES = ("18", "34")

# Chép trực tiếp từ Ultra-Fast-Lane-Detection-v2/configs/{dataset}_res18.py
# và {dataset}_res34.py - 2 backbone của CÙNG 1 dataset dùng chung các số
# này (backbone chỉ đổi phần trích xuất đặc trưng ResNet, không đổi số
# lượng anchor/kích thước train), nên chỉ cần bảng theo dataset.
#
# row_anchor_start/end: mốc đầu/cuối của dải hàng anchor (row anchor),
# TÍNH THEO TỈ LỆ chiều cao ảnh gốc dataset đó lúc train (0.0 = đỉnh ảnh,
# 1.0 = đáy ảnh). Với Tusimple, file gốc định nghĩa bằng pixel tuyệt đối
# (np.linspace(160, 710, num_row) / 720) - về mặt toán học, chia mỗi điểm
# của 1 dải linspace cho cùng 1 hằng số tương đương linspace 2 đầu mút đã
# chia trước, nên 160/720 và 710/720 cho đúng kết quả tương tự.
_DATASET_PRESETS: Dict[str, Dict] = {
    "culane": dict(
        num_row=72, num_col=81, train_width=1600, train_height=320,
        num_cell_row=200, num_cell_col=100, crop_ratio=0.6,
        use_aux=False, fc_norm=True, num_lanes=4,
        row_anchor_start=0.42, row_anchor_end=1.0,
    ),
    "tusimple": dict(
        num_row=56, num_col=41, train_width=800, train_height=320,
        num_cell_row=100, num_cell_col=100, crop_ratio=0.8,
        use_aux=False, fc_norm=False, num_lanes=4,
        row_anchor_start=160 / 720, row_anchor_end=710 / 720,
    ),
}


class LaneDetector:
    """
    Wrapper cho model Ultra-Fast-Lane-Detection-v2 (kiến trúc parsingNet),
    hỗ trợ 2 dataset (CULane, Tusimple) x 2 backbone (resnet18, resnet34).
    Xem _DATASET_PRESETS ở đầu file để biết các tham số cấu hình cụ thể.
    """

    # CULane/Tusimple đều có 4 làn (index 0-3). Model dự đoán 2 làn giữa
    # (1, 2) theo kiểu "row anchor" (quét theo hàng ngang, trả về x tại
    # từng y cố định) - phù hợp với làn gần thẳng đứng ở giữa ảnh. 2 làn
    # ngoài (0, 3) dự đoán theo kiểu "col anchor" (quét theo cột dọc, trả
    # về y tại từng x cố định) - phù hợp hơn với làn nghiêng mạnh gần rìa
    # ảnh, nơi 1 giá trị x có thể ứng với nhiều y nên không thể biểu diễn
    # tốt theo kiểu row anchor. Quy ước này giống hệt nhau cho cả CULane và
    # Tusimple (xác nhận từ chính pred2coords() trong demo.py gốc - dùng
    # chung 1 hàm, hardcode row_lane_idx=[1,2]/col_lane_idx=[0,3] cho cả 2
    # dataset), nên không cần đưa vào _DATASET_PRESETS.
    ROW_LANE_INDICES = (1, 2)
    COL_LANE_INDICES = (0, 3)

    def __init__(
        self,
        model_path: str,
        ufld_repo_path: str,
        dataset: str = "culane",
        backbone: str = "34",
        device: str = "cpu",
    ):
        """
        Args:
            model_path: đường dẫn tới file .pth đã train (ví dụ culane_res34.pth,
                        tusimple_res18.pth) - PHẢI khớp với đúng dataset/backbone
                        khai báo bên dưới, nếu không state_dict sẽ load sai/lệch shape.
            ufld_repo_path: đường dẫn tới thư mục gốc repo Ultra-Fast-Lane-Detection-v2
                             (chứa thư mục con `model/`) - cần thêm vào sys.path để
                             import được kiến trúc parsingNet gốc, tránh copy code model.
            dataset: "culane" hoặc "tusimple" (chưa hỗ trợ "curvelanes" - xem docstring đầu file).
            backbone: "18" hoặc "34".
            device: "cpu" | "cuda".
        """
        dataset = dataset.lower()
        if dataset not in _DATASET_PRESETS:
            raise ValueError(
                f"dataset='{dataset}' chưa được hỗ trợ. Hiện chỉ hỗ trợ: {list(_DATASET_PRESETS)} "
                "(CurveLanes cần kiến trúc model + thuật toán decode khác hẳn, xem docstring đầu file)."
            )
        if backbone not in SUPPORTED_BACKBONES:
            raise ValueError(f"backbone='{backbone}' không hợp lệ, phải là một trong {SUPPORTED_BACKBONES}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Không tìm thấy model làn đường tại: {model_path}")
        if not os.path.isdir(ufld_repo_path):
            raise FileNotFoundError(f"Không tìm thấy thư mục Ultra-Fast-Lane-Detection-v2 tại: {ufld_repo_path}")

        preset = _DATASET_PRESETS[dataset]
        self.dataset = dataset
        self.backbone = backbone
        self.TRAIN_WIDTH = preset["train_width"]
        self.TRAIN_HEIGHT = preset["train_height"]
        self.CROP_RATIO = preset["crop_ratio"]
        self.NUM_ROW = preset["num_row"]
        self.NUM_COL = preset["num_col"]
        self.NUM_CELL_ROW = preset["num_cell_row"]
        self.NUM_CELL_COL = preset["num_cell_col"]
        self.NUM_LANES = preset["num_lanes"]
        self.USE_AUX = preset["use_aux"]
        self.FC_NORM = preset["fc_norm"]

        self._add_ufld_repo_to_path(ufld_repo_path)

        # Import trễ (sau khi đã chỉnh sys.path) - lấy đúng kiến trúc model gốc
        # của Ultra-Fast-Lane-Detection-v2, không định nghĩa lại. CULane và
        # Tusimple dùng chung class này (xem docstring đầu file).
        from model.model_culane import parsingNet  # type: ignore

        logger.info(f"Đang khởi tạo parsingNet (dataset={dataset}, backbone=resnet{backbone})...")
        self.net = parsingNet(
            pretrained=False,  # Không tải backbone ImageNet - state_dict bên dưới sẽ ghi đè toàn bộ, tải làm gì cho tốn thời gian/cần mạng
            backbone=self.backbone,
            num_grid_row=self.NUM_CELL_ROW,
            num_cls_row=self.NUM_ROW,
            num_grid_col=self.NUM_CELL_COL,
            num_cls_col=self.NUM_COL,
            num_lane_on_row=self.NUM_LANES,
            num_lane_on_col=self.NUM_LANES,
            use_aux=self.USE_AUX,
            input_height=self.TRAIN_HEIGHT,
            input_width=self.TRAIN_WIDTH,
            fc_norm=self.FC_NORM,
        )

        logger.info(f"Đang load trọng số từ: {model_path}")
        checkpoint = torch.load(model_path, map_location="cpu")
        state_dict = checkpoint["model"] if "model" in checkpoint else checkpoint
        # Checkpoint train bằng DistributedDataParallel thường có tiền tố "module." trong tên layer
        compatible_state_dict = {
            (k[len("module."):] if k.startswith("module.") else k): v for k, v in state_dict.items()
        }
        self.net.load_state_dict(compatible_state_dict, strict=False)
        self.net.eval()
        self.net.to(device)
        self.device = device

        self.row_anchor = np.linspace(preset["row_anchor_start"], preset["row_anchor_end"], self.NUM_ROW)
        self.col_anchor = np.linspace(0, 1, self.NUM_COL)

        logger.info("LaneDetector sẵn sàng.")

    def _add_ufld_repo_to_path(self, ufld_repo_path: str) -> None:
        if ufld_repo_path not in sys.path:
            sys.path.insert(0, ufld_repo_path)

    def detect(self, image_bgr: np.ndarray) -> List[Lane]:
        """
        Nhận diện làn đường trên một ảnh.

        Args:
            image_bgr: ảnh gốc (BGR, kết quả cv2.imread), kích thước bất kỳ -
                       KHÔNG cần tự resize trước, hàm này tự lo tiền xử lý.

        Returns:
            Danh sách làn, mỗi làn là list các điểm (x, y) THEO TỌA ĐỘ CỦA
            ẢNH GỐC (image_bgr), sẵn sàng đưa thẳng vào analysis.lane_analyzer.
        """
        validation = validate_image(image_bgr)
        if not validation.is_valid:
            logger.warning(f"Ảnh đầu vào không hợp lệ, bỏ qua detect: {validation.issues}")
            return []

        original_height, original_width = image_bgr.shape[0], image_bgr.shape[1]

        resized_height_before_crop = int(self.TRAIN_HEIGHT / self.CROP_RATIO)
        cropped = resize_keep_ratio_then_crop(
            image_bgr,
            target_width=self.TRAIN_WIDTH,
            resized_height=resized_height_before_crop,
            crop_height=self.TRAIN_HEIGHT,
        )
        tensor = bgr_to_normalized_tensor(cropped).to(self.device)

        with torch.no_grad():
            pred = self.net(tensor)

        return self._decode_prediction(pred, original_width, original_height)

    def _decode_prediction(self, pred: dict, original_width: int, original_height: int) -> List[Lane]:
        """
        Chuyển output thô của model (phân bố xác suất theo lưới ô - grid) thành
        tọa độ pixel thực. Port gần nguyên vẹn từ pred2coords() trong
        Ultra-Fast-Lane-Detection-v2/demo.py.

        Ý tưởng cốt lõi: model không dự đoán trực tiếp tọa độ (x, y) mà dự
        đoán PHÂN LOẠI - "điểm này rơi vào ô lưới thứ mấy" (giống bài toán
        phân loại nhiều lớp). Để có tọa độ mượt hơn thay vì "nhảy bậc" theo
        từng ô, ta lấy trung bình có trọng số (kỳ vọng / soft-argmax) của các
        ô lân cận ô có xác suất cao nhất, thay vì chỉ lấy đúng 1 ô argmax.
        """
        local_width = 1
        loc_row, loc_col = pred["loc_row"].cpu(), pred["loc_col"].cpu()
        _, num_grid_row, num_cls_row, _ = pred["loc_row"].shape
        _, num_grid_col, num_cls_col, _ = pred["loc_col"].shape

        max_indices_row = pred["loc_row"].argmax(1).cpu()
        valid_row = pred["exist_row"].argmax(1).cpu()
        max_indices_col = pred["loc_col"].argmax(1).cpu()
        valid_col = pred["exist_col"].argmax(1).cpu()

        lanes: List[Lane] = []

        for lane_idx in self.ROW_LANE_INDICES:
            # Làn chỉ được coi là "tồn tại" nếu hơn một nửa số hàng anchor báo có điểm thuộc làn này
            if valid_row[0, :, lane_idx].sum() <= num_cls_row / 2:
                continue
            lane_points: Lane = []
            for row_k in range(valid_row.shape[1]):
                if not valid_row[0, row_k, lane_idx]:
                    continue
                center = int(max_indices_row[0, row_k, lane_idx])
                neighborhood = torch.arange(
                    max(0, center - local_width), min(num_grid_row - 1, center + local_width) + 1
                )
                # Kỳ vọng (expected value) vị trí ô theo phân bố softmax quanh ô có xác suất cao nhất
                grid_pos = (loc_row[0, neighborhood, row_k, lane_idx].softmax(0) * neighborhood.float()).sum() + 0.5
                x = float(grid_pos / (num_grid_row - 1) * original_width)
                y = float(self.row_anchor[row_k] * original_height)
                lane_points.append((x, y))
            if lane_points:
                lanes.append(lane_points)

        for lane_idx in self.COL_LANE_INDICES:
            if valid_col[0, :, lane_idx].sum() <= num_cls_col / 4:
                continue
            lane_points = []
            for col_k in range(valid_col.shape[1]):
                if not valid_col[0, col_k, lane_idx]:
                    continue
                center = int(max_indices_col[0, col_k, lane_idx])
                neighborhood = torch.arange(
                    max(0, center - local_width), min(num_grid_col - 1, center + local_width) + 1
                )
                grid_pos = (loc_col[0, neighborhood, col_k, lane_idx].softmax(0) * neighborhood.float()).sum() + 0.5
                y = float(grid_pos / (num_grid_col - 1) * original_height)
                x = float(self.col_anchor[col_k] * original_width)
                lane_points.append((x, y))
            if lane_points:
                lanes.append(lane_points)

        return lanes

    def self_test(self) -> dict:
        """
        Chạy thử model trên ảnh nhiễu ngẫu nhiên để xác định lỗi đến từ
        model/pipeline (crash) hay từ ảnh đầu vào thật (yêu cầu mục D.2).
        """
        rng = np.random.default_rng(seed=0)
        test_image = rng.integers(0, 255, size=(1080, 1920, 3), dtype=np.uint8)
        try:
            lanes = self.detect(test_image)
            return {"ok": True, "lanes_detected_on_noise_image": len(lanes)}
        except Exception as exc:  # noqa: BLE001 - self-test cần bắt mọi lỗi để báo cáo
            logger.error(f"self_test() thất bại: {exc}")
            return {"ok": False, "error": str(exc)}
