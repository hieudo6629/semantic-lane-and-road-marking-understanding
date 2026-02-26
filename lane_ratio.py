import os
import cv2
import numpy as np
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt

IMAGE_ROOT = r"C:\Users\hieud\.cache\kagglehub\datasets\greatgamedota\culane\versions\7\driver_161_90frame"
LABEL_ROOT = r"C:\Users\hieud\.cache\kagglehub\datasets\greatgamedota\culane\versions\7\driver_161_90frame_labels"

image_files = glob(os.path.join(IMAGE_ROOT, "**/*.jpg"), recursive=True)

records = []

for img_path in image_files[:15000]:  # subset trước
    relative_path = os.path.relpath(img_path, IMAGE_ROOT)
    mask_path = os.path.join(LABEL_ROOT, relative_path.replace(".jpg", ".png"))

    if not os.path.exists(mask_path):
        continue

    mask = cv2.imread(mask_path, 0)  # grayscale
    h, w = mask.shape

    lane_pixels = np.sum(mask > 0)
    ratio = lane_pixels / (h * w)

    records.append([img_path, ratio])

df = pd.DataFrame(records, columns=["image_path", "lane_ratio"])
print("Total processed:", len(df))

plt.hist(df["lane_ratio"], bins=50)
plt.show()