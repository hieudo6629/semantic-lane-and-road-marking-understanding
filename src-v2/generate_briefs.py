"""
Sinh file <ten>_brief.json cho toàn bộ JSON thô đã có sẵn trong 1 thư mục,
KHÔNG chạy lại model lane/sign detection (chỉ áp summarize_scene() lên JSON
đã có) - dùng khi JSON thô đã đúng/mới nhất (ví dụ output-v3/ sau khi sửa
lane_count) nhưng batch_process.py chưa từng chạy qua để sinh _brief.json
(ví dụ vì scene_summarizer.py được thêm SAU lần chạy batch_process.py đó).

Nếu muốn sinh JSON thô MỚI (chạy lại model thật), dùng batch_process.py.

Cách dùng:
    python generate_briefs.py --dir output-v3
"""

import argparse
import glob
import json
import os
import sys

from analysis.scene_summarizer import summarize_scene


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, AttributeError):
            pass

    parser = argparse.ArgumentParser(description="Sinh <ten>_brief.json từ JSON thô đã có, không chạy lại model")
    parser.add_argument("--dir", type=str, required=True, help="Thư mục chứa <ten>.json thô (ghi đè <ten>_brief.json trong cùng thư mục)")
    args = parser.parse_args()

    json_paths = [
        p for p in sorted(glob.glob(os.path.join(args.dir, "*.json")))
        if not os.path.basename(p).startswith("_") and not p.endswith("_brief.json")
    ]

    if not json_paths:
        print(f"Không tìm thấy JSON thô nào trong: {args.dir}")
        return

    count = 0
    errors = []
    for path in json_paths:
        base_name = os.path.splitext(os.path.basename(path))[0]
        brief_path = os.path.join(args.dir, f"{base_name}_brief.json")
        try:
            with open(path, encoding="utf-8") as f:
                scene_dict = json.load(f)
            brief = summarize_scene(scene_dict)
            with open(brief_path, "w", encoding="utf-8") as f:
                json.dump(brief, f, indent=2, ensure_ascii=False)
            count += 1
        except Exception as exc:  # noqa: BLE001 - lỗi 1 file không được dừng cả batch
            errors.append((base_name, str(exc)))

    print(f"Đã sinh {count}/{len(json_paths)} file _brief.json trong: {args.dir}")
    if errors:
        print(f"Lỗi ở {len(errors)} file:")
        for name, err in errors:
            print(f"  {name}: {err}")


if __name__ == "__main__":
    main()
