import os
import sys

ROOT = "Ultra-Fast-Lane-Detection-v2"

os.chdir(ROOT)

sys.path.append(os.getcwd())

from model.model_culane  import parsingNet

print("Import OK")
import torch
import cv2
import numpy as np
from matplotlib import pyplot as plt

from model.model_culane  import parsingNet
from utils.config import Config
from utils.common import merge_config, get_model
cfg = Config.fromfile("configs/culane_res34.py")
# =========================================================
# CULANE ANCHORS
# =========================================================
cfg.row_anchor = np.linspace(0.42, 1, cfg.num_row)

cfg.col_anchor = np.linspace(0, 1, cfg.num_col)
# =========================
# CONFIG
# =========================

MODEL_PATH = r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\model\culane_res34.pth"
# IMAGE_PATH = r"C:\Users\Hieu\.cache\kagglehub\datasets\greatgamedota\culane\versions\7\driver_161_90frame\06031125_0817.MP4\00270.jpg"
IMAGE_PATH = r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\image_test\10095_2.jpg"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# LOAD MODEL
# =========================

net = get_model(cfg).to(DEVICE)

ckpt = torch.load(MODEL_PATH, map_location=DEVICE)

state_dict = ckpt['model']

# remove DataParallel prefix
new_state_dict = {}

for k, v in state_dict.items():

    if k.startswith("module."):
        k = k[7:]

    new_state_dict[k] = v

state_dict = new_state_dict

net.load_state_dict(state_dict)

print("Model loaded successfully!")

# =========================
# OFFICIAL DECODER
# =========================

def pred2coords(
    pred,
    row_anchor,
    col_anchor,
    local_width=1,
    original_image_width=1640,
    original_image_height=590
):

    batch_size, num_grid_row, num_cls_row, num_lane_row = pred['loc_row'].shape
    batch_size, num_grid_col, num_cls_col, num_lane_col = pred['loc_col'].shape

    max_indices_row = pred['loc_row'].argmax(1).cpu()
    valid_row = pred['exist_row'].argmax(1).cpu()

    max_indices_col = pred['loc_col'].argmax(1).cpu()
    valid_col = pred['exist_col'].argmax(1).cpu()

    pred['loc_row'] = pred['loc_row'].cpu()
    pred['loc_col'] = pred['loc_col'].cpu()

    coords = []

    # row_lane_idx = [1, 2]
    # col_lane_idx = [0, 3]
    row_lane_idx = [0,1,2,3]
    col_lane_idx = [0,1,2,3]

    # ROW LANES
    for i in row_lane_idx:
        print(valid_row[0,:,i].sum())

        tmp = []

        if valid_row[0, :, i].sum() > num_cls_row / 2:

            for k in range(valid_row.shape[1]):

                if valid_row[0, k, i]:

                    all_ind = torch.tensor(
                        list(
                            range(
                                max(0, max_indices_row[0, k, i] - local_width),
                                min(num_grid_row - 1,
                                    max_indices_row[0, k, i] + local_width) + 1
                            )
                        )
                    )

                    out_tmp = (
                        pred['loc_row'][0, all_ind, k, i].softmax(0)
                        * all_ind.float()
                    ).sum() + 0.5

                    out_tmp = out_tmp / (num_grid_row - 1) * original_image_width

                    tmp.append(
                        (
                            int(out_tmp),
                            int(row_anchor[k] * original_image_height)
                        )
                    )

            coords.append(tmp)

    # COLUMN LANES
    for i in col_lane_idx:
        print(valid_col[0,:,i].sum())
        tmp = []

        if valid_col[0, :, i].sum() > num_cls_col / 4:

            for k in range(valid_col.shape[1]):

                if valid_col[0, k, i]:

                    all_ind = torch.tensor(
                        list(
                            range(
                                max(0, max_indices_col[0, k, i] - local_width),
                                min(num_grid_col - 1,
                                    max_indices_col[0, k, i] + local_width) + 1
                            )
                        )
                    )

                    out_tmp = (
                        pred['loc_col'][0, all_ind, k, i].softmax(0)
                        * all_ind.float()
                    ).sum() + 0.5

                    out_tmp = out_tmp / (num_grid_col - 1) * original_image_height

                    tmp.append(
                        (
                            int(col_anchor[k] * original_image_width),
                            int(out_tmp)
                        )
                    )

            coords.append(tmp)

    return coords


# =========================
# LOAD IMAGE
# =========================

from PIL import Image
import torchvision.transforms as transforms

img_pil = Image.open(IMAGE_PATH).convert("RGB")

orig = cv2.imread(IMAGE_PATH)

H, W = orig.shape[:2]

img_transforms = transforms.Compose([
    transforms.Resize(
        (
            int(cfg.train_height / cfg.crop_ratio),
            cfg.train_width
        )
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        (0.485, 0.456, 0.406),
        (0.229, 0.224, 0.225)
    ),
])

img_tensor = img_transforms(img_pil)

# CROP BOTTOM
img_tensor = img_tensor[
    :,
    -cfg.train_height:,
    :
]

img_tensor = img_tensor.unsqueeze(0).to(DEVICE)

print("Input tensor shape:", img_tensor.shape)

# =========================
# INFERENCE
# =========================

net.eval()

with torch.no_grad():

    pred = net(img_tensor)

print("Prediction keys:", pred.keys())

# =========================
# DECODE
# =========================

coords = pred2coords(
    pred,
    cfg.row_anchor,
    cfg.col_anchor,
    original_image_width=W,
    original_image_height=H
)

print("Detected lanes:", len(coords))

# =========================
# DRAW LANE POINTS
# =========================

vis = orig.copy()

for lane in coords:

    for coord in lane:

        cv2.circle(
            vis,
            coord,
            5,
            (0, 255, 0),
            -1
        )

# =========================
# SAVE RESULT
# =========================

cv2.imwrite("result.jpg", vis)

print("Saved result.jpg")

# =========================
# SAVE RESULT.TXT THEO ĐỊNH DẠNG CULANE
# =========================

def save_culane_format(coords, output_path="result.txt"):
    """
    Lưu file kết quả theo đúng định dạng CULane.
    Mỗi dòng là một lane: x1 y1 x2 y2 ... xn yn
    Kết thúc bằng dòng trống hoặc (0, 0)
    """
    with open(output_path, 'w') as f:
        for lane in coords:
            if not lane:
                f.write("\n")
                continue
            
            # Sắp xếp các điểm theo y tăng dần (từ trên xuống dưới)
            sorted_lane = sorted(lane, key=lambda p: p[1])
            
            # Ghi các điểm x y cách nhau bởi khoảng trắng
            points_str = []
            for x, y in sorted_lane:
                points_str.append(f"{x} {y}")
            
            f.write(" ".join(points_str) + "\n")
        
        # Thêm dòng trống kết thúc (theo chuẩn CULane)
        f.write("\n")
    
    print(f"Saved CULane format: {output_path}")

# Lưu file CULane format
save_culane_format(coords, "result.txt")

# =========================
# SHOW RESULT
# =========================

vis_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(14, 8))

plt.imshow(vis_rgb)

plt.axis("off")

plt.title("UltraFast Lane Detection V2")

plt.show()