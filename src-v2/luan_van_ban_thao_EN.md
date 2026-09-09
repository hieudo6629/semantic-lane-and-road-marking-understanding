# FPT INSTITUTE OF MANAGEMENT AND TECHNOLOGY

## SEMANTIC LANE AND TRAFFIC SIGN UNDERSTANDING USING LARGE LANGUAGE MODELS FOR DRIVING DECISION SUPPORT

*(Vietnamese title: Hiểu Làn đường và Biển báo Giao thông theo Ngữ nghĩa sử dụng Mô hình Ngôn ngữ Lớn để Hỗ trợ Ra quyết định Lái xe)*

**MASTER'S THESIS**

Major: Software Engineering

Author: Do Minh Hieu

Academic Supervisor: Dr. Doan Nhat Quang

Hanoi, 2026

---

## DECLARATION

I hereby declare that this thesis is my own work, carried out under the academic supervision of Dr. Doan Nhat Quang.

The data and experimental results presented in this thesis are truthful, collected and processed using tools and source code that I built myself, and have not been published in any other work. Content referenced from the work of other authors is fully and clearly cited in the References section.

Should any dishonesty or violation of scientific integrity regulations be found, I take full responsibility before the Thesis Committee and the University.

## ACKNOWLEDGMENTS

To complete this Master's program and this research, beyond my own effort, I have received enormous teaching, guidance, and encouragement from my teachers, my university, my friends, and my family.

First, I would like to express my sincere gratitude to my thesis supervisor, Dr. Doan Nhat Quang. He is the one who inspired and guided me in shaping the idea for this research topic, and who spent a great deal of time instructing me, sharing knowledge, and reviewing and commenting throughout the course of this work. His dedicated guidance not only helped me complete this thesis but will also be valuable groundwork for my professional development going forward.

I sincerely thank the faculty and staff at the FPT Institute of Management and Technology (FSB) for creating a professional, open educational environment in which I could build a solid foundation of specialized knowledge and take part in valuable seminars. I would also like to thank my friends and colleagues, who were always willing to share knowledge, discuss ideas, and accompany me throughout my studies.

Finally, I would like to devote my deepest affection and boundless gratitude to my parents and siblings. My family has always been my firmest anchor, providing peace of mind, trust, and the best possible conditions for me to persevere through difficulties and complete my academic dream.

Despite considerable effort in carrying out and presenting this research, certain limitations remain unavoidable. I sincerely welcome any valuable feedback from the members of the Thesis Committee so that this work can be further improved.

---

## TABLE OF CONTENTS

- CHAPTER 1. INTRODUCTION
  - 1.1. Background and Motivation
  - 1.2. Research Objectives
  - 1.3. Data Scope
  - 1.4. Research Questions
  - 1.5. Main Contributions
  - 1.6. Thesis Structure
- CHAPTER 2. LITERATURE REVIEW AND RELATED WORK
  - 2.1. Lane Detection
  - 2.2. Traffic Sign Detection
  - 2.3. Multimodal Large Language Models for Driving Decision Support
  - 2.4. Evaluating Natural-Language Output Quality with LLM-as-a-Judge
  - 2.5. Research Gap
- CHAPTER 3. METHODOLOGY
  - 3.1. Overall System Architecture
  - 3.2. Data
  - 3.3. Semantic Lane Analysis
  - 3.4. Semantic JSON Structure Sent to the LLM
  - 3.5. Prompt Design for the Reasoning Layer
  - 3.6. Model Selection for the Reasoning Layer
  - 3.7. Evaluation Methodology
- CHAPTER 4. RESULTS AND DISCUSSION
  - 4.1. Lane-Understanding Module Accuracy (CULane)
  - 4.2. Independent Verification on Real-Life Data
  - 4.3. Traffic Sign Module on CULane
  - 4.4. Comparison of LLM Models for the Reasoning Layer
  - 4.5. Main Result: The Contribution of Semantic JSON
  - 4.6. Verifying the Reliability of the Evaluation Method
  - 4.7. Limitation: Data-Leakage Risk
  - 4.8. Verifying VLM Self-Perception of Lane Semantics
  - 4.9. Discussion: The Real Mechanism Behind the Contribution of Semantic JSON
- CHAPTER 5. CONCLUSION
  - 5.1. Summary of Contributions
  - 5.2. Answers to the Research Questions
  - 5.3. Limitations
  - 5.4. Future Work
- REFERENCES

## LIST OF ABBREVIATIONS

| Abbreviation | Full Term | Description |
|---|---|---|
| ADAS | Advanced Driver Assistance System | An advanced system that supports driving |
| VLM | Vision-Language Model | A multimodal (vision + language) model |
| LLM | Large Language Model | A large language model |
| MLLM | Multimodal Large Language Model | A large multimodal language model |
| UFLD-v2 | Ultra Fast Lane Detection v2 | A high-speed lane-detection architecture (version 2) |
| SCNN | Spatial Convolutional Neural Network | A spatial convolutional neural network |
| YOLO | You Only Look Once | A family of single-stage object-detection architectures |
| TT100K | Tsinghua-Tencent 100K | A large-scale traffic-sign dataset |
| MAE | Mean Absolute Error | Mean absolute error |
| IoU | Intersection over Union | A localization metric |
| F1 | F1-score | The harmonic mean of Precision and Recall |
| API | Application Programming Interface | An application programming interface |
| NIM | NVIDIA Inference Microservices | NVIDIA's model-inference service (the platform used to call the VLM in this thesis) |
| JSON | JavaScript Object Notation | A structured data format used as the semantic intermediate representation |
| RQ | Research Question | Research question |
| QCVN | Quy chuẩn Việt Nam (Vietnamese National Technical Regulation) | The Vietnamese national technical-standard system (applies to Vietnamese traffic signs) |

## LIST OF TABLES

| No. | Label | Title |
|---|---|---|
| 1 | Table 4.1 | Lane-understanding module accuracy before and after fixing the off-by-one bug (N=200) |
| 2 | Table 4.2 | Lane-understanding module performance by presence/absence of clear lane markings |
| 3 | Table 4.3 | Comparison of the lane- and sign-understanding modules between CULane and independent real-life data |
| 4 | Table 4.4 | Detailed content-quality comparison between nemotron-nano-8b and ising-calibration-31b (Mean ± SD, statistical tests) |
| 5 | Table 4.5 | Driving-recommendation quality scores (Mean ± SD) across three input modes, rated by three independent judges |
| 6 | Table 4.6 | Statistical significance of pairwise comparisons across the three input modes, per judge (N=200, image-paired data) |
| 7 | Table 4.7 | Mean scores (Mean ± SD) of the Gemini judge's six evaluation criteria across input modes |
| 8 | Table 4.8 | Reliability ranking of the three judges against human evaluation |
| 9 | Table 4.9 | Comparison of lane-semantics self-perception between the UFLD-v2 pipeline and the VLM |

## LIST OF FIGURES

| No. | Label | Title |
|---|---|---|
| 1 | Figure 3.1 | Overall architecture of the four-layer pipeline: Perception – Semantic Analysis – LLM Reasoning – Evaluation |

---

## ABSTRACT

Current advanced driver-assistance systems (ADAS) typically stop at low-level perception (pixel coordinates, bounding boxes) and fail to translate this information into traffic semantics that a human can understand and trust. This thesis builds and quantitatively validates a four-layer pipeline (Perception – Semantic Analysis – LLM Reasoning – Evaluation) that combines a lane-detection model, UFLD-v2 (used as-is in its pretrained form), a traffic-sign detection model, YOLOv8n (self fine-tuned on TT100K), a self-designed structured semantic conversion layer (JSON), and a multimodal large language model (VLM) that generates driving recommendations in natural language. The reasoning layer follows a training-free approach with no model fine-tuning; the training cost of the whole system is therefore limited to one lightweight YOLOv8n fine-tuning step, rather than training a dedicated VLM or LLM.

On the CULane dataset (N=200 fully hand-labeled images), the lane-understanding module reaches an overall Accuracy of 69.0% and 77.3% on the subset of images with clear lane markings, after an off-by-one unit-conversion bug was discovered and fixed — a bug that had initially limited Accuracy to only 11.1%. The results generalize well to an independently collected real-life dataset (N=200), with lane-count Precision reaching 99.4%. The thesis's central research question — whether structured semantic information (JSON) improves the quality of a VLM's driving recommendations compared with using images alone — is answered through a quantitative experiment on N=200 images, independently scored by three judge models (Gemini, GPT-5 Mini, DeepSeek) on the same six-criterion rubric. All three judges agree that the image-only mode consistently scores lowest, while adding JSON improves scores by up to 36% (Gemini: 3.32 → 4.53/5). The reliability of the LLM-as-a-judge method is verified against human evaluation (N=20), reaching 79.2% agreement within a ±1-point margin — a high level of agreement, clearly outperforming the two alternative judges verified under the same methodology.

A supplementary experiment, in which the VLM was asked to perceive lane semantics directly from the image without going through the UFLD-v2 layer, shows that the VLM's raw visual-perception ability is far from weak — it even outperforms the specialized pipeline when lane markings are missing or on data outside the pipeline's training domain. This finding leads to an important adjustment in how the central result should be interpreted: semantic JSON improves recommendation quality mainly through its role as scaffolding for reasoning and presentation in a multi-step task, rather than simply compensating for a lack of visual perception in the VLM. The thesis also discusses verified limitations — data-leakage risk, the sparsity of traffic-sign data in CULane — and proposes directions for future work: a hybrid architecture combining the computer-vision pipeline with a VLM fallback mechanism, and expansion to Vietnamese traffic data.

**Keywords**: semantic traffic understanding, multimodal large language models, lane detection, traffic sign detection, LLM-as-a-judge, driving decision support.

---

# CHAPTER 1. INTRODUCTION

## 1.1. Background and Motivation

Modern advanced driver-assistance systems (ADAS) typically rely on low-level perception modules such as lane detection, traffic-sign detection, and traffic-light detection. However, the output of these modules — pixel coordinates, bounding boxes, class IDs — is not sufficient on its own to support driving decisions in a way that a human can understand and trust. An intermediate layer is needed to convert this raw perception information into traffic semantics: which lane the vehicle is in, whether it is off-center, how many adjacent lanes remain, whether the road is straight or curved, and which signs or rules must be followed.

