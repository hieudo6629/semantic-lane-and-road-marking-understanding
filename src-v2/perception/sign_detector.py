"""
Wrapper nhận diện biển báo giao thông bằng YOLOv8 (ultralytics).

Refactor từ src/yolo_detector.py.

BUG ĐÃ SỬA (quan trọng nhất trong file này): bản cũ dùng một dict
`SIGN_CLASSES` gồm 19 mục HARDCODE (class 0 = 'stop', class 9 = 'traffic
light', ...) để map class_id -> tên biển báo. Khi kiểm tra thực tế 2 file
model trong model/ (`traffic_sign_detector.pt`, `yolov8n_trained_best.pt`),
model thật chỉ có 15 class và thứ tự HOÀN TOÀN KHÁC:
    0 Green Light   1 Red Light   2 Speed Limit 10  3 Speed Limit 100
    4 Speed Limit 110  5 Speed Limit 120  6 Speed Limit 20  7 Speed Limit 30
    8 Speed Limit 40  9 Speed Limit 50  10 Speed Limit 60  11 Speed Limit 70
    12 Speed Limit 80  13 Speed Limit 90  14 Stop
Nghĩa là với dict cũ, mọi detection đều bị gán NHẦM tên biển báo (ví dụ
class 0 thật là "Green Light" nhưng code cũ đọc thành "stop").

Cách sửa: KHÔNG hardcode bảng tên nữa. Ultralytics tự lưu bảng
class_id -> tên lớp bên trong file .pt lúc train (`model.names`) - đây là
nguồn duy nhất đáng tin cậy, vì nó luôn khớp với đúng model đang chạy, kể
cả khi sau này đổi sang model khác (ví dụ model 94 lớp VNTSD thật).

TODO cũ về "đèn giao thông luôn trả về traffic_light_green" cũng không còn
cần thiết: model thật có 2 class riêng "Green Light" / "Red Light", tức là
màu đèn đã được chính model nhận diện, không cần suy đoán mặc định nữa.
"""

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from utils.logger import get_logger
from utils.preprocessing import validate_image

logger = get_logger(__name__)


@dataclass
class DetectedSign:
    """Kết quả detect một biển báo."""
    sign_type: str                       # Tên ngữ nghĩa đã chuẩn hóa, ví dụ "speed_limit_50", "stop"
    confidence: float
    bbox: Tuple[int, int, int, int]      # x1, y1, x2, y2 (pixel)
    relative_position: str               # "left" | "center" | "right"
    distance: str                        # "near" | "medium" | "far"
    raw_class_name: str                  # Tên gốc lấy thẳng từ model.names, chưa chuẩn hóa

    def to_dict(self) -> Dict:
        return {
            "sign_type": self.sign_type,
            "confidence": float(self.confidence),
            "bbox": list(self.bbox),
            "relative_position": self.relative_position,
            "distance": self.distance,
            "raw_class_name": self.raw_class_name,
        }


# Regex nhận diện "Speed Limit 50", "speed limit 50", "SpeedLimit50" -> lấy số 50
_SPEED_LIMIT_PATTERN = re.compile(r"speed\s*limit\s*(\d+)", re.IGNORECASE)


def normalize_sign_type(raw_class_name: str) -> str:
    """
    Chuẩn hóa tên class thô (lấy từ model.names) thành sign_type ngữ nghĩa,
    dùng thống nhất trong toàn bộ pipeline (reasoning/recommendation.py,
    analysis/scene_builder.py, ...).

    Viết dạng chuẩn hóa bằng regex/từ khóa thay vì so khớp chuỗi cứng, để
    hàm này không bị vỡ nếu đổi sang model khác có cách đặt tên hơi khác
    (ví dụ "Speed_Limit_50" hoặc "speed-limit-50km").
    """
    name = raw_class_name.strip()

    speed_match = _SPEED_LIMIT_PATTERN.search(name)
    if speed_match:
        return f"speed_limit_{speed_match.group(1)}"

    lowered = name.lower().replace("-", "_").replace(" ", "_")

    if "red" in lowered and "light" in lowered:
        return "traffic_light_red"
    if "green" in lowered and "light" in lowered:
        return "traffic_light_green"
    if "yellow" in lowered and "light" in lowered:
        return "traffic_light_yellow"
    if lowered == "stop":
        return "stop"
    if "yield" in lowered:
        return "yield"
    if "no_entry" in lowered:
        return "no_entry"
    if "pedestrian" in lowered:
        return "pedestrian_crossing"
    if "school" in lowered:
        return "school_zone"

    # Không nhận diện được ngữ nghĩa cụ thể -> giữ nguyên dạng snake_case
    # để reasoning/recommendation.py vẫn hiển thị được tên biển báo, thay vì
    # rơi vào một nhãn "unknown_class_N" vô nghĩa như bản cũ.
    return lowered


