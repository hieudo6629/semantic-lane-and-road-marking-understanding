# Semantic Lane and Traffic Sign Understanding Using Vision-Language Models for Driving Decision Support

This repository contains the source code for the master's thesis. The system takes a dashcam image and produces driving recommendations with a Vision-Language Model (VLM). Before the VLM, a detection step and a rule-based semantic representation step turn the image into **Structured Semantic Information (SSI)**. The thesis tests whether adding SSI to the VLM input changes the quality of the recommendations.

The code is in [`src-v2/`](src-v2/). All commands below are run from inside `src-v2/`.

---

## 1. Overall architecture (Thesis §3.2)

The pipeline has two modules. The evaluation stage runs separately from them.

```text
                    ┌──────────────── SSI extraction module ────────────────┐
Dashcam image I ──> │ Detection:          UFLD-v2  -> lane boundaries        │
                    │                     YOLOv8n  -> traffic signs          │
                    │ Semantic represent.: geometric rules (Φ) -> SSI (JSON) │
                    └───────────────────────────┬───────────────────────────┘
                                                v
                    ┌──────── Recommendation generation module ─────────────┐
                    │ VLM (pretrained, via API), 3 input modes:              │
                    │   c1 Image-only | c2 SSI-only | c3 Combined (image+SSI)│
                    │ Output: Situation / Recommendation / Safety note       │
                    └───────────────────────────┬───────────────────────────┘
                                                v
                    Evaluation: LLM-as-a-Judge (6 criteria, 1–5 scale),
                                checked against human ratings
```

Design assumptions (§3.1):
- Each image is processed on its own, with no temporal information.
- The camera is mounted at the horizontal center of the vehicle.
- There is no explicit depth estimation.
- The local modules run on a CPU.
- The VLM is used through an API and is not fine-tuned.

---

## 2. SSI extraction module

### 2.1 Detection (§3.3)

| Model | Role | Code |
|---|---|---|
| UFLD-v2 (ResNet-34, CULane checkpoint) | Lane detection | [`perception/lane_detector.py`](src-v2/perception/lane_detector.py) |
| YOLOv8n fine-tuned on TT100K | Traffic sign detection, confidence ≥ 0.5 | [`perception/sign_detector.py`](src-v2/perception/sign_detector.py) |

The two detectors process the same image in one call ([`pipeline.py`](src-v2/pipeline.py)).

### 2.2 Semantic representation (§3.4)

This step uses explicit geometric rules and has no learnable parameters.

**Lane semantics** ([`analysis/lane_analyzer.py`](src-v2/analysis/lane_analyzer.py), [`analysis/road_type.py`](src-v2/analysis/road_type.py)):
1. Sort the lane boundaries by their actual position.
2. Determine the ego lane at the reference row ρ = 0.919.
3. Compute the vehicle offset (direction, magnitude, percentage).
4. Estimate the curvature.
5. Classify the road shape (straight / gentle curve / sharp curve) and the curve direction.
6. Count the lanes and the neighboring lanes on each side.

**Traffic sign semantics** ([`perception/sign_detector.py`](src-v2/perception/sign_detector.py), [`configs/traffic_sign_mapping.json`](src-v2/configs/traffic_sign_mapping.json)):
1. Filter the detections.
2. Map each class code to `sign_name` and `sign_type`.
3. Assign the relative position (left / center / right) from the center of the bounding box.

**SSI construction** ([`analysis/scene_builder.py`](src-v2/analysis/scene_builder.py), [`analysis/scene_summarizer.py`](src-v2/analysis/scene_summarizer.py)): the lane and sign semantics are combined into one JSON per image, `<image>_brief.json`. It contains the lane count, ego lane, vehicle offset, neighboring lanes, road shape and traffic signs.

Run the module on a folder of images:

```bash
python batch_process.py --input <image_dir> --output <ssi_dir>
```

---

## 3. Recommendation generation module (§3.5)

[`llm_batch_client.py`](src-v2/llm_batch_client.py) sends one request per image and per mode to the VLM through NVIDIA NIM.

The prompt for each mode is `P_m = P_common ⊕ B_m ⊕ P_out`:
- `P_common` holds the role, the task, the rules for using evidence, and hallucination control.
- `B_m` is the mode-specific block.
- `P_out` is the output format.

`P_common` and `P_out` are the same in all three modes. When SSI is used, it is inserted into the prompt as raw JSON.

| Mode | `--mode` | VLM input |
|---|---|---|
| c1 Image-only | `image_only` | Image |
| c2 SSI-only | `json_only` | SSI |
| c3 Combined | `image_json` | Image + SSI |

The generation settings are the same for every request: `max_tokens=400`, `temperature=0.2`, `top_p=0.7`, `frequency_penalty=0.4`, and a 120 s timeout. Images are compressed to ≤ 150 KB before Base64 encoding.