Recent advances in multimodal large language models (Vision-Language Models — VLMs) open up a new possibility: combining visual information (the image) with structured information (semantic JSON) to generate driving recommendations in natural language that are explained and grounded in evidence. The thesis's core research question is: *does structured semantic information (JSON) actually improve the quality of a VLM's output compared with using the raw image alone, and if so, by how much?*

## 1.2. Research Objectives

The thesis focuses on two core semantic components of a traffic scene:

1. Lane understanding: lane count, ego lane, vehicle offset, adjacent lanes, road shape (straight/curved).
2. Traffic-sign understanding: detecting and classifying traffic signs.

These two components are converted into structured semantics, combined with the original image, and fed into a large language model to generate driving recommendations, which are then evaluated using a reliable quantitative methodology.

## 1.3. Data Scope

To ensure objectivity, reproducibility, and comparability with other studies, the thesis uses two public, widely used datasets that have been vetted by the research community and share a common traffic characteristic — Chinese urban traffic:

- **CULane** — the standard benchmark for lane detection, used to evaluate the lane-understanding module and as the primary dataset for the whole pipeline.
- **TT100K** (Tsinghua-Tencent 100K) — the standard benchmark for traffic-sign detection, used to train and evaluate the sign module.

Choosing these two popular, readily available datasets — rather than collecting Vietnamese data from the outset — is intended to verify the pipeline's effectiveness on standardized data that can be objectively compared with other work, before extending it to the Vietnamese traffic context. This extension is discussed in Chapter 5 (Section 5.4).

## 1.4. Research Questions

- **RQ1**: How accurate is the lane-understanding module (based on UFLD-v2 and semantic post-processing) against hand-labeled ground truth, and does this accuracy generalize to independent data?
- **RQ2**: How effective is the sign-understanding module (based on YOLOv8 and TT100K), and what limitations should be noted when applying it across different datasets?
- **RQ3**: Does structured semantic JSON information improve the quality of a VLM's driving recommendations compared with using images alone?
- **RQ4**: Among accessible (free, low-cost) VLMs, which model is best suited to this task, in terms of reliability, quality, and operability?
- **RQ5**: Is the LLM-as-a-judge evaluation method reliable, and how can that reliability be quantified?

## 1.5. Main Contributions

This thesis does not propose a new lane- or sign-detection architecture, nor does it build a large-scale end-to-end driving VLM such as DriveGPT4 [2], DriveLM [3], or LMDrive [4]. The contribution lies at the integration layer, the semantic-conversion layer, and the evaluation methodology, with the reasoning layer following a training-free approach — using a free VLM via API, with no model fine-tuning (Section 3.6); the sign-perception layer involves one lightweight YOLOv8n fine-tuning step on TT100K (Section 3.2). Specifically, the thesis makes four contributions:

1. **A quantitatively validated semantic-conversion layer**: converts the raw output of UFLD-v2 into decision-level semantics (lane count, ego lane, vehicle offset, road shape), reaching 77.3% Accuracy on images with clear lane markings (N=176/200) and generalizing well to an independently collected dataset (N=200, 99.4% Precision, 86.5% Ego-lane Accuracy).
2. **Evidence for the importance of the semantic-interpretation layer**: the process of building this conversion layer uncovered an off-by-one unit-conversion bug that initially limited Accuracy to 11.1%, even though UFLD-v2 itself had already reached F1 = 76.0% at the detection layer. Fixing this bug is not, in itself, an algorithmic contribution, but it is concrete experimental evidence for an important methodological argument: a good detector does not automatically guarantee a correct decision-support system — the error can lie in the semantic-interpretation layer downstream, a layer that research focused on improving detectors tends to overlook.
3. **A reliability-verified LLM-as-a-judge evaluation methodology**, rather than applying it "as-is" the way general-purpose benchmarks do: verification against human evaluation (N=20) and cross-checking against multiple judges (Gemini, GPT-5 Mini, DeepSeek) on the same rubric. Gemini reaches the highest agreement among the three judges (79.2% agreement within ±1 point), consistent with prior evidence that LLM-as-a-judge can approach human-level reliability under the right conditions [5] (Sections 2.4, 4.6).
4. **Quantitative experimental results for RQ3** (N=200, cross-checked by three independent judges): semantic JSON improves driving-recommendation quality over image-only input (Gemini: 3.32 → 4.53/5, a 36% improvement), consistently across all three judges.

**Practical significance**. Unlike end-to-end VLM/VLA systems that require large-scale driving data and training infrastructure, this pipeline shows that a decision-support system capable of natural-language explanation, at low deployment cost, can be built from readily available VLMs — a suitable foundation for dashcam or smart black-box applications, or as a starting point for expansion to Vietnamese traffic data (Section 5.4).

## 1.6. Thesis Structure

Chapter 2 presents an overview of related work, covering lane detection, traffic-sign detection, multimodal large language models for driving, and the LLM-as-a-judge methodology. Chapter 3 presents the methodology: system architecture, data, the semantic-analysis algorithm, prompt design, and evaluation methodology. Chapter 4 presents the experimental results and discussion, in nine sections — from the accuracy of each module, to the central result on the contribution of semantic JSON, to verification of the evaluation method's reliability, and finally a supplementary experiment and discussion that clarifies the true mechanism behind JSON's contribution. Chapter 5 summarizes the contributions, answers the research questions, discusses limitations, and proposes directions for future work.

---

# CHAPTER 2. LITERATURE REVIEW AND RELATED WORK

## 2.1. Lane Detection

Ultra-Fast-Lane-Detection-v2 (UFLD-v2) [1] is a high-speed lane-detection architecture that formulates lane detection as row/column-grid classification (hybrid anchor-driven ordinal classification) rather than direct coordinate regression or semantic segmentation as in earlier methods. This architecture reaches over 300 frames per second in its lightweight version while maintaining competitive accuracy — F1 = 76.0% on the CULane test set with a ResNet-34 backbone, exactly the pretrained variant used in this thesis (`culane_res34.pth`). CULane [6] is the standard benchmark for this task (88.9K training images, 9.7K validation images, 34.7K test images), consisting mainly of diverse urban road scenarios: intersections, high traffic density, and varying lighting conditions.

Two recent survey papers have systematized this field: [7] surveys the network architectures and optimization objectives of deep-learning-based lane-marking detection methods; [8] is a systematic literature review of 102 works published between 2018 and 2021, showing an industry-wide shift from traditional geometric models to deep learning.

It should be noted that the F1 = 76.0% figure above is a pixel-level detection metric (point-wise localization via IoU), fundamentally different from the metrics used in Section 4.1 of this thesis — the Accuracy and MAE of the inferred lane count, a higher-level semantic quantity computed from UFLD-v2's output through a post-processing layer built specifically for this thesis. These two kinds of metrics cannot be compared directly; the key point this thesis wants to make clear is that even when the detection layer achieves a competitive F1 on the original benchmark, the semantic-interpretation layer downstream can still contain serious errors, independent of the quality of the detector itself (Sections 4.1, 1.5).

## 2.2. Traffic Sign Detection

YOLOv8 (Ultralytics) is a single-stage object-detection architecture that balances speed and accuracy well, making it suitable for real-time applications. TT100K (Tsinghua-Tencent 100K) [9] is a large-scale benchmark for traffic-sign detection and classification in China, comprising roughly 100,000 images and 30,000 labeled sign instances, with a detailed sign-encoding scheme by category: prohibition signs ("p"), mandatory signs ("i"), warning signs ("w"), and speed-limit signs ("pl"/"il").

## 2.3. Multimodal Large Language Models for Driving Decision Support

**Precursors before the LLM era.** Hong et al. [10] laid the groundwork for encoding high-level traffic-scene semantics into a structured representation (a spatial grid) so that a deep model could reason about driving behavior. However, this work used a purely convolutional network and could not generate natural-language explanations.

**Large-scale end-to-end driving VLM/LLM systems.** DriveGPT4 [2] generates natural-language explanations alongside end-to-end control-signal predictions; DriveLM [3] frames driving as Graph Visual Question Answering; LMDrive [4] performs closed-loop, end-to-end driving with an LLM. What these systems have in common is that they require training or fine-tuning on large-scale driving datasets (nuScenes, CARLA, etc.), together with substantial computational and data infrastructure.

**Works closest to this thesis.** Following the same direction of combining specialized deep learning with a multimodal LLM for traffic semantics, SafeRoute [11] and its precursor "Advancing Autonomous Vehicle Intelligence" [12] — by the same group of authors — build a unified pipeline: three sign-detection architectures (ResNet-50 at 99.8%, YOLOv8 at 98.0%, RT-DETR at 96.6% accuracy) combined with an MLLM fine-tuned via instruction-tuning for lane understanding, using a Multimodal Adapter mechanism to fuse CNN features with EVA-CLIP embeddings; this work reports a Frame Overall Accuracy of 53.87% and a Question Overall Accuracy of 82.83% for the lane-understanding question-answering component. Similarly, DSC-LLM [13] combines behavioral features (modeled via LSTM/transformer) with traffic context extracted from images to predict trajectories along with LLM-explained risk reasoning.

The difference between these works and this thesis lies in two aspects. First, SafeRoute and Advancing-AV-Intelligence fuse information at the embedding layer (a Multimodal Adapter, which requires fine-tuning the MLLM), whereas this thesis fuses information at the prompt/text layer — semantic JSON is embedded directly into the prompt of a general-purpose, non-fine-tuned VLM — a simpler approach to implement, at the cost of depending more heavily on prompt-design quality. Second, and more importantly, none of the works above perform an ablation step that isolates the contribution of structured information from that of the raw image — this is precisely RQ3 and Section 4.5, the thesis's central research question — nor do they verify the reliability of their evaluation method against human judgment as in Section 4.6.

Overall, this thesis's approach differs in kind from both groups of related work: rather than training or fine-tuning a specialized model at the reasoning layer, this thesis leverages a general-purpose, already-trained, non-fine-tuned VLM (accessed via NVIDIA NIM's OpenAI-compatible API), combined with a semantic pre-processing layer built from specialized perception modules — in which UFLD-v2 is used as-is in pretrained form, while YOLOv8n for the sign task is self fine-tuned on TT100K (Section 3.2), a lightweight training step, very different in cost from re-training a VLM/LLM or collecting large-scale driving data as in the end-to-end systems above. As a result, an explainable decision-support system is built without requiring large-scale driving training data or the computational resources to retrain the VLM/LLM reasoning layer. This trade-off delivers simplicity, low cost, and rapid deployability, suited to the scale of an independent research thesis.

