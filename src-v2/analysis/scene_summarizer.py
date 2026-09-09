"""
Rút gọn/cô đặc JSON scene thô (analysis/scene_builder.py) thành các thông tin
CHÍNH thực sự cần để hiểu tình huống làn đường và hỗ trợ ra quyết định.

Bối cảnh: JSON thô (TrafficScene.to_dict()) lưu đầy đủ số liệu kỹ thuật/pixel
(tọa độ từng điểm làn, vanishing point, MSE fit, offset_pixels...) - cần thiết
để debug/tái tạo nhưng THỪA THÃI khi đưa cho LLM: LLM không cần biết
offset_pixels=97.35, chỉ cần biết "xe lệch nhẹ về bên phải". Module này KHÔNG
thay thế JSON thô (vẫn giữ nguyên, xem batch_process.py) mà tạo thêm 1 bản
rút gọn riêng, chỉ gồm 4 nhóm thông tin: số làn, vị trí ego lane + độ lệch
tâm, số làn trái/phải, hình dạng đường.

CỐ TÌNH KHÔNG đưa vào bản rút gọn: road_environment, active_speed_limit,
recommendation - các trường này trong JSON thô đang dựa trên heuristic
if-else đơn giản/giá trị fix cứng, chưa đủ bằng chứng để coi là thông tin
"chính" đáng tin cậy (vẫn giữ nguyên trong JSON thô, không xóa).

ĐÃ BỎ "road_condition" (từng suy ra từ confidence của model phát hiện làn) -
kiểm chứng bằng evaluate_road_condition.py cho thấy proxy này gần như không
có giá trị dự đoán (exact match ~29-34% so với nhãn tay 198 ảnh, kém hơn cả
việc đoán đại lớp phổ biến nhất) - không đáng tin để đưa vào bản rút gọn.
Không nằm trong mục tiêu cốt lõi (phân tích thông số làn đường ảnh hưởng
quyết định giao thông) nên bỏ qua, không đầu tư sửa sâu lane_detector.py để
lấy tín hiệu confidence thật nữa.
"""

from typing import Dict, Optional

# Ngưỡng offset_ratio_percent (đã chuẩn hóa theo bề rộng làn) để phân loại
# mức lệch tâm - lệch < 10% bề rộng làn coi như không đáng kể, > 30% là lệch
# rõ rệt (đủ để cân nhắc chỉnh lại vị trí).
OFFSET_THRESHOLD_SLIGHT = 10.0
OFFSET_THRESHOLD_SIGNIFICANT = 30.0


def _summarize_offset(vehicle_offset: Dict) -> Dict:
    """direction/magnitude/offset_percent dễ đọc, thay cho offset_pixels/lane_center_x thô."""
    direction_raw = vehicle_offset.get("direction", "unknown")

    if direction_raw == "unknown" or vehicle_offset.get("lane_width") is None:
        return {"direction": "unknown", "magnitude": "unknown", "offset_percent": None}

    percent = abs(vehicle_offset.get("offset_ratio_percent") or 0.0)

    if direction_raw == "centered" or percent < OFFSET_THRESHOLD_SLIGHT:
        magnitude = "none"
    elif percent < OFFSET_THRESHOLD_SIGNIFICANT:
        magnitude = "slight"
    else:
        magnitude = "significant"

    if "left" in direction_raw:
        direction = "left"
    elif "right" in direction_raw:
        direction = "right"
    else:
        direction = "centered"

    return {"direction": direction, "magnitude": magnitude, "offset_percent": round(percent, 1)}


def _summarize_road_shape(road_type: str) -> Dict:
    """type/severity/direction dễ đọc, thay cho chuỗi ghép road_type kiểu 'sharp_left_curve'."""
    if not road_type or road_type == "unknown":
        return {"type": "unknown", "severity": "unknown", "direction": None}

    if road_type == "straight":
        return {"type": "straight", "severity": "none", "direction": None}

    severity = "sharp" if "sharp" in road_type else "gentle"
    direction = "left" if "left" in road_type else "right" if "right" in road_type else None
    return {"type": "curve", "severity": severity, "direction": direction}


def summarize_scene(scene_dict: Dict) -> Dict:
    """
    Rút gọn 1 TrafficScene.to_dict() (JSON thô) thành các thông tin CHÍNH cho
    việc hiểu làn đường: số làn, vị trí ego lane, độ lệch tâm, số làn
    trái/phải, hình dạng đường.

    Args:
        scene_dict: dict trả về từ TrafficScene.to_dict().

    Returns:
        Dict rút gọn - xem docstring đầu file về các trường CỐ TÌNH không đưa vào.
    """
    road = scene_dict.get("road", {})
    lane = scene_dict.get("lane", {})
    geometry = road.get("geometry", {})
    ego_lane = lane.get("ego_lane", {})
    lane_classification = lane.get("lane_classification", {})
    vehicle_offset = lane.get("vehicle_offset", {})

    lane_count = geometry.get("lane_count", 0)
    left_count = lane_classification.get("left_neighbor_count", 0)
    right_count = lane_classification.get("right_neighbor_count", 0)
    # left_neighbor_count/right_neighbor_count đã đúng là SỐ LÀN 2 bên (không
    # phải số đường biên) - xem chứng minh trong lịch sử trao đổi khi hiệu
    # chỉnh road.geometry.lane_count; ego là làn thứ (left_count + 1).
    ego_lane_position = f"{left_count + 1}/{lane_count}" if lane_count > 0 else "unknown"

    return {
        "lane_count": lane_count,
        "ego_lane": {
            "position": ego_lane_position,
            "confidence": round(ego_lane.get("confidence", 0.0), 2),
        },
        "vehicle_offset": _summarize_offset(vehicle_offset),
        "neighbor_lanes": {"left_count": left_count, "right_count": right_count},
        "road_shape": _summarize_road_shape(road.get("road_type", "unknown")),
    }
