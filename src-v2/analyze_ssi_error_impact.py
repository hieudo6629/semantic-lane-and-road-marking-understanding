"""
Phân tích tác động của lỗi SSI lên chất lượng khuyến nghị (thực nghiệm chính, Mục 4.3.2).

Chia 200 ảnh CULane theo độ đúng của các trường SSI so với ground truth gán tay:
    - làn ego đúng/sai        : cột ego_lane_correct trong image_labels.xlsx
    - số làn đúng/sai         : lane_count trong output-v3/<ảnh>_brief.json (SSI mà VLM nhận) so với true_lane_count
    - nhóm ảnh Normal/Hard     : hard_reason_key != 0
Trong từng nhóm, so sánh điểm tổng hợp (trung bình 6 tiêu chí) của ba chế độ và
Δ = Kết hợp − Chỉ ảnh, cho cả ba judge (Gemini, GPT-5 Mini, DeepSeek).
Kiểm định: Wilcoxon signed-rank (Δ ≠ 0 trong nhóm), Mann–Whitney U (khác biệt giữa hai nhóm).

Chỉ đọc dữ liệu có sẵn, không gọi mô hình. Kết quả ghi vào evaluation_results/ssi_error_impact/.

Chạy (từ thư mục src-v2):
    python analyze_ssi_error_impact.py
"""

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats

CRITERIA = ["situation_understanding", "road_understanding", "lane_ego_position",
            "traffic_sign_rule", "driving_recommendation", "safety_considerations"]
JUDGES = {"Gemini": "evaluation_results/session_3_ising31b",
          "GPT-5 Mini": "evaluation_results/mode_comparison_gpt",
          "DeepSeek": "evaluation_results/mode_comparison_deepseek"}
MODES = {"image_only": "prompt_image", "ssi_only": "prompt_json", "combined": "prompt_image_json"}
GROUPINGS = [("ego_ok", "Làn ego trong SSI", {True: "đúng", False: "sai"}),
             ("lane_count_ok", "Số làn trong SSI", {True: "đúng", False: "sai"}),
             ("hard", "Nhóm ảnh", {False: "Normal", True: "Hard"})]
OUT_DIR = "evaluation_results/ssi_error_impact"


def overall(entry):
    vals = [entry["scores"][c] for c in CRITERIA]
    return float(np.mean([v["score"] if isinstance(v, dict) else v for v in vals]))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    log_lines = []

    def log(msg=""):
        print(msg)
        log_lines.append(msg)

    log(f"Chạy lúc {datetime.now().isoformat(timespec='seconds')}")
    labels = pd.read_excel("image_labels.xlsx")
    labels.columns = [c.strip() for c in labels.columns]
    groups = []
    for _, r in labels.iterrows():
        img = int(r["Image"])
        ssi = json.load(open(f"output-v3/{img}_brief.json", encoding="utf-8"))
        groups.append({"img": img,
                       "lane_count_ok": int(ssi["lane_count"]) == int(r["true_lane_count"]),
                       "ego_ok": bool(r["ego_lane_correct"]) if not pd.isna(r["ego_lane_correct"]) else False,
                       "hard": int(r["hard_reason_key"]) != 0})
    G = pd.DataFrame(groups).set_index("img")
    log(f"Số ảnh: {len(G)} | làn ego đúng: {int(G.ego_ok.sum())} | số làn đúng: {int(G.lane_count_ok.sum())} | Hard: {int(G.hard.sum())}")

    summary, per_image = {}, []
    for judge, folder in JUDGES.items():
        scores = {}
        for img in G.index:
            path = f"{folder}/{img}.json"
            if os.path.exists(path):
                data = json.load(open(path, encoding="utf-8"))
                scores[img] = {m: overall(data[k]) for m, k in MODES.items()}
        df = pd.DataFrame(scores).T.join(G)
        df["delta"] = df["combined"] - df["image_only"]
        for img, row in df.iterrows():
            per_image.append({"judge": judge, "img": img, **row.to_dict()})
        log(f"\n===== {judge} (N={len(df)})")
        summary[judge] = {}
        for col, name, lab in GROUPINGS:
            summary[judge][col] = {}
            log(f"  {name}:")
            for val in [True, False] if col != "hard" else [False, True]:
                g = df[df[col] == val]
                p_w = float(stats.wilcoxon(g["combined"], g["image_only"]).pvalue) if (g["delta"] != 0).sum() > 5 else float("nan")
                entry = {"n": int(len(g)), "image_only": g.image_only.mean(), "ssi_only": g.ssi_only.mean(),
                         "combined": g.combined.mean(), "delta": g.delta.mean(), "wilcoxon_p_delta": p_w}
                summary[judge][col][lab[val]] = entry
                log(f"    {lab[val]:6s} n={entry['n']:3d}  Chỉ ảnh={entry['image_only']:.2f}  Chỉ SSI={entry['ssi_only']:.2f}  "
                    f"Kết hợp={entry['combined']:.2f}  Δ={entry['delta']:+.2f} (Wilcoxon p={p_w:.3g})")
            a, b = df[df[col]], df[~df[col]]
            p_delta = float(stats.mannwhitneyu(a["delta"], b["delta"]).pvalue)
            p_ssi = float(stats.mannwhitneyu(a["ssi_only"], b["ssi_only"]).pvalue)
            p_comb = float(stats.mannwhitneyu(a["combined"], b["combined"]).pvalue)
            summary[judge][col]["mann_whitney_p"] = {"delta": p_delta, "ssi_only": p_ssi, "combined": p_comb}
            log(f"    Mann–Whitney giữa hai nhóm: Δ p={p_delta:.3g} | Chỉ SSI p={p_ssi:.3g} | Kết hợp p={p_comb:.3g}")

    json.dump(summary, open(f"{OUT_DIR}/summary.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    pd.DataFrame(per_image).to_csv(f"{OUT_DIR}/per_image.csv", index=False, encoding="utf-8-sig")
    open(f"{OUT_DIR}/log.txt", "w", encoding="utf-8").write("\n".join(log_lines) + "\n")
    print(f"\nĐã lưu: {OUT_DIR}/summary.json, per_image.csv, log.txt")


if __name__ == "__main__":
    main()