## 2.4. Evaluating Natural-Language Output Quality with LLM-as-a-Judge

The need for standardized evaluation of LLM and AI-agent systems is growing as fast as the field itself. A recent survey [14] systematizes the benchmarks and evaluation frameworks for LLMs/agents published between 2019 and 2025, showing that this remains a field still taking shape, without a unified methodology — further reinforcing the reason this thesis independently verifies the reliability of its evaluation method rather than applying one "as-is" without verification.

Evaluating the quality of a natural-language driving recommendation is a problem that is hard to quantify with traditional hard metrics (accuracy, F1, etc.) because there is no single "correct answer." The LLM-as-a-judge method — using a strong LLM as an automated "judge" that scores against a given rubric — has been widely applied in recent LLM evaluation benchmarks, most notably the MT-Bench and Chatbot Arena methodology [5], as well as AlpacaEval. On MT-Bench, GPT-4 acting as a judge reached 85% agreement with human experts (on non-tied comparison pairs), a level close to human-to-human agreement (81%) — showing that LLM-as-a-judge can approach human-level reliability under the right conditions, although inherent biases still exist (a bias toward longer answers, a bias toward certain writing styles, and self-preference bias among models of the same family) that must be verified separately for each specific application. This is exactly the approach applied in this thesis (Sections 3.7 and 4.6), at a smaller verification scale (N=20 versus thousands of pairs in the original MT-Bench) due to the resource constraints of an individual thesis.

Using a small-scale human-verification sample rather than manually scoring the entire dataset has its own methodological grounding in recent studies. Kim [15] proposes a two-stage sampling framework — the LLM scores the entire dataset, and humans only score a purposively selected subsample where the LLM's predictions are least reliable — and emphasizes that the literature currently lacks formal guidance on how much human oversight is sufficient when verifying a benchmark. Saha et al. [16] propose variance-adaptive query allocation instead of uniform allocation, to reduce estimation error within a fixed computational budget. Pan et al. [17] interview eight experts and emphasize the need to support the construction of evaluation criteria that match real users' expectations — informing the design of this thesis's six-criterion rubric (Section 3.7). This thesis currently uses N=20 randomly selected samples and does not yet apply variance-adaptive sampling; this is a feasible avenue for improvement noted in Section 5.4.

## 2.5. Research Gap

Four related research directions leave different gaps that this thesis addresses:

1. Traditional ADAS (based on UFLD-v2, YOLOv8, etc.) stops at the perception layer — coordinates, bounding boxes, class IDs — with no natural-language reasoning layer that a driver can interpret.
2. Large-scale end-to-end driving VLM systems (DriveGPT4, DriveLM, LMDrive) solve the interpretability problem, but require training or fine-tuning on large-scale driving data — a high cost and barrier to entry.
3. Recent hybrid deep-learning + MLLM systems (SafeRoute, Advancing-AV-Intelligence, DSC-LLM — Section 2.3) are the closest in spirit to this thesis, combining specialized deep learning with a multimodal LLM, but differ in two specific ways: they fuse information at the embedding layer rather than the prompt/text layer, and they lack a quantitative ablation step isolating the contribution of structured information from that of the raw image, nor do they verify their evaluation method's reliability against human judgment.
4. A general-purpose VLM used as-is (without semantic pre-processing) is not specifically designed for traffic semantics; as this thesis shows quantitatively in Section 4.5, the absence of a structured semantic layer clearly degrades recommendation quality compared with having one.

This thesis is positioned closest to group (3) in terms of goals, but chooses an implementation direction closer to groups (1) and (4) at the reasoning layer (no VLM fine-tuning). Specifically, the thesis combines: a verified, specialized perception layer — UFLD-v2 used as-is in pretrained form, and YOLOv8n for signs self fine-tuned on TT100K (Section 3.2), a lightweight training step compared with training a VLM/LLM; a self-designed structured semantic-conversion layer, the main technical contribution; a general-purpose, non-fine-tuned VLM reasoning layer; and a rigorous quantitative evaluation methodology, with the reliability of the evaluation tool itself verified against human judgment and multiple judges — a gap that neither group (2) nor group (3) has fully filled in the works surveyed.

---

# CHAPTER 3. METHODOLOGY

## 3.1. Overall System Architecture

The thesis's pipeline consists of four sequential processing layers, illustrated in Figure 3.1.

**Figure 3.1.** Overall architecture of the four-layer pipeline.

```
Dashcam image
    │
    ▼
[1. PERCEPTION]  UFLD-v2 (lanes) + YOLOv8/TT100K (signs)
    │
    ▼
[2. SEMANTIC ANALYSIS]  Convert raw coordinates → semantics (lane count, ego lane,
                          vehicle offset, adjacent lanes, road shape) → full JSON + brief JSON
    │
    ▼
[3. LLM REASONING]  A VLM (via the NVIDIA NIM API) generates driving recommendations
                      in natural language - 3 independent input modes: image only /
                      JSON only / image + JSON
    │
    ▼
[4. EVALUATION]  LLM-as-a-judge (6 criteria) + reliability verification via
                   humans and multiple judges
```

## 3.2. Data

**Primary dataset (CULane).** 200 images were randomly sampled from the CULane dataset (1640×590 resolution), representing diverse urban scenarios: straight roads, gentle curves, intersections, and varying traffic densities. Ground truth was manually labeled for all 200/200 images, including: the true number of same-direction lanes, road type (straight/gentle curve/sharp curve, with direction), the number of falsely detected lanes, the number of opposite-direction lanes mistakenly merged in, ego-lane determination accuracy, the true number of signs, and the number of correct/incorrect detections. All results in Chapter 4 — both ground-truth-based results and LLM-as-a-judge-based results — use the full N=200.

**Independent verification dataset (real-life).** 200 frames were extracted from real dashcam video (1280×720 resolution) and manually labeled using the same schema as above. The purpose of this dataset is to verify the system's ability to generalize to data that is entirely independent of the lane-detection model's training data (the data-leakage risk is discussed in Section 4.7).

**Lane-detection model.** UFLD-v2, ResNet-34 backbone, pretrained on CULane (`culane_res34.pth`).

**Sign-detection model.** YOLOv8n (the smallest variant in the YOLOv8 family, roughly 3.2 million parameters), self fine-tuned on a 50-class subset of TT100K, initialized from the original YOLOv8n checkpoint (pretrained on COCO). Training configuration:

- Input image resolution: 640×640; automatic batch size (`batch=-1`).
- SGD optimizer, initial learning rate `lr0=0.01`, momentum `0.937`, weight decay `0.0005`, 3-epoch warm-up.
- Up to 100 epochs, early stopping `patience=30` (stop if no improvement for 30 consecutive epochs).

Due to the time-limited working sessions of the training environment (Kaggle), the process was interrupted midway at epoch 82 and resumed from the latest checkpoint until completion. This is a standard, lightweight fine-tuning step compared with training or fine-tuning a VLM/LLM on large-scale driving data as in the end-to-end systems surveyed in Section 2.3 (DriveGPT4, DriveLM, LMDrive, SafeRoute) — and does not contradict the thesis's training-free orientation, which applies only to the VLM reasoning layer (Section 3.6), not to the perception layer.

## 3.3. Semantic Lane Analysis

This is a processing layer designed and implemented by the author, converting the raw list of pixel points for each lane boundary (returned by UFLD-v2) into four decision-level semantics: ego lane, vehicle offset, road shape, and adjacent lanes — constituting Contribution 1 of the thesis (Section 1.5).

### Preprocessing: sorting lane boundaries by actual position

UFLD-v2 does not guarantee returning lane boundaries in correct left-to-right order on the image. Therefore, before determining the ego lane, all boundaries are re-sorted by their x-coordinate at a reference row near the bottom of the image:

$$y_{ref} = 0.95 \times \text{image\_height}$$

The x-coordinate at $y_{ref}$ is interpolated by averaging the points within $|y - y_{ref}| \le 30$ pixels; if no point is close enough (the boundary is occluded or ends early), the coordinate is extrapolated by fitting a degree-1 line through all available points of that boundary. This replaces an earlier version that temporarily assigned $+\infty$ when no nearby point existed, which pushed the boundary erroneously to the far right and corrupted the left/right adjacent-lane classification.

### Determining the ego lane

With $n$ boundaries sorted left to right and $x_{veh} = \text{image\_width}/2$ (assuming the camera is mounted at the center of the vehicle), the algorithm computes a score for each pair of adjacent boundaries $(i, i+1)$:

$$\text{score}_i = \left| \frac{x_i + x_{i+1}}{2} - x_{veh} \right| \times p_{between} \times \left(1 + 0.2 \times \frac{|w_i - w_{exp}|}{w_{exp}}\right)$$

where $w_i = x_{i+1} - x_i$ is the width of the candidate lane pair, $w_{exp} = 0.15 \times \text{image\_width}$ is an assumed "typical" lane width, and

$$
p_{between} = \begin{cases} 0.5 & \text{if the vehicle lies between the two boundaries} \\ 1 & \text{otherwise} \end{cases}
$$

The pair with the smallest $\text{score}_i$ is chosen as the ego lane — chosen dynamically per image rather than assuming a fixed position, allowing for asymmetric cases (curved roads, or a missing boundary on one side).

Confidence is derived directly from the distance $d$ between the ego-lane center and the image center ($w$ = image_width):

| Condition | $d < 0.1w$ | $d < 0.25w$ | $d < 0.4w$ | otherwise |
|---|---|---|---|---|
| Confidence | 0.95 | 0.8 | 0.6 | 0.4 |

The special case of detecting only one boundary ($n=1$) is handled separately: that boundary is assigned as the right edge of the ego lane, with a fixed confidence of 0.5.

### Vehicle offset

With the ego-lane center $x_{lane} = (x_{left} + x_{right})/2$ determined above:

$$\Delta x = x_{veh} - x_{lane} \quad \text{(pixels)}, \qquad \Delta x_{\%} = \frac{\Delta x}{w} \times 100$$

