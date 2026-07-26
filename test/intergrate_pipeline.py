"""
Integrated Traffic Scene Understanding Pipeline
Kết hợp Lane Detection và Traffic Sign Detection thành JSON tình huống giao thông
"""

import os
import sys
import json
import cv2
import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from PIL import Image
import torchvision.transforms as transforms
from ultralytics import YOLO
from dataclasses import dataclass, field
from enum import Enum
import time

# ============================================================
# 1. LANE DETECTION MODULE (Ultra Fast Lane Detection V2)
# ============================================================

class LaneDetector:
    """Lane detection using Ultra Fast Lane Detection V2"""
    
    def __init__(self, model_path: str, config_path: str, device: str = 'cuda'):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        
        # Thêm đường dẫn Ultra-Fast-Lane-Detection-v2 vào sys.path
        root = "Ultra-Fast-Lane-Detection-v2"
        if os.path.exists(root):
            os.chdir(root)
            sys.path.append(os.getcwd())
        
        from model.model_culane import parsingNet
        from utils.config import Config
        from utils.common import get_model
        
        # Load config
        self.cfg = Config.fromfile(config_path)
        
        # Setup anchors
        self.cfg.row_anchor = np.linspace(0.42, 1, self.cfg.num_row)
        self.cfg.col_anchor = np.linspace(0, 1, self.cfg.num_col)
        
        # Load model
        self.net = get_model(self.cfg).to(self.device)
        ckpt = torch.load(model_path, map_location=self.device)
        state_dict = ckpt['model']
        
        # Remove DataParallel prefix
        new_state_dict = {}
        for k, v in state_dict.items():
            if k.startswith("module."):
                k = k[7:]
            new_state_dict[k] = v
        
        self.net.load_state_dict(new_state_dict)
        self.net.eval()
        
        print(f"LaneDetector loaded on {self.device}")
    
    def pred2coords(self, pred, row_anchor, col_anchor, local_width=1,
                    original_image_width=1640, original_image_height=590):
        """Convert prediction to lane coordinates"""
        
        batch_size, num_grid_row, num_cls_row, num_lane_row = pred['loc_row'].shape
        batch_size, num_grid_col, num_cls_col, num_lane_col = pred['loc_col'].shape

        max_indices_row = pred['loc_row'].argmax(1).cpu()
        valid_row = pred['exist_row'].argmax(1).cpu()
        max_indices_col = pred['loc_col'].argmax(1).cpu()
        valid_col = pred['exist_col'].argmax(1).cpu()

        pred['loc_row'] = pred['loc_row'].cpu()
        pred['loc_col'] = pred['loc_col'].cpu()

        coords = []
        row_lane_idx = [0, 1, 2, 3]
        col_lane_idx = [0, 1, 2, 3]

        # Row lanes
        for i in row_lane_idx:
            tmp = []
            if valid_row[0, :, i].sum() > num_cls_row / 2:
                for k in range(valid_row.shape[1]):
                    if valid_row[0, k, i]:
                        all_ind = torch.tensor(list(range(
                            max(0, max_indices_row[0, k, i] - local_width),
                            min(num_grid_row - 1, max_indices_row[0, k, i] + local_width) + 1
                        )))
                        out_tmp = (pred['loc_row'][0, all_ind, k, i].softmax(0) * all_ind.float()).sum() + 0.5
                        out_tmp = out_tmp / (num_grid_row - 1) * original_image_width
                        tmp.append((int(out_tmp), int(row_anchor[k] * original_image_height)))
            coords.append(tmp)

        # Column lanes
        for i in col_lane_idx:
            tmp = []
            if valid_col[0, :, i].sum() > num_cls_col / 4:
                for k in range(valid_col.shape[1]):
                    if valid_col[0, k, i]:
                        all_ind = torch.tensor(list(range(
                            max(0, max_indices_col[0, k, i] - local_width),
                            min(num_grid_col - 1, max_indices_col[0, k, i] + local_width) + 1
                        )))
                        out_tmp = (pred['loc_col'][0, all_ind, k, i].softmax(0) * all_ind.float()).sum() + 0.5
                        out_tmp = out_tmp / (num_grid_col - 1) * original_image_height
                        tmp.append((int(col_anchor[k] * original_image_width), int(out_tmp)))
            coords.append(tmp)

        return coords
    
    def detect(self, image_path: str) -> Tuple[np.ndarray, List[List[Tuple[int, int]]], int, int]:
        """Detect lanes from image"""
        
        from PIL import Image
        import torchvision.transforms as transforms
        
        img_pil = Image.open(image_path).convert("RGB")
        orig = cv2.imread(image_path)
        H, W = orig.shape[:2]
        
        # Preprocess
        img_transforms = transforms.Compose([
            transforms.Resize((int(self.cfg.train_height / self.cfg.crop_ratio), self.cfg.train_width)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])
        
        img_tensor = img_transforms(img_pil)
        img_tensor = img_tensor[:, -self.cfg.train_height:, :]
        img_tensor = img_tensor.unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            pred = self.net(img_tensor)
        
        # Decode
        coords = self.pred2coords(
            pred, self.cfg.row_anchor, self.cfg.col_anchor,
            original_image_width=W, original_image_height=H
        )
        
        # Filter empty lanes
        lanes = [lane for lane in coords if len(lane) > 0]
        
        return orig, lanes, W, H


# ============================================================
# 2. TRAFFIC SIGN DETECTION MODULE (YOLO)
# ============================================================

class TrafficSignDetector:
    """Traffic sign detection using YOLO"""
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.5):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.class_names = self.model.names
        
        print(f"TrafficSignDetector loaded with {len(self.class_names)} classes")
    
    def detect(self, image: np.ndarray, image_width: int, image_height: int) -> List[Dict]:
        """Detect traffic signs in image"""
        
        results = self.model(image, conf=self.confidence_threshold)
        
        detected_signs = []
        
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    xyxy = box.xyxy[0].tolist()
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    class_name = self.class_names.get(cls, f"class_{cls}")
                    
                    detected_signs.append({
                        'class_id': cls,
                        'class_name': class_name,
                        'confidence': conf,
                        'bbox': [int(x) for x in xyxy],
                        'x_center': int((xyxy[0] + xyxy[2]) / 2),
                        'y_center': int((xyxy[1] + xyxy[3]) / 2)
                    })
        
        return detected_signs


