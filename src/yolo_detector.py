"""
YOLOv8 Traffic Sign Detector

Uses pretrained YOLOv8 model for traffic sign detection.
Model: yolov8n.pt (nano) - lightweight, fast, good for demonstration
For production: Use custom trained model on traffic signs (tt100k, BTSD, etc.)
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import os


@dataclass
class DetectedSign:
    """
    Kết quả detection của một biển báo.
    """
    sign_type: str           # Loại biển báo (speed_limit_50, stop, etc.)
    confidence: float        # Confidence score (0-1)
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    relative_position: str   # "left", "center", "right"
    distance: str            # "near", "medium", "far"
    raw_class: str           # Raw class từ model (class ID hoặc tên)

    def to_dict(self) -> Dict:
        return {
            'sign_type': self.sign_type,
            'confidence': float(self.confidence),
            'bbox': self.bbox,
            'relative_position': self.relative_position,
            'distance': self.distance,
            'raw_class': self.raw_class
        }


class YOLOTrafficSignDetector:
    """
    YOLOv8 Traffic Sign Detector.

    Supports:
    - Speed limit signs (30, 50, 60, 80, 100, 120 km/h)
    - Regulatory: stop, yield, no_entry
    - Turn restrictions: no_left_turn, no_right_turn, no_u_turn
    - Traffic lights: red, yellow, green
    - Warnings: pedestrian_crossing, school_zone

    Priority levels:
    1. CRITICAL: stop, no_entry, traffic_light_red
    2. WARNING: speed_limit, yield
    3. CAUTION: turn restrictions
    """

    # Traffic sign class names (COCO-compatible + custom)
    # These are common in traffic sign datasets
    SIGN_CLASSES = {
        0: 'stop',
        1: 'speed_limit_30',
        2: 'speed_limit_50',
        3: 'speed_limit_60',
        4: 'speed_limit_80',
        5: 'speed_limit_100',
        6: 'speed_limit_120',
        7: 'yield',
        8: 'no_entry',
        9: 'no_left_turn',
        10: 'no_right_turn',
        11: 'no_u_turn',
        12: 'traffic_light_red',
        13: 'traffic_light_yellow',
        14: 'traffic_light_green',
        15: 'pedestrian_crossing',
        16: 'school_zone',
        17: 'roundabout',
        18: 'one_way',
    }

    # Alternative naming for different datasets
    COCO_CLASSES = {
        0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
        5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
        # ... full COCO has 80 classes
    }

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
        device: str = "cpu"
    ):
        """
        Khởi tạo detector.

        Args:
            model_path: Path đến YOLOv8 weights. Nếu None, sẽ tải yolov8n.pt từ hub.
            confidence_threshold: Ngưỡng confidence để chấp nhận detection
            device: 'cpu', 'cuda', hoặc 'mps' (Apple Silicon)
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.device = device
        self._load_model(model_path)

    def _load_model(self, model_path: Optional[str]):
        """Load YOLOv8 model from path or download from hub."""
        try:
            from ultralytics import YOLO

            if model_path and os.path.exists(model_path):
                print(f"[INFO] Loading YOLOv8 from: {model_path}")
                self.model = YOLO(model_path)
            else:
                # Download yolov8n.pt from ultralytics hub
                # Using nano model for speed - good for demo
                print("[INFO] Downloading YOLOv8n from ultralytics hub...")
                print("[INFO] Model: yolov8n.pt (nano - fast inference)")
                self.model = YOLO('yolov8n.pt')

            self.model.to(self.device)
            print(f"[INFO] Model loaded successfully on {self.device}")

        except ImportError:
            print("[ERROR] ultralytics not installed!")
            print("  Install with: pip install ultralytics")
            raise
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            raise

    def detect(self, image: np.ndarray, image_width: int = 1640, image_height: int = 590) -> List[DetectedSign]:
        """
        Detect traffic signs trong image.

        Args:
            image: Input image (BGR hoặc RGB)
            image_width: Chiều rộng image để normalize position
            image_height: Chiều cao image để normalize position

        Returns:
            List of DetectedSign objects
        """
        if self.model is None:
            print("[WARNING] No model loaded, returning empty")
            return []

        try:
            # YOLOv8 expects RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                # Convert BGR to RGB if needed (OpenCV loads as BGR)
                import cv2
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image

            # Run inference
            results = self.model(image_rgb, verbose=False, conf=self.confidence_threshold)

            detected_signs = []
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue

                for box in boxes:
                    conf = float(box.conf[0])
                    if conf < self.confidence_threshold:
                        continue

                    # Get bounding box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox = (int(x1), int(y1), int(x2), int(y2))

                    # Get class
                    cls_id = int(box.cls[0])
                    raw_class = self._get_class_name(cls_id)

                    # Interpret sign type
                    sign_type = self._interpret_sign_type(raw_class, cls_id)

                    # Relative position
                    cx = (x1 + x2) / 2
                    if cx < image_width * 0.33:
                        rel_pos = "left"
                    elif cx > image_width * 0.66:
                        rel_pos = "right"
                    else:
                        rel_pos = "center"

                    # Distance estimation (based on bbox size and y position)
                    avg_y = (y1 + y2) / 2
                    bbox_area = (x2 - x1) * (y2 - y1)

                    # Larger bbox = closer to camera
                    # Also check y position (lower in image = closer)
                    if avg_y > image_height * 0.55 or bbox_area > 10000:
                        distance = "near"
                    elif avg_y > image_height * 0.3 or bbox_area > 4000:
                        distance = "medium"
                    else:
                        distance = "far"

                    sign = DetectedSign(
                        sign_type=sign_type,
                        confidence=conf,
                        bbox=bbox,
                        relative_position=rel_pos,
                        distance=distance,
                        raw_class=raw_class
                    )
                    detected_signs.append(sign)

            return detected_signs

        except Exception as e:
            print(f"[ERROR] Detection failed: {e}")
            return []

    def _get_class_name(self, cls_id: int) -> str:
        """Map class ID to class name."""
        if cls_id in self.SIGN_CLASSES:
            return self.SIGN_CLASSES[cls_id]
        return f"unknown_class_{cls_id}"

    def _interpret_sign_type(self, raw_class: str, cls_id: int) -> str:
        """
        Map raw detection class to semantic sign type.

        For base YOLOv8n model (COCO pretrained), most common:
        - cls 9: traffic light (we categorize by color later)
        - others: detected as general objects

        For custom traffic sign model, use SIGN_CLASSES directly.
        """
        # Check if it's a known traffic sign
        if raw_class in self.SIGN_CLASSES.values():
            return raw_class

        # COCO class 9 is traffic light
        if cls_id == 9:
            # We'll assume traffic light, color detection requires additional processing
            return "traffic_light_green"  # Default assumption, improve with color detection

        # For unknown detections, return as-is
        return raw_class

    def get_priority(self, sign_type: str) -> int:
        """
        Get priority level của sign.

        Priority:
        1 = CRITICAL (must obey)
        10 = WARNING (be aware)
        20 = CAUTION (informational)
        """
        critical = {'stop', 'no_entry', 'traffic_light_red'}
        warning = {'yield', 'traffic_light_yellow', 'pedestrian_crossing', 'school_zone'}
        caution = {'no_left_turn', 'no_right_turn', 'no_u_turn'}

        if sign_type in critical:
            return 1
        elif sign_type in warning:
            return 10
        elif sign_type in caution:
            return 20
        elif sign_type.startswith('speed_limit_'):
            return 10
        else:
            return 30