where $w$ is the ego-lane width. The offset is labeled "centered" if $|\Delta x| < 10$ pixels, "right offset" if $\Delta x > 0$, and "left offset" otherwise.

### Curvature estimation

For each boundary with at least 4 valid points, the $y$-coordinate is normalized as $y_{norm} = (y - y_{min})/(y_{max} - y_{min})$, and two polynomials are fitted through the points $(y_{norm}, x)$: degree 1 (with error $\text{MSE}_1$) and degree 2 ($\text{MSE}_2$). Two curvature signals are then derived:

$$\text{drift\_ratio} = \frac{\sqrt{\text{MSE}_1}}{\text{image\_width}}, \qquad \text{fit\_improvement} = \max\!\left(0,\; \frac{\text{MSE}_1 - \text{MSE}_2}{\text{MSE}_1}\right)$$

`drift_ratio` measures the root-mean-square deviation from an ideal straight line, normalized by image width; `fit_improvement` measures the relative improvement gained from allowing a curved fit instead of forcing a straight one, and is trusted only when $\text{MSE}_1 > 4$ and the boundary has ≥10 points — otherwise, the difference $\text{MSE}_1-\text{MSE}_2$ is treated as measurement noise or overfitting and set to 0. This signal is needed for very gentle curves, where the absolute deviation is still too small for `drift_ratio` to detect.

The perspective vanishing point of each boundary is extrapolated using the degree-1 fit, at a shared "horizon" reference used for every boundary in the image:

$$y_{horizon} = 0.3 \times \text{image\_height}$$

instead of extrapolating separately at each boundary's own $y_{norm}=0$ as in the original design — the old approach could give two parallel straight boundaries two different vanishing points (because they were evaluated at two different image depths), artificially inflating the apparent spread of vanishing points even when the road is genuinely straight. Anchoring all boundaries to the same horizon row corrects this bias.

Four image-level aggregate signals — $\overline{\text{drift}}$, $\overline{\text{fit\_improvement}}$, the proportion of boundaries classified as "straight" ($\text{MSE}_1 < 1000$), and curve direction (comparing the average x-coordinate near the bottom of the image with that near the middle, using a $\text{shift\_ratio}$ threshold of $0.08$) — are used to classify the overall road shape.

### Calibrating the curvature-classification thresholds

Three thresholds were calibrated from statistics actually measured on CULane images, not set arbitrarily: $\overline{\text{drift}}_{straight}=0.02$ (above the observed p95 percentile for straight-road images, ≈0.014); $\overline{\text{drift}}_{sharp}=0.06$ (below the measured value of a visually confirmed sharp-curve image, 0.0994); and $\text{fit\_improvement}=0.3$, used to upgrade a road from "straight" to "gentle curve" when $\overline{\text{drift}}$ is too small to detect on its own but the evidence of curvature is still clear. The final classification rule:

$$
\text{classification} = \begin{cases}
\texttt{straight} & \overline{\text{drift}} < 0.02 \text{ and } \overline{\text{fit\_improvement}} < 0.3 \text{ and the proportion of straight boundaries} > 50\% \\
\texttt{sharp} & \overline{\text{drift}} \ge 0.06 \\
\texttt{gentle} & \text{otherwise}
\end{cases}
$$

An alternative geometric signal — the absolute spread of vanishing points in pixels ($\text{vp\_spread}$) — was considered but excluded from the classification rule: it is not normalized by image size, so it is unstable across images with different camera characteristics, and is still stored in the JSON for reference but does not take part in classification.

### Lane count

Equal to the number of detected boundaries minus 1, following the CULane convention — the formula that once contained the off-by-one unit-conversion bug, discussed quantitatively in Section 4.1.

## 3.4. Semantic JSON Structure Sent to the LLM

**Full JSON (`<name>.json`).** This is the direct output of the Semantic Analysis layer (Section 3.3), and is also the JSON embedded verbatim in the prompt in the `json_only`/`image_json` modes. Its structure comprises four groups of fields:

1. **Metadata**: `scene_id` (a processing-session identifier), `timestamp`, `image_size` (`width`, `height`).
2. **`road`** (road-level aggregates): `road_type`, `road_environment` (a heuristic estimate of the road-environment type via a simple if-else rule — low confidence, and therefore excluded from the brief version for this reason), `curvature_magnitude`/`curvature_direction`/`curvature_confidence` (results from Section 3.3), and `geometry` (`spread_pixels`, `coverage_ratio`, `convergence_ratio`, `lane_count`, `geometry_type`).
3. **`lane`** (lane-level detail, the main output of Section 3.3): `sorted_lanes` (the left-to-right sorted list of boundaries); `ego_lane` (boundaries, lane center, width, confidence); `lane_classification` (the count and list of left/right adjacent lanes); `vehicle_offset` (the full set of fields described in Section 3.3); `curvature` (the curvature-classification result); `lane_semantics` (per-lane semantics: type, whether it is the ego lane, whether it is drivable, relative position); and image dimensions.
4. **`traffic_signs`**: the list of detected signs with class labels and coordinates, along with the count.

**Brief JSON (`<name>_brief.json`).** A separate, much leaner schema containing only five decision-level fields: `lane_count`, `ego_lane` (position as "X/Y" plus confidence), `vehicle_offset` (direction, magnitude, percentage offset), `neighbor_lanes` (left/right lane counts), `road_shape` (type, magnitude, curve direction) — with no metadata and no `traffic_signs`. This design gives the LLM a minimal data snapshot, removing fields whose evidence is not reliable enough from the LLM's context. This schema serves its actual purpose in a different experiment of the thesis: as the target output format for the VLM self-perception verification experiment (Section 4.8), where the VLM is asked to extract these exact five fields directly from the image, with no hints given, and the result is then compared against the value computed by the UFLD-v2 pipeline. In that role, `_brief.json` only serves as the structural template for the output being compared, not as input given to the VLM, so it raises no fairness or leakage issue.

## 3.5. Prompt Design for the Reasoning Layer

The prompt was designed through many rounds of experimentation, focused on four lane-level semantics — lane count, ego lane, vehicle offset, adjacent lanes — together with anti-hallucination rules (do not infer information without evidence; do not treat a lack of detection as evidence that an object does not exist) and a required fixed three-part output structure: Situation, Recommendation, Safety Notes, to ensure consistency across generations. During development, two issues were identified and fixed: the model repeating the same answer indefinitely on low-information images, fixed with a frequency-penalty parameter; and the model giving overly short answers that did not follow the required structure, fixed by requiring specific supporting evidence for each part.

## 3.6. Model Selection for the Reasoning Layer

Due to cost and reproducibility constraints, the scope of model selection was limited to VLMs freely available via the NVIDIA NIM API (a unified OpenAI-compatible format). Three specific models were selected for comparison based on three criteria:

1. Multimodal support (accepting image and text simultaneously) — a mandatory pipeline requirement, excluding text-only models.
2. Free availability through the same unified API, guaranteeing zero deployment cost and experimental consistency, in line with the thesis's training-free/low-cost orientation (Section 1.5).
3. Spanning multiple parameter-scale tiers within the range of available models, allowing an observation of whether model scale correlates with reliability and output quality, directly serving RQ4.

Three models satisfy all three criteria simultaneously: `nemotron-nano-vl-8b` (8B parameters), `nemotron-nano-12b-v2-vl` (12B parameters), and `ising-calibration-1.5-31b` (31B parameters).

The criteria for comparing the three models, in strict priority order, are: reliability — the success rate over the full real batch, assessed first and independently of content quality, because a model that does not respond reliably cannot be deployed for a real-time decision-support system, no matter how good its answers are when it does respond successfully; compliance with the required output structure; and content quality, scored via LLM-as-a-judge, applied only to models that pass the minimum threshold on the first criterion.

**Experimental sequence.** Selecting the LLM in this section (RQ4) and the central result on the contribution of semantic JSON in Section 4.5 (RQ3) are two separate, sequentially run experiments, with no circular dependency between them:

1. *Stage 1 — model selection (Section 4.4)*: all three candidate models were run under a single fixed input mode — `image+json`, the mode that provides the most complete information, giving each model its best chance to perform — and were scored by exactly one judge (Gemini) to determine the most reliable and highest-quality model. Result: `ising-calibration-31b` was selected.
2. *Stage 2 — input-mode comparison (Section 4.5)*: the selected model was held fixed, and the only variable changed was the input mode (`image_only`/`json_only`/`image+json`), scored by all three independent judges to answer RQ3.

In other words, the actual processing sequence is: image → detection/semantic analysis → run three LLM models in `image+json` mode, Gemini scores them, the winning model is selected → fix the winning model, re-run it under all three input modes, all three judges score the outputs, conclude RQ3. The scoring pass used to select the model and the scoring pass used to compare input modes are two separate rounds serving two different research questions, not a single scoring round reused for both purposes.

**Why Stage 1 uses only one input mode and one judge.** This is a deliberate experimental-design choice, based on three grounds. First, RQ4 and RQ3 are orthogonal questions: running the full matrix of three models × three modes × three judges would cost many times more in API time and expense without directly serving RQ4, which only needs to identify which model is most reliable and highest quality, not how that model interacts with each specific input mode; fixing the input mode at `image+json` when comparing models is the standard way to ensure each model is evaluated under its most favorable conditions, separating "a weak model" from "a model starved of information." Second, this is a constraint arising from the actual development timeline: at the time Stage 1 was carried out, GPT-5 Mini and DeepSeek had not yet been integrated as judges — Gemini was the only judge that existed in the system at that stage — and adding multi-judge cross-checking (Section 4.6) is a methodological tightening step added later, specifically for the central result in Section 4.5, where the conclusion is genuinely sensitive to judge choice (the ranking of `json_only` versus `image+json` flips depending on the judge, Table 4.6). Third, the magnitude of the gap between models in RQ4 does not require multi-judge verification to be credible: `nemotron-nano-12b-v2-vl` failed as many as 82.9% of requests, and `ising-calibration-31b` outperformed `nemotron-nano-8b` with a Cohen's d of roughly 1.04 (Table 4.4) — a very large effect, unlikely to be reversed simply by switching judges; in addition, Section 4.6 (carried out afterward) confirms that Gemini is the judge with the highest correlation with human raters among the three tried, further reinforcing — although this evidence was not yet available at the time Stage 1 was carried out — that using Gemini as the sole judge for this decision was reasonable.

