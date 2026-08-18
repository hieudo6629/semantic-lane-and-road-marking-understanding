# TRƯỜNG ĐẠI HỌC FPT — FPT SCHOOL OF BUSINESS & TECHNOLOGY

## BÁO CÁO LUẬN VĂN THẠC SĨ

**Ngành:** Khoa học Máy tính

**Đề tài:** Hiểu ngữ nghĩa vạch kẻ đường và biển báo giao thông bằng mô hình ngôn ngữ lớn phục vụ hỗ trợ ra quyết định lái xe
*(Semantic Lane and Traffic Sign Understanding Using Large Language Models for Driving Decision Support)*

**Học viên:** Đỗ Minh Hiếu — MSE13172
**Giảng viên hướng dẫn:** TS. Đoàn Nhật Quang

Hà Nội, 2026

---

### LỜI CAM ĐOAN

Tôi xin cam đoan luận văn này là công trình nghiên cứu của riêng tôi, được thực hiện dưới sự hướng dẫn của TS. Đoàn Nhật Quang. Các số liệu, kết quả thực nghiệm trình bày trong luận văn được thu thập trực tiếp từ hệ thống do tôi xây dựng, chưa từng được công bố trong bất kỳ công trình nào khác. Các tài liệu tham khảo được trích dẫn đầy đủ và trung thực theo đúng quy định.

### LỜI CẢM ƠN

Tôi xin gửi lời cảm ơn chân thành tới TS. Đoàn Nhật Quang vì những định hướng và góp ý quý báu trong suốt quá trình thực hiện đề tài. Tôi cũng xin cảm ơn FPT School of Business & Technology đã tạo điều kiện học tập và nghiên cứu.

### TÓM TẮT

Các hệ thống hỗ trợ lái xe hiện nay thường tách rời hai lớp xử lý: (1) các mô hình thị giác máy tính phát hiện vạch kẻ đường và biển báo ở mức pixel nhưng không giải thích được ý nghĩa của phát hiện đó trong bối cảnh lái xe, và (2) các mô hình ngôn ngữ lớn (LLM) có khả năng suy luận ngôn ngữ tự nhiên nhưng không có khả năng tiếp cận trực tiếp với hình học không gian của cảnh giao thông. Luận văn này trình bày một pipeline ba tầng — **Nhận diện (Perception)** → **Ánh xạ Không gian sang Ngữ nghĩa (Spatial-to-Semantic Mapping)** → **Suy luận LLM (LLM Reasoning)** — nhằm nối hai lớp xử lý trên. Hệ thống được cài đặt và thực thi thực tế (`src-v2/`), sử dụng mô hình Ultra-Fast-Lane-Detection-v2 (kiến trúc `parsingNet`, backbone ResNet-34) để phát hiện làn đường, mô hình YOLOv8n tinh chỉnh để phát hiện biển báo, một tầng phân tích hình học (ego-lane, độ lệch xe, độ cong dựa trên vanishing point) chuyển kết quả thành JSON có cấu trúc, và một mô-đun sinh prompt kèm gọi LLM đa phương thức (NVIDIA NIM `llama-3.1-nemotron-nano-vl-8b-v1`) để sinh khuyến nghị lái xe có giải thích. Hệ thống được đánh giá trên 199 ảnh CULane, 200 ảnh Tusimple và 199 cặp ảnh/JSON được LLM xử lý. Kết quả cho thấy độ chính xác định tính cao ở các mô-đun xác định ego-lane (93%) và độ lệch xe (88%) theo đánh giá thủ công, trong khi mô-đun phân loại độ cong đường vẫn là điểm yếu nhất (43%) dù đã được hiệu chỉnh lại ngưỡng dựa trên số liệu thực đo. Luận văn cũng chỉ ra các khoảng cách còn tồn tại giữa tầm nhìn ban đầu (mô hình LLM lượng tử hoá chạy on-device, độ trễ 300–500 ms) và hệ thống hiện tại (LLM suy luận qua API đám mây, độ trễ trung bình ~9 giây/yêu cầu), từ đó đề xuất hướng phát triển tiếp theo.

**Từ khóa:** phát hiện làn đường, nhận diện biển báo giao thông, mô hình ngôn ngữ lớn, suy luận đa phương thức, hệ thống hỗ trợ lái xe, biểu diễn ngữ nghĩa cảnh giao thông.

### MỤC LỤC

- Chương 1: Giới thiệu và Đặt vấn đề
- Chương 2: Cơ sở lý thuyết và Công nghệ nền tảng
- Chương 3: Phương pháp và Kiến trúc hệ thống đề xuất
- Chương 4: Kết quả thực nghiệm và Đánh giá
- Chương 5: Kết luận và Hướng phát triển tương lai
- Tài liệu tham khảo

---

## CHƯƠNG 1: GIỚI THIỆU VÀ ĐẶT VẤN ĐỀ

### 1.1. Bối cảnh và động lực

Các hệ thống hỗ trợ lái xe tiên tiến (Advanced Driver Assistance Systems — ADAS) và xe tự hành đang ngày càng phụ thuộc vào các pipeline thị giác máy tính để nhận diện vạch kẻ đường và biển báo giao thông. Những mô hình phát hiện đối tượng dựa trên học sâu — từ các kiến trúc phân đoạn theo pixel (SCNN) đến các kiến trúc phân loại thứ tự theo anchor lai (hybrid-anchor ordinal classification) như Ultra-Fast-Lane-Detection-v2 — đã đạt độ chính xác rất cao trên các bộ dữ liệu chuẩn như CULane và Tusimple. Song song đó, các mô hình ngôn ngữ lớn (LLM) và mô hình đa phương thức (multimodal LLM/VLM) đã cho thấy năng lực suy luận ngôn ngữ tự nhiên vượt trội, mở ra khả năng sinh giải thích (explanation) cho các quyết định lái xe thay vì chỉ đưa ra nhãn phân loại thô.

Tuy nhiên, hai dòng công nghệ này phát triển gần như độc lập. Việc kết hợp chúng — để một hệ thống vừa "nhìn thấy" chính xác hình học của làn đường và biển báo, vừa "giải thích" được ý nghĩa của những gì nhìn thấy trong ngôn ngữ tự nhiên — là hướng đi tất yếu để tiến gần hơn tới trí tuệ lái xe giống con người, đúng như định hướng ban đầu của đề tài.

### 1.2. Vấn đề nghiên cứu

Vấn đề cốt lõi mà luận văn giải quyết là **khoảng cách giữa nhận thức hình học mức thấp (low-level geometric perception) và suy luận ngữ nghĩa mức cao (high-level semantic reasoning)**:

- Các pipeline nhận diện (YOLO, Ultra-Fast-Lane-Detection-v2, ResNet) xuất ra tọa độ điểm, bounding box, nhãn lớp — những con số "vô tri" không tự mang ý nghĩa lái xe (ví dụ: một danh sách điểm `(x, y)` không tự nói lên "xe đang lệch phải 19% bề rộng làn").
- Các hệ thống LLM hỗ trợ lái xe (DiLu, DriveGPT4, GPT-Driver) suy luận tốt về ngôn ngữ nhưng không được cấp một biểu diễn không gian chính xác của cảnh — chúng thường nhận đầu vào là văn bản mô tả hoặc embedding ảnh chung chung, không có cấu trúc hình học tường minh (vị trí ego-lane, độ cong, độ lệch xe theo pixel).

Trong quá trình xây dựng hệ thống thực tế cho đề tài này, vấn đề trên còn thể hiện cụ thể hơn: phiên bản đầu của pipeline (thư mục `src/`) từng có tình trạng dữ liệu làn đường và biển báo được xử lý **tách rời** — mô-đun tích hợp cảnh (`integrated_scene.py`) chỉ được gọi với dữ liệu làn đường giả lập hard-code, khiến khuyến nghị lái xe sinh ra không phản ánh đúng làn đường thật trong ảnh. Đây là một minh chứng cụ thể, ở cấp độ triển khai, cho chính "khoảng cách nhận thức–suy luận" được nêu trong vấn đề nghiên cứu.

### 1.3. Câu hỏi nghiên cứu

1. Có thể xây dựng một tầng ánh xạ (mapping layer) chuyển đổi đáng tin cậy từ đầu ra hình học thô (điểm làn đường, bounding box biển báo) thành một biểu diễn ngữ nghĩa có cấu trúc (JSON) mà LLM có thể suy luận trực tiếp hay không?
2. Việc hiệu chỉnh ngưỡng phân loại (ví dụ: ngưỡng phân loại độ cong đường) dựa trên số liệu thực đo trên nhiều bộ dữ liệu có cải thiện đáng kể độ chính xác so với ngưỡng chọn theo trực giác hay không?
3. Khi được cấp cả ảnh gốc và biểu diễn JSON có cấu trúc, một LLM đa phương thức tổng quát (không huấn luyện riêng cho lái xe) có sinh được khuyến nghị lái xe nhất quán với dữ liệu hình học hay không, và những dạng sai lệch/"ảo giác" (hallucination) nào có thể xảy ra?
4. Kiến trúc pipeline hiện tại còn cách bao xa so với mục tiêu triển khai thời gian thực trên thiết bị biên (edge, độ trễ 300–500 ms) mà đề xuất ban đầu đặt ra?

### 1.4. Đóng góp chính

1. **Một pipeline ba tầng đã được cài đặt và chạy thực tế** (không chỉ dừng ở thiết kế), nối liền nhận diện làn đường + biển báo → phân tích hình học → biểu diễn JSON → prompt LLM, khắc phục triệt để lỗi tách rời dữ liệu lane/sign của phiên bản trước đó (mục 1.2).
2. **Một bộ ngưỡng phân loại độ cong đường (curvature classification) được hiệu chỉnh lại bằng số liệu thực đo** trên 200 ảnh Tusimple và 199 ảnh CULane, khắc phục lỗi hệ thống luôn phân loại sai đường thẳng thành đường cong do ngưỡng ban đầu chọn theo trực giác lệch hàng trăm lần so với thang giá trị thực tế.
3. **Một bộ dữ liệu đánh giá thực nghiệm** gồm 399 ảnh (199 CULane + 200 Tusimple) đã qua xử lý toàn phần, cùng một tập 199 cặp ảnh/JSON đã được một LLM đa phương thức thương mại (NVIDIA NIM) sinh khuyến nghị, phục vụ phân tích định lượng và định tính ở Chương 4.
4. **Một khung đánh giá thủ công theo rubric** (0/1/2) cho từng thành phần của cảnh (làn đường, loại đường, ego-lane, độ lệch xe, phân loại làn, biển báo) trên 109 ảnh, cho phép định vị chính xác mô-đun nào là điểm yếu của hệ thống hiện tại (loại đường/độ cong) thay vì đánh giá cảm tính.
5. **Phân tích khoảng cách giữa tầm nhìn đề xuất và hệ thống thực tế** (mô hình LLM on-device lượng tử hoá 4-bit ở đề xuất ban đầu so với LLM đa phương thức qua API đám mây ở bản cài đặt hiện tại), làm cơ sở cho hướng phát triển ở Chương 5.