class SignDetector:
    """Wrapper YOLOv8 cho việc nhận diện biển báo giao thông."""

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.5,
        device: str = "cpu",
    ):
        """
        Args:
            model_path: đường dẫn tới file .pt đã train (bắt buộc phải tồn tại -
                        KHÔNG tự động tải model khác thay thế, vì như vậy sẽ
                        âm thầm chạy sai model mà không ai biết, giống lỗi cũ).
            confidence_threshold: ngưỡng confidence tối thiểu để giữ lại detection.
            device: "cpu" | "cuda" | "mps".
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Không tìm thấy model biển báo tại: {model_path}. "
                "Kiểm tra lại đường dẫn trong configs/config.yaml."
            )

        from ultralytics import YOLO

        logger.info(f"Đang load model biển báo từ: {model_path}")
        self.model = YOLO(model_path)
        self.model.to(device)
        self.confidence_threshold = confidence_threshold
        self.device = device

        # Đọc bảng tên lớp TRỰC TIẾP từ model, không hardcode (xem docstring đầu file)
        self.class_names: Dict[int, str] = dict(self.model.names)
        logger.info(f"Model có {len(self.class_names)} lớp: {list(self.class_names.values())}")

    def detect(
        self,
        image_bgr: np.ndarray,
        image_width: Optional[int] = None,
        image_height: Optional[int] = None,
    ) -> List[DetectedSign]:
        """
        Nhận diện biển báo trong một ảnh.

        Args:
            image_bgr: ảnh gốc, kênh BGR (kết quả cv2.imread), KHÔNG cần tự
                       chuyển RGB trước - ultralytics tự lo việc này khi nhận
                       numpy array BGR trực tiếp từ OpenCV.
            image_width, image_height: kích thước ảnh, dùng để tính vị trí
                       tương đối trái/giữa/phải. Mặc định lấy từ shape ảnh.

        Returns:
            Danh sách DetectedSign, rỗng nếu không phát hiện hoặc ảnh lỗi.
        """
        validation = validate_image(image_bgr)
        if not validation.is_valid:
            logger.warning(f"Ảnh đầu vào không hợp lệ, bỏ qua detect: {validation.issues}")
            return []

        width = image_width or validation.width
        height = image_height or validation.height

        results = self.model(image_bgr, verbose=False, conf=self.confidence_threshold)

        detected_signs: List[DetectedSign] = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                bbox = (int(x1), int(y1), int(x2), int(y2))

                cls_id = int(box.cls[0])
                raw_class_name = self.class_names.get(cls_id, f"unknown_class_{cls_id}")
                sign_type = normalize_sign_type(raw_class_name)

                detected_signs.append(
                    DetectedSign(
                        sign_type=sign_type,
                        confidence=conf,
                        bbox=bbox,
                        relative_position=self._relative_position(x1, x2, width),
                        distance=self._estimate_distance(y1, y2, x1, x2, height),
                        raw_class_name=raw_class_name,
                    )
                )

        return detected_signs

    def _relative_position(self, x1: float, x2: float, image_width: int) -> str:
        """Biển báo nằm bên trái / giữa / phải khung hình."""
        center_x = (x1 + x2) / 2
        if center_x < image_width * 0.33:
            return "left"
        if center_x > image_width * 0.66:
            return "right"
        return "center"

    def _estimate_distance(self, y1: float, y2: float, x1: float, x2: float, image_height: int) -> str:
        """
        Ước lượng khoảng cách gần/trung bình/xa dựa trên diện tích bbox và vị
        trí y. Biển báo càng gần camera thì bbox càng lớn và càng nằm thấp
        trong khung hình (giả định camera dashcam nhìn về phía trước).
        """
        avg_y = (y1 + y2) / 2
        bbox_area = (x2 - x1) * (y2 - y1)

        if avg_y > image_height * 0.55 or bbox_area > 10000:
            return "near"
        if avg_y > image_height * 0.3 or bbox_area > 4000:
            return "medium"
        return "far"

    def get_priority(self, sign_type: str) -> int:
        """
        Độ ưu tiên xử lý của biển báo: 1 = phải tuân thủ ngay lập tức,
        10 = cảnh báo, 30 = thông tin thêm. Dùng để sắp xếp thứ tự hiển thị
        và quyết định hành động trong reasoning/recommendation.py.
        """
        critical = {"stop", "no_entry", "traffic_light_red"}
        warning = {"yield", "traffic_light_yellow", "pedestrian_crossing", "school_zone"}

        if sign_type in critical:
            return 1
        if sign_type in warning:
            return 10
        if sign_type.startswith("speed_limit_"):
            return 10
        return 30

    def self_test(self) -> Dict:
        """
        Chạy thử model trên 1 ảnh giả (toàn màu xám) để xác định lỗi đến từ
        MODEL/PIPELINE (crash, exception) hay từ ẢNH ĐẦU VÀO thực tế
        (yêu cầu mục D.2 của dự án).

        Vì ảnh test là nhiễu ngẫu nhiên, kỳ vọng bình thường là KHÔNG có
        detection confidence cao nào - nếu hàm này raise exception thì lỗi
        chắc chắn nằm ở model/pipeline, không phải ở ảnh đầu vào thật.

        Lưu ý: cố tình dùng ảnh NHIỄU NGẪU NHIÊN thay vì ảnh đơn sắc, vì
        validate_image() sẽ từ chối ảnh gần như đồng nhất một màu (std thấp)
        - dùng ảnh đơn sắc ở đây sẽ khiến self-test bị chặn trước khi model
        kịp chạy, không phát hiện được lỗi thật sự nằm trong model.
        """
        rng = np.random.default_rng(seed=0)
        test_image = rng.integers(0, 255, size=(590, 1640, 3), dtype=np.uint8)
        try:
            signs = self.detect(test_image)
            return {
                "ok": True,
                "num_classes": len(self.class_names),
                "class_names": list(self.class_names.values()),
                "signs_detected_on_blank_image": len(signs),
            }
        except Exception as exc:  # noqa: BLE001 - self-test cần bắt mọi lỗi để báo cáo, không để crash pipeline
            logger.error(f"self_test() thất bại: {exc}")
            return {"ok": False, "error": str(exc)}