## 3.7. Evaluation Methodology

**Evaluating the lane- and sign-understanding modules.** Direct comparison against hand-labeled ground truth, using standard metrics: Accuracy (exact-match rate), MAE (mean absolute error), Precision, and Recall.

**Evaluating driving-recommendation quality.** LLM-as-a-judge is used with a six-criterion rubric, scored on a 1–5 scale: `situation_understanding`, `road_understanding`, `lane_ego_position`, `traffic_sign_rule`, `driving_recommendation`, `safety_considerations`. Each image is evaluated with a single API call that bundles all three experiments to be compared within the same context, both to save cost and to ensure evaluation consistency.

**Verifying judge reliability.** This consists of two steps: comparing Gemini's scores against human hand-scoring on a random sample of N=20; and cross-checking against two other independent judges (GPT-5 Mini, DeepSeek) on the same dataset, using the exact same rubric verbatim to ensure a fair comparison. The benchmark for judging "which judge is more accurate" is agreement with humans, not agreement among the judges themselves, since two AI judges may agree with each other while still sharing the same bias relative to humans.

---

# CHAPTER 4. RESULTS AND DISCUSSION

## 4.1. Lane-Understanding Module Accuracy (CULane)

In an early stage, 26 images belonging to hard-to-determine scenarios — plazas/squares without lane markings, parking garages, lane-merging situations, complex intersections — were temporarily assigned `lane_count=0` to exclude them from the statistics. A later review found that this practice concealed a bias: for most of these images, the model also predicted 0 because it saw no markings, so they were inadvertently counted as "exact matches," even though the model had actually failed completely rather than correctly guessing "0 lanes." All 200 images were subsequently relabeled with an estimated true lane count — based on road width, other vehicle positions, physical dividers — together with a difficulty-reason label (`hard_reason`), allowing the subset of images with clear lane markings ("Normal") to be separated from those without.

**Table 4.1.** Lane-understanding module accuracy before and after fixing the off-by-one bug (N=200).

| Metric | Before fixing the off-by-one bug | After fixing the bug (N=200) |
|---|---|---|
| Lane count – Accuracy (exact match) | 11.1% | **69.0%** |
| Lane count – MAE | 1.056 | **0.475** |
| Lane count – Precision | – | **96.6%** |
| Road type – Accuracy (exact match) | Not measurable (always "straight") | **76.5%** |
| Road type – Accuracy (matching straight/gentle/sharp group) | – | **78.5%** |
| Road type – Recall for gentle curves | 0% | **57.1%** (4/7) |
| Ego lane – Accuracy | – | **86.0%** |
| Falsely detected lanes | – | **0.8%** |

The figures in Table 4.1 are computed directly by comparing `image_labels.xlsx` against the pipeline's output on N=200 images:

- Lane count Accuracy = the proportion of images where the predicted lane count exactly matches the true count = 138/200 = 69.0%.
- Lane count MAE = the mean absolute difference between the true and predicted lane counts = 95/200 = 0.475.
- Lane count Precision = the total true lane count divided by the total true lane count plus falsely detected lanes plus opposite-direction lanes mistakenly merged in = 477/(477+5+12) = 96.6%.
- Road type Accuracy (exact match) = 153/200 = 76.5%; matching by straight/gentle/sharp group = 157/200 = 78.5%.
- Ego lane Accuracy = the proportion of images where the ego lane is correctly identified = 172/200 = 86.0%.

The most notable result at this stage is not the bug fix itself, but its methodological implications for the semantic-interpretation layer. The original system contained an off-by-one unit-conversion bug in the lane-count formula — counting boundaries instead of the actual number of lanes — causing most images to report one lane too many. Because this value was embedded directly into the JSON context sent to the LLM, this bug was the direct cause of the lane-count "hallucination" phenomenon observed in the LLM's recommendations during the early stage of the research. After the fix, Accuracy rose from 11.1% to 69.0%, measured on the exact same detection pass and differing only in the downstream processing formula — showing that this improvement comes from the semantic-interpretation layer, independent of the quality of the detection model itself. In other words, this is not an algorithmic contribution, but experimental evidence that the semantic-interpretation layer, if not built and verified carefully, can become the decisive bottleneck for the quality of the entire system, even when the upstream detection layer is already of good quality.

After relabeling the 26 hard images above, separating the results by `hard_reason` shows that the model's performance depends very strongly on the presence of lane markings.

**Table 4.2.** Lane-understanding module performance by presence/absence of clear lane markings.

| Group | N | Lane count Accuracy | Lane count MAE | Precision | Ego lane Accuracy |
|---|---|---|---|---|---|
| Clear markings ("Normal") | 176 | **77.3%** | 0.273 | 96.2% | **96.6%** |
| No clear markings (plazas/parking garages/merging/complex intersections) | 24 | **8.3%** | 1.958 | 100.0% | **8.3%** |

The raw figures behind Table 4.2: the Normal group had 136/176 exact-match images, a total absolute error of 48 (MAE = 48/176 = 0.273), total true/false/opposite-direction lane counts of 427/5/12 respectively (Precision = 427/444 = 96.2%), and 170/176 images with a correctly identified ego lane (96.6%). The Hard group had 2/24 exact-match images, a total absolute error of 47 (MAE = 47/24 = 1.958), total true/false/opposite-direction lane counts of 50/0/0 respectively (Precision = 50/50 = 100%), and 2/24 images with a correctly identified ego lane (8.3%).

Notably, Precision still reaches 100% even on the hard group, despite an Accuracy of only 8.3%. The reason lies in the formula itself: Precision measures the proportion of what the model *dares to assert* that is correct, not how complete its output is. In 19/24 images in this group, the pipeline returned `pred_lane_count = 0` — detecting nothing at all — so there was no lane left to count as "wrong" or "fabricated"; Σfalse and Σopposite are therefore both zero, and Precision = 50/(50+0+0) = 100% almost by necessity. This is most visible for the `no_markings` and `merging` difficulty reasons, where the average predicted lane count is 0.00 while the average true lane count is around 1.7–2.5: the model does not "fabricate" fake lanes — it simply stays silent when markings are missing. This is an inherent limitation of a detector based on lane markings — UFLD-v2 was trained on CULane, which mostly consists of images with clear markings — not a logic error in the downstream semantic-processing layer, and is discussed further in Section 5.3.

**Comparison with related work (hybrid deep learning + MLLM).** Work [12] (Section 2.3) reports a Frame Overall Accuracy of 53.87% and a Question Overall Accuracy of 82.83% for question-answering-style lane understanding with an MLLM. This thesis's results — 69.0% overall, 77.3% on images with clear markings — fall between these two figures. This is reasonable, since the two studies define "accuracy" differently (Frame Overall Accuracy is measured across the whole frame, including adverse weather and lighting conditions, while Question Overall Accuracy is measured per specific VQA question), so they cannot be treated as a direct one-to-one comparison; nevertheless, the accuracy achieved falls within a reasonable range relative to the general standard of the hybrid deep-learning + MLLM research direction for lane semantics.

## 4.2. Independent Verification on Real-Life Data

**Table 4.3.** Comparison of the lane- and sign-understanding modules between CULane and independent real-life data (N=200 for each set).

| Metric | CULane | Independent real-life |
|---|---|---|
| Lane count – Accuracy | 69.0% | 50.5% |
| Lane count – MAE | 0.475 | 0.715 |
| Lane count – Precision | 96.6% | **99.4%** |
| Road type – Accuracy | 76.5% | 53.0% |
| Ego lane – Accuracy | 86.0% | **86.5%** |
| Signs – Precision | Not measurable (data too sparse) | **60.9%** |
| Signs – Recall | Not measurable (data too sparse) | **60.9%** |

Lane-count Precision and ego-lane Accuracy hold steady or even improve on entirely independent data — evidence that the core algorithm (ego-lane pairing, the lane-count formula) generalizes well and is not overfit to CULane's specific characteristics. In contrast, the exact-match rate drops noticeably, because the model tends to under-detect same-direction lanes under camera and lighting conditions different from CULane's, rather than fabricating fake lanes — Precision remains very high. This is also the first time Precision/Recall for the sign module could be measured, which was not possible on CULane due to the sparsity of sign data (Section 4.3).

## 4.3. Traffic Sign Module on CULane

Using the YOLOv8n model self fine-tuned on TT100K (Section 3.2), an important finding is that the CULane dataset has a very low density of signs and traffic lights: only 6% of CULane images (12/200) have any detection at the standard 0.5 threshold, and 20% of images have no detection at all even after lowering the threshold to 0.01. This is a limitation of the benchmark data — CULane was originally designed for the lane-detection task — not a limitation of the model, which is confirmed by markedly better results on the self-collected real-life dashcam data (Section 4.2, 60.9% Precision/Recall).

**Comparison with related work.** SafeRoute and Advancing-AV-Intelligence [11], [12] report sign-classification accuracy ranging from 96.6% to 99.8% (YOLOv8 at 98.0%) — considerably higher than this thesis's 60.9% Precision/Recall. This gap mainly stems from a difference in task difficulty: the 96.6–99.8% figures are classification accuracy on signs that have already been localized, whereas this thesis's 60.9% Precision/Recall is measured on detection from scratch — requiring both localization and classification across the whole frame with no prior location hint — an inherently harder task.

## 4.4. Comparison of LLM Models for the Reasoning Layer

The entire comparison in this section (Stage 1, Section 3.6) was run under a single fixed input mode, `image+json`, and scored by exactly one judge (Gemini), in order to select the LLM to be held fixed for Stage 2 — the input-mode comparison, Section 4.5 — rather than being part of the three-judge/three-mode experiment answering RQ3.

**Reliability and speed.** `ising-calibration-31b` reached a 200/200 success rate (0% error), with an average time of 3.80 seconds per image. `nemotron-nano-12b-v2-vl` reached only 34/200 (83% of requests received a 500 Internal Server Error from the NVIDIA NIM server side).