### 1.5. Công thức hóa vấn đề

Gọi $I$ là ảnh dashcam đầu vào. Một pipeline nhận thức truyền thống học một ánh xạ:

$$f_{\text{perception}}: I \rightarrow (L, S)$$

trong đó $L = \{l_1, l_2, \dots, l_n\}$ là tập điểm của $n$ làn đường phát hiện được ($l_i = \{(x_j, y_j)\}$) và $S = \{s_1, \dots, s_m\}$ là tập biển báo phát hiện được (mỗi $s_k$ gồm lớp, độ tin cậy, bounding box). Đây là điểm dừng của phần lớn hệ thống ADAS hiện nay: $(L, S)$ không tự mang ngữ nghĩa lái xe.

Luận văn bổ sung một ánh xạ trung gian:

$$f_{\text{semantic}}: (L, S) \rightarrow J$$

trong đó $J$ là một biểu diễn JSON có cấu trúc, chứa các đại lượng đã được diễn giải: ego-lane, độ lệch xe $\delta$, độ cong đường, loại đường, luật giao thông áp dụng. Cuối cùng, một mô hình suy luận sinh khuyến nghị có giải thích:

$$f_{\text{reasoning}}: J \rightarrow (a, e)$$

với $a$ là hành động lái xe khuyến nghị và $e$ là phần giải thích ngôn ngữ tự nhiên. Toàn bộ hệ thống là hợp thành $f_{\text{reasoning}} \circ f_{\text{semantic}} \circ f_{\text{perception}}$. Chương 3 trình bày cách mỗi ánh xạ này được cài đặt cụ thể trong mã nguồn của đề tài.

**[GỢI Ý THÊM HÌNH 1.1]** Sơ đồ khối tổng quan ba tầng $f_{\text{perception}} \to f_{\text{semantic}} \to f_{\text{reasoning}}$, đặt cạnh sơ đồ Hình 1 trong bản đề xuất ban đầu (Geometric Perception Module → Spatial-to-Semantic Mapping Module → LLM-based Reasoning Module) để nhấn mạnh tính nhất quán giữa đề xuất và cài đặt thực tế.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ NỀN TẢNG

### 2.1. Nhận diện vạch kẻ đường

**Từ xử lý ảnh cổ điển đến học sâu.** Các phương pháp sớm dựa trên biến đổi Hough, lọc màu/cạnh (edge-based) có chi phí tính toán thấp nhưng dễ thất bại với vạch kẻ mờ, bị che khuất hoặc điều kiện ánh sáng yếu — đúng những điều kiện phổ biến trong giao thông đô thị Việt Nam mà đề tài hướng tới. Các mô hình học sâu dựa trên phân đoạn theo pixel (semantic segmentation), tiêu biểu là **SCNN** (Spatial CNN), cải thiện đáng kể khả năng suy luận theo ngữ cảnh không gian rộng (ví dụ đạt F1 71.6% trên CULane) nhưng có chi phí suy luận cao vì phải phân loại từng pixel.

**Hướng tiếp cận anchor-based hiệu quả.** Để đạt tốc độ thời gian thực, một hướng khác coi bài toán phát hiện làn đường là bài toán *phân loại thứ tự theo anchor* (ordinal classification theo hàng/cột) thay vì phân đoạn dày đặc. **Ultra-Fast-Lane-Detection-v2** (Qin và cộng sự, *"Ultra Fast Deep Lane Detection With Hybrid Anchor Driven Ordinal Classification"*, IEEE TPAMI 2022) — kiến trúc được lựa chọn làm bộ phát hiện làn đường trong hệ thống của luận văn này (xem Chương 3) — biểu diễn mỗi làn bằng một tập điểm thưa (sparse coordinates) trên các **anchor lai**: anchor hàng (row anchor) cho các làn gần thẳng đứng ở giữa ảnh, và anchor cột (col anchor) cho các làn nghiêng mạnh gần rìa ảnh, nơi một giá trị hoành độ có thể ứng với nhiều tung độ nên không thể biểu diễn tốt theo kiểu row-anchor thuần túy. Cách tiếp cận này giải quyết đồng thời hai vấn đề: tốc độ (không cần phân loại từng pixel) và độ chính xác trong điều kiện bị che khuất/thiếu sáng.

Ở góc độ đánh giá tình trạng vật lý của vạch kẻ (không chỉ vị trí hình học), Alzraiee và cộng sự (*"Detecting of Pavement Marking Defects Using Faster R-CNN"*, ASCE Journal of Performance of Constructed Facilities, 2021) áp dụng Faster R-CNN để phát hiện tự động các hư hỏng của vạch sơn kẻ đường, phản ánh một nhánh nghiên cứu liên quan: vạch kẻ đường không chỉ cần được *định vị* mà còn cần được *đánh giá chất lượng* để phục vụ bảo trì hạ tầng — một chiều thông tin có thể bổ sung cho ngữ cảnh lái xe trong tương lai (xem Chương 5).

### 2.2. Nhận diện biển báo giao thông

Bài toán nhận diện biển báo giao thông thường được chia thành hai bài toán con: phát hiện (detection — định vị bounding box) và phân loại (classification — gán nhãn lớp). Các mô hình CNN phân loại như **ResNet-50** đạt độ chính xác rất cao (tới 99% theo các báo cáo trên tập dữ liệu biển báo chuẩn), trong khi họ mô hình **YOLO** (You Only Look Once, từ YOLOv3 đến YOLOv8/v11) tối ưu cho việc cân bằng giữa tốc độ suy luận và độ chính xác, phù hợp với ràng buộc thời gian thực của ADAS. Bài báo tham khảo chính của đề tài — Sah và cộng sự, *"Advancing Autonomous Vehicle Intelligence: Deep Learning and Multimodal LLM for Traffic Sign Recognition and Robust Lane Detection"* (arXiv:2503.06313, 2025) — báo cáo ResNet-50 đạt 99.8% trên bài toán nhận diện biển báo và so sánh thêm với YOLOv8, RT-DETR; đây cũng là bài báo có định hướng gần nhất với đề tài này (kết hợp nhận diện biển báo + phát hiện làn đường + LLM đa phương thức), được dùng làm mốc so sánh chính xuyên suốt luận văn.

Một thách thức thực tế mà quá trình cài đặt hệ thống của luận văn này bộc lộ (xem mục 3.2.2) là bảng ánh xạ *class ID → tên lớp* phải luôn được đọc trực tiếp từ trọng số mô hình đã huấn luyện, không được hard-code trong mã nguồn xử lý — nếu không, một thay đổi nhỏ trong thứ tự lớp lúc huấn luyện lại (ví dụ đổi bộ dữ liệu, thêm/bớt lớp biển báo Việt Nam) sẽ khiến toàn bộ hệ thống phía sau gán nhầm tên biển báo mà không có bất kỳ lỗi runtime nào cảnh báo.

### 2.3. Mô hình ngôn ngữ lớn (LLM) và suy luận đa phương thức

**Cơ chế Attention.** Nền tảng của các LLM hiện đại là kiến trúc Transformer, với cơ chế self-attention cho phép mô hình gán trọng số động cho từng phần tử trong chuỗi đầu vào khi biểu diễn một phần tử khác:

$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V$$

trong đó $Q$ (query), $K$ (key), $V$ (value) là các phép chiếu tuyến tính của biểu diễn đầu vào, $d_k$ là chiều của vector key (dùng để chuẩn hóa, tránh tích $QK^{\top}$ có phương sai quá lớn khi $d_k$ lớn). Trong bối cảnh của luận văn, cơ chế này giải thích vì sao LLM có thể "chú ý" đồng thời tới nhiều trường dữ liệu khác nhau trong một prompt dài (loại đường, vị trí ego-lane, biển báo, khuyến nghị rule-based) khi sinh câu trả lời — nhưng cũng lý giải vì sao mô hình dễ bị chi phối bởi các phần thông tin không liên quan hoặc bị "lạc hướng" nếu prompt quá dài, đặc biệt với các mô hình nhỏ.

**Suy luận có cấu trúc (structured reasoning).** Bên cạnh việc sinh câu trả lời trực tiếp (zero-shot), các chiến lược prompt như chuỗi suy nghĩ (Chain-of-Thought) và các biến thể có cấu trúc cây/đồ thị đã được chứng minh giúp LLM suy luận chính xác và nhất quán hơn với các bài toán nhiều bước. Zhang và cộng sự (*"RATT: A Thought Structure for Coherent and Correct LLM Reasoning"*, AAAI 2025) đề xuất kết hợp khả năng lập kế hoạch/nhìn trước (planning and lookahead) với việc kiểm chứng sự kiện qua truy hồi (retrieval-augmented fact-checking) ngay tại mỗi bước suy luận, nhằm cân bằng giữa tính đúng đắn thực tế và tính tối ưu logic — một hướng tiếp cận có thể áp dụng để mở rộng mô-đun suy luận rule-based hiện tại của hệ thống (mục 3.4) thành một chuỗi suy luận nhiều bước có kiểm chứng.

**LLM đa phương thức (multimodal LLM/VLM).** Khi đầu vào không chỉ là văn bản mà còn gồm ảnh (vision-language model), mô hình cần một tầng mã hóa thị giác (vision encoder) chiếu đặc trưng ảnh vào cùng không gian embedding với văn bản trước khi đưa vào Transformer decoder. Bài báo tham khảo chính (Sah và cộng sự, 2025) giới thiệu một khung đa phương thức nhẹ, sử dụng instruction tuning mà không cần giai đoạn tiền huấn luyện (pretraining) riêng, để kết hợp trực tiếp thông tin thị giác với suy luận ngôn ngữ. Đây chính là nguyên lý mà mô-đun `llm_batch_client.py` của hệ thống (mục 3.4) khai thác ở chế độ `image_json`: gửi đồng thời ảnh gốc và biểu diễn JSON có cấu trúc trong cùng một request tới một mô hình VLM thương mại.

