import cv2
import numpy as np
import matplotlib.pyplot as plt

def diagnose_preprocessing(image_path, model_input_size=(512, 512)):
    """
    Kiểm tra chất lượng ảnh đầu vào và preprocessing
    """
    # Đọc ảnh gốc
    img_original = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]
    
    print(f"📸 Ảnh gốc: {w}x{h} pixels, {img_rgb.dtype}")
    
    # 1. Kiểm tra tỷ lệ khung hình
    aspect_ratio = w / h
    print(f"  - Tỷ lệ khung hình: {aspect_ratio:.2f}")
    if aspect_ratio < 1.5 or aspect_ratio > 2.5:
        print(f"    ⚠️  Tỷ lệ khung hình bất thường (thường là 1.78-2.0 cho dashcam)")
    
    # 2. Kiểm tra độ sáng
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    brightness = np.mean(gray)
    print(f"  - Độ sáng trung bình: {brightness:.1f}/255")
    if brightness < 50:
        print(f"    ⚠️  Ảnh quá tối (<50)")
    elif brightness > 200:
        print(f"    ⚠️  Ảnh quá sáng (>200)")
    
    # 3. Kiểm tra độ tương phản
    contrast = np.std(gray)
    print(f"  - Độ tương phản: {contrast:.1f}")
    if contrast < 30:
        print(f"    ⚠️  Độ tương phản thấp, khó phân biệt vật thể")
    
    # 4. Kiểm tra nhiễu
    noise = np.std(img_rgb - cv2.GaussianBlur(img_rgb, (5, 5), 0))
    print(f"  - Nhiễu: {noise:.1f}")
    if noise > 20:
        print(f"    ⚠️  Nhiễu cao, có thể làm giảm chất lượng detection")
    
    # 5. Kiểm tra resize
    img_resized = cv2.resize(img_rgb, model_input_size)
    print(f"  - Resize về {model_input_size[0]}x{model_input_size[1]}")
    
    # 6. Hiển thị ảnh
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(img_rgb)
    axes[0].set_title(f"Original ({w}x{h})")
    axes[0].axis('off')
    
    axes[1].imshow(img_resized)
    axes[1].set_title(f"Resized ({model_input_size[0]}x{model_input_size[1]})")
    axes[1].axis('off')
    
    # Histogram
    axes[2].hist(gray.ravel(), bins=256, range=(0, 255))
    axes[2].set_title("Histogram")
    axes[2].axvline(brightness, color='r', linestyle='dashed', label=f'Mean: {brightness:.0f}')
    axes[2].legend()
    
    plt.tight_layout()
    plt.show()
    
    return {
        'original_size': (w, h),
        'aspect_ratio': aspect_ratio,
        'brightness': brightness,
        'contrast': contrast,
        'noise': noise
    }

# Chạy kiểm tra
print("="*50)
print("LANE DETECTION PREPROCESSING CHECK")
print("="*50)
lane_metrics = diagnose_preprocessing(
    'path/to/your/test_image.jpg',
    model_input_size=(512, 512)  # Kích thước bạn dùng cho lane detection
)

print("\n" + "="*50)
print("TRAFFIC SIGN PREPROCESSING CHECK")
print("="*50)
sign_metrics = diagnose_preprocessing(
    'path/to/your/test_image.jpg',
    model_input_size=(640, 640)  # Kích thước YOLO của bạn
)