`nemotron-nano-12b-v2-vl` was excluded from the quality-comparison round for two independent reasons, not because its answers — when it did respond — were themselves of low quality. First, as noted in Section 3.6, reliability is treated as an exclusionary criterion, assessed before and independently of content quality: a model that responds successfully to only 17.1% of requests cannot be deployed in a real-time decision-support system, regardless of how good the remaining 17% of its answers are. The 500 error originates from the NVIDIA NIM server infrastructure hosting the model, not a direct reflection of the model's own capability, but from a practical deployment standpoint, a model that cannot be accessed reliably is simply not usable, whatever the underlying technical cause. Second, even setting aside this exclusionary criterion, the remaining 34 successful responses do not form a fair comparison sample: this is a subset self-selected by the server's own error mechanism, likely biased toward simpler images or requests that take less processing time, rather than a random sample representative of the full 200 images achieved by the other two models in this comparison. Comparing quality between 34 biased samples and the full 200 samples of the other models would violate the fair-comparison principle set out for the thesis's entire evaluation methodology (Section 3.7).

**Compliance with the output structure.** Over N=200, counting outputs shorter than 80 characters — equivalent to skipping the required three-part structure — shows that `nemotron-nano-8b` had 99/200 (49.5%) truncated outputs, while `ising-calibration-31b` had 0/200 (0%) on this same reference set. Looking at overall output length, `nemotron-nano-8b` generated an average of 95 characters per response (SD = 78), while `ising-calibration-31b` generated an average of 876 characters per response (SD = 198) — more than 9 times longer, enough to fully present all three parts (Situation/Recommendation/Safety Notes) as required by the prompt (Section 3.5), rather than a truncated response that fails to meet the minimum structure.

**Content quality** (versus `nemotron-nano-8b`, N=200, same images, same judge Gemini, same six-criterion rubric). This is the most direct and fair comparison among the three models, since both pass the exclusionary reliability criterion — `nemotron-nano-8b` completed 200/200, and was not excluded for sample-bias reasons the way `nemotron-nano-12b-v2-vl` was. Applying the same statistical method used in Section 4.5 — computing the six-criterion mean score per image first, then running a paired test on 200 per-image score pairs — the results in Table 4.4 show a gap that is not only large but statistically very significant.

**Table 4.4.** Detailed content-quality comparison between `nemotron-nano-8b` and `ising-calibration-31b` (Mean ± SD, N=200, image-paired Wilcoxon signed-rank test).

| Criterion | nemotron-nano-8b | ising-calibration-31b | Wilcoxon p |
|---|---|---|---|
| situation_understanding | 1.97 ± 1.15 | 3.48 ± 1.24 | p < 0.001 |
| road_understanding | 2.08 ± 1.27 | 3.77 ± 0.92 | p < 0.001 |
| lane_ego_position | 2.03 ± 1.13 | 3.77 ± 1.24 | p < 0.001 |
| traffic_sign_rule | 2.17 ± 1.42 | 3.18 ± 1.32 | p < 0.001 |
| driving_recommendation | 3.98 ± 1.13 | 4.16 ± 1.20 | p = 0.066 |
| safety_considerations | 1.69 ± 0.98 | 3.74 ± 1.19 | p < 0.001 |
| **Mean of 6 criteria (per image)** | **2.32 ± 0.99** | **3.68 ± 0.96** | paired t: t = −14.68, p < 0.001; Cohen's d = −1.04 (very large) |

