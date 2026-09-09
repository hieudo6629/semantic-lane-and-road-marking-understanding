import os
import cv2
from pathlib import Path

def extract_frames_from_video(
    video_path: str,
    output_dir: str = 'extracted_frames',
    interval: int = 30,
    max_frames: int = None,
    resize: tuple = None,
    save_format: str = 'jpg'
):
    """
    Trích xuất frame từ video đã có sẵn trên máy.
    
    Args:
        video_path: Đường dẫn đến file video
        output_dir: Thư mục lưu ảnh
        interval: Khoảng cách frame (30 = 1 ảnh/giây nếu video 30fps)
        max_frames: Số ảnh tối đa (None = tất cả)
        resize: (width, height) để resize ảnh
        save_format: 'jpg' hoặc 'png'
    
    Returns:
        list: Danh sách đường dẫn ảnh đã lưu
    """
    # Kiểm tra video tồn tại
    if not os.path.exists(video_path):
        print(f"❌ Video không tồn tại: {video_path}")
        return []
    
    # Tạo thư mục output
    os.makedirs(output_dir, exist_ok=True)
    
    # Mở video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Không thể mở video: {video_path}")
        return []
    
    # Lấy thông tin video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"📊 Thông tin video:")
    print(f"   - Đường dẫn: {video_path}")
    print(f"   - Tổng số frame: {total_frames}")
    print(f"   - FPS: {fps:.2f}")
    print(f"   - Thời lượng: {duration:.2f} giây")
    print(f"   - Khoảng cách cắt: {interval} frame (~{interval/fps:.1f} giây/ảnh)")
    
    # Tạo thư mục con cho video
    video_name = Path(video_path).stem
    frame_dir = os.path.join(output_dir, video_name)
    os.makedirs(frame_dir, exist_ok=True)
    
    frame_count = 0
    saved_count = 0
    saved_paths = []
    
    print(f"📸 Bắt đầu trích xuất ảnh...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Chỉ lưu frame ở khoảng cách interval
        if frame_count % interval == 0:
            # Resize nếu cần
            if resize is not None:
                frame = cv2.resize(frame, resize)
            
            # Lưu ảnh
            ext = 'jpg' if save_format == 'jpg' else 'png'
            frame_path = os.path.join(frame_dir, f"frame_{saved_count:06d}.{ext}")
            cv2.imwrite(frame_path, frame)
            saved_paths.append(frame_path)
            saved_count += 1
            
            # In tiến độ
            if saved_count % 10 == 0:
                progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                print(f"   ⏳ Đã lưu {saved_count} ảnh ({progress:.1f}%)")
            
            # Dừng nếu đạt max_frames
            if max_frames is not None and saved_count >= max_frames:
                print(f"✅ Đã đạt giới hạn {max_frames} ảnh")
                break
        
        frame_count += 1
    
    cap.release()
    print(f"✅ Đã trích xuất và lưu {saved_count} ảnh tại: {frame_dir}")
    return saved_paths


# ============================================================
# SỬ DỤNG
# ============================================================

if __name__ == "__main__":
    # --- CẤU HÌNH ---
    VIDEO_PATH = r"D:\MSE23\Luận văn\YTSave_YouTube_Driving-in-Chongqing-This-is-a-city-with_Media_Boh66Pjjiq0_002_720p.mp4"  # Đường dẫn video của bạn
    OUTPUT_DIR = "extracted_frames"
    
    # --- CHẠY ---
    frames = extract_frames_from_video(
        video_path=VIDEO_PATH,
        output_dir=OUTPUT_DIR,
        interval=1500,        # Lấy 1 ảnh mỗi 900 frame (~8.3 giây)
        max_frames=20,      # Chỉ lấy 200 ảnh
        resize=None,  # Resize về 640x360 (giảm dung lượng)
        save_format='jpg'   # Định dạng ảnh
    )
    
    print(f"\n📊 TÓM TẮT")
    print(f"   - Số ảnh đã lưu: {len(frames)}")
    if frames:
        print(f"   - Thư mục: {os.path.dirname(frames[0])}")
        print(f"   - Ảnh đầu tiên: {frames[0]}")