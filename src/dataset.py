import os
import cv2

class CULaneDataset:
    def __init__(self, root_dir):
        # Thư mục gốc chứa dữ liệu CULane
        self.root_dir = root_dir
        # Thư mục chứa ảnh trong tập dữ liệu (ví dụ: driver_161_90frame)
        self.image_root = os.path.join(root_dir, "driver_161_90frame")
        # Danh sách các mẫu (ảnh + annotation)
        self.samples = self._scan_dataset()

    def _scan_dataset(self):
        # Hàm quét toàn bộ dataset để lấy danh sách ảnh và annotation tương ứng
        samples = []

        # Duyệt qua từng thư mục video trong image_root
        for video_folder in os.listdir(self.image_root):
            video_path = os.path.join(self.image_root, video_folder)

            # Bỏ qua nếu không phải thư mục
            if not os.path.isdir(video_path):
                continue

            # Duyệt qua từng file trong thư mục video
            for file in os.listdir(video_path):
                # Chỉ lấy các file ảnh có đuôi .jpg
                if file.endswith(".jpg"):
                    img_path = os.path.join(video_path, file)
                    # Annotation có cùng tên file nhưng đuôi là .lines.txt
                    ann_path = img_path.replace(".jpg", ".lines.txt")

                    # Nếu annotation tồn tại thì thêm vào danh sách mẫu
                    if os.path.exists(ann_path):
                        samples.append((img_path, ann_path))

        print(f"Found {len(samples)} samples.")  # In ra số lượng mẫu tìm được
        return samples

    def __len__(self):
        # Trả về số lượng mẫu trong dataset
        return len(self.samples)

    def get_item(self, idx):
        # Lấy một mẫu theo chỉ số idx
        img_path, ann_path = self.samples[idx]

        # Đọc ảnh bằng OpenCV
        image = cv2.imread(img_path)
        # Đọc annotation (tọa độ các lane)
        lanes = self._load_annotation(ann_path)

        # Trả về ảnh, danh sách lane, và đường dẫn ảnh
        return image, lanes, img_path

    def _load_annotation(self, ann_path):
        # Hàm đọc annotation từ file .lines.txt
        lanes = []

        with open(ann_path, "r") as f:
            for line in f:
                # Mỗi dòng chứa danh sách tọa độ (x1 y1 x2 y2 ...)
                coords = list(map(float, line.strip().split()))
                # Gom các cặp (x, y) thành một lane
                lane = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
                lanes.append(lane)

        return lanes