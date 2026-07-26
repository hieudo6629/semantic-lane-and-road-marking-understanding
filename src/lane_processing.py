import numpy as np


def classify_lanes(lanes, image_width):
    """
    Phân loại và phân tích các làn đường.

    Args:
        lanes: danh sách các lane points từ annotation
        image_width: chiều rộng ảnh

    Returns:
        dict chứa:
        - all_lanes: tất cả lanes (sorted từ trái sang phải)
        - same_direction_lanes: lanes cùng chiều (bên phải center)
        - opposite_direction_lanes: lanes ngược chiều (bên trái center)
        - same_direction_count: số làn cùng chiều
        - total_lanes: tổng số lane lines
    """
    lane_info = []

    center_x = image_width / 2

    for i, lane in enumerate(lanes):
        xs = [pt[0] for pt in lane]
        mean_x = np.mean(xs)

        if mean_x < center_x:
            side = "opposite"  # Ngược chiều (bên trái)
        else:
            side = "same_direction"  # Cùng chiều (bên phải)

        lane_info.append({
            "id": i,
            "points": lane,
            "mean_x": mean_x,
            "side": side  # "same_direction" hoặc "opposite"
        })

    # Sort từ trái sang phải
    lane_info = sorted(lane_info, key=lambda x: x["mean_x"])

    # Đếm lanes cùng chiều
    same_direction_count = sum(1 for lane in lane_info if lane["side"] == "same_direction")

    # Cập nhật lại lane index cho lanes cùng chiều (để đếm 1, 2 thay vì index gốc)
    current_same_idx = 0
    for lane in lane_info:
        if lane["side"] == "same_direction":
            lane["same_direction_index"] = current_same_idx
            current_same_idx += 1
        else:
            lane["same_direction_index"] = None

    result = {
        "all_lanes": lane_info,
        "total_lanes": len(lane_info),
        "same_direction_lanes": [l for l in lane_info if l["side"] == "same_direction"],
        "opposite_direction_lanes": [l for l in lane_info if l["side"] == "opposite"],
        "same_direction_count": same_direction_count
    }

    return result


def filter_same_direction_lanes(lane_info):
    """Lọc chỉ lấy lanes cùng chiều."""
    if isinstance(lane_info, dict):
        return lane_info["same_direction_lanes"]
    return [lane for lane in lane_info if lane.get("side") == "same_direction"]