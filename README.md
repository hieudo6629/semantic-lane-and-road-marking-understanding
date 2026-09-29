# Semantic Lane and Traffic Sign Understanding Using Vision-Language Models for Driving Decision Support

This repository contains the code for the thesis. The pipeline takes a dashcam image and produces **Structured Semantic Information (SSI)**, a JSON description of the lanes and traffic signs. A Vision-Language Model (VLM) then uses the SSI to generate driving recommendations. The recommendations are scored with **LLM-as-a-Judge**, and the judge scores are checked against human ratings.

All current code is in [`src-v2/`](src-v2/). The old `src/` and `test/` folders are no longer used and are ignored by git.

All commands below are run from inside `src-v2/`.

---

## 1. Pipeline overview (Thesis Ch. 3)

```text
Dashcam image I
  ├─> perception/lane_detector.py   UFLD-v2 (ResNet-34, CULane)  -> lane boundaries
  └─> perception/sign_detector.py   YOLOv8n (fine-tuned TT100K) -> traffic signs
          │
          v
  analysis/scene_builder.py         geometric rules, no learned parameters (Φ)
  analysis/lane_analyzer.py         ego lane, vehicle offset, curvature, lane count
  analysis/road_type.py             road shape / curve direction
          │
          v
  <image>.json        full TrafficScene
  analysis/scene_summarizer.py -> <image>_brief.json   = SSI sent to the VLM
          │
          v
  llm_batch_client.py               VLM via NVIDIA NIM, 3 input modes:
                                      image_only (c1) | json_only (c2, SSI-only) | image_json (c3, Combined)
          │
          v
  score_output_by_{gemini,gpt,deepseek}.py   LLM-as-a-Judge, 6 criteria, 1–5 scale
```

| File | Role |
|---|---|
| [`pipeline.py`](src-v2/pipeline.py) | `TrafficScenePipeline`: runs lane and sign detection on the same image, then builds the scene |
| [`main.py`](src-v2/main.py) | CLI for a single image (`--image`, `--culane`, `--demo`, `--self-test`) |
| [`batch_process.py`](src-v2/batch_process.py) | Runs the pipeline on a folder and writes `<img>.json`, `<img>_brief.json`, `<img>_vis.jpg` |
| [`generate_briefs.py`](src-v2/generate_briefs.py) | Rebuilds `_brief.json` from existing raw JSON without rerunning the models |
| [`reasoning/prompt_builder.py`](src-v2/reasoning/prompt_builder.py) | Builds prompts from a `TrafficScene` |
| [`configs/config.yaml`](src-v2/configs/config.yaml) | Model paths, sign confidence threshold (0.5), CULane root |
| [`configs/traffic_sign_mapping.json`](src-v2/configs/traffic_sign_mapping.json) | Maps TT100K classes to sign types |

---

## 2. Setup

```bash
pip install -r src-v2/requirements.txt
pip install pandas openpyxl scipy google-generativeai openai   # needed by the evaluation scripts
```

