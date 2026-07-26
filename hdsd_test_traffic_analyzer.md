# README.md

# Semantic Road Marking Understanding System

Một hệ thống trí tuệ nhân tạo để hiểu cấu trúc giao thông trong thế giới thực bằng cách tích hợp:
- Phát hiện làn đường với CULane ResNet34
- Phát hiện biển báo giao thông với YOLOv8 (vntsd_yolov8n_trained_best)
- Phân tích hình học làn đường
- Tạo mô tả JSON toàn diện về môi trường giao thông

## Các thành phần chính

1. **TrafficAnalyzer**: Lõi hệ thống xử lý đa bước
2. **Lane Detection**: Phát hiện các đường làn bằng CULane
3. **Traffic Sign Detection**: Nhận diện biển báo giao thông với YOLOv8
4. **Geometry Analysis**: Phân tích độ cong, chiều rộng, vị trí làn đường
5. **Environment Description**: Tạo JSON mô tả chi tiết môi trường giao thông

## Cách cài đặt

```bash
# 1. Tạo môi trường ảo (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc venv\Scripts\activate  # Windows

# 2. Cài đặt dependency
pip install -r requirements.txt

# 3. Tải mô hình
# Đặt mô hình CULane vào thư mục model: culane_res34.pt
# Đặt mô hình YOLOv8 vào thư mục model: vntsd_yolov8n_trained_best.pt

# 4. Chạy hệ thống
python src/main.py