# ============================================================
# 3. LANE ANALYZER MODULE
# ============================================================

class LaneAnalyzer:
    """Analyze lane geometry and topology"""
    
    def __init__(self):
        pass
    
    def analyze(self, lanes: List[List[Tuple[int, int]]], image_width: int, image_height: int) -> Dict:
        """Analyze lanes and return structured information"""
        
        if not lanes:
            return self._empty_result()
        
        # Sort lanes by x position at vehicle level (bottom of image)
        vehicle_y = image_height - 50  # 50px from bottom
        lanes_with_x = []
        for idx, lane in enumerate(lanes):
            if lane:
                # Find point closest to vehicle_y
                closest_point = min(lane, key=lambda p: abs(p[1] - vehicle_y))
                lanes_with_x.append({
                    'index': idx,
                    'x_at_vehicle': closest_point[0],
                    'points': lane
                })
        
        # Sort left to right
        sorted_lanes = sorted(lanes_with_x, key=lambda l: l['x_at_vehicle'])
        
        # Find ego lane (vehicle center)
        vehicle_center_x = image_width // 2
        ego_lane_idx = None
        min_distance = float('inf')
        
        for i, lane_data in enumerate(sorted_lanes):
            dist = abs(lane_data['x_at_vehicle'] - vehicle_center_x)
            if dist < min_distance:
                min_distance = dist
                ego_lane_idx = i
        
        # Determine lane boundaries
        left_boundary = None
        right_boundary = None
        lane_width = None
        ego_center_x = None
        
        if ego_lane_idx is not None and ego_lane_idx + 1 < len(sorted_lanes):
            left_boundary = sorted_lanes[ego_lane_idx]
            right_boundary = sorted_lanes[ego_lane_idx + 1]
            lane_width = right_boundary['x_at_vehicle'] - left_boundary['x_at_vehicle']
            ego_center_x = (left_boundary['x_at_vehicle'] + right_boundary['x_at_vehicle']) / 2
        
        # Calculate vehicle offset
        offset_pixels = vehicle_center_x - ego_center_x if ego_center_x else 0
        offset_ratio = (offset_pixels / lane_width * 100) if lane_width and lane_width > 0 else 0
        
        return {
            'total_lanes': len(sorted_lanes),
            'ego_lane_index': ego_lane_idx,
            'left_neighbor_count': ego_lane_idx if ego_lane_idx is not None else 0,
            'right_neighbor_count': len(sorted_lanes) - ego_lane_idx - 1 if ego_lane_idx is not None else 0,
            'left_boundary': left_boundary['x_at_vehicle'] if left_boundary else None,
            'right_boundary': right_boundary['x_at_vehicle'] if right_boundary else None,
            'lane_width_pixels': lane_width,
            'ego_center_x': ego_center_x,
            'vehicle_offset_pixels': offset_pixels,
            'vehicle_offset_ratio_percent': offset_ratio,
            'is_centered': abs(offset_ratio) < 10,  # Centered if within 10%
            'lanes': [
                {
                    'index': l['index'],
                    'x_at_vehicle': l['x_at_vehicle'],
                    'num_points': len(l['points'])
                }
                for l in sorted_lanes
            ]
        }
    
    def _empty_result(self) -> Dict:
        return {
            'total_lanes': 0,
            'ego_lane_index': None,
            'left_neighbor_count': 0,
            'right_neighbor_count': 0,
            'left_boundary': None,
            'right_boundary': None,
            'lane_width_pixels': None,
            'ego_center_x': None,
            'vehicle_offset_pixels': 0,
            'vehicle_offset_ratio_percent': 0,
            'is_centered': False,
            'lanes': []
        }


