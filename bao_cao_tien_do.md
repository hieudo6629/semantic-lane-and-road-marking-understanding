# BÁO CÁO TIẾN ĐỘ LUẬN VĂN THẠC SĨ

**Đề tài:** Semantic Lane and Traffic Sign Understanding Using Large Language Models for Driving Decision Support

**Học viên:** Đỗ Minh Hiếu — MSE13172
**Giảng viên hướng dẫn:** TS. Đoàn Nhật Quang
**Ngày báo cáo:** 24/08/2026 (cập nhật số liệu mới nhất từ `output-v3/`)

---

## 1. TÓM TẮT TIẾN ĐỘ

Em đã cài đặt và chạy thực nghiệm thành công một pipeline hoàn chỉnh gồm 3 tầng (Nhận diện → Ánh xạ ngữ nghĩa → Suy luận LLM), khắc phục các lỗi thiết kế của phiên bản đầu, và **vừa hoàn thành một vòng lặp cải tiến mới**: sửa lỗi đếm số làn (off-by-one), kích hoạt đầy đủ tín hiệu phát hiện cong nhẹ (`fit_improvement`), thêm tầng rút gọn JSON cho LLM (`_brief.json`), và viết lại prompt LLM theo hướng chặt chẽ hơn. Batch xử lý mới nhất (`output-v3/`, 199 ảnh CULane) phản ánh đúng trạng thái pipeline hiện tại. Em cũng đã xây xong một khung đánh giá tự động bằng LLM-as-judge (Gemini) để so sánh có hệ thống 3 chế độ đầu vào LLM — kết quả cho một phát hiện bất ngờ cần thảo luận thêm với thầy: chế độ chỉ dùng JSON hiện đang bị chấm điểm thấp nhất, thay vì cao nhất như kỳ vọng ban đầu của đề tài (chi tiết Mục 4.6). Đồng thời đã thử nghiệm và loại bỏ một proxy "tình trạng mặt đường" không đủ tin cậy dựa trên bằng chứng đo được (Mục 4.6). Nội dung chi tiết trình bày ở các mục dưới.

## 2. PIPELINE HỆ THỐNG ĐÃ CÀI ĐẶT

Hệ thống hiện tại (thư mục mã nguồn `src-v2/`) gồm 3 tầng xử lý nối tiếp, luôn chạy trên **cùng một ảnh trong cùng một lần gọi**:

```
Ảnh dashcam (BGR)
  → (1) NHẬN DIỆN
       - LaneDetector: Ultra-Fast-Lane-Detection-v2 (parsingNet, backbone ResNet-34)
       - SignDetector: YOLOv8n đã fine-tune, 15 lớp biển báo/đèn tín hiệu
         (config hiện trỏ tới checkpoint mới `yolov8n_tt100k_best.pt`, xem lưu ý Mục 5)
  → (2) ÁNH XẠ NGỮ NGHĨA (SceneBuilder)
       - LaneAnalyzer: xác định ego-lane, độ lệch xe, độ cong đường (vanishing point,
         kết hợp drift_ratio + fit_improvement)
       - RoadTypeAnalyzer: suy luận loại đường + môi trường đường, số làn thật
         (đã sửa lỗi đếm làn, xem Mục 3)
       - SignRuleInterpreter + RecommendationEngine: diễn giải luật giao thông,
         sinh khuyến nghị rule-based (tham khảo)
       → xuất ra 2 dạng JSON: bản đầy đủ (`<ảnh>.json`) và bản RÚT GỌN
         (`<ảnh>_brief.json`, mới thêm) chỉ giữ 4 nhóm thông tin chính:
         số làn, vị trí ego-lane, độ lệch tâm, hình dạng đường
  → (3) SUY LUẬN LLM
       - PromptBuilder: sinh prompt (4 chiến lược: zero-shot / chain-of-thought /
         explainable / safety-focused)
       - llm_batch_client.py: gọi LLM đa phương thức (NVIDIA NIM,
         nvidia/llama-3.1-nemotron-nano-vl-8b-v1) với 3 chế độ đầu vào
         (chỉ ảnh / chỉ JSON / cả ảnh + JSON) — prompt vừa được viết lại
         (xem Mục 3, mục 4)
       → khuyến nghị lái xe kèm giải thích ngôn ngữ tự nhiên
```

