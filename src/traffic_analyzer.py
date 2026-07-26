# src/traffic_analyzer.py
import cv2
import numpy as np
import json
import os
import torch
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrafficAnalyzer:
    """ Hệ thống phân tích giao thông toàn diện: 
    1. Phát hiện làn đường bằng CULane 
    2. Phân tích đặc điểm làn đường 
    3. Phát hiện biển báo giao thông bằng YOLOv8 
    4. Xây dựng JSON mô tả trạng thái giao thông """
    
    def __init__(self, lane_model_path: str, traffic_sign_model_path: str):
        """ Khởi tạo bộ phân tích giao thông
        Args:
            lane_model_path: Đường dẫn đến model phát hiện làn đường (CULane)
            traffic_sign_model_path: Đường dẫn đến model phát hiện biển báo (YOLOv8)
        """
        self.lane_model_path = lane_model_path
        self.traffic_sign_model_path = traffic_sign_model_path
        self.lane_model = None
        self.traffic_sign_model = None
        self.loaded = False
        
        # Thông tin cấu hình CULane lấy từ file configs/culane_res34.py
        self.culane_config = {
            'train_height': 288,
            'train_width': 800,
            'crop_ratio': 0.8,
            'num_row': 18,  # num_row trong configs/culane_res34.py
            'num_col': 100,  # num_col trong configs/culane_res34.py
            'row_anchor': None,  # sẽ được tính sau
            'col_anchor': None,  # sẽ được tính sau
            'griding_col': 100,  # num_col
            'griding_row': 18,   # num_row
            'original_image_height': 590,
            'original_image_width': 1640
        }
        
        # Tính toán row_anchor và col_anchor từ config
        self.culane_config['row_anchor'] = np.linspace(0.42, 1, self.culane_config['num_row'])
        self.culane_config['col_anchor'] = np.linspace(0, 1, self.culane_config['num_col'])
        
        # Các tham số để chuyển đổi kết quả
        self.local_width = 1
        
    def load_models(self) -> bool:
        """ Tải các model cần thiết """
        try:
            # Tải model phát hiện làn đường (CULane)
            logger.info(f"Đang tải model phát hiện làn đường: {self.lane_model_path}")
            if not os.path.exists(self.lane_model_path):
                logger.error(f"Không tìm thấy model làn đường tại: {self.lane_model_path}")
                return False
            
            # Tải mô hình CULane
            try:
                from model.model_culane import parsingNet, get_model
                from utils.config import Config
                from utils.common import merge_config
                
                # Load config
                config_path = os.path.join(os.path.dirname(__file__), "../configs/culane_res34.py")
                if not os.path.exists(config_path):
                    logger.warning(f"Config file không tìm thấy: {config_path}, sử dụng cấu hình mặc định")
                    # Tạo cấu hình mặc định
                    cfg = {
                        "num_row": self.culane_config['num_row'],
                        "num_col": self.culane_config['num_col'],
                        "train_height": self.culane_config['train_height'],
                        "train_width": self.culane_config['train_width'],
                        "crop_ratio": self.culane_config['crop_ratio'],
                        "row_anchor": self.culane_config['row_anchor'],
                        "col_anchor": self.culane_config['col_anchor']
                    }
                else:
                    cfg = Config.fromfile(config_path)
                
                # Tạo và load model
                self.lane_model = get_model(cfg).to('cuda' if torch.cuda.is_available() else 'cpu')
                
                # Load weights
                ckpt = torch.load(self.lane_model_path, map_location='cpu')
                state_dict = ckpt['model']
                
                # Loại bỏ tiền tố 'module.' từ tên layer (nếu có DataParallel)
                new_state_dict = {}
                for k, v in state_dict.items():
                    if k.startswith("module."):
                        k = k[7:]
                    new_state_dict[k] = v
                
                self.lane_model.load_state_dict(new_state_dict)
                self.lane_model.eval()
                logger.info("Đã tải thành công model CULane")
                
            except Exception as e:
                logger.error(f"Lỗi khi tải mô hình CULane: {str(e)}")
                logger.info("Chuyển sang chế độ fallback để phát hiện làn đường")
                self.lane_model = None
            
            # Tải model YOLOv8 cho biển báo giao thông
            logger.info(f"Đang tải model phát hiện biển báo: {self.traffic_sign_model_path}")
            try:
                from ultralytics import YOLO
                self.traffic_sign_model = YOLO(self.traffic_sign_model_path)
                logger.info("Đã tải thành công model YOLOv8 cho biển báo giao thông")
            except ImportError:
                logger.error("Không tìm thấy thư viện ultralytics. Vui lòng cài đặt: pip install ultralytics")
                return False
            except Exception as e:
                logger.error(f"Lỗi khi tải model YOLOv8: {str(e)}")
                return False
            
            self.loaded = True
            logger.info("Đã tải thành công tất cả các model")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model: {str(e)}")
            return False
    
    def preprocess_for_culane(self, frame: np.ndarray) -> torch.Tensor:
        """ Tiền xử lý ảnh trước khi đưa vào CULane
        Đây là cách bạn đã làm trong lane_detect.py """
        # Lấy kích thước ảnh gốc
        orig_h, orig_w = frame.shape[:2]
        
        # Resize ảnh về kích thước chuẩn của CULane
        train_height = self.culane_config['train_height']
        train_width = self.culane_config['train_width']
        
        # Resize ảnh
        img_resized = cv2.resize(frame, (train_width, train_height))
        
        # Chuyển sang RGB (CULane thường dùng RGB)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        # Chuyển thành PIL Image để xử lý với torchvision
        from PIL import Image
        import torchvision.transforms as transforms
        
        img_pil = Image.fromarray(img_rgb)
        
        # Các phép biến đổi giống với lane_detect.py
        img_transforms = transforms.Compose([
            transforms.Resize((int(train_height / self.culane_config['crop_ratio']), train_width)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])
        
        # Crop bottom
        img_tensor = img_transforms(img_pil)
        img_tensor = img_tensor[:, -train_height:, :]  # Crop bottom
        
        # Add batch dimension
        img_tensor = img_tensor.unsqueeze(0)
        
        # Đưa tensor về thiết bị
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        img_tensor = img_tensor.to(device)
        
        return img_tensor, frame
    
    def pred2coords(self, pred, original_image_width: int = 1640, original_image_height: int = 590) -> List[List[Tuple[int, int]]]:
        """ Chuyển đổi đầu ra của mô hình CULane thành tọa độ làn đường
        Hàm này được lấy và điều chỉnh từ lane_detect.py """
        
        # Trích xuất các thông tin từ output của mô hình
        # Giả định đầu ra có các khóa: 'loc_row', 'exist_row', 'loc_col', 'exist_col'
        if 'loc_row' not in pred or 'exist_row' not in pred or 'loc_col' not in pred or 'exist_col' not in pred:
            logger.error("Output của mô hình không có định dạng mong đợi")
            return []
        
        # Chuyển các tensor về CPU và numpy
        loc_row = pred['loc_row'].cpu().detach()
        exist_row = pred['exist_row'].cpu().detach()
        loc_col = pred['loc_col'].cpu().detach()
        exist_col = pred['exist_col'].cpu().detach()
        
        # Lấy indices
        max_indices_row = loc_row.argmax(dim=1)
        valid_row = exist_row.argmax(dim=1)
        max_indices_col = loc_col.argmax(dim=1)
        valid_col = exist_col.argmax(dim=1)
        
        coords = []
        
        # Cấu hình lane index
        row_lane_idx = [0, 1, 2, 3]
        col_lane_idx = [0, 1, 2, 3]
        
        # Xử lý ROW LANES (lanes theo chiều ngang)
        for i in row_lane_idx:
            tmp = []
            if valid_row[0, :, i].sum() > (self.culane_config['num_row'] / 2):
                for k in range(valid_row.shape[1]):
                    if valid_row[0, k, i]:
                        # Tìm vị trí x gần nhất
                        all_ind = torch.arange(
                            max(0, max_indices_row[0, k, i] - self.local_width),
                            min(self.culane_config['griding_row'] - 1, max_indices_row[0, k, i] + self.local_width) + 1
                        )
                        
                        # Tính toán vị trí chính xác bằng weighted average
                        weighted_sum = (loc_row[0, all_ind, k, i].softmax(0) * all_ind.float()).sum() + 0.5
                        normalized_x = weighted_sum / (self.culane_config['griding_row'] - 1) * original_image_width
                        
                        # Tọa độ y tương ứng với row_anchor
                        y = int(self.culane_config['row_anchor'][k] * original_image_height)
                        
                        tmp.append((int(normalized_x), y))
            coords.append(tmp)
        
        # Xử lý COLUMN LANES (lanes theo chiều dọc)
        for i in col_lane_idx:
            tmp = []
            if valid_col[0, :, i].sum() > (self.culane_config['num_col'] / 4):
                for k in range(valid_col.shape[1]):
                    if valid_col[0, k, i]:
                        # Tìm vị trí y gần nhất
                        all_ind = torch.arange(
                            max(0, max_indices_col[0, k, i] - self.local_width),
                            min(self.culane_config['griding_col'] - 1, max_indices_col[0, k, i] + self.local_width) + 1
                        )
                        
                        # Tính toán vị trí chính xác bằng weighted average
                        weighted_sum = (loc_col[0, all_ind, k, i].softmax(0) * all_ind.float()).sum() + 0.5
                        normalized_y = weighted_sum / (self.culane_config['griding_col'] - 1) * original_image_height
                        
                        # Tọa độ x tương ứng với col_anchor
                        x = int(self.culane_config['col_anchor'][k] * original_image_width)
                        
                        tmp.append((x, int(normalized_y)))
            coords.append(tmp)
        
        return coords
    
    def detect_lanes(self, frame: np.ndarray) -> Dict:
        """ Phát hiện làn đường bằng model CULane
        Args:
            frame: Khung hình đầu vào (np.ndarray)
        Returns:
            Dict chứa thông tin về các làn đường phát hiện được
        """
        
        # Kiểm tra và chuẩn bị model
        if not self.loaded:
            if not self.load_models():
                return {
                    "detected": False,
                    "lanes": [],
                    "frame_size": {
                        "width": frame.shape[1],
                        "height": frame.shape[0]
                    },
                    "lane_count": 0
                }
        
        # Tiền xử lý ảnh
        img_tensor, orig_frame = self.preprocess_for_culane(frame)
        
        # Thực hiện inference
        try:
            with torch.no_grad():
                pred = self.lane_model(img_tensor)
        except Exception as e:
            logger.error(f"Lỗi khi thực hiện inference trên CULane: {str(e)}")
            # Trả về kết quả tạm thời
            return {
                "detected": False,
                "lanes": [],
                "frame_size": {
                    "width": frame.shape[1],
                    "height": frame.shape[0]
                },
                "lane_count": 0
            }
        
        # Chuyển đổi kết quả thành tọa độ
        coords = self.pred2coords(
            pred, 
            original_image_width=self.culane_config['original_image_width'], 
            original_image_height=self.culane_config['original_image_height']
        )
        
        # Chuyển đổi tọa độ thành định dạng yêu cầu
        lane_info = {
            "detected": len(coords) > 0,
            "lanes": [],
            "frame_size": {
                "width": frame.shape[1],
                "height": frame.shape[0]
            },
            "lane_count": len(coords)
        }
        
        # Xử lý từng làn để tạo định dạng mong muốn
        for i, lane_coords in enumerate(coords):
            if len(lane_coords) < 2:
                continue
            
            # Sắp xếp các điểm theo tọa độ y tăng dần (từ trên xuống dưới)
            # Tạo danh sách điểm theo dạng [[x1,y1], [x2,y2], ...]
            points = [[int(x), int(y)] for x, y in lane_coords if 0 <= x <= frame.shape[1] and 0 <= y <= frame.shape[0]]
            
            if len(points) == 0:
                continue
            
            # Tính toán độ dốc
            if len(points) >= 2:
                x1, y1 = points[0]
                x2, y2 = points[-1]
                slope = (y2 - y1) / (x2 - x1 + 1e-5)  # Tránh chia cho 0
            else:
                slope = 0
            
            # Tính toán khoảng cách từ trung tâm
            if len(points) > 0:
                x_center = frame.shape[1] // 2
                avg_x = sum(p[0] for p in points) / len(points)
                distance_from_center = avg_x - x_center
            else:
                distance_from_center = 0
            
            # Xác định loại làn (solid hoặc dashed)
            # Giả định: nếu điểm cách nhau nhiều thì là dashed
            if len(points) >= 2:
                # Đếm các khoảng trống trong làn
                total_points = len(points)
                y_coords = [p[1] for p in points]
                y_diff = max(y_coords) - min(y_coords)
                if y_diff > 0:
                    # Tính số điểm trên một đơn vị chiều cao
                    density = total_points / y_diff
                    if density < 0.02:
                        lane_type = "dashed"
                    else:
                        lane_type = "solid"
                else:
                    lane_type = "solid"
            else:
                lane_type = "solid"
            
            lane = {
                "id": i + 1,
                "points": points,
                "slope": float(slope),
                "distance_from_center": float(distance_from_center),
                "type": lane_type
            }
            lane_info["lanes"].append(lane)
        
        # Tìm làn đường trung tâm
        if lane_info["lanes"]:
            center_lane = min(
                lane_info["lanes"], 
                key=lambda x: abs(x["distance_from_center"])
            )
            lane_info["center_lane"] = center_lane["id"]
        
        return lane_info
    
    def detect_traffic_signs(self, frame: np.ndarray) -> List[Dict]:
        """ Phát hiện biển báo giao thông bằng YOLOv8
        Args:
            frame: Khung hình đầu vào (np.ndarray)
        Returns:
            List chứa thông tin về các biển báo phát hiện được
        """
        if not self.traffic_sign_model:
            logger.error("Model biển báo chưa được tải")
            return []
        
        try:
            # Thực hiện phát hiện biển báo
            results = self.traffic_sign_model(frame)
            traffic_signs = []
            
            # Xử lý kết quả YOLOv8
            for result in results:
                if hasattr(result, 'boxes'):
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            class_id = int(box.cls[0]) if box.cls.numel() > 0 else -1
                            confidence = float(box.conf[0]) if box.conf.numel() > 0 else 0.0
                            xyxy = box.xyxy[0].cpu().numpy() if box.xyxy.numel() > 0 else np.array([0,0,0,0])
                            
                            # Lấy tên nhãn (bạn cần định nghĩa danh sách nhãn của bạn)
                            # Giả định danh sách nhãn theo mô hình của bạn
                            class_names = [
                                "stop", "yield", "speed_limit_30", "speed_limit_50", 
                                "speed_limit_80", "no_entry", "pedestrian_crossing", 
                                "turn_left", "turn_right", "danger", "speed_limit_60",
                                "speed_limit_40", "speed_limit_20", "warning", "crosswalk"
                            ]
                            
                            if class_id < len(class_names):
                                label = class_names[class_id]
                            else:
                                label = f"unknown_{class_id}"
                            
                            # Tính toán tọa độ hình chữ nhật
                            x1, y1, x2, y2 = map(int, xyxy)
                            width = x2 - x1
                            height = y2 - y1
                            
                            # Tính toán trung tâm
                            center_x = (x1 + x2) / 2
                            center_y = (y1 + y2) / 2
                            
                            traffic_sign = {
                                "type": label,
                                "confidence": round(confidence, 4),
                                "bbox": {
                                    "x1": x1,
                                    "y1": y1,
                                    "x2": x2,
                                    "y2": y2
                                },
                                "center": {
                                    "x": float(center_x),
                                    "y": float(center_y)
                                },
                                "size": {
                                    "width": width,
                                    "height": height
                                }
                            }
                            traffic_signs.append(traffic_sign)
            
            return traffic_signs
            
        except Exception as e:
            logger.error(f"Lỗi khi phát hiện biển báo: {str(e)}")
            return []
    
    def analyze_lane_geometry(self, lane_info: Dict) -> Dict:
        """ Phân tích hình học của làn đường
        Args:
            lane_info: Kết quả từ detect_lanes
        Returns:
            Dict chứa các thông số hình học được phân tích
        """
        if not lane_info["detected"] or not lane_info["lanes"]:
            return {
                "curvature": 0.0,
                "road_width_estimation": 0.0,
                "lane_alignment": "centered",
                "lane_count": 0,
                "shoulder_found": False,
                "road_type": "unknown"
            }
        
        lanes = lane_info["lanes"]
        
        # Phân tích độ cong của làn đường (dựa trên độ nghiêng)
        slopes = [lane["slope"] for lane in lanes]
        avg_slope = sum(slopes) / len(slopes)
        
        # Ước tính độ cong
        curvature = abs(avg_slope)
        
        # Ước tính chiều rộng đường (dựa trên khoảng cách giữa làn đường ngoài cùng)
        if len(lanes) >= 2:
            # Tìm hai làn đường ngoài cùng
            leftmost = min(lanes, key=lambda x: x["distance_from_center"])
            rightmost = max(lanes, key=lambda x: x["distance_from_center"])
            
            # Giả định 1 pixel = 0.05 mét (giá trị ước tính)
            # Tính khoảng cách giữa hai làn ngoài cùng
            if leftmost["distance_from_center"] > 0 and rightmost["distance_from_center"] < 0:
                # Là 2 bên so với trung tâm
                distance_between = abs(leftmost["distance_from_center"]) + abs(rightmost["distance_from_center"])
                road_width = distance_between * 0.05  # ước tính mét
            else:
                # Cả hai đều ở cùng một bên
                distance_between = abs(leftmost["distance_from_center"] - rightmost["distance_from_center"])
                road_width = distance_between * 0.05
        else:
            # Dựa vào vị trí làn duy nhất
            road_width = 6.0  # giá trị mặc định
        
        # Xác định hướng căn chỉnh làn đường
        lane_alignment = "centered"
        if lane_info["center_lane"]:
            center_lane = next((lane for lane in lanes if lane["id"] == lane_info["center_lane"]), None)
            if center_lane:
                dist = center_lane["distance_from_center"]
                if dist > 100:
                    lane_alignment = "left"
                elif dist < -100:
                    lane_alignment = "right"
        
        # Ước tính loại đường (đường cao tốc, đường đô thị, ...)
        road_type = "unknown"
        if len(lanes) >= 4:
            road_type = "highway"
        elif len(lanes) == 2:
            road_type = "urban"
        elif len(lanes) == 1:
            road_type = "two_way_single_lane"
        elif len(lanes) == 3:
            road_type = "urban_with_center_lane"
        
        # Kiểm tra có lề đường không
        shoulder_found = False
        if len(lanes) == 1:
            # Nếu chỉ có một làn và nó ở bên phải
            leftmost = min(lanes, key=lambda x: x["distance_from_center"])
            if leftmost["distance_from_center"] > 50:
                shoulder_found = True
        
        return {
            "curvature": round(curvature, 4),
            "road_width_estimation": round(road_width, 2),
            "lane_alignment": lane_alignment,
            "lane_count": len(lanes),
            "shoulder_found": shoulder_found,
            "road_type": road_type
        }
    
    def create_road_environment_description(self, frame: np.ndarray, lane_info: Dict, traffic_signs: List[Dict], geometry_analysis: Dict) -> Dict:
        """ Tổng hợp tất cả thông tin để tạo ra mô tả môi trường giao thông JSON
        Args:
            frame: Khung hình đầu vào
            lane_info: Thông tin làn đường
            traffic_signs: Danh sách biển báo phát hiện được
            geometry_analysis: Phân tích hình học làn đường
        Returns:
            Dict chứa mô tả đầy đủ môi trường giao thông
        """
        # Xác định các hành động khuyến nghị dựa trên biển báo và làn đường
        recommendations = []
        
        # Kiểm tra biển báo dừng
        has_stop_sign = any(sign["type"] == "stop" for sign in traffic_signs)
        if has_stop_sign:
            recommendations.append("Cần dừng lại trước vạch dừng")
        
        # Kiểm tra biển báo nhường đường
        has_yield_sign = any(sign["type"] == "yield" for sign in traffic_signs)
        if has_yield_sign:
            recommendations.append("Cần nhường đường cho phương tiện ưu tiên")
        
        # Kiểm tra biển báo giới hạn tốc độ
        speed_signs = [sign for sign in traffic_signs if sign["type"].startswith("speed_limit")]
        if speed_signs:
            max_speed = max([int(s["type"].split("_")[-1]) for s in speed_signs])
            recommendations.append(f"Giới hạn tốc độ tối đa: {max_speed} km/h")
        
        # Kiểm tra làn đường
        if geometry_analysis["lane_alignment"] != "centered":
            recommendations.append(f"Xe đang lệch {geometry_analysis['lane_alignment']} so với trung tâm đường")
        
        # Kiểm tra độ cong
        if geometry_analysis["curvature"] > 0.3:
            recommendations.append("Đường đang có độ cong đáng kể - cảnh báo giảm tốc")
        
        # Kiểm tra loại đường
        if geometry_analysis["road_type"] == "highway":
            recommendations.append("Đang di chuyển trên đường cao tốc - giữ khoảng cách an toàn")
        
        # Kiểm tra lề đường
        if geometry_analysis["shoulder_found"]:
            recommendations.append("Có lề đường bên phải - có thể dừng khẩn cấp")
        
        # Tạo cấu trúc JSON mô tả môi trường giao thông
        description = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "frame_info": {
                "width": frame.shape[1],
                "height": frame.shape[0],
                "resolution": f"{frame.shape[1]}x{frame.shape[0]}"
            },
            "lane_detection": lane_info,
            "traffic_sign_detection": {
                "count": len(traffic_signs),
                "signs": traffic_signs,
                "types_detected": list(set([sign["type"] for sign in traffic_signs]))
            },
            "lane_geometry_analysis": geometry_analysis,
            "environment_status": {
                "road_type": geometry_analysis["road_type"],
                "traffic_density": "low",  # Có thể mở rộng để ước tính mật độ giao thông
                "weather_condition": "clear",  # Có thể mở rộng nếu có cảm biến thời tiết
                "visibility": "good"
            },
            "driving_recommendations": recommendations,
            "confidences": {
                "lane_detection": round(len(lane_info["lanes"]) / 4.0, 2) if lane_info["detected"] else 0.0,
                "traffic_sign_detection": round(sum([sign["confidence"] for sign in traffic_signs]) / len(traffic_signs) if traffic_signs else 0.0, 2)
            },
            "system_metadata": {
                "model_versions": {
                    "lane_detection": "CULANERes34",
                    "traffic_sign_detection": "yolov8n_custom_trained"
                },
                "software_version": "1.0.0",
                "timestamp": str(datetime.now())
            }
        }
        
        return description
    
    def analyze_scene(self, image_path: str) -> Dict:
        """ Phân tích toàn bộ cảnh giao thông
        Args:
            image_path: Đường dẫn đến hình ảnh
        Returns:
            Dict chứa mô tả chi tiết về môi trường giao thông
        """
        # Kiểm tra model đã được tải hay chưa
        if not self.loaded:
            if not self.load_models():
                raise Exception("Không thể tải các model cần thiết")
        
        # Đọc hình ảnh
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Không thể đọc hình ảnh từ: {image_path}")
        
        # Bước 1: Phát hiện làn đường
        logger.info("Bắt đầu phát hiện làn đường...")
        lane_info = self.detect_lanes(frame)
        
        # Bước 2: Phân tích hình học làn đường
        logger.info("Bắt đầu phân tích hình học làn đường...")
        geometry_analysis = self.analyze_lane_geometry(lane_info)
        
        # Bước 3: Phát hiện biển báo giao thông
        logger.info("Bắt đầu phát hiện biển báo giao thông...")
        traffic_signs = self.detect_traffic_signs(frame)
        
        # Bước 4: Tạo mô tả môi trường giao thông
        logger.info("Tạo mô tả JSON cho môi trường giao thông...")
        full_description = self.create_road_environment_description(
            frame, lane_info, traffic_signs, geometry_analysis
        )
        
        return full_description

def process_scene(image_path: str) -> Dict:
    """ Hàm tiện ích để xử lý cảnh giao thông """
    analyzer = TrafficAnalyzer(
        lane_model_path="model/culane_res34.pth",
        traffic_sign_model_path="model/vntsd_yolov8n_trained_best.pt"
    )
    
    try:
        result = analyzer.analyze_scene(image_path)
        return result
    except Exception as e:
        logger.error(f"Lỗi khi xử lý cảnh giao thông: {str(e)}")
        return {
            "error": str(e),
            "timestamp": str(datetime.now())
        }