# ============================================================
# 4. ROAD TYPE INFERENCE
# ============================================================

class RoadTypeInference:
    """Infer road type from lane geometry"""
    
    def __init__(self):
        pass
    
    def infer(self, lanes: List[List[Tuple[int, int]]], image_width: int, image_height: int) -> Dict:
        """Infer road type (straight, curve left, curve right)"""
        
        if len(lanes) < 2:
            return {'road_type': 'unknown', 'confidence': 0}
        
        # Get vanishing point from lane lines
        # Simplified: use polynomial fitting to estimate curvature
        road_type = 'straight'
        confidence = 0.5
        
        # Analyze lane curvature
        curvatures = []
        for lane in lanes:
            if len(lane) < 3:
                continue
            
            # Fit polynomial to lane points
            y_vals = np.array([p[1] for p in lane])
            x_vals = np.array([p[0] for p in lane])
            
            try:
                coeffs = np.polyfit(y_vals, x_vals, 2)
                curvature = coeffs[0] * 2  # Curvature magnitude
                curvatures.append(curvature)
            except:
                continue
        
        if curvatures:
            avg_curvature = np.mean(curvatures)
            if abs(avg_curvature) < 0.001:
                road_type = 'straight'
                confidence = 0.8
            elif avg_curvature > 0.001:
                road_type = 'curve_right'
                confidence = min(0.9, abs(avg_curvature) * 10)
            else:
                road_type = 'curve_left'
                confidence = min(0.9, abs(avg_curvature) * 10)
        
        return {
            'road_type': road_type,
            'confidence': confidence,
            'curvature_magnitude': abs(np.mean(curvatures)) if curvatures else 0
        }


# ============================================================
# 5. INTEGRATED SCENE BUILDER
# ============================================================