Điểm mấu chốt: tầng (2) chuyển tọa độ điểm/bounding box thô thành JSON có ngữ nghĩa (ví dụ: *"xe lệch phải 19% bề rộng làn (mức nhẹ), đường thẳng, ego-lane là làn 2/3"*) — đây là cầu nối giữa nhận thức hình học và suy luận ngôn ngữ mà đề xuất ban đầu đặt ra. Việc thêm bản JSON rút gọn (`_brief.json`) là bước tinh chỉnh mới nhất của cầu nối này, nhằm giảm nhiễu cho LLM (LLM không cần biết `offset_pixels = 97.35`, chỉ cần biết "lệch nhẹ về bên phải").

## 3. CÁC ĐÓNG GÓP ĐÃ THỰC HIỆN

1. **Hợp nhất luồng dữ liệu lane + sign.** Phiên bản đầu (`src/`) từng xử lý lane thật và sign thật ở hai luồng tách rời (khuyến nghị lái xe dùng lane giả lập hard-code). Bản hiện tại (`src-v2/`) đảm bảo lane và sign luôn được phát hiện trên cùng một ảnh, cùng một lần chạy.
2. **Xây dựng tầng ánh xạ hình học → JSON ngữ nghĩa** (`SceneBuilder`), gồm: xác định ego-lane theo thuật toán chấm điểm cặp làn kề nhau, tính độ lệch xe, ước lượng độ cong đường bằng phân tích vanishing point.
3. **Hiệu chỉnh ngưỡng phân loại độ cong đường qua 2 vòng lặp dựa trên số liệu thực đo**: vòng 1 hiệu chỉnh lại 2 ngưỡng `drift_ratio` theo phân phối thực đo trên 399 ảnh; vòng 2 (mới hoàn thành) kích hoạt đầy đủ tín hiệu `fit_improvement` để bắt thêm các trường hợp cong nhẹ ở cự ly gần mà `drift_ratio` bỏ sót — kết quả định lượng cả 2 vòng ở Mục 4.2.
4. **Sửa lỗi đếm số làn (off-by-one), mới hoàn thành.** Trường `lane_count` trước đây lấy trực tiếp số **đường biên** phát hiện được, trong khi số **làn** thật = số đường biên − 1 (một làn nằm giữa 2 đường biên kề nhau). Đối chiếu tay 199 ảnh xác nhận lỗi lệch +1 ở ~90% ảnh. Vì trường này được nhúng thẳng vào JSON gửi cho LLM, lỗi lệch từng khiến LLM nhận thông tin sai (ví dụ ảnh có 2 làn thật bị mô tả nhầm thành "4 lanes"). Đã sửa bằng hàm `_count_real_lanes()` trong `road_type.py`.
5. **Thêm tầng rút gọn JSON cho LLM** (`analysis/scene_summarizer.py`, mới) — sinh file `_brief.json` chỉ giữ 4 nhóm thông tin cốt lõi (số làn, vị trí + độ tin cậy ego-lane, độ lệch tâm đã phân loại mức độ, hình dạng đường), cố tình bỏ các trường chưa đủ tin cậy (`road_environment`, `active_speed_limit`, khuyến nghị rule-based) thay vì để LLM tự tin dùng các heuristic if-else còn thô.
6. **Sửa lỗi logic khuyến nghị tốc độ**: bản cũ chỉ dựa vào độ tin cậy nhận diện biển báo (YOLO) để quyết định "tăng tốc/giảm tốc", không so sánh với tốc độ thực tế của xe; bản hiện tại so sánh trực tiếp tốc độ xe với giá trị ghi trên biển báo.
7. **Viết lại prompt LLM** (`llm_batch_client.py`) theo hướng chặt chẽ hơn: tách phần luật chung (`common`) dùng lại cho cả 3 chế độ, giới hạn độ dài câu trả lời (~120 từ), và bổ sung ràng buộc mới — nếu bằng chứng cho thấy điều kiện bắt buộc dừng (đèn đỏ, biển STOP, luật nhường đường rõ ràng), khuyến nghị **bắt buộc phải là dừng/nhường đường**, không được vừa nêu bằng chứng vừa khuyến nghị tiếp tục di chuyển.
8. **Xây dựng bộ mã nguồn đánh giá thực nghiệm**: `batch_process.py` (chạy hàng loạt, xuất JSON đầy đủ + JSON rút gọn + ảnh overlay), `llm_batch_client.py` (gọi LLM hàng loạt qua API, 3 chế độ đầu vào), `generate_briefs.py` (tái sinh `_brief.json` từ JSON thô có sẵn mà không cần chạy lại model, dùng khi `scene_summarizer.py` thay đổi sau khi đã có JSON thô) — phục vụ tạo bộ số liệu ở Mục 4.
9. **Thực hiện đánh giá thủ công theo rubric** (thang 0/1/2) trên 109 ảnh cho từng thành phần đầu ra (làn đường, loại đường, ego-lane, độ lệch xe, phân loại làn, biển báo) — kết quả ở Mục 4.1 (lưu ý về thời điểm đánh giá ở Mục 5).
10. **Thử nghiệm và loại bỏ một proxy không đủ tin cậy, dựa trên bằng chứng đo được.** Từng thử suy ra `road_condition` (tình trạng mặt đường tốt/thường/xấu) từ độ tin cậy (`confidence`) của mô hình phát hiện làn + độ cong. Viết `evaluate_road_condition.py` để đối chiếu với 198 ảnh gán nhãn tay — kết quả tỉ lệ khớp đúng chỉ **29–34%**, kém hơn cả việc luôn đoán lớp phổ biến nhất. Đã loại bỏ hẳn trường này khỏi `_brief.json` thay vì giữ lại một tín hiệu không đáng tin — kết quả chi tiết ở Mục 4.6.
11. **Xây dựng khung đánh giá tự động bằng LLM-as-judge** (`score_output_by_gemini.py`, mô hình giám khảo Gemini 3.5 Flash): chấm điểm độc lập 6 tiêu chí (thang 1–5) cho 3 nhánh thử nghiệm (chỉ ảnh / chỉ JSON / cả ảnh + JSON) trên cùng 199 ảnh, mỗi ảnh chỉ gọi API đúng 1 lần (gộp cả 3 nhánh vào 1 request để tiết kiệm quota và đảm bảo giám khảo chấm nhất quán) — đây chính là phép so sánh có hệ thống giữa 3 chế độ đầu vào mà báo cáo kỳ trước còn thiếu. Kết quả ở Mục 4.6.