Ở một hướng gần với bài toán của luận văn hơn, một chương sách năm 2025/2026 (Lecture Notes in Computer Science, DOI 10.1007/978-3-032-05179-0_15) trình bày một khung đa phương thức thực hiện dự đoán quỹ đạo có nhận biết bối cảnh cảnh lái xe (driving-scene-context-aware trajectory prediction) kèm giải thích có nhận biết rủi ro (risk-aware explanation), tích hợp trạng thái đối tượng theo thời gian (quỹ đạo, vận tốc, góc yaw) với thông tin ngữ nghĩa từ camera phía trước — một minh chứng cho thấy hướng "kết hợp dữ liệu hình học có cấu trúc với suy luận ngôn ngữ có giải thích" mà luận văn theo đuổi đang là một hướng nghiên cứu đang tích cực phát triển, không chỉ giới hạn ở bài toán biển báo/làn đường.

Ở phạm vi rộng hơn, Ferrag và cộng sự (*"From LLM Reasoning to Autonomous AI Agents: A Comprehensive Review"*, arXiv:2504.19678, 2025) tổng hợp các khung tác nhân AI (2023–2025) tích hợp LLM với bộ công cụ module để ra quyết định tự trị — cung cấp bối cảnh cho việc mô-đun suy luận rule-based (`RecommendationEngine`) trong hệ thống hiện tại có thể tiến hoá thành một tác nhân (agent) thực thụ, có khả năng gọi công cụ và tự kiểm chứng, thay vì chỉ sinh văn bản một lượt như hiện nay.

### 2.4. Tổng quan các nghiên cứu liên quan và khoảng trống nghiên cứu

Bảng 2.1 tổng hợp các hướng tiếp cận liên quan, đối chiếu điểm mạnh và giới hạn của từng hướng so với mục tiêu của luận văn.

**[GỢI Ý THÊM BẢNG 2.1]** Bảng so sánh các hướng tiếp cận liên quan:

| Hướng tiếp cận | Đại diện | Điểm mạnh | Giới hạn so với mục tiêu luận văn |
|---|---|---|---|
| Phát hiện làn đường theo phân đoạn pixel | SCNN | Chính xác theo ngữ cảnh không gian rộng | Chi phí tính toán cao, không tự sinh ngữ nghĩa lái xe |
| Phát hiện làn đường theo anchor lai | Ultra-Fast-Lane-Detection-v2 (Qin và cộng sự, 2022) | Nhanh, chính xác, phù hợp thời gian thực | Chỉ dừng ở tọa độ điểm, cần tầng diễn giải riêng |
| Nhận diện biển báo bằng CNN/YOLO | ResNet-50, YOLOv8/v11 | Độ chính xác rất cao (~99%) trên bộ dữ liệu chuẩn | Không đảm bảo khi bộ dữ liệu chuẩn không khớp phân bố biển báo Việt Nam |
| LLM suy luận lái xe theo quỹ đạo/văn bản | DiLu, DriveGPT4, GPT-Driver | Suy luận ngôn ngữ tự nhiên, có giải thích | Thiếu khả năng tiếp cận hình học không gian tường minh |
| Dự đoán hành vi lái xe bằng biểu diễn ngữ nghĩa dạng raster | Rules of the Road (Hong và cộng sự, CVPR 2019) | Biểu diễn cảnh có cấu trúc, không cần LLM | Không sinh giải thích ngôn ngữ tự nhiên |
| Hiểu cảnh giao thông hợp nhất | SafeRoute (Shaw và cộng sự, ICCV 2025 Workshop) | Hợp nhất nhiều tác vụ hiểu cảnh trong một khung học sâu | Đang ở giai đoạn workshop, chưa tập trung vào tầng suy luận LLM có giải thích |
| Đa phương thức thị giác + LLM cho biển báo/làn đường | Sah và cộng sự, arXiv:2503.06313 (2025) | Gần nhất với đề tài: kết hợp cả 3 thành phần | Không công bố một biểu diễn trung gian JSON tường minh giữa nhận thức và LLM |

Từ Bảng 2.1, khoảng trống nghiên cứu được xác định lại rõ ràng: các hướng tiếp cận nhận thức (hàng 1–3) dừng lại ở đầu ra hình học/nhãn lớp; các hướng tiếp cận suy luận (hàng 4, 6) không được cấp một biểu diễn không gian tường minh; hướng gần nhất (hàng 7) chưa công bố cơ chế ánh xạ trung gian. Luận văn định vị đóng góp của mình chính tại **tầng ánh xạ trung gian** ($f_{\text{semantic}}$ ở mục 1.5) — nơi mà theo khảo sát trên, chưa có công trình nào công bố một đặc tả tường minh và đã được kiểm chứng thực nghiệm.

---

## CHƯƠNG 3: PHƯƠNG PHÁP VÀ KIẾN TRÚC HỆ THỐNG ĐỀ XUẤT

Toàn bộ nội dung chương này mô tả **hệ thống đã được cài đặt và chạy được** trong thư mục `src-v2/` của mã nguồn đề tài (phiên bản hiện hành trên nhánh `v2`), không phải một thiết kế lý thuyết. Phiên bản trước đó (`src/`) được giữ lại trong mã nguồn như một mốc so sánh: nó minh họa chính xác vấn đề nêu ở mục 1.2 (lane thật + sign thật nhưng không cùng một lần chạy trên cùng một ảnh).

### 3.1. Tổng quan kiến trúc hệ thống

Lớp điều phối trung tâm là `TrafficScenePipeline` (`pipeline.py`), nhận một ảnh dashcam (BGR, đọc bằng OpenCV) và tốc độ xe hiện tại (tuỳ chọn), thực hiện tuần tự:

```
Ảnh dashcam (BGR)
  → LaneDetector.detect(image)                     [perception/lane_detector.py]
  → SignDetector.detect(image, W, H)                [perception/sign_detector.py]
  → SceneBuilder.build(lanes, signs, W, H, speed)   [analysis/scene_builder.py]
      → LaneAnalyzer.analyze(...)                   [analysis/lane_analyzer.py]
      → RoadTypeAnalyzer.infer(...)                 [analysis/road_type.py]
      → SignRuleInterpreter.interpret(...)           [reasoning/recommendation.py]
      → RecommendationEngine.generate(...)           [reasoning/recommendation.py]
  → TrafficScene (đối tượng JSON có cấu trúc)
  → PromptBuilder.build_scene_prompt(scene)          [reasoning/prompt_builder.py]
  → (batch, ngoại tuyến) llm_batch_client.py gọi LLM đa phương thức qua API
```

Điểm khác biệt cốt lõi so với `src/main.py` cũ: `lane` và `sign` **luôn được phát hiện trên cùng một ảnh trong cùng một lần gọi `process()`** — loại bỏ hoàn toàn khả năng ghép lane thật với sign thật nhưng lane giả lập, vốn là nguyên nhân khiến khuyến nghị lái xe trước đây không phản ánh đúng làn đường thật.

**[GỢI Ý THÊM HÌNH 3.1]** Sơ đồ khối chi tiết theo đúng luồng gọi hàm nêu trên, đặt các tên class/module thật (`LaneDetector`, `SignDetector`, `SceneBuilder`, `LaneAnalyzer`, `RoadTypeAnalyzer`, `SignRuleInterpreter`, `RecommendationEngine`, `PromptBuilder`) tại từng khối để hình vẽ tra cứu trực tiếp được với mã nguồn.

Toàn bộ tham số cấu hình (đường dẫn model, ngưỡng confidence, loại môi trường đô thị/cao tốc) được tập trung tại `configs/config.yaml`, tránh tình trạng hard-code rải rác từng gây ra lệch tên file model so với bản cũ.

### 3.2. Mô-đun nhận diện (Perception Module)

#### 3.2.1. Phát hiện vạch kẻ đường

Bộ phát hiện làn đường (`perception/lane_detector.py`, lớp `LaneDetector`) là một wrapper cho kiến trúc `parsingNet` của Ultra-Fast-Lane-Detection-v2 (mục 2.1), hỗ trợ 2 bộ dữ liệu huấn luyện (`culane`, `tusimple`) × 2 backbone (`ResNet-18`, `ResNet-34`), tham số hóa qua bảng `_DATASET_PRESETS`. Cấu hình đang sử dụng trong `configs/config.yaml` là **`tusimple_res34.pth`** (`lane_dataset: tusimple`, `lane_backbone: 34`).

Quy trình suy luận gồm 3 bước:

1. **Tiền xử lý:** ảnh gốc được resize giữ tỉ lệ rồi crop về đúng kích thước huấn luyện (`train_width × train_height`, ví dụ 800×320 với Tusimple, tỉ lệ crop 0.8), sau đó chuẩn hóa thành tensor.
2. **Suy luận:** mô hình `parsingNet` trả về 4 tensor xác suất: `loc_row`, `loc_col` (phân bố theo ô lưới) và `exist_row`, `exist_col` (làn có tồn tại tại hàng/cột anchor đó hay không).
3. **Giải mã (decode):** mỗi làn được biểu diễn theo **anchor lai** — 2 làn giữa (index 1, 2) dùng row-anchor (quét theo hàng, trả về hoành độ $x$ tại mỗi tung độ $y$ cố định), 2 làn ngoài (index 0, 3) dùng col-anchor (quét theo cột). Tọa độ mỗi điểm không lấy trực tiếp ô có xác suất cao nhất (argmax) mà lấy **kỳ vọng có trọng số (soft-argmax)** trên các ô lân cận:

$$\hat{p} = \sum_{k \in \mathcal{N}(\text{argmax})} k \cdot \text{softmax}(z)_k + 0.5$$

trong đó $z$ là vector logit của các ô trong lân cận $\mathcal{N}$ quanh ô có xác suất cao nhất, giúp tọa độ ra mượt hơn thay vì "nhảy bậc" theo từng ô lưới rời rạc. Toạ độ pixel cuối cùng được quy đổi theo **đúng kích thước ảnh gốc truyền vào `detect()`**, không hard-code kích thước ảnh huấn luyện — đây là điểm khác biệt so với `demo.py` gốc của Ultra-Fast-Lane-Detection-v2 (vốn hard-code 1640×590 của CULane), cần thiết vì hệ thống hướng tới ảnh dashcam có độ phân giải khác.

