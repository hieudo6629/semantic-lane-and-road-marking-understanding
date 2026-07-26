"""
Tiền xử lý ảnh dashcam trước khi đưa vào các model nhận diện.

Module này tách riêng phần tiền xử lý (resize, normalize, crop) ra khỏi
wrapper của từng model để:
1. Có thể unit-test tiền xử lý độc lập, không cần load model nặng.
2. Có hàm validate_image() dùng để kiểm tra nhanh "lỗi detection đến từ
   ảnh đầu vào sai định dạng hay từ chính model" (yêu cầu mục D của dự án).

Lưu ý quan trọng về hệ trục tọa độ:
- OpenCV (cv2.imread) đọc ảnh theo thứ tự kênh BGR.
- Model Ultra-Fast-Lane-Detection-v2 (và hầu hết model torchvision) được
  huấn luyện với ảnh RGB đã chuẩn hóa theo thống kê ImageNet.
- Nếu quên đổi BGR -> RGB, model vẫn chạy được (không lỗi runtime) nhưng
  cho kết quả sai lệch một cách âm thầm -> đây là lỗi rất hay gặp và khó
  phát hiện nếu không có hàm kiểm tra riêng.
"""

from dataclasses import dataclass, field
from typing import List, Tuple

import cv2
import numpy as np
import torch

from utils.logger import get_logger

logger = get_logger(__name__)

# Thống kê chuẩn hóa ImageNet - dùng chung cho các model backbone ResNet
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


@dataclass
class ImageValidationResult:
    """Kết quả kiểm tra ảnh đầu vào."""

    is_valid: bool
    width: int
    height: int
    channels: int
    dtype: str
    issues: List[str] = field(default_factory=list)


def validate_image(image: np.ndarray) -> ImageValidationResult:
    """
    Kiểm tra ảnh đầu vào có hợp lệ để đưa vào pipeline hay không.

    Dùng hàm này TRƯỚC khi debug model, để loại trừ khả năng lỗi
    detection đến từ ảnh đầu vào sai định dạng (kênh màu sai, ảnh quá nhỏ,
    ảnh toàn đen do đọc file lỗi, v.v.) thay vì đến từ chính model.

    Args:
        image: ảnh dạng numpy array (kết quả của cv2.imread).

    Returns:
        ImageValidationResult liệt kê các vấn đề tìm thấy (nếu có).
    """
    issues: List[str] = []

    if image is None:
        return ImageValidationResult(
            is_valid=False, width=0, height=0, channels=0, dtype="None",
            issues=["Ảnh là None - có thể cv2.imread() đọc file thất bại (sai đường dẫn?)"],
        )

    if image.ndim != 3:
        issues.append(f"Ảnh phải có 3 chiều (H, W, C), hiện có {image.ndim} chiều")

    height, width = image.shape[0], image.shape[1]
    channels = image.shape[2] if image.ndim == 3 else 1

    if channels != 3:
        issues.append(f"Ảnh phải có 3 kênh màu (BGR/RGB), hiện có {channels} kênh")

    if width < 64 or height < 64:
        issues.append(f"Ảnh quá nhỏ ({width}x{height}), có thể đã bị resize/crop nhầm trước đó")

    if image.dtype != np.uint8:
        issues.append(f"Ảnh nên có dtype uint8 (giá trị 0-255), hiện là {image.dtype}")

    # Ảnh gần như đồng nhất một màu (std rất thấp) thường là dấu hiệu đọc file lỗi
    # hoặc camera bị che, không phải lỗi từ model.
    if image.size > 0 and float(np.std(image)) < 2.0:
        issues.append(
            f"Ảnh gần như đồng nhất một màu (std={float(np.std(image)):.2f}) - "
            "kiểm tra lại nguồn ảnh (camera bị che, file hỏng, hoặc đọc nhầm frame đen)"
        )

    return ImageValidationResult(
        is_valid=len(issues) == 0,
        width=width,
        height=height,
        channels=channels,
        dtype=str(image.dtype),
        issues=issues,
    )