## 4. KẾT QUẢ THỰC NGHIỆM

### 4.1. Đánh giá thủ công theo rubric (109 ảnh, thang điểm 0–2)

| Thành phần | Điểm TB /2 | Tỉ lệ | Phân phối (0 / 1 / 2) |
|---|---|---|---|
| Làn đường phát hiện | 1.68 | 84.0% | 6 / 23 / 80 |
| Loại đường / độ cong | 0.86 | 43.1% | 26 / 72 / 11 |
| Xác định ego-lane | 1.85 | 92.7% | 5 / 6 / 98 |
| Độ lệch xe | 1.76 | 88.1% | 8 / 10 / 91 |
| Phân loại làn lân cận/mép | 1.45 | 72.5% | 18 / 24 / 67 |

→ Ego-lane và độ lệch xe là hai thành phần đáng tin cậy nhất (88–93%); loại đường/độ cong là điểm yếu nhất (43.1%). **Lưu ý:** bảng này được chấm trên batch chạy **trước** khi sửa lỗi đếm làn và kích hoạt đầy đủ `fit_improvement` (Mục 3, mục 4) — vì phân bố `road_type` đã thay đổi đáng kể ở batch mới nhất (Mục 4.2), điểm số "Loại đường/độ cong" cần được chấm lại trên `output-v3/` để phản ánh đúng hiện trạng.