Ngưỡng "làn có tồn tại": với row-anchor, một làn chỉ được giữ lại nếu hơn một nửa số hàng anchor báo `exist_row = 1`; với col-anchor, ngưỡng nới hơn (một phần tư số cột anchor) do đặc tính hình học của làn nghiêng mạnh xuất hiện trong ít cột hơn.

#### 3.2.2. Phát hiện biển báo giao thông

Bộ phát hiện biển báo (`perception/sign_detector.py`, lớp `SignDetector`) là wrapper cho YOLOv8 (thư viện `ultralytics`), sử dụng trọng số đã huấn luyện tại `model/yolov8n_trained_best.pt` (cấu hình trong `sign_model_path`), gồm **15 lớp**: `Green Light`, `Red Light`, `Speed Limit {10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120}`, `Stop`.

Một nguyên tắc thiết kế quan trọng được áp dụng: bảng ánh xạ *class ID → tên lớp* được đọc **trực tiếp từ `model.names`** của file trọng số tại thời điểm chạy, không hard-code trong mã nguồn (đúng như phân tích ở mục 2.2) — đảm bảo tên biển báo luôn khớp với đúng mô hình đang chạy kể cả khi thay sang một bộ trọng số khác (ví dụ mô hình 94 lớp theo bộ biển báo Việt Nam trong tương lai). Tên lớp thô sau đó được chuẩn hoá về `sign_type` ngữ nghĩa (ví dụ `"Speed Limit 50"` → `speed_limit_50`) bằng hàm `normalize_sign_type()`, dùng biểu thức chính quy (regex) thay vì so khớp chuỗi cứng, để không bị vỡ khi đổi mô hình có quy ước đặt tên hơi khác.

Với mỗi biển báo phát hiện được (đối tượng `DetectedSign`), hệ thống suy ra thêm 2 thuộc tính ngữ cảnh từ hình học bounding box $(x_1, y_1, x_2, y_2)$:

- **Vị trí tương đối** (trái/giữa/phải khung hình), dựa trên hoành độ tâm bounding box so với $0.33 W$ và $0.66 W$ ($W$ = chiều rộng ảnh).
- **Khoảng cách ước lượng** (gần/trung bình/xa): biển báo càng gần camera thì bounding box càng lớn và càng nằm thấp trong khung hình — hệ thống dùng ngưỡng kết hợp giữa tung độ trung bình và diện tích bounding box để phân loại `near`/`medium`/`far`.

### 3.3. Mô-đun phân tích làn đường và xây dựng biểu diễn cảnh (Scene Representation)

Đây là tầng $f_{\text{semantic}}$ (mục 1.5) — nơi luận văn tập trung đóng góp chính. Mô-đun `analysis/lane_analyzer.py` (lớp `LaneAnalyzer`) thực hiện phân tích **theo hướng lấy xe làm gốc (ego-centric)**, dựa trên tô-pô các làn (không dựa vào vị trí tuyệt đối trên ảnh), qua 4 bước.

**Bước 1 — Sắp xếp làn theo trục hoành thực tế.** Với mỗi làn, hoành độ tham chiếu $x_{\text{ref}}$ được lấy tại tung độ $y_{\text{ref}} = 0.95 \times H$ (gần đáy ảnh, nơi camera dashcam "nhìn thấy" đầu xe), bằng nội suy trung bình các điểm lân cận $y_{\text{ref}}$; nếu làn không có điểm nào gần $y_{\text{ref}}$ (bị che khuất hoặc kết thúc sớm), hệ thống **ngoại suy tuyến tính** qua các điểm sẵn có của chính làn đó thay vì gán $x_{\text{ref}} = +\infty$ như cách làm trước đây — cách làm cũ khiến làn bị che luôn bị xếp nhầm về tận cùng bên phải bất kể vị trí thực tế.

**Bước 2 — Xác định ego-lane.** Với $n$ làn đã sắp xếp trái→phải, có $(n-1)$ cặp làn kề nhau khả dĩ. Mỗi cặp $(i, i+1)$ được chấm điểm theo khoảng cách từ tâm cặp làn tới tâm xe $x_{\text{vehicle}} = W/2$:

$$\text{score}(i) = \big|\,c_i - x_{\text{vehicle}}\,\big| \times \begin{cases} 0.5 & \text{nếu } x_{\text{vehicle}} \text{ nằm giữa 2 vạch} \\ 1.0 & \text{ngược lại} \end{cases} \times \Big(1 + 0.2 \cdot \frac{|w_i - w_{\text{expected}}|}{w_{\text{expected}}}\Big)$$

với $c_i = (x_i + x_{i+1})/2$ là tâm cặp làn, $w_i = x_{i+1} - x_i$ là bề rộng cặp làn, $w_{\text{expected}} = 0.15 W$ là bề rộng làn "điển hình". Cặp có điểm số thấp nhất được chọn làm ego-lane. Độ tin cậy được gán theo khoảng cách $|c_{\text{best}} - x_{\text{vehicle}}|$ (4 mức: 0.95/0.8/0.6/0.4).

**Bước 3 — Độ lệch xe so với tâm làn:**

$$\delta_{\text{px}} = x_{\text{vehicle}} - c_{\text{ego}}, \qquad \delta_{\%} = \frac{\delta_{\text{px}}}{w_{\text{ego}}} \times 100$$

Quy ước: $\delta_{\text{px}} > 0$ nghĩa là tâm làn nằm bên trái tâm xe, tức xe đang lệch **phải**; $|\delta_{\text{px}}| < 10$ px được coi là "đã căn giữa" (`centered`).

**Bước 4 — Độ cong đường (curvature), dựa trên vanishing point.** Với mỗi làn, hệ thống fit đa thức bậc 1 và bậc 2 qua các điểm $(y_{\text{norm}}, x)$ (tung độ đã chuẩn hóa $[0,1]$ theo khoảng quan sát được của chính làn đó):

$$\text{MSE}_{\text{linear}} = \frac{1}{k}\sum_{j=1}^{k}\big(x_j - \hat{x}^{(1)}_j\big)^2, \qquad \text{MSE}_{\text{quad}} = \frac{1}{k}\sum_{j=1}^{k}\big(x_j - \hat{x}^{(2)}_j\big)^2$$

Điểm hội tụ phối cảnh (vanishing point) được ngoại suy bằng đúng fit bậc 1 tại một **mốc chân trời chung** $y_{\text{horizon}} = 0.3H$ cho mọi làn (không phải tại đỉnh riêng của từng làn) — vì phép chiếu phối cảnh khiến các làn thẳng song song chỉ thực sự hội tụ khi được so sánh tại cùng một độ sâu ảnh; so sánh tại các độ sâu khác nhau sẽ thổi phồng sai độ phân tán vanishing point dù đường thực sự thẳng. Hai chỉ số được dùng để phân loại độ cong:

$$\text{drift\_ratio} = \frac{\sqrt{\text{MSE}_{\text{linear}}}}{W}, \qquad \text{fit\_improvement} = \max\!\Big(0,\ \frac{\text{MSE}_{\text{linear}} - \text{MSE}_{\text{quad}}}{\text{MSE}_{\text{linear}}}\Big)$$

`drift_ratio` đo độ lệch tuyệt đối (đã chuẩn hóa theo chiều rộng ảnh) so với một đường thẳng; `fit_improvement` đo mức cải thiện *tương đối* khi cho phép mô hình cong bậc 2, dùng để bắt các trường hợp cong thật nhưng rất nhẹ (near-field) mà `drift_ratio` không đủ nhạy để phát hiện — chỉ tin tín hiệu này khi $\text{MSE}_{\text{linear}} > 4$ và làn có $\geq 10$ điểm, để tránh nhầm với hiện tượng overfit của bậc tự do dư ra khi có ít điểm.

Kết quả tổng hợp từ mọi làn (`avg_drift`, `avg_fit_improvement`) được phân loại theo 2 ngưỡng đã **hiệu chỉnh lại bằng số liệu thực đo** trên 200 ảnh Tusimple + 199 ảnh CULane (xem mục 4.3 để biết chi tiết quá trình hiệu chỉnh và tác động của nó):

| Ngưỡng | Giá trị | Căn cứ hiệu chỉnh |
|---|---|---|
| `DRIFT_THRESHOLD_STRAIGHT` | 0.02 | Trên bách phân vị 95 (p95) của `avg_drift` đo được trên ảnh "thẳng" ở cả 2 bộ dữ liệu (~0.014) |
| `DRIFT_THRESHOLD_SHARP` | 0.06 | Dưới giá trị `avg_drift` của 1 ảnh cua gắt đã xác nhận đúng bằng mắt (0.0994) |
| `FIT_IMPROVEMENT_THRESHOLD_CURVE` | 0.3 | Cao hơn hẳn mức cải thiện "giả" do overfit thường gặp (~15%) với dữ liệu ≥10 điểm |

Chỉ số `vanishing_point_spread` (độ phân tán điểm hội tụ giữa các làn) được tính và lưu vào JSON để tham khảo/debug nhưng **không** được dùng làm căn cứ phân loại, vì độ lớn tuyệt đối theo pixel không so sánh được xuyên bộ dữ liệu (trung vị của CULane lớn hơn Tusimple khoảng 10 lần dù cả hai chủ yếu là đường thẳng).

**Ngữ nghĩa từng làn.** Mỗi làn được gán một trong các loại `ego` (2 vạch biên ego-lane), `neighbor` (làn lân cận có thể đi được), `shoulder` (vạch mép ngoài cùng, không xem là đi được), dựa trên **chỉ số sau khi sắp xếp** (`sorted_index`), không dùng chỉ số gốc do mô hình trả về — vì mô hình phát hiện làn không đảm bảo trả kết quả theo đúng thứ tự trái→phải trên ảnh.

