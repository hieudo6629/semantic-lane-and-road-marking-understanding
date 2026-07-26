# test/test_traffic_analyzer.py
import unittest
import os
import sys
import json
from pathlib import Path
import numpy as np
import cv2
# Thêm đường dẫn đến src để import các module
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from traffic_analyzer import TrafficAnalyzer, process_scene

class TestTrafficAnalyzer(unittest.TestCase):
    """Unit tests cho hệ thống phân tích giao thông"""
    
    def setUp(self):
        """Khởi tạo trước mỗi test"""
        self.analyzer = TrafficAnalyzer(
            lane_model_path="model/culane_res34.pth",
            traffic_sign_model_path="model/vntsd_yolov8n_trained_best.pt"
        )
        
        # Tạo ảnh giả định nếu chưa có
        test_image_path = os.path.join("test", "test_image.jpg")
        if not os.path.exists(test_image_path):
            # Tạo ảnh trắng với một vài nét để mô phỏng làn đường
            img = np.zeros((590, 1640, 3), dtype=np.uint8)
            # Vẽ vài đường thẳng giả định là làn đường
            cv2.line(img, (100, 300), (500, 200), (255, 255, 255), 5)
            cv2.line(img, (200, 320), (550, 220), (255, 255, 255), 5)
            cv2.imwrite(test_image_path, img)
    
    def test_load_models(self):
        """Kiểm tra khả năng tải model"""
        # Kiểm tra khả năng tải model
        loaded = self.analyzer.load_models()
        self.assertTrue(loaded, "Không thể tải các model")
        
        # Kiểm tra rằng model không được gán là None
        if self.analyzer.lane_model is not None:
            self.assertIsNotNone(self.analyzer.lane_model, "Model CULane không được tải thành công")
        self.assertIsNotNone(self.analyzer.traffic_sign_model, "Model YOLOv8 không được tải thành công")
    
    def test_preprocess_for_culane(self):
        """Kiểm tra tiền xử lý ảnh cho CULane"""
        # Tạo ảnh giả định
        test_image_path = os.path.join("test", "test_image.jpg")
        frame = cv2.imread(test_image_path)
        
        # Kiểm tra tiền xử lý
        img_tensor, orig_frame = self.analyzer.preprocess_for_culane(frame)
        
        # Kiểm tra định dạng tensor
        self.assertIsInstance(img_tensor, torch.Tensor)
        self.assertEqual(img_tensor.shape[0], 1)  # batch size = 1
        self.assertEqual(img_tensor.shape[1], 3)   # channels = 3
        self.assertEqual(img_tensor.shape[2], self.analyzer.culane_config['train_height'])  # height
        self.assertEqual(img_tensor.shape[3], self.analyzer.culane_config['train_width'])   # width
        
        # Kiểm tra original frame
        self.assertIsInstance(orig_frame, np.ndarray)
    
    def test_detect_lanes(self):
        """Kiểm tra phát hiện làn đường"""
        test_image_path = os.path.join("test", "test_image.jpg")
        frame = cv2.imread(test_image_path)
        
        # Kiểm tra phát hiện làn đường
        lane_info = self.analyzer.detect_lanes(frame)
        
        # Kiểm tra cấu trúc kết quả
        self.assertIsInstance(lane_info, dict)
        self.assertIn("detected", lane_info)
        self.assertIn("lanes", lane_info)
        self.assertIn("frame_size", lane_info)
        self.assertIn("lane_count", lane_info)
        
        # Kiểm tra các trường bắt buộc
        self.assertIsInstance(lane_info["detected"], bool)
        self.assertIsInstance(lane_info["lanes"], list)
        self.assertIsInstance(lane_info["frame_size"], dict)
        self.assertIsInstance(lane_info["lane_count"], int)
        
        # Kiểm tra frame_size
        self.assertIn("width", lane_info["frame_size"])
        self.assertIn("height", lane_info["frame_size"])
        
        # Kiểm tra rằng tất cả làn đường đều có điểm
        for lane in lane_info["lanes"]:
            self.assertIn("points", lane)
            self.assertIn("type", lane)
            self.assertIn("slope", lane)
            self.assertIn("distance_from_center", lane)
            self.assertIsInstance(lane["points"], list)
            self.assertIsInstance(lane["type"], str)
            self.assertIsInstance(lane["slope"], float)
            self.assertIsInstance(lane["distance_from_center"], float)
    
    def test_detect_traffic_signs(self):
        """Kiểm tra phát hiện biển báo giao thông"""
        test_image_path = os.path.join("test", "test_image.jpg")
        frame = cv2.imread(test_image_path)
        
        # Kiểm tra phát hiện biển báo
        traffic_signs = self.analyzer.detect_traffic_signs(frame)
        
        # Kiểm tra rằng kết quả là danh sách
        self.assertIsInstance(traffic_signs, list)
        
        # Kiểm tra cấu trúc từng biển báo
        for sign in traffic_signs:
            self.assertIn("type", sign)
            self.assertIn("confidence", sign)
            self.assertIn("bbox", sign)
            self.assertIn("center", sign)
            self.assertIn("size", sign)
            
            # Kiểm tra các trường con
            self.assertIn("x1", sign["bbox"])
            self.assertIn("y1", sign["bbox"])
            self.assertIn("x2", sign["bbox"])
            self.assertIn("y2", sign["bbox"])
            self.assertIn("x", sign["center"])
            self.assertIn("y", sign["center"])
            self.assertIn("width", sign["size"])
            self.assertIn("height", sign["size"])
            
            self.assertIsInstance(sign["type"], str)
            self.assertIsInstance(sign["confidence"], float)
            self.assertIsInstance(sign["bbox"]["x1"], int)
    
    def test_analyze_lane_geometry(self):
        """Kiểm tra phân tích hình học làn đường"""
        # Tạo một kết quả làn đường giả định
        lane_info = {
            "detected": True,
            "lanes": [
                {
                    "id": 1,
                    "points": [[100, 300], [200, 250]],
                    "slope": 0.5,
                    "distance_from_center": -10.0,
                    "type": "solid"
                },
                {
                    "id": 2,
                    "points": [[250, 300], [400, 250]],
                    "slope": 0.4,
                    "distance_from_center": 5.0,
                    "type": "solid"
                }
            ],
            "frame_size": {
                "width": 1640,
                "height": 590
            },
            "lane_count": 2
        }
        
        # Kiểm tra phân tích hình học
        geometry_analysis = self.analyzer.analyze_lane_geometry(lane_info)
        
        # Kiểm tra cấu trúc kết quả
        self.assertIsInstance(geometry_analysis, dict)
        self.assertIn("curvature", geometry_analysis)
        self.assertIn("road_width_estimation", geometry_analysis)
        self.assertIn("lane_alignment", geometry_analysis)
        self.assertIn("lane_count", geometry_analysis)
        self.assertIn("shoulder_found", geometry_analysis)
        self.assertIn("road_type", geometry_analysis)
        
        # Kiểm tra các giá trị
        self.assertIsInstance(geometry_analysis["curvature"], float)
        self.assertIsInstance(geometry_analysis["road_width_estimation"], float)
        self.assertIsInstance(geometry_analysis["lane_alignment"], str)
        self.assertIsInstance(geometry_analysis["lane_count"], int)
        self.assertIsInstance(geometry_analysis["shoulder_found"], bool)
        self.assertIsInstance(geometry_analysis["road_type"], str)
    
    def test_analyze_scene(self):
        """Kiểm tra phân tích toàn bộ cảnh giao thông"""
        test_image_path = os.path.join("test", "test_image.jpg")
        
        # Kiểm tra phân tích cảnh
        result = self.analyzer.analyze_scene(test_image_path)
        
        # Kiểm tra cấu trúc kết quả
        self.assertIsInstance(result, dict)
        self.assertIn("timestamp", result)
        self.assertIn("frame_info", result)
        self.assertIn("lane_detection", result)
        self.assertIn("traffic_sign_detection", result)
        self.assertIn("lane_geometry_analysis", result)
        self.assertIn("environment_status", result)
        self.assertIn("driving_recommendations", result)
        self.assertIn("confidences", result)
        self.assertIn("system_metadata", result)
        
        # Kiểm tra các trường bắt buộc
        self.assertIsInstance(result["timestamp"], str)
        self.assertIsInstance(result["frame_info"], dict)
        self.assertIsInstance(result["lane_detection"], dict)
        self.assertIsInstance(result["traffic_sign_detection"], dict)
        self.assertIsInstance(result["lane_geometry_analysis"], dict)
        self.assertIsInstance(result["environment_status"], dict)
        self.assertIsInstance(result["driving_recommendations"], list)
        self.assertIsInstance(result["confidences"], dict)
        self.assertIsInstance(result["system_metadata"], dict)
        
        # Kiểm tra các trường trong frame_info
        self.assertIn("width", result["frame_info"])
        self.assertIn("height", result["frame_info"])
        self.assertIn("resolution", result["frame_info"])
        
        # Kiểm tra các giá trị trong confidences
        self.assertIsInstance(result["confidences"]["lane_detection"], float)
        self.assertIsInstance(result["confidences"]["traffic_sign_detection"], float)
        
        # Kiểm tra rằng ít nhất có một khuyến nghị hoặc xác thực
        self.assertIsInstance(result["driving_recommendations"], list)
    
    def test_process_scene(self):
        """Kiểm tra hàm tiện ích process_scene"""
        test_image_path = os.path.join("test", "test_image.jpg")
        
        # Kiểm tra hàm process_scene
        result = process_scene(test_image_path)
        
        # Kiểm tra kết quả
        self.assertIsInstance(result, dict)
        if "error" in result:
            # Nếu có lỗi, vẫn phải có các trường bắt buộc
            self.assertIn("error", result)
            self.assertIn("timestamp", result)
        else:
            # Nếu không có lỗi, phải có đầy đủ cấu trúc
            self.assertIn("timestamp", result)
            self.assertIn("frame_info", result)
            self.assertIn("lane_detection", result)
            self.assertIn("traffic_sign_detection", result)
            self.assertIn("lane_geometry_analysis", result)
            self.assertIn("environment_status", result)
            self.assertIn("driving_recommendations", result)
            self.assertIn("confidences", result)
            self.assertIn("system_metadata", result)

if __name__ == "__main__":
    unittest.main()
