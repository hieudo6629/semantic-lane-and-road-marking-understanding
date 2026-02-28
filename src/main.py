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

culane_path = r"C:\Users\Hieu\.cache\kagglehub\datasets\greatgamedota\culane\versions\7"

dataset = CULaneDataset(culane_path)

image, lanes, path = dataset.get_item(0)

print("Image path:", path)
print("Number of lanes:", len(lanes))
lane_info = classify_lanes(lanes, image.shape[1])

for i, lane in enumerate(lane_info):
    print(f"Lane {i}: side={lane['side']}, mean_x={lane['mean_x']:.2f}")
vis = draw_lanes(image, lanes)

cv2.imshow("Lane Visualization", vis)
cv2.waitKey(0)
cv2.destroyAllWindows()