```bash
python llm_batch_client.py --mode image_only --image-dir <image_dir>                      --output-dir <out_dir>
python llm_batch_client.py --mode json_only                          --json-dir <ssi_dir> --output-dir <out_dir>
python llm_batch_client.py --mode image_json --image-dir <image_dir> --json-dir <ssi_dir> --output-dir <out_dir>
```

---

## 4. Evaluation method (§3.6)

**Controlled comparison design:**
- Independent variable: the input mode.
- Dependent variables: the 6 criterion scores and the aggregate score.
- Unit of analysis: one image. The three modes of the same image form one set of paired observations.

**Rubric:** six criteria, each scored 1–5:
- Situation understanding
- Road geometry understanding
- Ego-lane position
- Signs and rules
- Driving recommendation
- Safety considerations

**LLM-as-a-Judge:** in one call per image, the judge receives the image, the recommendations to compare and the rubric. Scores are compared only within the same scoring session. The rubric is defined in [`score_output_by_gemini.py`](src-v2/score_output_by_gemini.py) and shared by all judges.

| Judge | Model | Script |
|---|---|---|
| Gemini (primary) | `gemini-3.5-flash` | `score_output_by_gemini.py` |
| GPT-5 Mini | `gpt-5-mini` | `score_output_by_gpt.py` |
| DeepSeek | `deepseek-v4-flash-vision-exp` | `score_output_by_deepseek.py` |

**Statistics:**
- Δ = S(Combined) − S(Image-only).
- Each pair of modes is compared with the two-sided Wilcoxon signed-rank test, using a Bonferroni correction.
- The effect size is Cohen's d_z.

---

## 5. Experiments (Thesis Ch. 4)

### 5.1 Data (§4.1.2)

| Dataset | Folder | Ground truth | Purpose |
|---|---|---|---|
| TT100K (85/15 split) | external | — | Fine-tuning YOLOv8n |
| CULane, 200 images (Normal / Hard) | `input/` | `image_labels.xlsx` | Main evaluation |
| Self-collected dashcam, 200 images | `input_real_life/` | `new_image_labels.xlsx` | Evaluation outside CULane |

The self-collected images are frames taken from dashcam video with [`get_image_from_video.py`](src-v2/get_image_from_video.py).

### 5.2 Mapping from thesis sections to code

| Section | Experiment | Code |
|---|---|---|
| 4.2.1 | Lane semantic extraction: lane count, ego lane, road shape | SSI (`batch_process.py`) compared with the hand-labelled ground truth; `evaluate_real_life.py` |
| 4.2.2 | Traffic sign detection: Precision, Recall, F1, classification accuracy | YOLOv8n output reviewed by eye; `evaluate_real_life.py` |
| 4.2.3 | SSI field quality | Ground truth from 4.2.1 and 4.2.2 |
| 4.2.4 | CPU cost of the SSI extraction module | `benchmark_cpu_latency.py`, `benchmark_yolov8n_predict.py`, `benchmark_yolo_variants_real_life.py` |
| 4.3.1 | Screening of candidate VLMs (Combined mode, Gemini judge) | `llm_batch_client.py --model <model>`, `evaluate_model_comparison_full.py` |
| 4.3.2 | Role of SSI: 3 modes × 3 judges | `evaluate_mode_comparison_v5.py`, `evaluate_mode_comparison_v5_gpt.py`, `evaluate_mode_comparison_v5_deepseek.py` |
| 4.3.3 | Effect of SSI accuracy on recommendation quality | `analyze_ssi_error_impact.py` |
| 4.4 | LLM-as-a-Judge vs human ratings (20 images, Combined mode) | `evaluate_human_agreement.py`, `evaluate_model_comparison_gpt.py`, `evaluate_model_comparison_deepseek.py` |
| 4.5.1 | Can the VLM extract lane semantics by itself? | `llm_lane_perception.py`, `evaluate_llm_lane_perception.py` |
| 4.5.2 | Influence of the prompt (v1 / v2 / v3) | `evaluate_prompt_ablation.py`, `analyze_prompt_ablation_stats.py` |

The prompt versions in §4.5.2 correspond to these files:
- v1 is [`prompt_p1_minimal.txt`](src-v2/prompt_p1_minimal.txt).
- v2 is [`prompt_p2_minimal_structured.txt`](src-v2/prompt_p2_minimal_structured.txt).
- v3 is the main prompt, `DEFAULT_PROMPTS` in `llm_batch_client.py`.

Judge scores are saved in `src-v2/evaluation_results/`.

---

## 6. Setup

```bash
pip install -r src-v2/requirements.txt
pip install pandas openpyxl scipy google-generativeai openai
```

- Clone [Ultra-Fast-Lane-Detection-v2](https://github.com/cfzd/Ultra-Fast-Lane-Detection-v2) and download `culane_res34.pth`. You also need the YOLOv8n checkpoint fine-tuned on TT100K.
- Set the model paths in [`configs/config.yaml`](src-v2/configs/config.yaml).
- Set these environment variables: `NVIDIA_API_KEY` (VLM), `GEMINI_API_KEY`, `OPENAI_API_KEY` and `DEEPSEEK_API_KEY` (judges).
