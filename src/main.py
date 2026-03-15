# from dataset import CULaneDataset
# from structure_builder import LaneStructureBuilder
# from rule_based import RuleBasedIndication
# from llm_interface import SimpleLLM

# def main():
#     # Đường dẫn đến thư mục chứa dataset CULane
#     culane_path = r"C:\Users\Hieu\.cache\kagglehub\datasets\greatgamedota\culane\versions\7"

#     # Khởi tạo dataset CULane
#     dataset = CULaneDataset(culane_path)
#     # Khởi tạo đối tượng xây dựng cấu trúc lane
#     builder = LaneStructureBuilder()
#     # Khởi tạo mô hình rule-based (dựa trên luật)
#     rule_model = RuleBasedIndication()
#     # Khởi tạo mô hình LLM (Large Language Model)
#     llm_model = SimpleLLM()

#     # Lấy một mẫu từ dataset (ảnh, lanes, đường dẫn ảnh)
#     image, lanes, img_path = dataset.get_item(0)

#     # In thông tin cơ bản về mẫu
#     print("Image path:", img_path)
#     print("Lane count:", len(lanes))

#     # Xây dựng cấu trúc lane từ ảnh và annotation
#     structure = builder.build(image, lanes)

#     # In ra cấu trúc lane đã xây dựng
#     print("\nStructured Representation:")
#     print(structure)

#     # Sinh kết quả dựa trên luật
#     print("\nRule-based output:")
#     print(rule_model.generate(structure))

#     # Sinh kết quả dựa trên LLM
#     print("\nLLM-based output:")
#     print(llm_model.generate(structure))


# if __name__ == "__main__":
#     main()

# v2
from dataset import CULaneDataset
from visualize import draw_lanes
import cv2
from lane_processing import classify_lanes
from ego_lane_detector import EgoLaneDetector
from lane_geometry import LaneGeometry
from lane_width_estimator import LaneWidthEstimator
from scene_builder import SceneBuilder
from road_inference import RoadInference
from scene_description import SceneDescription
culane_path = r"C:\Users\Hieu\.cache\kagglehub\datasets\greatgamedota\culane\versions\7"

dataset = CULaneDataset(culane_path)

image, lanes, path = dataset.get_item(0)

print("Image path:", path)
print("Number of lanes:", len(lanes))
lane_info = classify_lanes(lanes, image.shape[1])
detector = EgoLaneDetector()

for i, lane in enumerate(lane_info):
    print(f"Lane {i}: side={lane['side']}, mean_x={lane['mean_x']:.2f}")
# detect ego lane
ego_lane = detector.detect(lane_info, image.shape[1])

print("\nEgo lane detection:")
print(ego_lane)
# lane geometry
geometry = LaneGeometry()

lane_geometry = geometry.process_lanes(lanes, image.shape[0])

print("\nLane geometry:")
for i, g in enumerate(lane_geometry):
    print(f"Lane {i} curvature: {g['curvature']:.2f}")

# road type inference
road_infer = RoadInference()

road_info = road_infer.infer(
    lane_geometry,
    ego_lane
)

print("\nRoad inference:")
print(road_info)

# lane width estimator
width_estimator = LaneWidthEstimator()

lane_width = width_estimator.estimate(
    lanes,
    ego_lane,
    image.shape[0]
)

print("\nLane width estimation:")
print(lane_width)

# sence representation builder
scene_builder = SceneBuilder()

scene = scene_builder.build(
    lane_info,
    ego_lane,
    lane_geometry,
    lane_width
)

print("\nScene representation:")
print(scene)

# sence description
desc = SceneDescription()

text = desc.generate(scene, road_info)

print("\nScene description:")
print(text)

# draw lane
vis = draw_lanes(image, lanes)
cv2.imshow("Lane Visualization", vis)
cv2.waitKey(0)
cv2.destroyAllWindows()