- **UFLD-v2**: clone [Ultra-Fast-Lane-Detection-v2](https://github.com/cfzd/Ultra-Fast-Lane-Detection-v2) and download `culane_res34.pth`.
- **YOLOv8n TT100K**: the checkpoint `yolov8n_tt100k_best.pt`, fine-tuned on a Kaggle GPU (640×640, batch 83, SGD, up to 100 epochs, patience 30).
- Set `lane_model_path`, `ufld_repo_path` and `sign_model_path` in `configs/config.yaml`.
- **API keys** (environment variables): `NVIDIA_API_KEY` for the VLM, `GEMINI_API_KEY`, `OPENAI_API_KEY` and `DEEPSEEK_API_KEY` for the judges.

---

## 3. Data (Thesis §4.1.2)

| Dataset | Folder | Purpose |
|---|---|---|
| TT100K | (external) | Fine-tuning YOLOv8n, 85/15 train/val split |
| CULane, 200 images (176 Normal / 24 Hard) | `input/` | Main evaluation of SSI and the VLM experiments |
| Self-collected dashcam images, 200 images | `input_real_life/` | Evaluation on data outside CULane |

Hand-labelled ground truth:
- `image_labels.xlsx` for CULane.
- `new_image_labels.xlsx` for the self-collected set.
- `human_agreement_sample.xlsx` for the 20 images rated by a human.

**Building the self-collected set:** [`get_image_from_video.py`](src-v2/get_image_from_video.py) extracts up to 200 frames from a dashcam video at random intervals. Set `VIDEO_PATH` and `OUTPUT_DIR` at the bottom of the file first.

```bash
python get_image_from_video.py
```

---

## 4. Experiment workflow (Thesis Ch. 4)

### Step 1: Extract SSI (input to every later experiment)

```bash
python batch_process.py --input input            --output output-v3          # CULane
python batch_process.py --input input_real_life  --output output_real_life   # self-collected
```

### Step 2: Evaluate the SSI extraction module (§4.2)

| Section | Content | Script / source |
|---|---|---|
| 4.2.1 | Lane semantics on CULane: lane count Acc/MAE/Precision, ego lane, road shape (Normal/Hard) | `output-v3/*_brief.json` compared with `image_labels.xlsx` (also used by `evaluate_llm_lane_perception.py`, `evaluate_road_condition.py`) |
| 4.2.1 | Lane semantics on the self-collected set | `python evaluate_real_life.py` |
| 4.2.2 | YOLOv8n training results on the TT100K validation set (Precision/Recall/mAP50/mAP50-95) | Computed automatically by Ultralytics during fine-tuning on Kaggle (the fine-tuning script is not in this repo) |
| 4.2.2 | Traffic signs on CULane and the self-collected set, at confidence 0.5: Precision/Recall/F1/Classification Acc | Visual review of `sign_crops_culane/`, `sign_crops/`, `culane_recall_check/`, `sign_type_labeling_worksheet*.xlsx`. On the self-collected set: `evaluate_real_life.py` |
| 4.2.3 | SSI field quality | Same ground truth as 4.2.1 and 4.2.2 |
| 4.2.4 | CPU latency (lane / sign / semantic step, batch 1) on 200 CULane and 200 self-collected images | `python benchmark_cpu_latency.py`<br>`python benchmark_yolov8n_predict.py`<br>`python benchmark_yolo_variants_real_life.py` → `evaluation_results/cpu_latency/` |

The ego-lane reference row is set to ρ = 0.919 (`vehicle_position_y_ratio` in `analysis/lane_analyzer.py`). This value is the share of the CULane image that is still visible above the hood.

### Step 3: Generate recommendations with the VLM (§3.5)

The API settings are the same for every request: `max_tokens=400`, `temperature=0.2`, `top_p=0.7`, `frequency_penalty=0.4`, and a 120 s timeout. The default model is `nvidia/ising-calibration-1.5-31b`.

```bash
python llm_batch_client.py --mode image_only --image-dir input                          --output-dir output-suggest-image-only-prompt-v5-31b
python llm_batch_client.py --mode json_only                     --json-dir output-v3    --output-dir output-suggest-json-only-prompt-v5-31b
python llm_batch_client.py --mode image_json --image-dir input  --json-dir output-v3    --output-dir output-suggest-image-json-prompt-v5-31b
```

`json_only` and `image_json` send `<img>_brief.json` (the SSI) to the VLM. The prompts are hard-coded in `DEFAULT_PROMPTS`, and the full text is in the thesis appendix.

### Step 4: Evaluate recommendation quality (§4.3)

| Section | Content | Script → result |
|---|---|---|
| 4.3.1 | Screening of 3 candidate VLMs (`ising-calibration-31b`, `nemotron-nano-vl-8b`, `nemotron-nano-12b-v2-vl`) on 200 CULane images, Combined mode, Gemini judge | Generate the outputs with `llm_batch_client.py --mode image_json --model <model>`. Then run `python evaluate_model_comparison_full.py` → `evaluation_results/model_comparison_full/`. `nemotron-nano-12b-v2-vl` returned only 34/200 responses (166 HTTP 500 errors), so it is left out of the quality comparison. |
| 4.3.2 | 3 input modes (`ising-calibration-31b`, 200 CULane images) × 3 judges | Gemini: `evaluate_mode_comparison_v5.py` → `session_3_ising31b/`<br>GPT-5 Mini: `evaluate_mode_comparison_v5_gpt.py` → `mode_comparison_gpt/`<br>DeepSeek: `evaluate_mode_comparison_v5_deepseek.py` → `mode_comparison_deepseek/` |
| 4.3.3 | Effect of SSI accuracy: images are split by whether the SSI ego lane is correct (172 correct / 28 incorrect). Wilcoxon tests Δ within each group; Mann–Whitney U compares the two groups. | `python analyze_ssi_error_impact.py` → `evaluation_results/ssi_error_impact/` (reads existing results, no API calls) |

**Statistical tests for §4.3.2.** These scripts only produce the per-image scores. The tests are run on those scores:
- For each image, the aggregate score is the mean of the 6 criteria, and Δ = Combined − Image-only.
- The pairs (c1,c2), (c1,c3) and (c2,c3) are tested per judge with the two-sided Wilcoxon signed-rank test. The Bonferroni threshold is 0.05/9 = 0.0056.
- The effect size is Cohen's d_z = mean(d) / sd(d).

**Judges.** All three judges use the same rubric. It is defined in `score_output_by_gemini.py` and imported by the GPT and DeepSeek scripts.

| Judge | Model | Settings |
|---|---|---|
| Gemini | `gemini-3.5-flash` | temperature 0.1, up to 8192 tokens |
| GPT-5 Mini | `gpt-5-mini` | up to 4096 tokens, API default temperature |
| DeepSeek | `deepseek-v4-flash-vision-exp` | temperature 0.1, up to 8192 tokens |

Each judge retries up to 5 times. In one call, it scores the outputs of all three modes for the same image, so scores are compared only within the same scoring session. Before running DeepSeek, check that the model accepts images with `python score_output_by_deepseek.py --test-only`.

### Step 5: Compare LLM-as-a-Judge with human ratings (§4.4)

This uses 20 images in Combined mode, which gives 120 score pairs per judge.

```bash
python evaluate_human_agreement.py              # Gemini vs human
python score_output_by_gpt.py        && python evaluate_model_comparison_gpt.py       # GPT-5 Mini
python score_output_by_deepseek.py   && python evaluate_model_comparison_deepseek.py  # DeepSeek
```

### Step 6: Supplementary experiments (§4.5)

**4.5.1: Can the VLM extract the semantics by itself?** The VLM receives only the image and returns JSON in the SSI schema. The result is compared with the UFLD-v2 pipeline and the ground truth.

```bash
python llm_lane_perception.py --input-dir input --output-dir output-llm-lane-perception
python evaluate_llm_lane_perception.py
python evaluate_llm_lane_perception.py --labels new_image_labels.xlsx \
    --pipeline-dir output_real_life --llm-dir output-llm-lane-perception-real-life
```

**4.5.2: Effect of the prompt.** Three prompt versions are compared. The model (`ising-calibration-31b`), the Combined mode and the 200 CULane images stay the same. The thesis names map to the code as follows:

| Thesis | Code | Content |
|---|---|---|
| Prompt v1 | `p1_minimal` ([prompt_p1_minimal.txt](src-v2/prompt_p1_minimal.txt)) | Asks only for a recommendation from the image and the SSI |
| Prompt v2 | `p2_minimal_structured` ([prompt_p2_minimal_structured.txt](src-v2/prompt_p2_minimal_structured.txt)) | v1 plus the 3-part output structure |
| Prompt v3 | `current` (`DEFAULT_PROMPTS` in `llm_batch_client.py`) | v2 plus rules on evidence, inference, and conflicts between the image and the SSI |

Gemini scores all three versions together in one call per image, in a separate scoring session (`evaluation_results/session_prompt_ablation/`).

```bash
python evaluate_prompt_ablation.py        # generate + score the three versions in one call
python analyze_prompt_ablation_stats.py   # Wilcoxon signed-rank for each pair of versions
```

The script also prints a paired t-test and Cohen's d as a cross-check. The thesis reports Wilcoxon with a Bonferroni threshold of 0.05/3 = 0.0167, which you compare against the p-values yourself.

---

## 5. Where the results are

- `evaluation_results/`: judge scores for each experiment, one JSON file per image, plus `_final_summary.json`. [`evaluation_results/README_NGUON_DU_LIEU.md`](src-v2/evaluation_results/README_NGUON_DU_LIEU.md) maps each thesis table to the folder and script it comes from.
- `output-v3/`, `output_real_life/`: SSI for CULane and for the self-collected set.
- `output-suggest-*/`: VLM recommendations (`.txt`) for each mode and prompt version.
- `figures/`: figures used in the thesis.
