import os
import time
import glob
from pathlib import Path
from googletrans import Translator

def translate_folder(
    input_folder: str,
    output_folder: str,
    limit: int = None,
    delay: float = 1.5,
    src_lang: str = 'en',
    dest_lang: str = 'vi'
):
    """
    Dịch toàn bộ file .txt trong thư mục input sang tiếng Việt.
    """
    
    # --- Kiểm tra và sửa lỗi đường dẫn ---
    # Loại bỏ dấu cách thừa
    input_folder = input_folder.strip()
    output_folder = output_folder.strip()
    
    # Kiểm tra thư mục input
    if not os.path.exists(input_folder):
        print(f"❌ Lỗi: Thư mục input không tồn tại: {input_folder}")
        
        # Thử tìm kiếm
        parent_dir = os.path.dirname(input_folder)
        folder_name = os.path.basename(input_folder)
        
        if os.path.exists(parent_dir):
            print(f"\n🔍 Đang tìm kiếm thư mục '{folder_name}' trong {parent_dir}")
            for item in os.listdir(parent_dir):
                if folder_name.lower() in item.lower():
                    possible_path = os.path.join(parent_dir, item)
                    if os.path.isdir(possible_path):
                        print(f"✅ Tìm thấy: {possible_path}")
                        input_folder = possible_path
                        break
        
        if not os.path.exists(input_folder):
            print(f"❌ Không thể tìm thấy thư mục cần dịch.")
            return
    
    # --- Tạo thư mục output ---
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"📁 Input:  {input_folder}")
    print(f"📁 Output: {output_folder}")
    
    # --- Tìm file .txt ---
    txt_files = glob.glob(os.path.join(input_folder, "*.txt"))
    txt_files.extend(glob.glob(os.path.join(input_folder, "*.md")))
    
    if not txt_files:
        print(f"⚠️  Không tìm thấy file .txt hoặc .md trong {input_folder}")
        return
    
    print(f"📄 Tìm thấy {len(txt_files)} file")
    
    # Áp dụng giới hạn
    if limit is not None and limit > 0:
        txt_files = txt_files[:limit]
        print(f"🎯 Chỉ dịch {len(txt_files)} file đầu tiên")
    
    # Khởi tạo translator
    translator = Translator()
    
    # Dịch từng file
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, file_path in enumerate(txt_files, 1):
        file_name = os.path.basename(file_path)
        output_path = os.path.join(output_folder, file_name)
        
        print(f"\n[{i}/{len(txt_files)}] 📝 {file_name}")
        
        try:
            # Đọc file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(f"   ⚠️  File rỗng, bỏ qua")
                skipped_count += 1
                continue
            
            if os.path.exists(output_path):
                print(f"   ⚠️  File đã tồn tại, bỏ qua")
                skipped_count += 1
                continue
            
            # Dịch
            print(f"   ⏳ Đang dịch...")
            translated = translator.translate(content, src=src_lang, dest=dest_lang)
            
            # Ghi file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated.text)
            
            success_count += 1
            print(f"   ✅ Đã dịch xong")
            
            # Chờ trước request tiếp theo
            if i < len(txt_files):
                time.sleep(delay)
                
        except Exception as e:
            error_count += 1
            print(f"   ❌ Lỗi: {e}")
    
    # Thống kê
    print("\n" + "="*50)
    print(f"✅ Thành công: {success_count}")
    print(f"❌ Lỗi: {error_count}")
    print(f"⏭️  Bỏ qua: {skipped_count}")
    print(f"📁 Lưu tại: {output_folder}")


if __name__ == "__main__":
    # --- CẤU HÌNH ---
    # Đường dẫn input (có thể có hoặc không có dấu cách)
    INPUT_FOLDER = r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\semantic-road-marking-understanding\src-v2\output-suggest-json-only-prompt-v2"
    
    # Đường dẫn output
    OUTPUT_FOLDER = r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\semantic-road-marking-understanding\src-v2\output-suggest-json-only-prompt-v2-vi"
    
    # Số file tối đa (None = tất cả)
    LIMIT = None
    
    # Thời gian chờ (giây)
    DELAY = 1.5
    
    # --- CHẠY ---
    translate_folder(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        limit=LIMIT,
        delay=DELAY
    )