### 4.2. Hiệu chỉnh phân loại độ cong đường — 3 vòng lặp trên cùng 199 ảnh CULane

| `road_type` | V1: ngưỡng ban đầu (trực giác) | V2: ngưỡng đã hiệu chỉnh số liệu | **V3: + kích hoạt `fit_improvement` + sửa đếm làn (mới nhất, `output-v3/`)** |
|---|---|---|---|
| `straight` (đường thẳng) | 9 ảnh (4.5%) | 179 ảnh (89.9%) | **155 ảnh (77.9%)** |
| `gentle_curve` (cong nhẹ) | 156 ảnh (78.4%) | 1 ảnh (0.5%) | **26 ảnh (13.1%)** |
| `sharp_curve` (cong gắt) | 16 ảnh (8.0%) | 1 ảnh (0.5%) | **0 ảnh (0%)** |
| `unknown` (không phát hiện làn) | 18 ảnh (9.0%) | 18 ảnh (9.0%) | 18 ảnh (9.0%) |

→ V1→V2 (đã báo cáo kỳ trước): hiệu chỉnh 2 ngưỡng `drift_ratio` theo đúng phân phối thực đo đưa tỉ lệ nhận đúng "đường thẳng" từ 4.5% lên 89.9%. V2→V3 (mới): sau khi kích hoạt đầy đủ tín hiệu `fit_improvement` (thiết kế để bắt các khúc cong nhẹ ở cự ly gần mà `drift_ratio` một mình bỏ sót), số ảnh được phân loại `gentle_curve` tăng từ 1 lên 26 ảnh, đúng như mục tiêu thiết kế của tín hiệu này. Số ảnh `unknown` (18) không đổi qua cả 3 vòng — xác nhận thay đổi chỉ nằm ở logic phân loại, không phải kết quả phát hiện làn (đã kiểm tra: toạ độ làn phát hiện được ở V2 và V3 giống hệt nhau).

**Điểm cần lưu ý (chưa giải thích được đầy đủ):** `sharp_curve` giảm từ 1 ảnh (V2) xuống 0 ảnh (V3) dù `fit_improvement` theo thiết kế chỉ tác động tới việc phân biệt `straight`/`gentle_curve`, không trực tiếp thay đổi ngưỡng `sharp_curve`. Em chưa xác định chắc chắn nguyên nhân (có thể do tương tác giữa các nhánh phân loại) — sẽ kiểm tra lại ảnh cụ thể này và báo cáo thầy ở kỳ tới.

### 4.3. Hiệu năng và tỉ lệ phát hiện

| Bộ dữ liệu | Số ảnh | Tỉ lệ ảnh có ≥1 làn | Thời gian xử lý TB/ảnh (CPU) |
|---|---|---|---|
| CULane (`output-v3/`, mới nhất) | 199 | 91.0% | 0.62 giây |
| Tusimple | 200 | 100% | 0.39 giây |

Số làn (đường biên) phát hiện được không đổi so với các lần chạy trước (0 làn: 9.0%, 1 làn: 4.5%, 2 làn: 2.0%, 3 làn: 43.2%, 4 làn: 41.2%) và thời gian xử lý không thay đổi đáng kể — các cập nhật ở Mục 3 chỉ can thiệp vào tầng phân tích/ánh xạ ngữ nghĩa, không làm lại bước phát hiện làn đường.

### 4.4. Đánh giá LLM đa phương thức

- 199/199 cặp ảnh + JSON được gửi thành công tới mô hình `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` (chế độ ảnh + JSON), thời gian trung bình **≈ 9.1 giây/yêu cầu**.
- Khảo sát định tính cho thấy khuyến nghị của LLM nhất quán với khuyến nghị rule-based trong phần lớn trường hợp, và các chi tiết ngữ cảnh LLM thêm vào được xác nhận là có thật trong ảnh gốc — không phải "ảo giác".
- **Lưu ý:** batch đánh giá LLM này chạy trên JSON sinh ra **trước** khi sửa lỗi đếm làn và trước khi có `_brief.json`/prompt mới (Mục 3) — cần chạy lại batch LLM trên `output-v3/` để đo đúng tác động của các thay đổi mới nhất tới chất lượng suy luận, em dự kiến làm ở kỳ tới.