**Loại đường và môi trường đường** (`analysis/road_type.py`, lớp `RoadTypeAnalyzer`) tái sử dụng trực tiếp kết quả phân loại độ cong ở trên (không tính lại), kết hợp với hình học tổng thể (độ phủ ảnh của các làn `coverage_ratio = \text{spread}_{\text{bottom}}/W$, mức hội tụ `convergence_ratio`) để suy ra môi trường đường: `narrow_road`, `highway`, `rural_road`, `urban_multi_lane`, `urban_marketplace` — dựa trên số làn quan sát được và độ phủ ảnh.

**Ví dụ biểu diễn JSON đầu ra** (rút gọn từ `output-v2/1.json` — ảnh `1.jpg` của tập CULane-199, kích thước 1640×590):

```json
{
  "road": {
    "road_type": "straight",
    "road_environment": "urban_marketplace",
    "curvature_magnitude": 0.0022,
    "geometry": { "lane_count": 4, "geometry_type": "multi_lane" }
  },
  "lane": {
    "ego_lane": {
      "left_boundary_index": 0, "right_boundary_index": 1,
      "ego_lane_center_x": 722.64, "lane_width": 503.29,
      "confidence": 0.95, "reason": "best_adjacent_pair"
    },
    "vehicle_offset": {
      "offset_pixels": 97.36, "offset_ratio_percent": 19.34,
      "direction": "right_of_lane_center",
      "is_vehicle_between_boundaries": true
    },
    "curvature": { "classification": "straight", "confidence": 0.90 }
  },
  "traffic_signs": { "detected": [], "count": 0 },
  "traffic_situation": { "active_speed_limit": 50, "urgent_action_required": false },
  "recommendation": {
    "action": "maintain_lane", "confidence": 0.6,
    "reasoning": "Không có biển báo khẩn cấp, đường và làn hiện tại ổn định."
  }
}
```

Có thể đọc trực tiếp từ ví dụ trên: xe đang lệch phải 19.34% bề rộng làn (503 px) trên một đoạn đường thẳng 4 làn tại khu vực đô thị đông đúc (`urban_marketplace`), không có biển báo, giới hạn tốc độ mặc định 50 km/h (khu vực đô thị) — đúng là loại thông tin có cấu trúc, sẵn sàng cho LLM suy luận, mà một danh sách tọa độ điểm thô không thể cung cấp trực tiếp.

### 3.4. Mô-đun suy luận và hỗ trợ quyết định (LLM Reasoning Module)

Mô-đun suy luận gồm hai lớp bổ trợ nhau: một lớp **rule-based** chạy cục bộ, tức thời (không gọi LLM), và một lớp **LLM đa phương thức** dùng để sinh khuyến nghị có giải thích bằng ngôn ngữ tự nhiên.

#### 3.4.1. Diễn giải biển báo và khuyến nghị rule-based

`reasoning/recommendation.py` gồm 2 lớp:

- **`SignRuleInterpreter`** chuyển danh sách `DetectedSign` thành `TrafficSituation` — tập luật giao thông áp dụng, có độ ưu tiên (số càng nhỏ càng khẩn cấp: STOP/cấm vào = 1–2, đèn đỏ = 3, nhường đường/đèn vàng = 10, giới hạn tốc độ = 20, đèn xanh = 50). Với biển giới hạn tốc độ, hành động khuyến nghị (`SLOW_DOWN`/`MAINTAIN_SPEED`/`SPEED_UP`) được quyết định bằng cách **so sánh trực tiếp tốc độ hiện tại của xe với giá trị ghi trên biển báo** — đây là điểm đã được sửa so với phiên bản trước, vốn chỉ dựa vào độ tin cậy nhận diện của YOLO (một biển "tốc độ tối đa 30" với độ tin cậy nhận diện > 85% từng bị diễn giải thành "tăng tốc" bất kể xe đang chạy bao nhiêu).
- **`RecommendationEngine`** tổng hợp toàn bộ `TrafficScene` thành một `Recommendation` cuối cùng, theo thứ tự ưu tiên: biển báo khẩn cấp (STOP/đèn đỏ) → điều chỉnh tốc độ theo biển báo → vị trí trong làn (nếu $|\delta_{\text{px}}| > 100$, đề xuất chỉnh nhẹ vị trí xe).

Khuyến nghị rule-based này **không phải là sản phẩm cuối cùng thay thế LLM**, mà được nhúng vào chính prompt gửi cho LLM như một gợi ý tham khảo ("for reference, you may agree or refine it") — LLM có thể đồng ý, tinh chỉnh hoặc phản biện lại dựa trên toàn bộ ngữ cảnh JSON + ảnh.

#### 3.4.2. Sinh prompt và giao tiếp với LLM

`reasoning/prompt_builder.py` (lớp `PromptBuilder`) chuyển một `TrafficScene` thành đoạn văn bản ngữ cảnh súc tích (loại đường, ego-lane, độ lệch xe, biển báo, khuyến nghị rule-based), rồi ghép với một trong 4 chiến lược prompt (`PromptStrategy`): `ZERO_SHOT`, `CHAIN_OF_THOUGHT` (suy luận từng bước: trạng thái làn/đường → vị trí xe → hình học đường phía trước → luật cần tuân thủ → rủi ro và khuyến nghị), `EXPLAINABLE` (yêu cầu nêu rõ quan sát – suy luận – mức độ tin cậy), `SAFETY_FOCUSED` (ưu tiên giữ làn và tuân thủ biển báo khi không chắc chắn). Mô-đun này được thiết kế hướng tới một mô hình nhỏ chạy on-device (Phi-3-mini, 3.8B tham số) — vì vậy system prompt được giữ ngắn gọn thay vì nhiều đoạn văn dài, do các mô hình nhỏ dễ "lạc hướng" khỏi chỉ dẫn với prompt dài (liên hệ trực tiếp tới cơ chế attention ở mục 2.3).

**Client gọi LLM thực tế dùng cho thực nghiệm** (`llm_batch_client.py`) khác với mục tiêu thiết kế "on-device" nêu trên: đây là một client gọi hàng loạt (batch) tới **NVIDIA NIM** (`https://integrate.api.nvidia.com/v1`, mô hình `nvidia/llama-3.1-nemotron-nano-vl-8b-v1`) — một API đám mây, không chạy cục bộ. Client hỗ trợ 3 chế độ đầu vào, cho phép so sánh vai trò của từng nguồn thông tin:

| Chế độ | Đầu vào gửi LLM | Mục đích |
|---|---|---|
| `image_only` | Chỉ ảnh gốc + prompt | Đánh giá khả năng suy luận thuần thị giác, không có dữ liệu hình học |
| `json_only` | Chỉ prompt có nhúng JSON | Đánh giá khả năng suy luận thuần từ biểu diễn có cấu trúc, không "nhìn thấy" ảnh |
| `image_json` | Cả ảnh gốc và prompt có nhúng JSON | Chế độ chính dùng cho thực nghiệm (mục 4.5); JSON được coi là nguồn thông tin có độ tin cậy ưu tiên khi mâu thuẫn với ảnh |

Ảnh được nén/resize lặp lại (giảm chất lượng JPEG rồi giảm kích thước) cho tới khi dung lượng base64 nằm dưới ngưỡng cấu hình (mặc định 150 KB) trước khi nhúng vào request dạng data URI, do giới hạn kích thước ảnh inline của API. Prompt yêu cầu mô hình trả lời theo cấu trúc cố định 3 phần — **Situation Assessment / Driving Recommendation / Safety Considerations** — và ràng buộc rõ: chỉ được suy luận dựa trên thông tin được cung cấp, không giả định các đối tượng/biển báo/điều kiện đường không được quan sát hoặc mô tả rõ ràng. Kết quả mỗi lượt gọi được lưu ra file `.txt`, kèm một `_summary.json` tổng hợp toàn batch (số lượng thành công/thất bại, tổng thời gian).

**[GỢI Ý THÊM HÌNH 3.2]** Sơ đồ chi tiết mô-đun suy luận, tách rõ 2 nhánh: (a) `RecommendationEngine` rule-based cục bộ, tức thời; (b) `llm_batch_client.py` gọi LLM đa phương thức qua API đám mây, nhận cả ảnh và JSON làm đầu vào — nhấn mạnh nhánh (b) là nơi khuyến nghị rule-based từ nhánh (a) được nhúng vào prompt làm ngữ cảnh tham khảo.

---

## CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ

### 4.1. Thiết lập thực nghiệm

**Phần cứng/phần mềm.** Toàn bộ thực nghiệm chạy trên CPU (`device: cpu` trong `configs/config.yaml`), dùng PyTorch ≥ 2.0, `ultralytics` ≥ 8.4 cho YOLOv8, OpenCV ≥ 4.9 cho tiền xử lý ảnh (xem `src-v2/requirements.txt`).

**Dữ liệu.** Ba lô thực nghiệm được sử dụng, chạy qua `batch_process.py`:

| Lô | Số ảnh | Model làn đường | Độ phân giải ảnh | Thư mục kết quả |
|---|---|---|---|---|
| CULane (trước hiệu chỉnh ngưỡng) | 199 | `culane_res34.pth` (khớp bộ dữ liệu) | 1640×590 | `output/` |
| CULane (sau hiệu chỉnh ngưỡng) | 199 (cùng ảnh) | `culane_res34.pth` | 1640×590 | `output-v2/` |
| Tusimple | 200 | `tusimple_res34.pth` (khớp bộ dữ liệu) | ảnh gốc Tusimple | `output-v2-tusimple/` |

Hai lô CULane dùng **chính xác cùng 199 ảnh đầu vào**, chỉ khác nhau ở phiên bản ngưỡng phân loại độ cong trong `LaneAnalyzer` (mục 3.3) — đây là một thí nghiệm đối chứng trước/sau (ablation) tự nhiên, được khai thác ở mục 4.2.2. Model làn đường dùng cho từng lô luôn được khớp đúng với bộ dữ liệu tương ứng (xác nhận qua lịch sử thay đổi `configs/config.yaml` và độ phân giải ảnh gốc), tránh sai lệch do dùng nhầm checkpoint.

**Chỉ số đánh giá.** Với các bài toán phát hiện đối tượng (làn đường, biển báo), hai chỉ số phổ biến trong tài liệu tham khảo (Chương 2) là:

$$\text{Precision} = \frac{TP}{TP+FP}, \quad \text{Recall} = \frac{TP}{TP+FN}, \quad F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision}+\text{Recall}}$$

$$\text{IoU}(\hat{B}, B) = \frac{\text{area}(\hat{B}\cap B)}{\text{area}(\hat{B}\cup B)}, \qquad \text{AP} = \int_0^1 p(r)\,dr, \qquad \text{mAP} = \frac{1}{C}\sum_{c=1}^{C}\text{AP}_c$$