class TrafficSceneBuilder:
    """Build integrated traffic scene from lanes and signs"""
    
    def __init__(self):
        self.lane_analyzer = LaneAnalyzer()
        self.road_inferer = RoadTypeInference()
    
    def build(self, lanes: List[List[Tuple[int, int]]], 
              signs: List[Dict],
              image_width: int,
              image_height: int,
              current_speed: float = 60) -> Dict:
        """Build integrated traffic scene JSON"""
        
        # Analyze lanes
        lane_analysis = self.lane_analyzer.analyze(lanes, image_width, image_height)
        
        # Infer road type
        road_type = self.road_inferer.infer(lanes, image_width, image_height)
        
        # Build scene
        scene = {
            'timestamp': time.time(),
            'image_dimensions': {
                'width': image_width,
                'height': image_height
            },
            'current_speed': current_speed,
            'lane_analysis': {
                'total_lanes': lane_analysis['total_lanes'],
                'ego_lane_index': lane_analysis['ego_lane_index'],
                'lane_width_pixels': lane_analysis['lane_width_pixels'],
                'left_neighbor_count': lane_analysis['left_neighbor_count'],
                'right_neighbor_count': lane_analysis['right_neighbor_count'],
                'ego_center_x': lane_analysis['ego_center_x'],
                'left_boundary_x': lane_analysis['left_boundary'],
                'right_boundary_x': lane_analysis['right_boundary'],
                'lanes': lane_analysis['lanes']
            },
            'vehicle_position': {
                'offset_pixels': lane_analysis['vehicle_offset_pixels'],
                'offset_ratio_percent': lane_analysis['vehicle_offset_ratio_percent'],
                'is_centered': lane_analysis['is_centered'],
                'is_between_boundaries': lane_analysis['left_boundary'] is not None and lane_analysis['right_boundary'] is not None
            },
            'road_type': road_type,
            'traffic_signs': signs,
            'safety_assessment': {
                'is_lane_centered': lane_analysis['is_centered'],
                'is_road_clear': True,  # Simplified
                'has_warning_signs': any(s.get('class_name', '').lower() in ['warning', 'danger'] for s in signs),
                'speed_limit': self._get_speed_limit(signs)
            },
            'recommendations': self._generate_recommendations(
                lane_analysis, road_type, signs, current_speed
            )
        }
        
        return scene
    
    def _get_speed_limit(self, signs: List[Dict]) -> Optional[int]:
        """Extract speed limit from signs"""
        speed_limits = []
        for sign in signs:
            name = sign.get('class_name', '').lower()
            # Look for speed limit patterns
            if 'speed' in name or 'limit' in name:
                # Try to extract number
                import re
                numbers = re.findall(r'\d+', name)
                if numbers:
                    speed_limits.append(int(numbers[0]))
        return min(speed_limits) if speed_limits else None
    
    def _generate_recommendations(self, lane_analysis: Dict, road_type: Dict, 
                                  signs: List[Dict], current_speed: float) -> List[str]:
        """Generate driving recommendations"""
        recommendations = []
        
        # Lane position
        if not lane_analysis['is_centered']:
            offset = lane_analysis['vehicle_offset_ratio_percent']
            if offset > 10:
                recommendations.append(f"Vehicle is {offset:.1f}% right of center. Adjust to left.")
            elif offset < -10:
                recommendations.append(f"Vehicle is {abs(offset):.1f}% left of center. Adjust to right.")
        
        # Speed limit
        speed_limit = self._get_speed_limit(signs)
        if speed_limit and current_speed > speed_limit:
            recommendations.append(f"Speed limit is {speed_limit} km/h. Reduce speed.")
        elif speed_limit and current_speed < speed_limit - 10:
            recommendations.append(f"Speed limit is {speed_limit} km/h. You can increase speed.")
        
        # Road type
        if road_type.get('road_type') == 'curve_left':
            recommendations.append("Left curve ahead. Reduce speed and stay in lane.")
        elif road_type.get('road_type') == 'curve_right':
            recommendations.append("Right curve ahead. Reduce speed and stay in lane.")
        
        # Warning signs
        for sign in signs:
            if 'warning' in sign.get('class_name', '').lower():
                recommendations.append(f"Warning: {sign['class_name']}. Proceed with caution.")
        
        if not recommendations:
            recommendations.append("Road is clear. Continue driving safely.")
        
        return recommendations