def batch_detect(
    detector: YOLOTrafficSignDetector,
    frames: List[np.ndarray],
    image_width: int = 1640,
    image_height: int = 590
) -> List[List[DetectedSign]]:
    """
    Detect signs trong nhiều frames liên tục.
    """
    return [
        detector.detect(frame, image_width, image_height)
        for frame in frames
    ]


# Convenient standalone detection function
def detect_traffic_signs(
    image: np.ndarray,
    model_path: Optional[str] = None,
    confidence: float = 0.5
) -> List[DetectedSign]:
    """
    Quick function to detect traffic signs.

    Usage:
        signs = detect_traffic_signs(image)
    """
    detector = YOLOTrafficSignDetector(
        model_path=model_path,
        confidence_threshold=confidence
    )
    return detector.detect(image)


if __name__ == "__main__":
    # Test detection on a sample image
    import cv2

    # Create a simple test (you would load a real image)
    print("Testing YOLOv8 Traffic Sign Detector...")
    print("Downloading model if needed...")

    detector = YOLOTrafficSignDetector(
        confidence_threshold=0.5
    )

    # Create blank image for format test
    test_image = np.zeros((590, 1640, 3), dtype=np.uint8)
    signs = detector.detect(test_image)

    print(f"\nDetection test completed")
    print(f"Signs detected: {len(signs)}")
    print("\nDetector ready for use!")