### 4.5. Nhận diện biển báo giao thông

Tỉ lệ khung hình có biển báo được phát hiện trên `output-v3/` giữ nguyên như batch trước (CULane 2.0%, Tusimple 1.0%) — cỡ mẫu chưa đủ lớn để đánh giá định lượng có ý nghĩa cho mô-đun này. **Lưu ý:** số liệu này vẫn dùng checkpoint biển báo cũ (`yolov8n_trained_best.pt`); config hiện đã trỏ sang checkpoint mới `yolov8n_tt100k_best.pt` nhưng chưa có batch nào được chạy lại để đánh giá checkpoint mới này (xem Mục 5).

### 4.6. So sánh 3 chế độ đầu vào LLM bằng chấm điểm tự động (Gemini-as-judge)

Dùng `score_output_by_gemini.py` (mô hình giám khảo `gemini-3.5-flash`), chấm độc lập 6 tiêu chí (thang 1–5, không cộng trọng số) cho 3 nhánh thử nghiệm trên cùng 199 ảnh CULane (mỗi nhánh dùng cùng prompt "v2" của `llm_batch_client.py`, chỉ khác đầu vào):

| Tiêu chí (1–5) | Chỉ ảnh (`prompt_image`) | Chỉ JSON (`prompt_json`) | Ảnh + JSON (`prompt_image_json`) |
|---|---|---|---|
| Hiểu tình huống chung | **3.48** | 2.36 | 3.25 |
| Hiểu đúng hình học đường/làn | **3.53** | 2.81 | 3.39 |
| Vị trí ego-lane/độ lệch xe | 3.01 | 2.80 | **3.14** |
| Biển báo/luật giao thông | **3.31** | 2.69 | 3.09 |
| Khuyến nghị lái xe | **3.57** | 3.17 | 3.53 |
| Cân nhắc an toàn | **3.35** | 2.41 | 3.12 |
| **Trung bình 6 tiêu chí** | **3.375** | 2.709 | 3.251 |

**Phát hiện quan trọng nhất (bất ngờ so với kỳ vọng ban đầu của đề tài):** chế độ **chỉ JSON đang kém nhất ở cả 6/6 tiêu chí**, kể cả tiêu chí liên quan trực tiếp tới hình học (đường/làn, ego-lane) mà JSON lẽ ra phải có lợi thế rõ ràng nhất. Chế độ chỉ ảnh lại cao nhất ở hầu hết tiêu chí; chế độ ảnh+JSON chỉ vượt trội duy nhất ở tiêu chí ego-lane/độ lệch xe — đúng phần thông tin JSON mô tả tường minh nhất.

**Cần diễn giải thận trọng, chưa vội kết luận:** batch LLM này được sinh từ JSON của **trước khi sửa lỗi đếm làn** (Mục 3, mục 4.4) — nếu JSON từng mô tả sai số làn (+1 so với thực tế), hoàn toàn có khả năng đó là một phần nguyên nhân khiến nhánh "chỉ JSON" bị đánh giá thấp ở đúng tiêu chí hình học đường/làn. Cần chạy lại phép so sánh này trên JSON đã sửa lỗi (`output-v3/`) để biết khoảng cách có thu hẹp hay không, trước khi kết luận liệu lược đồ JSON hiện tại có thực sự cần bổ sung thêm thông tin hay không.

## 5. KHÓ KHĂN / HẠN CHẾ HIỆN TẠI

