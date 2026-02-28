import cv2
import random

def draw_lanes(image, lanes):
    vis = image.copy()

    for lane in lanes:
        color = (
            random.randint(0,255),
            random.randint(0,255),
            random.randint(0,255)
        )

        for i in range(len(lane)-1):
            pt1 = (int(lane[i][0]), int(lane[i][1]))
            pt2 = (int(lane[i+1][0]), int(lane[i+1][1]))

            cv2.line(vis, pt1, pt2, color, 2)

    return vis