trong đó $TP/FP/FN$ được xác định qua ngưỡng IoU giữa dự đoán $\hat{B}$ và nhãn thật $B$, $p(r)$ là đường cong precision–recall, $C$ là số lớp. **Đây là các chỉ số chuẩn được các công trình ở Chương 2 báo cáo** (ví dụ ResNet-50 ~99%/99.8% cho phân loại biển báo, LaneNet 96.4% trên Tusimple). Tuy nhiên, việc tính `mAP`/`F1` cho chính hệ thống của luận văn đòi hỏi nhãn ground-truth ở mức pixel/bounding-box khớp với 15 lớp biển báo và với từng làn đường trên đúng 399 ảnh thực nghiệm — nhãn này **chưa có sẵn** cho tập ảnh CULane/Tusimple đã dùng (các nhãn `.lines.txt` gốc của CULane/Tusimple mô tả làn đường nhưng không có nhãn biển báo kiểu Việt Nam). Do đó, đánh giá định lượng trong chương này dùng **một khung đánh giá thủ công theo rubric** (mục 4.2.1) do người đánh giá cho điểm trực tiếp trên ảnh, và các thống kê hành vi hệ thống rút ra từ `_summary.json` của từng lô batch — việc xây dựng một tập nhãn box-level cho biển báo Việt Nam để tính `mAP`/`F1` chính thức được đưa vào hướng phát triển (Chương 5).

### 4.2. Kết quả nhận diện vạch kẻ đường và phân tích làn

#### 4.2.1. Đánh giá thủ công theo rubric (109 ảnh)

Một tập con 109/127 ảnh (từ lô CULane, sau hiệu chỉnh ngưỡng) được một người đánh giá chấm điểm thủ công theo thang **0 (sai) / 1 (một phần đúng) / 2 (đúng)** cho từng thành phần đầu ra, lưu tại `result_review_version_1.xlsx`. Kết quả:

| Thành phần | Điểm trung bình /2 | Tỉ lệ | Phân phối (0 / 1 / 2) |
|---|---|---|---|
| Làn đường phát hiện (Lane) | 1.68 | 84.0% | 6 / 23 / 80 |
| Loại đường / độ cong (Road) | 0.86 | **43.1%** | 26 / 72 / 11 |
| Xác định ego-lane (Ego) | 1.85 | 92.7% | 5 / 6 / 98 |
| Độ lệch xe (Offset) | 1.76 | 88.1% | 8 / 10 / 91 |
| Phân loại làn lân cận/mép (Lane classification) | 1.45 | 72.5% | 18 / 24 / 67 |

**[GỢI Ý THÊM BIỂU ĐỒ 4.1]** Biểu đồ cột (bar chart) so sánh điểm trung bình/2 của 5 thành phần trên, giúp thấy trực quan khoảng cách giữa Road (0.86) và Ego (1.85).

Kết quả cho thấy các thành phần dựa trực tiếp trên hình học tương đối của xe (ego-lane, độ lệch xe) đạt độ tin cậy cao (88–93%) — phù hợp với kỳ vọng, vì hai đại lượng này chỉ phụ thuộc vào việc xác định đúng *cặp làn kề nhau gần tâm ảnh nhất* (mục 3.3, Bước 2), một bài toán cục bộ, ít nhạy với nhiễu ở xa. Ngược lại, **loại đường/độ cong (Road) là thành phần yếu nhất hệ thống (43.1%)**, dù đã được hiệu chỉnh lại ngưỡng bằng số liệu thực đo (mục 3.3, mục 4.2.2) — cho thấy giới hạn không chỉ nằm ở việc chọn ngưỡng mà còn ở chính tín hiệu đầu vào (độ lệch của làn so với đường thẳng ở khoảng cách quan sát được, vốn dễ nhiễu với làn ngắn/bị che).

**Các dạng lỗi định tính** (ghi chú trên 44/109 = 40.4% ảnh có ghi chú của người đánh giá):

| Ghi chú (nguyên văn) | Số lần | Diễn giải |
|---|---|---|
| Thiếu lane do model | 10 | Mô hình bỏ sót một làn có thể quan sát được bằng mắt |
| Không phát hiện ngược chiều | 9 | Hệ thống không phân biệt làn cùng chiều/ngược chiều |
| Đường khó phát hiện | 8 | Vạch kẻ mờ, thiếu, hoặc điều kiện ảnh khó |
| Không chấm vì xe đằng trước che | 5 | Bỏ qua chấm điểm do bị che khuất hoàn toàn (không phải lỗi hệ thống) |
| Đường 2 chiều | 4 | Ghi chú ngữ cảnh, liên quan tới hạn chế "không phát hiện ngược chiều" |
| Đường rất thẳng | 3 | Ghi chú ngữ cảnh |
| Đường khó phát hiện, không phát hiện đèn giao thông | 2 | Kết hợp lỗi làn đường và biển báo/đèn tín hiệu |
| Cong nhưng phát hiện cong nhẹ / thẳng nhưng phát hiện cong nhẹ | 2 | Lỗi phân loại độ cong còn sót lại sau hiệu chỉnh ngưỡng |

Phát hiện quan trọng nhất từ bảng trên: hệ thống **hiện không có khái niệm "chiều di chuyển"** — `LaneAnalyzer` coi mọi vạch phát hiện được là đối xứng nhau về mặt tô-pô (trái/phải), không phân biệt được làn ngược chiều (thường thấy trên đường 2 chiều không dải phân cách cứng). Đây là một khoảng trống ngữ nghĩa thực sự, không phải lỗi cài đặt, được đưa vào hướng phát triển ở Chương 5.

#### 4.2.2. Thí nghiệm đối chứng: hiệu chỉnh ngưỡng phân loại độ cong

Bảng 4.2 so sánh phân phối `road_type` trên **cùng 199 ảnh CULane**, trước và sau khi hiệu chỉnh ngưỡng `DRIFT_THRESHOLD_STRAIGHT`/`DRIFT_THRESHOLD_SHARP` (mục 3.3) bằng số liệu thực đo:

| `road_type` | Trước hiệu chỉnh (`output/`) | Sau hiệu chỉnh (`output-v2/`) |
|---|---|---|
| `straight` | 9 (4.5%) | **179 (89.9%)** |
| `gentle_curve` | **156 (78.4%)** | 1 (0.5%) |
| `sharp_curve` | 16 (8.0%) | 1 (0.5%) |
| `unknown` (0 làn phát hiện) | 18 (9.0%) | 18 (9.0%) |

**[GỢI Ý THÊM BIỂU ĐỒ 4.2]** Biểu đồ cột kép (trước/sau) minh họa Bảng 4.2 — cho thấy trực quan sự đảo ngược gần như hoàn toàn giữa `straight` và `gentle_curve`.

Trước hiệu chỉnh, ngưỡng `DRIFT_THRESHOLD_STRAIGHT` được đặt theo trực giác (0.1) — lớn hơn hàng trăm lần so với thang giá trị `avg_drift` thực đo được (bách phân vị 95 trên ảnh thẳng chỉ ~0.014), khiến hệ thống hầu như **luôn** phân loại nhầm đường thẳng thành `gentle_curve` (78.4% số ảnh). Sau khi hiệu chỉnh ngưỡng theo đúng thang giá trị đo được trên 399 ảnh của cả hai bộ dữ liệu, tỉ lệ `straight` tăng từ 4.5% lên 89.9% — phù hợp hơn nhiều với thực tế phần lớn ảnh CULane trong tập mẫu là các đoạn đường tương đối thẳng. Số ảnh `unknown` (18, ứng đúng với 18 ảnh có `lane_count = 0`) **không đổi** giữa hai lần chạy — một phép kiểm tra chéo (sanity check) xác nhận rằng thay đổi duy nhất giữa hai lô là ngưỡng phân loại, không phải kết quả phát hiện làn đường. Kết quả này minh chứng bằng số liệu cho luận điểm ở mục 1.2 và câu hỏi nghiên cứu 2 (mục 1.3): hiệu chỉnh ngưỡng dựa trên phân phối thực đo mang lại cải thiện lớn hơn nhiều so với việc chỉ thay đổi mô hình hoặc thuật toán.

Tuy vậy, như đã nêu ở mục 4.2.1, việc hiệu chỉnh ngưỡng không giải quyết triệt để mọi trường hợp (2/109 ảnh review vẫn còn lỗi phân loại độ cong) — điểm số 43.1% của thành phần Road cho thấy đây vẫn là hướng cần tiếp tục cải thiện, có thể bằng cách bổ sung tín hiệu hình học khác (ví dụ ước lượng độ cong trực tiếp từ hệ số bậc 2 đã hiệu chỉnh theo phối cảnh, thay vì chỉ dựa trên `drift_ratio`/`fit_improvement`).

#### 4.2.3. Hiệu năng và tỉ lệ phát hiện

| Lô | Số làn/ảnh trung bình | % ảnh không phát hiện làn nào | Thời gian xử lý trung bình/ảnh (CPU) |
|---|---|---|---|
| CULane (199 ảnh) | — (phân phối: 0 làn: 9.0%, 1 làn: 4.5%, 2 làn: 2.0%, 3 làn: 43.2%, 4 làn: 41.2%) | 9.0% | 0.602 s (trước) / 0.628 s (sau hiệu chỉnh — chênh lệch không đáng kể vì chỉ đổi ngưỡng) |
| Tusimple (200 ảnh) | phân phối: 2 làn: 4.0%, 3 làn: 28.0%, 4 làn: 68.0% | 0.0% | 0.392 s |

Tỉ lệ phát hiện được ít nhất 1 làn trên Tusimple đạt 100% (0/200 ảnh rỗng) so với 91.0% trên CULane (18/199 ảnh rỗng) — phù hợp với ghi nhận định tính ở mục 4.2.1 rằng CULane trong tập mẫu chứa nhiều cảnh đô thị đông đúc, dễ bị che khuất hơn (đúng như phân loại `road_environment = urban_marketplace` xuất hiện trong ví dụ JSON ở mục 3.3). Thời gian xử lý trung bình (0.39–0.63 giây/ảnh, chạy trên CPU, bao gồm cả 2 model + toàn bộ tầng phân tích) **cao hơn đáng kể so với mục tiêu 300–500 ms/khung hình** mà đề xuất ban đầu đặt ra cho toàn bộ pipeline (mục 2.3 của bản đề xuất) — thảo luận thêm ở mục 4.5 và Chương 5.

### 4.3. Kết quả nhận diện biển báo giao thông

| Lô | Ảnh không có biển báo | Ảnh có ≥1 biển báo | Tổng số biển báo phát hiện |
|---|---|---|---|
| CULane (199 ảnh) | 195 (98.0%) | 4 (2.0%) | 5 (3 ảnh × 1 biển, 1 ảnh × 2 biển) |
| Tusimple (200 ảnh) | 198 (99.0%) | 2 (1.0%) | 2 |