`ising-calibration-31b` outperforms with statistical significance on five of six criteria (p < 0.001), with a very large overall effect size (Cohen's d ≈ 1.04, i.e., the mean difference exceeds one standard deviation). For the `driving_recommendation` criterion alone, the difference between 3.98 and 4.16 is not statistically significant (p = 0.066) — the two models are rated equivalently on this specific criterion, so `ising-calibration-31b` does not win outright on all six criteria. This does not weaken the model-selection decision: the remaining five of six criteria, together with the very large gap in reliability and in output length/structural completeness (876 versus 95 characters), already constitute a sufficiently strong and comprehensive basis.

Combining all three criteria in the priority order set out in Section 3.6 — reliability, structural compliance, content quality — `ising-calibration-31b` is the best choice among the three models, and was selected as the primary model for all remaining experiments in the thesis.

## 4.5. Main Result: The Contribution of Semantic JSON

This is the central result answering RQ3, measured on the primary model (`ising-calibration-31b`), across three input modes, scored by three independent judges (Gemini, GPT-5 Mini, DeepSeek) using the exact same rubric, over the full N=200 images.

For each image, a mode's aggregate score is computed as the arithmetic mean of its six per-criterion scores on that image (1–5 scale); this yields, for each judge, three sequences of 200 image-paired scores — one sequence per mode. The sample mean score for a mode, reported in Table 4.5, is the arithmetic mean of that sequence of 200 per-image scores:

$$\text{Score(mode)} = \frac{1}{200} \sum_{j=1}^{200} \left[ \frac{1}{6} \sum_{i=1}^{6} \text{score}(\text{image } j, \text{criterion } i, \text{mode}) \right]$$

Computing the score per image first, and only then averaging, ensures each image contributes exactly once to the final result and enables paired statistical testing between modes on the same image, rather than merely comparing two isolated mean values.

**Table 4.5.** Driving-recommendation quality scores (Mean ± SD over 200 images) across three input modes, rated by three independent judges (1–5 scale).

| Judge | image_only | json_only | image+json | Ranking |
|---|---|---|---|---|
| Gemini | 3.32 ± 0.95 | **4.53 ± 0.77** | 3.97 ± 0.95 | json > image+json > image |
| GPT-5 Mini | 3.13 ± 0.75 | 3.55 ± 1.14 | **3.96 ± 0.86** | image+json > json > image |
| DeepSeek | 3.11 ± 0.96 | **3.41 ± 1.17** | 3.40 ± 1.02 | json ≈ image+json > image |

These mean scores are nearly unchanged from the earlier measurement at N=200 (the difference appears only in the third decimal place), showing that the conclusion is stable and not sensitive to adding or removing a handful of samples. The relatively large standard deviations across all three modes (0.75–1.17 on a 1–5 scale) reflect the natural diversity among images: easy images — straight roads, few obstacles — score high in every mode, while hard images — intersections, missing markings — score low in every mode. The gap between modes therefore needs to be statistically tested rather than judged from two raw numbers alone, presented in Table 4.6.

**Table 4.6.** Statistical significance of pairwise comparisons across the three input modes, per judge (N=200, image-paired data; paired t-test and Wilcoxon signed-rank test; d is Cohen's d for the paired difference).

| Judge | Comparison | Paired t (df=199) | p (t-test) | Wilcoxon p | Cohen's d |
|---|---|---|---|---|---|
| Gemini | image_only vs json_only | −13.62 | p < 0.001 | p < 0.001 | −0.96 (large) |
| Gemini | image_only vs image+json | −8.37 | p < 0.001 | p < 0.001 | −0.59 (medium–large) |
| Gemini | json_only vs image+json | 7.28 | p < 0.001 | p < 0.001 | 0.51 (medium) |
| GPT-5 Mini | image_only vs json_only | −4.33 | p < 0.001 | p < 0.001 | −0.31 (small) |
| GPT-5 Mini | image_only vs image+json | −11.16 | p < 0.001 | p < 0.001 | −0.79 (large) |
| GPT-5 Mini | json_only vs image+json | −4.93 | p < 0.001 | p < 0.001 | −0.35 (small) |
| DeepSeek | image_only vs json_only | −2.83 | p = 0.005 | p = 0.003 | −0.20 (small) |
| DeepSeek | image_only vs image+json | −3.19 | p = 0.002 | p < 0.001 | −0.23 (small) |
| DeepSeek | json_only vs image+json | 0.09 | p = 0.930 | p = 0.625 | 0.01 (negligible) |

These test results reinforce the conclusion in Table 4.5: across the six comparisons directly involving `image_only` — three judges times two comparison pairs — all are statistically significant at p < 0.01, confirming that `image_only` scoring lower than the other two modes is not due to chance. Effect sizes range from small for DeepSeek (d ≈ 0.20–0.23) to large for Gemini (d ≈ 0.59–0.96), consistent with Gemini also being the judge with the highest agreement with humans (Section 4.6) — suggesting that Gemini's larger score gap is not merely statistical noise but reflects a genuinely clearer signal. The `json_only` versus `image+json` comparison for DeepSeek alone is not statistically significant (p = 0.930, d ≈ 0.01), quantitatively confirming the "json ≈ image+json" observation noted in Table 4.5: these are not two modes whose scores happen to be randomly close, but modes that are genuinely indistinguishable according to this judge.

Table 4.7 illustrates how the mean per-criterion score is computed, using a detailed example from the Gemini judge, together with the standard deviation of each criterion and Wilcoxon test results for the two main comparisons.

**Table 4.7.** Mean scores (Mean ± SD, N=200 per criterion) of the Gemini judge's six evaluation criteria across input modes, with Wilcoxon tests against `image_only`.

| Criterion | image_only | json_only | image+json | Wilcoxon p (image vs json) | Wilcoxon p (image vs image+json) |
|---|---|---|---|---|---|
| situation_understanding | 2.76 ± 1.12 | 4.38 ± 0.95 | 3.51 ± 1.31 | p < 0.001 | p < 0.001 |
| road_understanding | 3.27 ± 1.00 | 4.47 ± 0.87 | 4.04 ± 1.02 | p < 0.001 | p < 0.001 |
| lane_ego_position | 3.27 ± 1.25 | 4.64 ± 0.76 | 4.21 ± 1.17 | p < 0.001 | p < 0.001 |
| traffic_sign_rule | 3.84 ± 1.51 | 4.72 ± 0.75 | 4.24 ± 1.24 | p < 0.001 | p < 0.001 |
| driving_recommendation | 3.50 ± 1.41 | 4.58 ± 0.87 | 3.97 ± 1.38 | p < 0.001 | p < 0.001 |
| safety_considerations | 3.31 ± 1.21 | 4.39 ± 0.95 | 3.85 ± 1.30 | p < 0.001 | p < 0.001 |
| **Mean of 6 criteria** | **3.32 ± 0.95** | **4.53 ± 0.77** | **3.97 ± 0.95** | — | — |

All six criteria show a strongly significant difference (p < 0.001) when comparing `image_only` with either `json_only` or `image+json`; with six simultaneous tests, the corresponding Bonferroni threshold is p < 0.0083, which is still satisfied by all six criteria. The highest standard deviation occurs for `traffic_sign_rule` under `image_only` (± 1.51) — sensible, since this criterion depends heavily on whether the image happens to contain a sign that is visually easy to notice, a factor that varies widely across images; the lowest standard deviation occurs for `lane_ego_position` under `json_only` (± 0.76), consistent with ego-lane-position information being supplied as precise, ready-made figures in the JSON, making it less dependent on visual reasoning ability, which varies more across images.

The most consistent conclusion, agreed upon without exception by all three independent judges, is that the `image_only` mode always scores lowest. After fixing the systemic errors at the perception layer (Section 4.1) and refining the reasoning layer (Section 4.4), semantic JSON clearly improves driving-recommendation quality compared with using images alone.

That said, the conclusion needs one nuance: the ranking between `json_only` and `image+json` depends on which judge is used — one judge favors JSON alone, one favors the combination, and one treats the two modes as equal — so there is no absolute answer to the question "is combining images and JSON better than using JSON alone?" This is precisely the value of the multi-judge methodology: relying on a single judge alone would risk reporting a falsely "certain" conclusion that is in fact just an idiosyncrasy of that particular judge.

## 4.6. Verifying the Reliability of the Evaluation Method

With 120 score pairs — 20 images times 6 criteria, each pair consisting of one human score and one judge score for the same image/criterion — three agreement metrics are defined as follows: Exact agreement is the proportion of pairs with |human score − judge score| = 0; Agreement within ±1 is the proportion of pairs with |human score − judge score| ≤ 1; Pearson correlation r is computed on the two corresponding sequences of 120 human and judge scores.

**Gemini versus humans** (N=20, 120 score pairs): exact agreement 44/120 = 36.7%, agreement within ±1 point 95/120 = 79.2%, Pearson correlation 0.427.

Some caution is warranted when comparing this figure with MT-Bench: that study reports GPT-4 reaching 85% agreement with humans on a binary pairwise-comparison task, counted only on non-tied pairs [5] — fundamentally different from this thesis's absolute scoring on a 1–5 scale. A binary right/wrong decision is not equally difficult to a ±1-point tolerance on a 5-point scale, which has a much higher random-chance baseline. Given the differing task types, differing definitions of agreement, and differing verification scale (N=20 versus thousands of pairs), 79.2% and 85% are not directly comparable figures — their numerical closeness is not, on its own, evidence for Gemini's reliability, and the thesis does not use this as its main basis for that claim.

Stronger evidence, and the main basis for the decision to use Gemini as the thesis's primary judge, comes from within the study itself: Gemini reaches markedly higher agreement and correlation than the other two judges, verified under the exact same method, the same scale, and the same N=20 sample (Table 4.8) — a fair, same-unit comparison that does not depend on referencing a different study using a different task.

**GPT-5 Mini versus humans** (same N=20): exact agreement 23.3%, agreement within ±1 point 62.5%, correlation 0.194 — lower than Gemini on all three metrics, reinforcing the decision to use Gemini as the primary judge.

**DeepSeek versus humans** (same N=20, 120 score pairs): exact agreement 25.8%, agreement within ±1 point 55.0%, correlation 0.143 — the lowest of the three judges, with a Pearson correlation that carries essentially no practical statistical significance at this sample size. Notably, DeepSeek tends to systematically score lower than humans — the mean human-minus-DeepSeek difference is +1.21, much larger than for Gemini and GPT — with many cases where humans scored 4–5 but DeepSeek scored only 1–2, particularly on the `traffic_sign_rule` and `lane_ego_position` criteria. DeepSeek may interpret the rubric more strictly, or be less tolerant of indirect reasoning that lacks explicit evidence in the JSON.

**Table 4.8.** Reliability ranking of the three judges against human evaluation (N=20).

| Judge | Exact agreement | Within ±1 | Pearson correlation |
|---|---|---|---|
| Gemini | **36.7%** | **79.2%** | **0.427** |
| DeepSeek | 25.8% | 55.0% | 0.143 |
| GPT-5 Mini | 23.3% | 62.5% | 0.194 |

Gemini clearly outperforms the other two judges on all three metrics, reinforcing the decision to use Gemini as the primary judge for all of the thesis's central conclusions (Sections 4.4, 4.5); GPT-5 Mini and DeepSeek serve only as reference and cross-checking judges (Section 4.5).

A notable methodological finding is that the correlation between GPT and Gemini (0.511) is even higher than either judge's correlation with humans (0.427 and 0.194) — direct evidence that the two AI judges tend to agree with each other more than they agree with humans, possibly because they share a similar degree of strictness that differs from that of non-expert human raters. The correlation between DeepSeek and Gemini also reaches 0.395, still higher than the DeepSeek-human correlation (0.143), reinforcing the same finding. This is the methodological reason the thesis uses exactly one fixed judge (Gemini) for its main comparisons, and uses agreement with humans — not agreement among judges — as the benchmark.

## 4.7. Limitation: Data-Leakage Risk

The 200 images evaluated in Section 4.1 were randomly sampled from CULane, the same data source used to pretrain the lane-detection model (`culane_res34.pth`), without cross-checking against the official train/val/test split, since this information was not available in the locally used copy of the dataset. It therefore cannot be ruled out that some evaluation images overlap with data the model has already seen during training, which could make the absolute Accuracy and Precision figures in Section 4.1 more optimistic than the system's true generalization ability. This limitation does not affect the relative comparisons — the before/after bug-fix improvement, or the results throughout Sections 4.4–4.6 — since these comparisons use the same detection pass, differing only in the downstream processing step or model. The results in Section 4.2, verified on entirely independent real-life data, were carried out specifically to mitigate this risk.

## 4.8. Verifying VLM Self-Perception of Lane Semantics

A natural question arises: without going through the UFLD-v2 layer and semantic post-processing, how accurately can the VLM itself (`ising-calibration-31b`) perceive lane semantics just by observing the image? To answer this, a supplementary experiment was carried out: the VLM was given only the image, with no accompanying JSON or hints, and asked to return a JSON matching the current `_brief.json` schema (`lane_count`, `ego_lane`, `vehicle_offset`, `neighbor_lanes`, `road_shape`), on both datasets (CULane N=200, real-life N=200). All 200/200 images in both sets returned a valid JSON.

**Table 4.9.** Comparison of lane-semantics self-perception between the UFLD-v2 pipeline and the VLM.

| Dataset / Group | Lane count Accuracy (Pipeline) | Lane count Accuracy (VLM) | Lane count MAE (Pipeline) | Lane count MAE (VLM) | Road shape bucket match (Pipeline) | Road shape bucket match (VLM) |
|---|---|---|---|---|---|---|
| CULane – Normal (N=176, clear markings) | **77.3%** | 54.5% | **0.273** | 0.477 | 84.1% | **95.5%** |
| CULane – Hard (N=24, no clear markings) | 8.3% | **37.5%** | 1.958 | **0.792** | 20.8% | **91.7%** |
| CULane – Overall (N=200) | **69.0%** | 52.5% | **0.475** | 0.515 | 76.5% | **95.0%** |
| Independent real-life (N=200) | 50.5% | **53.5%** | 0.715 | **0.510** | 53.0% | **69.5%** |

The main finding from Table 4.9 is that the specialized pipeline (UFLD-v2) only clearly outperforms the VLM under exactly one condition: CULane images with clear markings, precisely the domain it was pretrained on. In the other two conditions — CULane images without clear markings, and the entire real-life dataset, which falls outside the CULane domain — VLM self-perception matches or exceeds the pipeline on every metric, especially for road shape (straight/curved classification), where the VLM outperforms the pipeline in all four rows of the table. This suggests that the pipeline's advantage stems in part from sharing a domain with its training data, not solely from the inherent architecture of a specialized detector: the pipeline becomes brittle outside that safe zone, whereas the general-purpose VLM — not fine-tuned specifically for the lane-understanding task — proves more stable.

## 4.9. Discussion: The Real Mechanism Behind the Contribution of Semantic JSON

Section 4.8 shows that VLM self-perception of lane semantics is far from weak — so why do `json_only`/`image+json` still clearly outperform `image_only` in Section 4.5? The hypothesis this thesis proposes: JSON does not merely compensate for missing visual ability, but mainly acts as **scaffolding** for reasoning and presentation in a multi-step task. Three points of evidence support this hypothesis:

- **Different task complexity.** Section 4.8 asks for only one thing — extracting figures according to a rigid schema; `image_only` in Section 4.5 packs three things into a single generation pass (self-perception, self-reasoning, and writing to a required three-part structure following a long prompt — Section 3.5). Strong performance on one narrow task does not guarantee equal quality when that task is only one hidden step within a more complex chain.
- **Non-equivalent prompts.** `json_only` supplies ready-made, structured data to reference directly when writing the answer; `image_only` only asks for general image observation, with far less scaffolding.
- **The judge scores writing style, not ground truth.** An answer that cites specific figures ("lane 2/3, 19.3% offset") is more easily judged as well-grounded and confident, even though the actual accuracy of those figures is not necessarily higher — precisely the writing-style bias that MT-Bench has documented as an inherent limitation of LLM-as-judge [5] (Section 2.4), the reason this thesis verifies against human judgment rather than trusting the judge unconditionally (Section 4.6).

This interpretation does not weaken the RQ3 conclusion — JSON still improves recommendation quality, verified by three independent judges — but clarifies the mechanism: JSON helps make answers more coherent and better grounded within a multi-step task, not simply because the VLM "cannot see the road." This is an inference based on indirect evidence — the two experiments use prompts of different complexity — rather than the result of a direct controlled experiment (same prompt complexity, differing only in the presence or absence of JSON); this is proposed as a direction for future work in Section 5.4.

---

# CHAPTER 5. CONCLUSION

## 5.1. Summary of Contributions

This thesis builds and quantitatively verifies a complete pipeline for LLM-based semantic understanding of lanes and traffic signs to support driving decisions, using two widely used standard datasets (CULane, TT100K). The reasoning layer follows a training-free approach — unlike end-to-end driving VLM systems (DriveGPT4 [2], DriveLM [3], LMDrive [4]), which require large-scale training (Sections 2.3, 2.5) — while the sign-perception layer involves one lightweight YOLOv8n fine-tuning step on TT100K (Section 3.2). The main results, with specific quantitative figures, are:

1. **The lane-understanding module** reaches 77.3% Accuracy on images with clear markings (N=176/200), generalizes well to an independently collected dataset (99.4% Precision, 86.5% Ego-lane Accuracy, N=200), but drops sharply to 8.3% on the 24 images without clear markings — an inherent limitation of a marking-based detector (Section 4.1).
2. **Evidence for the importance of the semantic-interpretation layer**: an off-by-one bug discovered while building the semantic-conversion layer initially limited Accuracy to 11.1%, even though UFLD-v2 itself had already reached F1 = 76.0% at the detection layer [1]. Fixing this bug is not, in itself, an algorithmic contribution, but it is experimental evidence for the argument that a detector's quality does not automatically guarantee the quality of the decision-support system built on top of it — showing the value of investing in careful verification of the semantic-interpretation layer (Sections 2.1, 4.1).
3. **The sign module** proves genuinely effective when data is dense enough (60.9% Precision/Recall on real-life data), but is limited on CULane due to the dataset's sparse sign density (6% of images have any detection).
4. **Semantic JSON clearly improves driving-recommendation quality**: Gemini 3.32 → 4.53/5, a 36% improvement, consistently verified by three independent judges over N=200 (Section 4.5).
5. **A verified LLM-as-a-judge evaluation method**: 79.2% agreement with humans within ±1 point (N=20), and cross-checking three judges under the same method establishes that Gemini clearly outperforms GPT-5 Mini and DeepSeek on all three agreement metrics against humans (Section 4.6) — the main basis for choosing Gemini as the primary judge, rather than directly benchmarking against other LLM-as-a-judge studies that use fundamentally different tasks and scales [5].
6. **Clarifying the mechanism behind JSON's contribution**: a supplementary verification shows that VLM self-perception of lanes from raw images is far from weak, even outperforming the UFLD-v2 pipeline when markings are missing or on out-of-domain data (Section 4.8), so JSON improves recommendation quality mainly through its role as scaffolding for reasoning and presentation in a multi-step task, not solely by compensating for missing visual perception (Section 4.9).

**Practical significance.** These results show that a driving decision-support system capable of natural-language explanation can be built at low cost: the reasoning layer uses a free VLM via API, requiring no retraining; the sign-perception layer needs only one lightweight fine-tuning step on a small model (YOLOv8n, roughly 3.2 million parameters) rather than collecting data and training a large-scale end-to-end system. This makes a suitable foundation for low-cost dashcam or smart black-box applications, or as a starting point for expansion to Vietnamese traffic data without having to rebuild the system from scratch — only requiring light fine-tuning at the lane- and sign-perception layers (Section 5.4).

## 5.2. Answers to the Research Questions

- **RQ1–RQ2**: fully answered quantitatively in Sections 4.1–4.3.
- **RQ3**: semantic JSON improves driving-recommendation quality compared with using images alone — a conclusion with solid verification (Section 4.5), with the underlying mechanism further clarified in Sections 4.8–4.9.
- **RQ4**: `ising-calibration-31b` is the most suitable choice within the range of models surveyed, based on reliability, structural compliance, and content quality (Section 4.4).
- **RQ5**: LLM-as-a-judge (Gemini) reaches an acceptable level of reliability against human judgment, better than the two alternative judges tested — GPT-5 Mini, DeepSeek — on all three agreement metrics (Section 4.6).

## 5.3. Limitations

- **The computer-vision pipeline's lane-understanding module depends heavily on lane markings and on sharing a domain with its training data.** On the 24/200 CULane images belonging to scenarios without clear markings, lane-count Accuracy drops from 77.3% to 8.3%, even though Precision still reaches 100% (Section 4.1). The supplementary verification in Section 4.8 shows that this is a limitation of the computer-vision pipeline specifically, not of the overall approach: VLM self-perception directly from the image does not share this exact weakness, and even outperforms the pipeline under those two conditions — opening up the hybrid design direction discussed in Section 5.4.
- Data-leakage risk on the CULane data (Section 4.7), partially mitigated by independent verification on real-life data.
- Comparison of LLM models and judges is limited to free, low-cost options, and has not been extended to larger or newer commercial versions of the model families tried (Gemini, GPT, DeepSeek) or to other models such as Claude.
- The sign module on CULane is limited by the dataset's own sparse data density.

## 5.4. Future Work

The following three directions are listed in order of priority, from the highest practical impact to additional technical improvements.

**1. Expanding to Vietnamese data, combined with a hybrid architecture.** The highest-priority direction is to apply and re-evaluate the pipeline on real Vietnamese traffic data — lane markings and signs following the QCVN national standard, high motorbike density, and different traffic behavior; an initial positive signal has already been observed through the self-collected real-life dataset (Section 4.2). Because Vietnamese traffic includes many scenarios without clear lane markings — exactly the UFLD-v2 pipeline's weak point (Sections 4.1, 5.3) — this direction should be paired with a hybrid architecture: keep UFLD-v2 as the primary source, and automatically fall back to the VLM's self-perception result (Section 4.8) when the pipeline returns a low-confidence signal (`lane_count=0`, low confidence).

**2. Strengthening the evaluation methodology.** Two specific tasks: (a) a direct controlled experiment for the "scaffolding" hypothesis in Section 4.9 — running `image_only` with a two-step prompt that forces the VLM to first extract a structured JSON before writing its recommendation, then comparing the result with the original `json_only`; if the gap narrows, the hypothesis is reinforced; (b) extending human–AI agreement verification beyond the current N=20 scale, potentially applying Kim's [15] adaptive sampling framework instead of random sampling.

**3. Technical improvements to the reasoning and perception layers.** These include: applying a verified reasoning structure such as RATT [18] (planning, fact-checking via RAG) to further reduce hallucination risk in complex scenarios — intersections, lane merging (Section 5.3); adding the ability to distinguish opposite-direction lanes and one-way/two-way roads; improving the sign module with higher-density data; and testing more advanced commercial LLMs.

---

# REFERENCES

[1] Z. Qin, P. Zhang, and X. Li, "Ultra fast deep lane detection with hybrid anchor driven ordinal classification," *IEEE Trans. Pattern Anal. Mach. Intell.*, 2022. [Online]. Available: https://arxiv.org/abs/2206.07389

[2] Z. Xu, Y. Zhang, E. Xie, Z. Zhao, Y. Guo, K. K. Y. Wong, Z. Li, and H. Zhao, "DriveGPT4: Interpretable end-to-end autonomous driving via large language model," *IEEE Robot. Autom. Lett.*, vol. 9, no. 10, pp. 8186–8193, Oct. 2024.

[3] C. Sima, K. Renz, K. Chitta, L. Chen, H. Zhang, C. Xie, J. Beißwenger, P. Luo, A. Geiger, and H. Li, "DriveLM: Driving with graph visual question answering," in *Proc. Eur. Conf. Comput. Vis. (ECCV)*, 2024.

[4] H. Shao, Y. Hu, L. Wang, S. L. Waslander, Y. Liu, and H. Li, "LMDrive: Closed-loop end-to-end driving with large language models," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2024.

[5] L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. P. Xing, H. Zhang, J. E. Gonzalez, and I. Stoica, "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena," in *Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)*, 2023.

[6] X. Pan, X. Zhan, J. Shi, P. Luo, X. Wang, and X. Tang, "Spatial as deep: Spatial CNN for traffic scene understanding," in *Proc. AAAI Conf. Artif. Intell.*, 2018.

[7] Y. Zhang, Z. Lu, X. Zhang, J.-H. Xue, and Q. Liao, "Deep learning in lane marking detection: A survey," *IEEE Trans. Intell. Transp. Syst.*, 2021.

[8] N. J. Zakaria, M. I. Shapiai, R. A. Ghani, M. N. M. Yassin, M. Z. Ibrahim, and N. Wahid, "Lane detection in autonomous vehicles: A systematic review," *IEEE Access*, vol. 11, pp. 3729–3765, 2023.

[9] Z. Zhu, D. Liang, S. Zhang, X. Huang, B. Li, and S. Hu, "Traffic-sign detection and classification in the wild," in *Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2016.

[10] J. Hong, B. Sapp, and J. Philbin, "Rules of the road: Predicting driving behavior with a convolutional model of semantic interactions," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2019, pp. 8454–8462.

[11] A. K. Shaw, C. K. Sah, X. Lian, A. S. Baig, T. Wen, K. Jiang, M. Yang, D. Yang, and L. Zhang, "SafeRoute: Enhancing traffic scene understanding via a unified deep learning and multimodal LLM," in *Proc. IEEE/CVF Int. Conf. Comput. Vis. Workshops (ICCVW)*, 2025.

[12] C. K. Sah, A. K. Shaw, X. Lian, A. S. Baig, T. Wen, K. Jiang, M. Yang, and D. Yang, "Advancing autonomous vehicle intelligence: Deep learning and multimodal LLM for traffic sign recognition and robust lane detection," *arXiv:2503.06313*, 2025.

[13] S. Kim, J. Jin, S. Hong, D. Ka, H. Kim, and B. Noh, "DSC-LLM: Driving scene context representation-based trajectory prediction framework with risk factor reasoning using LLMs," *Sensors*, vol. 25, no. 23, Art. no. 7112, 2025, doi: 10.3390/s25237112.

[14] M. A. Ferrag, N. Tihanyi, and M. Debbah, "From LLM reasoning to autonomous AI agents: A comprehensive review," *arXiv:2504.19678*, 2025.

[15] J. P. Kim, "Augmenting human evaluation with LLM judges: How many human reviews do you need?" *arXiv:2605.16354*, 2026.

[16] A. Saha, A. Wagde, and B. Kveton, "LLM-as-judge on a budget," *arXiv:2602.15481*, 2026.

[17] Q. Pan, Z. Ashktorab, M. Desmond, M. Santillán Cooper, J. Johnson, R. Nair, E. Daly, and W. Geyer, "Human-centered design recommendations for LLM-as-a-judge," in *Proc. 1st Hum.-Centered Large Lang. Model Workshop (HuCLLM)*, 2024.

[18] J. Zhang, X. Wang, W. Ren, L. Jiang, D. Wang, and K. Liu, "RATT: A thought structure for coherent and correct LLM reasoning," in *Proc. AAAI Conf. Artif. Intell.*, vol. 39, no. 25, pp. 26733–26741, 2025.
