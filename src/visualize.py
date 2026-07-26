import cv2
import random
import numpy as np


def draw_lanes(image, lanes, ego_lane_info=None, vehicle_offset=None, show_labels=True):
    """
    Vẽ các lane trên ảnh với highlight cho ego lane.

    Args:
        image: ảnh gốc
        lanes: danh sách các lane points
        ego_lane_info: thông tin ego lane (ego_lane_index, left_boundary, right_boundary)
        vehicle_offset: thông tin offset của xe
        show_labels: có hiển thị nhãn không

    Returns:
        ảnh đã vẽ lanes
    """
    vis = image.copy()
    image_height, image_width = image.shape[:2]

    # Màu cố định cho mỗi lane
    colors = [
        (0, 255, 0),    # xanh lá - lane 0
        (255, 0, 0),    # đỏ - lane 1
        (0, 0, 255),    # xanh dương - lane 2
        (255, 255, 0),  # vàng - lane 3
        (255, 0, 255),  # tím - lane 4
        (0, 255, 255),  # cyan - lane 5
    ]

    # Vẽ tất cả các lane
    for i, lane in enumerate(lanes):
        color = colors[i % len(colors)]

        # Vẽ dày hơn cho ego lane
        thickness = 3 if ego_lane_info and i == ego_lane_info.get("ego_lane_index") else 2

        for j in range(len(lane) - 1):
            pt1 = (int(lane[j][0]), int(lane[j][1]))
            pt2 = (int(lane[j + 1][0]), int(lane[j + 1][1]))
            cv2.line(vis, pt1, pt2, color, thickness)

        # Vẽ nhãn cho mỗi lane
        if show_labels and len(lane) > 0:
            # Lấy điểm gần bottom
            bottom_point = max(lane, key=lambda p: p[1])
            label = f"L{i} ({'EGO' if ego_lane_info and i == ego_lane_info.get('ego_lane_index') else ''})"
            cv2.putText(vis, label, (int(bottom_point[0]) + 10, int(bottom_point[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Vẽ vehicle position (center của ảnh)
    vehicle_x = image_width // 2
    vehicle_y = image_height - 50

    # Vẽ đường thẳng đứng tại vị trí xe
    cv2.line(vis, (vehicle_x, vehicle_y - 30), (vehicle_x, vehicle_y + 30), (255, 255, 255), 2)

    # Vẽ mũi tên chỉ hướng đi (đi xuống = đi về phía trước)
    cv2.arrowedLine(vis, (vehicle_x, vehicle_y + 10), (vehicle_x, vehicle_y + 40), (255, 255, 255), 2)

    # Vẽ vòng tròn tại vị trí xe
    cv2.circle(vis, (vehicle_x, vehicle_y), 8, (255, 255, 255), -1)
    cv2.circle(vis, (vehicle_x, vehicle_y), 8, (0, 0, 0), 2)

    # Vẽ ego lane boundaries nếu có
    if ego_lane_info:
        left_idx = ego_lane_info.get("left_boundary")
        right_idx = ego_lane_info.get("right_boundary")

        # Tô màu vùng ego lane (giữa left_boundary và right_boundary)
        if left_idx is not None and right_idx is not None and left_idx < len(lanes) and right_idx < len(lanes):
            left_lane = lanes[left_idx]
            right_lane = lanes[right_idx]

            # Tạo polygon cho vùng ego lane
            left_points = sorted(left_lane, key=lambda p: p[1])
            right_points = sorted(right_lane, key=lambda p: p[1])

            # Lấy điểm từ bottom lên
            bottom_left = left_points[-1] if len(left_points) > 0 else None
            bottom_right = right_points[-1] if len(right_points) > 0 else None
            top_left = left_points[0] if len(left_points) > 0 else None
            top_right = right_points[0] if len(right_points) > 0 else None

            if all([bottom_left, bottom_right, top_left, top_right]):
                pts = np.array([
                    [bottom_left[0], bottom_left[1]],
                    [bottom_right[0], bottom_right[1]],
                    [top_right[0], top_right[1]],
                    [top_left[0], top_left[1]]
                ], np.int32)

                pts = pts.reshape((-1, 1, 2))
                overlay = vis.copy()
                cv2.fillPoly(overlay, [pts], (100, 200, 100, 50))
                cv2.addWeighted(vis, 0.7, overlay, 0.3, 0, vis)
                cv2.polylines(vis, [pts], True, (100, 200, 100), 2)

        # Vẽ điểm giữa của ego lane
        ego_idx = ego_lane_info.get("ego_lane_index")
        if ego_idx is not None and ego_idx < len(lanes):
            ego_center_x = image_width // 2  # Tạm tính
            for pt in lanes[ego_idx]:
                if abs(pt[1] - vehicle_y) < 30:
                    ego_center_x = pt[0]
                    break

    # Hiển thị vehicle offset nếu có
    if vehicle_offset:
        offset_text = f"Offset: {vehicle_offset['offset_pixels']:.1f}px ({vehicle_offset['direction']})"
        cv2.putText(vis, offset_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return vis