Tỉ lệ khung hình có biển báo được phát hiện rất thấp trên cả hai bộ dữ liệu. Trong khung đánh giá thủ công (mục 4.2.1), chỉ 3/109 ảnh có giá trị chấm điểm cho cột "Traffic sign", và cả 3 đều bị chấm 0/2. Cỡ mẫu này quá nhỏ để kết luận về độ chính xác thật của bộ phát hiện biển báo (`yolov8n_trained_best.pt`, 15 lớp) — nguyên nhân nhiều khả năng là CULane và Tusimple vốn là các bộ dữ liệu lái xe cao tốc/đô thị Trung Quốc và Hoa Kỳ, không được xây dựng để có mật độ biển báo cao hoặc khớp đúng 15 lớp biển báo mà mô hình được huấn luyện (bao gồm các mức giới hạn tốc độ và đèn tín hiệu). Kết quả này **không thể dùng để kết luận về hiệu năng của mô-đun nhận diện biển báo trên bối cảnh giao thông Việt Nam** — mục tiêu ban đầu của đề tài (mục tiêu nghiên cứu 1 trong Chương 1). Việc xây dựng và gán nhãn một tập kiểm thử biển báo Việt Nam riêng để tính `mAP`/`F1` (công thức mục 4.1) cho đúng 15 lớp là điều kiện tiên quyết để đánh giá định lượng mô-đun này, được đưa vào Chương 5.

### 4.4. Đánh giá khả năng suy luận của LLM

Lô `output-suggest/` gồm 199 cặp ảnh/JSON (đúng bằng lô CULane sau hiệu chỉnh, `output-v2/`) được gửi tới mô hình đa phương thức thương mại **`nvidia/llama-3.1-nemotron-nano-vl-8b-v1`** qua NVIDIA NIM, ở chế độ `image_json` (mục 3.4.2). Theo `_summary.json`: **199/199 yêu cầu thành công (100%)**, tổng thời gian 1817.48 giây, tương đương **≈ 9.13 giây/yêu cầu** (bao gồm thời gian mã hóa+gửi ảnh, suy luận phía server, và độ trễ mạng). Một lô bổ sung ở chế độ `image_only` (`output-suggest-image-only/`) dừng lại ở 165/200 mục xử lý (không có `_summary.json`, khả năng là một lượt chạy thử/bị gián đoạn) — được dùng để đối chiếu định tính, không đưa vào số liệu định lượng chính của mục này.

**Ví dụ minh họa** (ảnh `1.jpg`, JSON tương ứng đã trình bày ở mục 3.3):

> **Situation Assessment:** *"The scene shows a straight, urban road with a clear sky and moderate traffic. The road has multiple lanes, and there are buildings and greenery on both sides. The traffic signs are not visible..."*
> **Driving Recommendation:** *"Maintain your current lane and continue driving at a safe speed. There are no visible traffic signs or signals that indicate a need for a lane change or speed adjustment."*
> **Safety Considerations:** *(khuyến nghị quan sát xe phía trước, người đi bộ/xe đạp gần khu vực có công trình, tuân thủ giới hạn tốc độ, sẵn sàng dừng nếu cần.)*

Đối chiếu với ảnh gốc và JSON: JSON chỉ chứa thông tin hình học/quy tắc (đường thẳng, 4 làn, ego-lane lệch phải 19.3%, không biển báo, giới hạn tốc độ mặc định 50 km/h) — không có trường nào mô tả bầu trời, tòa nhà, cây xanh hay số lượng xe. Kiểm tra trực tiếp ảnh gốc `1.jpg` xác nhận các chi tiết này (trời quang, các tòa nhà văn phòng bên phải, dải cây xanh/bụi rậm hai bên, 2 xe ô tô con phía xa bên trái) **thực sự có trong ảnh** — tức đây không phải là hiện tượng "ảo giác" (hallucination) mà là bằng chứng cho thấy kênh ảnh và kênh JSON đang **bổ trợ nhau đúng như thiết kế**: JSON neo giữ các sự kiện hình học/quy tắc định lượng (mà mô hình rule-based đã tính chính xác — khuyến nghị `maintain_lane` của LLM trùng khớp với `recommendation.action` rule-based trong JSON), còn kênh ảnh cho phép mô hình bổ sung ngữ cảnh trực quan (công trình, cây xanh, phương tiện khác) mà lược đồ JSON hiện tại **chưa đặc tả**. Điểm cần lưu ý duy nhất là cụm "moderate traffic" — một diễn đạt hơi phóng đại so với chỉ 2 xe quan sát được trong ảnh — cho thấy mô hình có xu hướng dùng ngôn ngữ chung chung/an toàn hơn là mô tả định lượng chính xác, nhất quán với đặc điểm "quy về trung bình" thường gặp ở các mô hình ngôn ngữ khi không được ép buộc bằng số liệu cụ thể.

Nhận xét chung qua khảo sát định tính nhiều mẫu khác trong `output-suggest/`: khi `recommendation.action` rule-based là `maintain_lane` (chiếm 196/199 = 98.5% số cảnh, theo phân phối ở mục 4.2.3), LLM hầu như luôn đồng thuận và diễn giải lại thành ngôn ngữ tự nhiên mạch lạc; đây là bằng chứng gián tiếp cho câu hỏi nghiên cứu 3 (mục 1.3) — LLM đa phương thức tổng quát, khi được cấp cả JSON có cấu trúc và ảnh gốc, sinh khuyến nghị **nhất quán** với dữ liệu hình học trong phần lớn trường hợp quan sát được, dù luận văn chưa thực hiện một so sánh có hệ thống giữa 3 chế độ (`image_only`/`json_only`/`image_json`) hay giữa 4 chiến lược prompt (mục 3.4.2) trên cùng một tập ảnh — đây là một giới hạn của đánh giá hiện tại, được nêu lại ở Chương 5.

### 4.5. Phân tích trường hợp đặc biệt và thảo luận

Tổng hợp lại các phát hiện chính của Chương 4:

1. **Hiệu chỉnh ngưỡng dựa trên số liệu thực đo là can thiệp hiệu quả nhất** đã thực hiện: một thay đổi 2 hằng số (`DRIFT_THRESHOLD_STRAIGHT`, `DRIFT_THRESHOLD_SHARP`) đưa tỉ lệ phân loại đúng loại đường "thẳng" từ 4.5% lên 89.9% trên cùng một tập ảnh, không cần huấn luyện lại bất kỳ mô hình nào.
2. **Ego-lane và độ lệch xe là hai đại lượng đáng tin cậy nhất** (88–93% theo đánh giá thủ công) — phù hợp để làm nền tảng cho các khuyến nghị giữ làn tức thời.
3. **Loại đường/độ cong vẫn là điểm yếu lớn nhất** (43.1%) ngay cả sau hiệu chỉnh, và **hệ thống chưa có khái niệm chiều di chuyển** (không phân biệt làn ngược chiều) — hai khoảng trống ngữ nghĩa cụ thể, không phải lỗi cài đặt ngẫu nhiên.
4. **Nhận diện biển báo chưa được đánh giá định lượng có ý nghĩa** trên các bộ dữ liệu thử nghiệm hiện tại (CULane/Tusimple) do mật độ biển báo khớp lớp quá thấp — mục tiêu "gần như hoàn hảo" của đề xuất ban đầu (mục 1.4 bản đề xuất) chưa được kiểm chứng cho bối cảnh Việt Nam.
5. **Độ trễ toàn hệ thống còn xa mục tiêu thời gian thực on-device**: tầng nhận thức mất 0.39–0.63 s/khung hình trên CPU (chưa tính LLM), còn tầng suy luận LLM thực tế (qua API đám mây) mất trung bình ≈ 9.1 s/yêu cầu — cả hai đều vượt xa ngưỡng 300–500 ms/khung hình mà bản đề xuất đặt ra cho toàn bộ pipeline chạy trên thiết bị biên.
6. **Kênh ảnh và kênh JSON bổ trợ nhau** trong chế độ `image_json`: các sự kiện định lượng (vị trí, độ lệch, quy tắc tốc độ) được neo giữ đúng nhờ JSON, trong khi ngữ cảnh trực quan (công trình, cây xanh, phương tiện khác) đến từ kênh ảnh — gợi ý rằng mở rộng lược đồ JSON để đặc tả thêm các đối tượng xung quanh (Chương 5) có thể giảm phụ thuộc vào khả năng "tự nhìn" của LLM và tăng khả năng kiểm chứng được của khuyến nghị sinh ra.

---

## CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN TƯƠNG LAI

### 5.1. Kết luận

Luận văn đã cài đặt và đánh giá thực nghiệm một pipeline ba tầng — Nhận diện → Ánh xạ Không gian sang Ngữ nghĩa → Suy luận LLM — nhằm nối khoảng cách giữa nhận thức hình học mức thấp và suy luận ngữ nghĩa mức cao trong bài toán hỗ trợ lái xe, đúng như vấn đề nghiên cứu đặt ra ở Chương 1. Năm đóng góp chính (mục 1.4) đều đã được hiện thực hóa và kiểm chứng bằng số liệu thực đo, không chỉ dừng ở thiết kế lý thuyết:

- Một pipeline hoàn chỉnh, đã chạy thành công trên 399 ảnh thực tế (199 CULane + 200 Tusimple), khắc phục lỗi tách rời dữ liệu lane/sign của phiên bản trước.
- Một tầng ánh xạ hình học → JSON có cấu trúc (`SceneBuilder`), với các đại lượng đã được diễn giải (ego-lane, độ lệch xe, độ cong, loại đường, luật giao thông áp dụng) thay vì tọa độ thô.
- Một bộ ngưỡng phân loại độ cong được hiệu chỉnh bằng số liệu thực đo, cải thiện tỉ lệ phân loại đúng "đường thẳng" từ 4.5% lên 89.9% trên cùng một tập ảnh — minh chứng định lượng rõ ràng nhất của luận văn.
- Một khung đánh giá thủ công theo rubric trên 109 ảnh, định vị chính xác Ego-lane/Offset (88–93%) là điểm mạnh và Road/độ cong (43.1%) là điểm yếu của hệ thống hiện tại.
- Một thực nghiệm đối chiếu LLM đa phương thức thương mại (199/199 yêu cầu thành công) cho thấy khuyến nghị sinh ra nhất quán với dữ liệu hình học trong phần lớn trường hợp, đồng thời kênh ảnh và kênh JSON bổ trợ nhau như kỳ vọng thiết kế.