# ============================================================
# 6. MAIN PIPELINE FUNCTION
# ============================================================

def process_traffic_scene(
    image_path: str,
    lane_model_path: str,
    lane_config_path: str,
    sign_model_path: str,
    confidence_threshold: float = 0.5,
    current_speed: float = 60
) -> Dict:
    """
    Complete traffic scene processing pipeline
    
    Args:
        image_path: Path to input image
        lane_model_path: Path to lane detection model (.pth)
        lane_config_path: Path to lane detection config (.py)
        sign_model_path: Path to traffic sign detection model (.pt)
        confidence_threshold: Confidence threshold for sign detection
        current_speed: Current vehicle speed in km/h
    
    Returns:
        Dict: Integrated traffic scene JSON
    """
    
    print("=" * 80)
    print("  INTEGRATED TRAFFIC SCENE UNDERSTANDING PIPELINE")
    print("=" * 80)
    
    # Step 1: Lane Detection
    print("\n[1/4] Detecting lanes...")
    lane_detector = LaneDetector(lane_model_path, lane_config_path)
    image, lanes, width, height = lane_detector.detect(image_path)
    print(f"  Detected {len(lanes)} lanes")
    
    # Step 2: Traffic Sign Detection
    print("\n[2/4] Detecting traffic signs...")
    sign_detector = TrafficSignDetector(sign_model_path, confidence_threshold)
    signs = sign_detector.detect(image, width, height)
    print(f"  Detected {len(signs)} traffic signs")
    for sign in signs:
        print(f"    - {sign['class_name']} ({sign['confidence']:.0%})")
    
    # Step 3: Build Scene
    print("\n[3/4] Building traffic scene...")
    builder = TrafficSceneBuilder()
    scene = builder.build(lanes, signs, width, height, current_speed)
    
    # Step 4: Save JSON
    print("\n[4/4] Saving scene JSON...")
    output_path = 'traffic_scene.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scene, f, indent=2, ensure_ascii=False)
    print(f"  Saved to: {output_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("  SCENE SUMMARY")
    print("=" * 80)
    print(f"  Total lanes: {scene['lane_analysis']['total_lanes']}")
    print(f"  Ego lane: {scene['lane_analysis']['ego_lane_index']}")
    print(f"  Vehicle offset: {scene['vehicle_position']['offset_ratio_percent']:.1f}%")
    print(f"  Centered: {'✅' if scene['vehicle_position']['is_centered'] else '❌'}")
    print(f"  Road type: {scene['road_type']['road_type']}")
    print(f"  Traffic signs: {len(scene['traffic_signs'])}")
    print(f"  Speed limit: {scene['safety_assessment']['speed_limit'] or 'Unknown'} km/h")
    print("\n  Recommendations:")
    for rec in scene['recommendations']:
        print(f"    - {rec}")
    print("=" * 80)
    
    return scene


# ============================================================
# 7. EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    
    # Configuration
    CONFIG = {
        'image_path': r'C:\Users\Hieu\IdeaProjects\Semantic Traffic\image_test\10095_2.jpg',
        'lane_model_path': r'C:\Users\Hieu\IdeaProjects\Semantic Traffic\model\culane_res34.pth',
        'lane_config_path': 'configs/culane_res34.py',
        'sign_model_path': r'C:\Users\Hieu\IdeaProjects\Semantic Traffic\model\vntsd_yolov8n_trained_best.pt',
        'confidence_threshold': 0.5,
        'current_speed': 60
    }
    
    # Run pipeline
    scene = process_traffic_scene(**CONFIG)
    
    # Display full JSON
    print("\n" + "=" * 80)
    print("  FULL JSON OUTPUT")
    print("=" * 80)
    print(json.dumps(scene, indent=2, ensure_ascii=False))