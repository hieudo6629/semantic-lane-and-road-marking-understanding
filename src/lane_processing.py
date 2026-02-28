import numpy as np

def classify_lanes(lanes, image_width):

    lane_info = []

    center_x = image_width / 2

    for lane in lanes:
        xs = [pt[0] for pt in lane]
        mean_x = np.mean(xs)

        if mean_x < center_x:
            side = "left"
        else:
            side = "right"

        lane_info.append({
            "points": lane,
            "mean_x": mean_x,
            "side": side
        })

    # sort from left to right
    lane_info = sorted(lane_info, key=lambda x: x["mean_x"])

    return lane_info