1. **Chưa có tập nhãn chuẩn (ground truth) ở mức box/pixel** khớp đúng lớp biển báo và làn đường trên tập ảnh thực nghiệm, nên chưa tính được các chỉ số chuẩn `mAP`/`F1` cho hai bộ phát hiện — đánh giá hiện dựa trên rubric thủ công (109 ảnh, và bản rubric này đang cũ hơn pipeline hiện tại — xem điểm 3 dưới đây).
2. **Mật độ biển báo trong CULane/Tusimple quá thấp** (1–2% số ảnh) để đánh giá đúng năng lực mô-đun nhận diện biển báo cho bối cảnh Việt Nam — cần một bộ ảnh test riêng có nhiều biển báo hơn.
3. **Đánh giá thủ công (Mục 4.1) và batch LLM (Mục 4.4) hiện đang "lệch pha"** so với pipeline mới nhất (`output-v3/`): cả hai được thực hiện trước khi sửa lỗi đếm làn, trước khi `fit_improvement` được kích hoạt đầy đủ, và trước khi có `_brief.json`/prompt mới. Cần chạy lại cả hai trên `output-v3/` để biết chính xác các cải tiến mới có thực sự nâng điểm "Loại đường/độ cong" (điểm yếu nhất, 43.1%) hay không.
4. **Model biển báo vừa đổi sang checkpoint mới (`yolov8n_tt100k_best.pt`) nhưng chưa được chạy/đánh giá lại** trên bất kỳ batch nào — chưa biết checkpoint mới có cải thiện so với checkpoint cũ hay không.
5. **Hệ thống chưa có khái niệm "chiều di chuyển"** (không phân biệt làn cùng chiều/ngược chiều) — phát hiện qua quá trình đánh giá thủ công, chưa có hướng xử lý cụ thể.
6. **Độ trễ toàn hệ thống còn xa mục tiêu thời gian thực on-device** (300–500 ms/khung hình theo đề xuất ban đầu): tầng nhận thức mất ~0.62 giây/ảnh trên CPU (chưa tính LLM), tầng LLM qua API đám mây mất thêm ~9.1 giây/yêu cầu. Em chưa thử nghiệm trên GPU/thiết bị biên hay mô hình LLM chạy on-device như định hướng ban đầu.
7. **Chưa lý giải được nguyên nhân JSON-only bị chấm điểm thấp nhất ở cả 6/6 tiêu chí** (Mục 4.6) — nghi ngờ một phần do lỗi đếm làn của batch JSON dùng để đánh giá, nhưng chưa loại trừ khả năng bản thân lược đồ JSON đầy đủ hiện tại quá dài/khó dùng với LLM (đúng lý do đã thêm `_brief.json`, nhưng batch đánh giá Gemini ở Mục 4.6 vẫn dùng JSON đầy đủ, chưa thử với `_brief.json`). Chưa so sánh phiên bản prompt "v2" (dùng để chấm điểm) với các bản "v3"/"v4" mới hơn đã có sẵn trong `llm_batch_client.py`.
8. **Chưa tìm được tín hiệu đủ tin cậy để mô tả tình trạng mặt đường** (`road_condition`) — proxy dựa trên confidence đã bị loại bỏ (Mục 3, mục 4.6) vì độ chính xác quá thấp (29–34%); hiện chưa có hướng thay thế cụ thể, có thể cần một mô hình/tín hiệu chuyên biệt riêng thay vì suy ra gián tiếp từ confidence của mô hình làn đường.
9. **Chưa so sánh giữa 4 chiến lược prompt** (zero-shot/chain-of-thought/explainable/safety-focused) đã cài đặt trong `PromptBuilder` — khung Gemini-as-judge (Mục 4.6) mới so sánh 3 chế độ đầu vào, chưa mở rộng sang so sánh chiến lược prompt.

Em mong nhận được góp ý của thầy về việc **ưu tiên xử lý hạn chế nào trước** cho giai đoạn tiếp theo — đặc biệt giữa việc (a) chạy lại đánh giá thủ công + so sánh Gemini-as-judge trên `output-v3/`/`_brief.json` để có số liệu nhất quán và trả lời câu hỏi tại sao JSON-only kém, (b) xây tập nhãn chuẩn cho `mAP`/`F1`, và (c) tối ưu độ trễ.