def resize_keep_ratio_then_crop(
    image_bgr: np.ndarray,
    target_width: int,
    resized_height: int,
    crop_height: int,
) -> np.ndarray:
    """
    Resize ảnh về (resized_height, target_width) rồi cắt lấy phần dưới cao crop_height.

    Đây chính là bước tiền xử lý mà Ultra-Fast-Lane-Detection-v2 dùng khi test/infer
    (xem Ultra-Fast-Lane-Detection-v2/demo.py + data/dataset.py:LaneTestDataset):
    resize ảnh cao hơn kích thước train, rồi crop lấy phần đáy ảnh (nơi có mặt đường),
    bỏ phần trời/ngọn cây phía trên - giúp model tập trung vào vùng làn đường.

    Args:
        image_bgr: ảnh gốc, kênh BGR (từ cv2.imread), giá trị 0-255.
        target_width: chiều rộng sau resize (ví dụ 1600 cho culane_res34).
        resized_height: chiều cao sau resize, TRƯỚC khi crop (ví dụ 320/0.6 ≈ 533).
        crop_height: chiều cao giữ lại sau khi crop từ đáy ảnh lên (ví dụ 320).

    Returns:
        Ảnh BGR đã resize + crop, shape (crop_height, target_width, 3).
    """
    resized = cv2.resize(image_bgr, (target_width, resized_height), interpolation=cv2.INTER_LINEAR)
    cropped = resized[-crop_height:, :, :]
    return cropped


def bgr_to_normalized_tensor(
    image_bgr: np.ndarray,
    mean: Tuple[float, float, float] = IMAGENET_MEAN,
    std: Tuple[float, float, float] = IMAGENET_STD,
) -> torch.Tensor:
    """
    Chuyển ảnh BGR uint8 (H, W, C) thành tensor RGB đã chuẩn hóa (1, C, H, W).

    Đây là bước hay bị làm sai nhất trong pipeline: quên đổi BGR->RGB,
    hoặc quên chia 255 trước khi chuẩn hóa. Hàm này gộp cả 2 bước để
    tránh lặp lại logic (và lặp lại lỗi) ở nhiều nơi trong code.

    Args:
        image_bgr: ảnh BGR uint8, giá trị 0-255.
        mean: giá trị trung bình dùng để chuẩn hóa từng kênh RGB.
        std: độ lệch chuẩn dùng để chuẩn hóa từng kênh RGB.

    Returns:
        Tensor float32 shape (1, 3, H, W), đã chuẩn hóa, sẵn sàng đưa vào model.
    """
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_float = image_rgb.astype(np.float32) / 255.0

    mean_arr = np.array(mean, dtype=np.float32)
    std_arr = np.array(std, dtype=np.float32)
    image_norm = (image_float - mean_arr) / std_arr

    # (H, W, C) -> (C, H, W) -> thêm batch dimension -> (1, C, H, W)
    tensor = torch.from_numpy(image_norm.transpose(2, 0, 1)).unsqueeze(0)
    return tensor


def check_tensor_stats(tensor: torch.Tensor) -> dict:
    """
    Kiểm tra nhanh thống kê của tensor đầu vào model - dùng để debug.

    Tensor đã chuẩn hóa đúng theo ImageNet thường có mean gần 0 và
    std xấp xỉ 1. Nếu mean lệch xa 0 (ví dụ > 2.0 hoặc < -2.0), rất có thể
    bước normalize đã bị làm sai (quên chia 255, hoặc dùng sai mean/std).

    Args:
        tensor: tensor ảnh sau khi qua bgr_to_normalized_tensor().

    Returns:
        dict chứa min/max/mean/std và cảnh báo nếu giá trị bất thường.
    """
    stats = {
        "shape": tuple(tensor.shape),
        "min": float(tensor.min()),
        "max": float(tensor.max()),
        "mean": float(tensor.mean()),
        "std": float(tensor.std()),
        "warning": None,
    }
    if abs(stats["mean"]) > 2.5 or stats["std"] > 3.0:
        stats["warning"] = (
            "Thống kê tensor bất thường so với ảnh đã chuẩn hóa ImageNet "
            "(mean nên gần 0, std nên gần 1) - kiểm tra lại bước normalize."
        )
        logger.warning(stats["warning"])
    return stats