Trả lời trực tiếp 4 câu hỏi nghiên cứu (mục 1.3): (1) Có thể xây dựng tầng ánh xạ đáng tin cậy — đã cài đặt và kiểm chứng qua ví dụ JSON cụ thể (mục 3.3); (2) hiệu chỉnh ngưỡng bằng số liệu thực đo cải thiện đáng kể độ chính xác — đã lượng hóa bằng thí nghiệm đối chứng (mục 4.2.2); (3) LLM đa phương thức tổng quát sinh khuyến nghị nhất quán với dữ liệu hình học trong đa số trường hợp quan sát được, và các chi tiết bổ sung của nó chủ yếu bắt nguồn từ nội dung ảnh thật chứ không phải ảo giác vô căn cứ (mục 4.4); (4) pipeline hiện tại **còn cách khá xa** mục tiêu thời gian thực on-device 300–500 ms — cả tầng nhận thức (CPU, 0.39–0.63 s) lẫn tầng suy luận LLM qua API đám mây (≈ 9.1 s) đều vượt ngưỡng này.

### 5.2. Hạn chế

1. **Chưa có đánh giá định lượng chuẩn (mAP/F1)** cho cả hai bộ phát hiện, do thiếu tập nhãn box-level khớp đúng 15 lớp biển báo và khớp làn đường trên đúng ảnh thực nghiệm; đánh giá hiện dựa trên rubric thủ công (109 ảnh) — có giá trị định hướng nhưng không thay thế được benchmark chuẩn.
2. **Mật độ biển báo trong dữ liệu thử nghiệm quá thấp** (2.0% và 1.0% số ảnh có biển báo trên CULane/Tusimple) để rút ra kết luận có ý nghĩa thống kê về hiệu năng mô-đun nhận diện biển báo, đặc biệt cho bối cảnh Việt Nam mà đề tài hướng tới.
3. **Hệ thống chưa có khái niệm chiều di chuyển** (không phân biệt làn cùng chiều/ngược chiều) — một khoảng trống ngữ nghĩa được phát hiện qua đánh giá thủ công (9/109 ảnh), chưa được xử lý trong phiên bản hiện tại.
4. **Mô-đun loại đường/độ cong vẫn là điểm yếu** (43.1%) dù đã hiệu chỉnh ngưỡng — tín hiệu `drift_ratio`/`fit_improvement` hiện tại chưa đủ để xử lý mọi trường hợp cong nhẹ/near-field.
5. **Khoảng cách giữa tầm nhìn đề xuất và hệ thống thực tế ở tầng LLM**: bản đề xuất hướng tới một mô hình lượng tử hoá 4-bit chạy on-device (độ trễ 300–500 ms); hệ thống hiện tại dùng một API đám mây thương mại (độ trễ ~9 s/yêu cầu, phụ thuộc kết nối mạng và nhà cung cấp) — phù hợp để đánh giá chất lượng suy luận nhưng chưa khả thi cho triển khai thời gian thực trên xe.
6. **Chưa có so sánh có hệ thống** giữa 3 chế độ đầu vào (`image_only`/`json_only`/`image_json`) hay giữa 4 chiến lược prompt đã cài đặt (`zero_shot`/`chain_of_thought`/`explainable`/`safety_focused`) trên cùng một tập ảnh — kiến trúc đã hỗ trợ nhưng chưa được benchmark đầy đủ.
7. **Toàn bộ thực nghiệm chạy trên CPU**; chưa đo thời gian trên GPU/thiết bị biên thực tế, nên chưa thể kết luận chắc chắn về khả năng đáp ứng mục tiêu độ trễ khi triển khai đúng phần cứng mục tiêu.

### 5.3. Hướng phát triển tương lai

1. **Xây dựng tập nhãn box-level cho biển báo Việt Nam** (mở rộng từ 15 lớp hiện tại lên bộ nhãn VNTSD-style đầy đủ hơn được đề cập trong mã nguồn), làm cơ sở tính `mAP`/`F1` chuẩn và đánh giá đúng mục tiêu ban đầu của đề tài.
2. **Bổ sung khái niệm chiều di chuyển** vào `LaneAnalyzer`, ví dụ suy luận từ hướng vạch kẻ (đứt/liền, màu vàng/trắng nếu mô hình phân loại được kiểu vạch) hoặc từ ngữ cảnh chuyển động giữa các khung hình liên tiếp (thay vì chỉ xử lý từng ảnh tĩnh độc lập).
3. **Cải thiện ước lượng độ cong** bằng cách kết hợp thêm tín hiệu thời gian (theo dõi độ cong qua nhiều khung hình liên tiếp thay vì ước lượng độc lập từng ảnh), hoặc bổ sung một mô hình hồi quy độ cong huấn luyện riêng thay vì chỉ dựa trên polyfit + ngưỡng.
4. **Tối ưu hoá độ trễ theo đúng định hướng ban đầu**: thử nghiệm mô hình LLM lượng tử hoá 4-bit chạy on-device (Phi-3-mini hoặc tương đương) thay cho API đám mây, đo độ trễ thực tế trên phần cứng biên mục tiêu (GPU nhúng hoặc NPU), đối chiếu với ngưỡng 300–500 ms/khung hình.
5. **So sánh có hệ thống giữa các chế độ đầu vào và chiến lược prompt** (đã có sẵn trong `llm_batch_client.py` và `PromptBuilder`) trên cùng một tập ảnh, dùng chính khung rubric thủ công của mục 4.2.1 để định lượng chất lượng suy luận theo từng cấu hình.
6. **Mở rộng lược đồ JSON** để đặc tả thêm các đối tượng xung quanh (phương tiện khác, người đi bộ, điều kiện thời tiết/ánh sáng) — như phân tích ở mục 4.4 cho thấy đây hiện là thông tin chỉ đến từ kênh ảnh, chưa được kênh JSON đặc tả tường minh, hạn chế khả năng kiểm chứng và tái lập của khuyến nghị sinh ra.
7. **Tích hợp cấu trúc suy luận nhiều bước có kiểm chứng** (theo hướng RATT, mục 2.3) để `RecommendationEngine` tiến hoá từ rule-based thuần túy thành một tác nhân suy luận có khả năng tự kiểm tra tính nhất quán giữa khuyến nghị LLM và dữ liệu JSON gốc trước khi xuất ra khuyến nghị cuối cùng.

---

## TÀI LIỆU THAM KHẢO

1. Sah, C. K., Shaw, A. K., Lian, X., Baig, A. S., Wen, T., Jiang, K., Yang, M., & Yang, D. (2025). *Advancing Autonomous Vehicle Intelligence: Deep Learning and Multimodal LLM for Traffic Sign Recognition and Robust Lane Detection.* arXiv:2503.06313.
2. Qin, Z., Wang, H., & Li, X. (2022). *Ultra Fast Deep Lane Detection With Hybrid Anchor Driven Ordinal Classification.* IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI). IEEE Xplore document 9795098.
3. Pan, X., Shi, J., Luo, P., Wang, X., & Tang, X. (2018). *Spatial As Deep: Spatial CNN for Traffic Scene Understanding (SCNN).* AAAI Conference on Artificial Intelligence. (dẫn theo số liệu F1 71.6% trên CULane, trích trong bản đề xuất luận văn).
4. Alzraiee, H., Leal Ruiz, A., & Sprotte, R. (2021). *Detecting of Pavement Marking Defects Using Faster R-CNN.* Journal of Performance of Constructed Facilities, 35(4). DOI: 10.1061/(ASCE)CF.1943-5509.0001606.
5. Hong, J., Sapp, B., & Philbin, J. (2019). *Rules of the Road: Predicting Driving Behavior With a Convolutional Model of Semantic Interactions.* Proceedings of CVPR 2019.
6. Shaw, A. K., et al. (2025). *SafeRoute: Enhancing Traffic Scene Understanding via a Unified Deep Learning Framework.* ICCV 2025 Workshop on Data-driven and Foundation Models for Autonomous Driving (WDFM-AD).
7. Zhang, J., Wang, X., Ren, W., Jiang, L., Wang, D., & Liu, K. (2025). *RATT: A Thought Structure for Coherent and Correct LLM Reasoning.* Proceedings of the AAAI Conference on Artificial Intelligence, 39(25), 26733–26741. DOI: 10.1609/aaai.v39i25.34876.
8. Ferrag, M. A., Tihanyi, N., & Debbah, M. (2025). *From LLM Reasoning to Autonomous AI Agents: A Comprehensive Review.* arXiv:2504.19678.
9. Tác giả chưa xác định (2025/2026). *Driving-Scene-Context-Aware Trajectory Prediction with Risk-Aware Explanation* (chương sách). Lecture Notes in Computer Science, Springer. DOI: 10.1007/978-3-032-05179-0_15.
10. Chen, Y., Li, X., Cong, G., Bao, Z., et al. (2021). *Robust Road Network Representation Learning.* Proceedings of the 30th ACM International Conference on Information & Knowledge Management (CIKM '21). DOI: 10.1145/3459637.3482293.
11. Qin, Z., et al. Mã nguồn tham chiếu kiến trúc `parsingNet`: kho `Ultra-Fast-Lane-Detection-v2` (GitHub: `cfzd/Ultra-Fast-Lane-Detection-v2`), dùng làm nền tảng cho `perception/lane_detector.py` của hệ thống.
12. Vuong, K. D., Hu, J. Y. C., et al. — *DiLu*, *DriveGPT4*, *GPT-Driver*: các hệ thống LLM hỗ trợ quyết định lái xe được dẫn trong bản đề xuất ban đầu của đề tài (mục 1.3 bản đề xuất) làm cơ sở xác định khoảng trống nghiên cứu; luận văn không truy cập trực tiếp bản đầy đủ các công trình này trong quá trình viết báo cáo — khuyến nghị người đọc tra cứu bản gốc khi trích dẫn chính thức.

> **Ghi chú về nguồn tham khảo:** Trong số các đường dẫn được cung cấp cho quá trình viết luận văn, một số (IEEE Xplore document 10006813/9398517/9350286/10105922; DOI liên quan tới ScienceDirect S174680941300178X và Springer s42979-024-02773-w) không thể truy cập nội dung đầy đủ do giới hạn quyền truy cập của nhà xuất bản hoặc thuộc lĩnh vực không liên quan trực tiếp tới đề tài (ví dụ xử lý tín hiệu EEG) khi được xác minh, nên đã **không được đưa vào danh sách trích dẫn** để tránh trích dẫn sai lệch. Học viên nên tự tra cứu và bổ sung các nguồn này trực tiếp nếu xác nhận chúng thực sự liên quan.

