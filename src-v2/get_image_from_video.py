import os
import cv2
import random
from pathlib import Path

def extract_frames_from_video(
    video_path: str,
    output_dir: str = 'extracted_frames',
    interval: int = 60,
    max_frames: int = None,
    resize: tuple = None,
    save_format: str = 'jpg'
):
    """
    Trich xuat frame tu video da co san tren may.
    
    Args:
        video_path: Duong dan den file video
        output_dir: Thu muc luu anh
        interval: Khoang cach toi da giua cac frame duoc lay (random tu 60 den interval)
        max_frames: So anh toi da (None = tat ca)
        resize: (width, height) de resize anh
        save_format: 'jpg' hoac 'png'
    
    Returns:
        list: Danh sach duong dan anh da luu
    """
    # Kiem tra video ton tai
    if not os.path.exists(video_path):
        print(f"Video khong ton tai: {video_path}")
        return []
    
    # Tao thu muc output
    os.makedirs(output_dir, exist_ok=True)
    
    # Mo video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Khong the mo video: {video_path}")
        return []
    
    # Lay thong tin video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"Thong tin video:")
    print(f"   - Duong dan: {video_path}")
    print(f"   - Tong so frame: {total_frames}")
    print(f"   - FPS: {fps:.2f}")
    print(f"   - Thoi luong: {duration:.2f} giay")
    print(f"   - Khoang cach cat: random tu 60 den {interval} frame")
    
    # Tao thu muc con cho video
    video_name = Path(video_path).stem
    frame_dir = os.path.join(output_dir, video_name)
    os.makedirs(frame_dir, exist_ok=True)
    
    frame_count = 0
    saved_count = 0
    saved_paths = []
    
    # Xac dinh frame tiep theo can lay (random trong [60, interval])
    min_gap = min(60, interval)
    max_gap = max(60, interval)
    next_capture_frame = random.randint(min_gap, max_gap)
    
    print(f"Bat dau trich xuat anh...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Chi luu frame khi den frame duoc chon ngau nhien
        if frame_count >= next_capture_frame:
            # Resize neu can
            if resize is not None:
                frame = cv2.resize(frame, resize)
            
            # Luu anh
            ext = 'jpg' if save_format == 'jpg' else 'png'
            frame_path = os.path.join(frame_dir, f"frame_{saved_count:06d}.{ext}")
            cv2.imwrite(frame_path, frame)
            saved_paths.append(frame_path)
            saved_count += 1
            
            # In tien do
            if saved_count % 10 == 0:
                progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                print(f"Da luu {saved_count} anh ({progress:.1f}%)")
            
            # Dung neu dat max_frames
            if max_frames is not None and saved_count >= max_frames:
                print(f"Da dat gioi han {max_frames} anh")
                break
            
            # Chon frame tiep theo: cong them mot khoang random [60, interval]
            next_capture_frame = frame_count + random.randint(min_gap, max_gap)
        
        frame_count += 1
    
    cap.release()
    print(f"Da trich xuat va luu {saved_count} anh tai: {frame_dir}")
    return saved_paths


# ============================================================
# SU DUNG
# ============================================================

if __name__ == "__main__":
    # --- CAU HINH ---
    VIDEO_PATH = r"D:\MSE23\Luan van\YTSave_YouTube_Driving-in-Chongqing-This-is-a-city-with_Media_Boh66Pjjiq0_002_720p.mp4"
    OUTPUT_DIR = "extracted_frames"
    
    # --- CHAY ---
    frames = extract_frames_from_video(
        video_path=VIDEO_PATH,
        output_dir=OUTPUT_DIR,
        interval=6000,      # Khoang cach toi da giua cac frame (random 60 -> 6000)
        max_frames=200,     # Chi lay 200 anh
        resize=None,        # Khong resize
        save_format='jpg'   # Dinh dang anh
    )
    
    print(f"\nTOM TAT")
    print(f"   - So anh da luu: {len(frames)}")
    if frames:
        print(f"   - Thu muc: {os.path.dirname(frames[0])}")
        print(f"   - Anh dau tien: {frames[0]}")