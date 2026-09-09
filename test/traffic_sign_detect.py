import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt

# Load model
# model_path = 'model/yolov8n_trained_best.pt'  # Đường dẫn đến file .pt của bạn
model_path = r'C:\Users\Hieu\IdeaProjects\Semantic Traffic\model\yolov8n.pt'
model = YOLO(model_path)

# Đường dẫn ảnh input
image_path = r'C:\Users\Hieu\IdeaProjects\Semantic Traffic\semantic-road-marking-understanding\src-v2\input-traffic-sign\116.jpg'  # Đường dẫn đến ảnh cần detect

# Chạy detection
results = model(image_path)

# Hiển thị kết quả
for r in results:
    im_array = r.plot()  # Vẽ bounding boxes lên ảnh
    im_array = cv2.cvtColor(im_array, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(10, 10))
    plt.imshow(im_array)
    plt.axis('off')
    plt.show()

# In thông tin chi tiết
for r in results:
    boxes = r.boxes
    if boxes is not None:
        for box in boxes:
            xyxy = box.xyxy[0].tolist()  # Tọa độ [x1, y1, x2, y2]
            conf = box.conf[0].item()     # Confidence score
            cls = box.cls[0].item()       # Class ID
            print(f"Class: {int(cls)}, Confidence: {conf:.05f}, Box: {xyxy}")