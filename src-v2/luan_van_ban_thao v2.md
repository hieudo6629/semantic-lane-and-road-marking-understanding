# VIỆN QUẢN TRỊ VÀ CÔNG NGHỆ FPT

## HIỂU LÀN ĐƯỜNG VÀ BIỂN BÁO GIAO THÔNG THEO NGỮ NGHĨA SỬ DỤNG MÔ HÌNH NGÔN NGỮ LỚN ĐỂ HỖ TRỢ RA QUYẾT ĐỊNH LÁI XE

*(Semantic Lane and Traffic Sign Understanding Using Large Language Models for Driving Decision Support)*

**LUẬN VĂN THẠC SĨ**

Chuyên ngành: Kỹ thuật Phần mềm

Học viên thực hiện: Đỗ Minh Hiếu

Người hướng dẫn khoa học: Tiến sĩ Đoàn Nhật Quang

Hà Nội, 2026

---

## LỜI CAM ĐOAN

Tôi xin cam đoan đây là công trình nghiên cứu do chính tôi thực hiện dưới sự hướng dẫn khoa học của Tiến sĩ Đoàn Nhật Quang.

Các số liệu, kết quả thực nghiệm trình bày trong luận văn là trung thực, được thu thập và xử lý bằng các công cụ, mã nguồn do tôi tự xây dựng, chưa từng được công bố trong bất kỳ công trình nào khác. Các nội dung tham khảo từ công trình của tác giả khác đều được trích dẫn đầy đủ, rõ ràng trong mục Tài liệu tham khảo.

Nếu có bất kỳ sự gian dối hay vi phạm quy định về liêm chính khoa học nào, tôi xin chịu hoàn toàn trách nhiệm trước Hội đồng và Nhà trường.

## LỜI CẢM ƠN

Để hoàn thành chương trình đào tạo Thạc sĩ và hoàn thiện công trình nghiên cứu này, bên cạnh những nỗ lực của bản thân, tôi đã nhận được sự dạy dỗ, hướng dẫn và động viên vô cùng to lớn của các thầy, cô, nhà trường, bạn bè và gia đình.

Trước tiên, tôi xin bày tỏ lòng biết ơn chân thành đến giảng viên hướng dẫn luận văn của mình — Tiến sĩ Đoàn Nhật Quang. Thầy là người đã truyền cảm hứng và định hướng cho tôi hình thành nên ý tưởng của đề tài nghiên cứu này, đã dành nhiều thời gian chỉ dẫn, truyền tải kiến thức, đồng thời đánh giá và góp ý trong suốt quá trình thực hiện đề tài. Những chỉ bảo tâm huyết của thầy không chỉ giúp tôi hoàn thiện bài luận văn mà còn là hành trang quý giá cho con đường phát triển chuyên môn của tôi sau này.

Tôi xin chân thành cảm ơn đội ngũ giảng viên, nhân viên tại Viện Quản trị & Công nghệ FPT (FSB) vì đã tạo ra một môi trường giáo dục chuyên nghiệp, cởi mở để tôi có thể theo học những kiến thức chuyên môn vững chắc và tham gia những buổi hội thảo hữu ích. Tôi cũng xin gửi lời cảm ơn đến các bạn bè, đồng nghiệp đã luôn sẵn sàng chia sẻ kiến thức, thảo luận và đồng hành cùng tôi trong suốt quá trình học tập.

Cuối cùng, tôi xin dành trọn tình cảm và lòng biết ơn vô hạn tới cha mẹ, anh chị em trong gia đình. Gia đình luôn là điểm tựa vững chắc nhất, mang lại sự bình yên, niềm tin và luôn tạo điều kiện tốt nhất để tôi kiên trì nỗ lực vượt qua khó khăn, hoàn thành ước mơ học tập của mình.

Mặc dù đã có nhiều cố gắng trong quá trình nghiên cứu và trình bày, công việc này không tránh khỏi những hạn chế nhất định. Tôi rất mong nhận được những ý kiến đóng góp quý báu từ Quý Thầy/Cô trong Hội đồng để công trình nghiên cứu này được hoàn thiện hơn.

---

## MỤC LỤC

- CHƯƠNG 1. GIỚI THIỆU
  - 1.1. Bối cảnh và động lực
  - 1.2. Mục tiêu nghiên cứu
  - 1.3. Đóng góp chính
  - 1.4. Cấu trúc luận văn
- CHƯƠNG 2. TỔNG QUAN VÀ CÁC CÔNG TRÌNH LIÊN QUAN
  - 2.1. Phát hiện làn đường (Lane Detection)
  - 2.2. Phát hiện biển báo giao thông (Traffic Sign Detection)
  - 2.3. Mô hình ngôn ngữ lớn đa phương thức cho hỗ trợ quyết định lái xe
  - 2.4. Đánh giá chất lượng output ngôn ngữ tự nhiên bằng LLM-as-a-Judge
  - 2.5. Khoảng trống nghiên cứu
- CHƯƠNG 3. PHƯƠNG PHÁP LUẬN
  - 3.1. Kiến trúc hệ thống tổng thể
  - 3.2. Dữ liệu
  - 3.3. Phân tích ngữ nghĩa làn đường
  - 3.4. Cấu trúc JSON ngữ nghĩa gửi cho LLM
  - 3.5. Thiết kế prompt cho tầng suy luận
  - 3.6. Lựa chọn mô hình cho tầng suy luận
  - 3.7. Phương pháp luận đánh giá
- CHƯƠNG 4. KẾT QUẢ VÀ BÀN LUẬN
  - 4.1. Độ chính xác module hiểu làn đường (CULane)
  - 4.2. Kiểm chứng độc lập trên dữ liệu real-life
  - 4.3. Module biển báo giao thông trên CULane
  - 4.4. So sánh mô hình LLM cho tầng suy luận
  - 4.5. Kết quả chính: đóng góp của thông tin ngữ nghĩa có cấu trúc
  - 4.6. Kiểm chứng độ tin cậy của phương pháp đánh giá
  - 4.7. Kiểm chứng khả năng tự nhận diện làn đường của VLM
  - 4.8. Bàn luận: giả thuyết về cơ chế đóng góp của thông tin ngữ nghĩa có cấu trúc
  - 4.9. Hạn chế: rủi ro trùng lặp dữ liệu (data leakage) và hiệu chỉnh tham số
- CHƯƠNG 5. KẾT LUẬN
  - 5.1. Trả lời câu hỏi nghiên cứu
  - 5.2. Tóm tắt đóng góp
  - 5.3. Hạn chế
  - 5.4. Hướng phát triển tiếp theo
- TÀI LIỆU THAM KHẢO

## DANH MỤC TỪ VIẾT TẮT

| Từ viết tắt | Tiếng Anh | Giải thích |
|---|---|---|
| ADAS | Advanced Driver Assistance System | Hệ thống hỗ trợ lái xe tiên tiến |
| VLM | Vision-Language Model | Mô hình thị giác ngôn ngữ |
| LLM | Large Language Model | Mô hình ngôn ngữ lớn |
| MLLM | Multimodal Large Language Model | Mô hình ngôn ngữ lớn đa phương thức |
| UFLD-v2 | Ultra Fast Lane Detection v2 | Kiến trúc phát hiện làn đường tốc độ cao (phiên bản 2) |
| SCNN | Spatial Convolutional Neural Network | Mạng nơ-ron tích chập không gian |
| YOLO | You Only Look Once | Họ kiến trúc object detection một giai đoạn |
| TT100K | Tsinghua-Tencent 100K | Bộ dữ liệu biển báo giao thông quy mô lớn |
| MAE | Mean Absolute Error | Sai số tuyệt đối trung bình |
| IoU | Intersection over Union | Tỉ lệ giao trên hợp (metric localization) |
| F1 | F1-score | Trung bình điều hòa của Precision và Recall |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| NIM | NVIDIA Inference Microservices | Dịch vụ suy luận model của NVIDIA (nền tảng gọi VLM trong đề tài) |
| JSON | JavaScript Object Notation | Định dạng dữ liệu có cấu trúc dùng làm ngữ nghĩa trung gian |
| QCVN | Quy chuẩn Việt Nam | Hệ thống quy chuẩn kỹ thuật quốc gia (áp dụng cho biển báo Việt Nam) |

## DANH MỤC BẢNG

| STT | Ký hiệu | Tên bảng |
|---|---|---|
| 1 | Bảng 2.1 | Tổng hợp các công trình liên quan về LLM/VLM cho lái xe |
| 2 | Bảng 3.1 | Tổng hợp tham số cấu hình của mô-đun phân tích ngữ nghĩa |
| 3 | Bảng 3.2 | Các nhóm trường trong Thông tin ngữ nghĩa có cấu trúc phiên bản đầy đủ và lý do đưa vào |
| 4 | Bảng 3.3 | Các trường trong Thông tin ngữ nghĩa có cấu trúc phiên bản rút gọn và lý do giữ lại |
| 5 | Bảng 3.4 | Cấu hình gọi API dùng chung cho ba mô hình ứng viên và ba chế độ input |
| 6 | Bảng 3.5 | Mô tả từng mức điểm trong thang đánh giá 1–5 |
| 7 | Bảng 4.1 | Độ chính xác module hiểu làn đường trên CULane (N=200) |
| 8 | Bảng 4.2 | So sánh hiệu năng module hiểu làn đường theo nhóm có/không vạch kẻ đường rõ |
| 9 | Bảng 4.3 | Đối chiếu module hiểu làn đường và biển báo giữa CULane và dữ liệu real-life độc lập |
| 10 | Bảng 4.4 | So sánh chi tiết chất lượng nội dung giữa nemotron-nano-8b và ising-calibration-31b (Mean ± SD, kiểm định thống kê) |
| 11 | Bảng 4.5 | Điểm chất lượng khuyến nghị lái xe (Mean ± SD) theo 3 chế độ input, chấm bởi 3 judge độc lập |
| 12 | Bảng 4.6 | Kiểm định ý nghĩa thống kê khi so sánh cặp giữa 3 chế độ input, theo từng judge (N=200, dữ liệu bắt cặp theo ảnh) |
| 13 | Bảng 4.7 | Điểm trung bình (Mean ± SD) 6 tiêu chí đánh giá của judge Gemini theo từng chế độ input |
| 14 | Bảng 4.8 | Xếp hạng độ tin cậy của 3 judge khi đối chiếu với đánh giá của con người |
| 15 | Bảng 4.9 | So sánh khả năng tự nhận diện ngữ nghĩa làn đường giữa pipeline UFLD-v2 và VLM |

## DANH MỤC HÌNH

| STT | Ký hiệu | Tên hình |
|---|---|---|
| 1 | Hình 3.1 | Kiến trúc tổng thể của pipeline 4 giai đoạn: Perception – Semantic Analysis – LLM Reasoning – Evaluation |
| 2 | Hình 3.2 | Ví dụ trực quan hóa output của mô-đun phân tích ngữ nghĩa trên một ảnh CULane thật |
| 3 | Hình 3.3 | So sánh cấu trúc trường giữa Thông tin ngữ nghĩa có cấu trúc phiên bản đầy đủ và Thông tin ngữ nghĩa có cấu trúc phiên bản rút gọn |

---

## TÓM TẮT

Các hệ thống hỗ trợ lái xe (ADAS) hiện nay thường dừng lại ở tầng nhận diện cấp thấp (tọa độ điểm ảnh, bounding box), chưa chuyển hóa được thành ngữ nghĩa giao thông mà con người có thể hiểu và tin tưởng. Luận văn này xây dựng và kiểm chứng định lượng một pipeline bốn giai đoạn (Perception – Semantic Analysis – LLM Reasoning – Evaluation), kết hợp mô hình phát hiện làn đường UFLD-v2 (dùng nguyên trạng ở dạng pretrained), mô hình phát hiện biển báo YOLOv8n (tự tinh chỉnh trên TT100K), một mô-đun chuyển đổi ngữ nghĩa có cấu trúc tự thiết kế, và một mô hình ngôn ngữ lớn đa phương thức (VLM) để sinh khuyến nghị lái xe bằng ngôn ngữ tự nhiên. Tầng suy luận theo hướng tiếp cận training-free, không tinh chỉnh lại mô hình; chi phí huấn luyện của toàn hệ thống do đó chỉ giới hạn ở một bước tinh chỉnh YOLOv8n quy mô nhẹ, thay vì huấn luyện một VLM hoặc LLM chuyên biệt.

Trên bộ dữ liệu CULane (N=200 ảnh, gán nhãn tay đầy đủ), module hiểu làn đường đạt Accuracy 69,0% tổng thể và 77,3% trên nhóm ảnh có vạch kẻ đường rõ. Kết quả tổng quát hóa tốt sang một bộ dữ liệu real-life độc lập tự thu thập (N=200), với Precision số làn đạt 99,4%. Câu hỏi nghiên cứu trung tâm — liệu thông tin ngữ nghĩa có cấu trúc có cải thiện chất lượng khuyến nghị lái xe của VLM so với chỉ dùng ảnh hay không — được trả lời bằng thực nghiệm định lượng trên N=200 ảnh, chấm điểm độc lập bởi ba mô hình judge (Gemini, GPT-5 Mini, DeepSeek) trên cùng một rubric sáu tiêu chí. Ba judge được áp dụng độc lập đều nhất quán xếp chế độ chỉ dùng ảnh ở điểm thấp nhất, trong khi chế độ có thông tin ngữ nghĩa có cấu trúc cải thiện điểm số tới đáng kể (Gemini: 3,32 → 4,53/5). Độ tin cậy của phương pháp LLM-as-a-judge được kiểm chứng bằng đối chiếu với đánh giá của con người (N=20), đạt mức đồng thuận 79,2% trong sai số ≤1 điểm — một mức đồng thuận cao, vượt trội rõ rệt so với hai judge thay thế được kiểm chứng theo cùng phương pháp.

Một thực nghiệm bổ sung, yêu cầu VLM tự nhận diện ngữ nghĩa làn đường trực tiếp từ ảnh mà không qua tầng UFLD-v2, cho thấy năng lực cảm nhận thị giác của VLM không hề yếu — thậm chí vượt trội pipeline chuyên biệt khi thiếu vạch kẻ đường hoặc trên dữ liệu ngoài domain huấn luyện. Phát hiện này dẫn tới một điều chỉnh quan trọng trong cách diễn giải kết quả trung tâm: thông tin ngữ nghĩa có cấu trúc cải thiện chất lượng khuyến nghị chủ yếu nhờ vai trò khung đỡ (scaffolding) cho việc suy luận và trình bày trong một tác vụ ghép nhiều bước, không đơn thuần vì bù đắp năng lực cảm nhận thị giác còn thiếu của VLM. Luận văn cũng thảo luận các hạn chế đã kiểm chứng — rủi ro trùng lặp dữ liệu, giới hạn dữ liệu biển báo trên CULane — và đề xuất hướng phát triển: kiến trúc hybrid kết hợp pipeline thị giác máy tính với cơ chế fallback sang VLM, và mở rộng sang dữ liệu giao thông Việt Nam.

**Từ khóa**: hiểu ngữ nghĩa giao thông, mô hình ngôn ngữ lớn đa phương thức, phát hiện làn đường, phát hiện biển báo, LLM-as-a-judge, hỗ trợ ra quyết định lái xe.

---

# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh và động lực

ADAS (Advanced Driver Assistance Systems) là các hệ thống điện tử trên xe, dùng cảm biến (camera, radar, LiDAR...) để tự động phát hiện tình huống giao thông và hỗ trợ hành vi lái xe — ví dụ cảnh báo chệch làn, hỗ trợ giữ làn, phanh khẩn cấp tự động [20]. Nhu cầu này gắn liền với quy mô vấn đề an toàn giao thông toàn cầu: tai nạn đường bộ gây khoảng 1,19 triệu ca tử vong mỗi năm [31], trong khi hệ thống cảnh báo chệch làn đã được chứng minh giảm 11% tỉ lệ va chạm và 21% tỉ lệ thương tích liên quan [32].

Phần lớn nghiên cứu ADAS hiện nay tập trung vào tầng nhận diện, với các mô-đun phát hiện làn đường, biển báo ngày càng nhanh và chính xác (mục 2.1, 2.2). Tuy nhiên, đầu ra của các mô-đun này — tọa độ điểm ảnh, bounding box, class ID — được thiết kế cho thuật toán điều khiển, không phải để con người trực tiếp đọc hiểu (khả năng diễn giải cho con người là một hạn chế đã được ghi nhận ở nhiều hệ ADAS dựa trên AI [19]); điều này đòi hỏi một tầng trung gian chuyển thông tin nhận diện thô thành ngữ nghĩa giao thông — làn đường, độ lệch tâm, hình dạng đường, biển báo cần tuân thủ — trước khi trình bày cho người lái bằng ngôn ngữ tự nhiên. Trọng tâm nghiên cứu của đề tài là tầng biểu diễn ngữ nghĩa có cấu trúc này và tác động của nó lên VLM; khả năng diễn giải bằng ngôn ngữ tự nhiên là một thuộc tính của đầu ra, không phải bản thân đối tượng nghiên cứu.

Sự phát triển gần đây của mô hình ngôn ngữ đa phương thức (Vision-Language Model — VLM) mở ra hướng tiếp cận lấp đầy khoảng trống này, nhờ khả năng tổng hợp ảnh quan sát và dữ liệu ngữ nghĩa có cấu trúc để sinh khuyến nghị bằng ngôn ngữ tự nhiên. Nguyên lý cấp thêm ngữ cảnh có cấu trúc để tăng độ chính xác và giảm ảo giác cho mô hình sinh đã được kiểm chứng cả ở LLM nói chung (Retrieval-Augmented Generation [34]) lẫn trong lái xe cụ thể: DriveVLM [23] kết hợp VLM với thông tin không gian có cấu trúc để bù hạn chế suy luận không gian, còn Talk2BEV [25] cho thấy đặt VLM vào biểu diễn bản đồ có cấu trúc cải thiện rõ chất lượng suy luận so với chỉ dùng ảnh. Kế thừa nguyên lý này, đề tài đặt giả thuyết trung tâm — kết hợp ảnh với thông tin ngữ nghĩa có cấu trúc sẽ cải thiện khuyến nghị lái xe của VLM so với chỉ dùng ảnh thô — và kiểm chứng định lượng ở mục 4.5.

Do không gian ngữ nghĩa giao thông đầy đủ bao quát rất nhiều yếu tố (hạ tầng đường bộ, phương tiện xung quanh, chướng ngại vật động...), để đảm bảo tính khả thi, đề tài này thu hẹp phạm vi vào hai thành phần hạ tầng cố định nền tảng nhất — làn đường và biển báo giao thông — quyết định trực tiếp việc định vị không gian và quy tắc bắt buộc đối với phương tiện.

Về dữ liệu, đề tài kiểm chứng định lượng trên hai tập dữ liệu chuẩn công khai, phổ biến quốc tế — CULane [6] cho bài toán làn đường, TT100K [9] cho bài toán biển báo — nhằm đảm bảo khả năng tái lập và đối sánh khách quan với các công trình liên quan (mục 2.1, 2.2), đồng thời bổ sung một bộ dữ liệu real-life tự thu thập (200 khung hình dashcam), độc lập với dữ liệu huấn luyện của UFLD-v2, để kiểm chứng khả năng tổng quát hóa ngoài phân bố huấn luyện (chi tiết dữ liệu ở mục 3.2, kết quả kiểm chứng ở mục 4.2). Việc ưu tiên hai bộ benchmark chuẩn hóa thay vì thu thập riêng dữ liệu Việt Nam ở giai đoạn này là một lựa chọn phương pháp luận có chủ đích — tách bạch hiệu năng của giải pháp đề xuất khỏi nhiễu do chất lượng gán nhãn thủ công, tạo tiền đề kiểm chứng chính xác giả thuyết nghiên cứu; việc mở rộng sang dữ liệu giao thông Việt Nam được thảo luận như một hướng phát triển trọng tâm ở mục 5.4.

Trên cơ sở đó, đề tài hướng tới câu hỏi nghiên cứu cốt lõi:

"Việc tích hợp thông tin ngữ nghĩa có cấu trúc có cải thiện chất lượng, độ chính xác và tính căn cứ của khuyến nghị lái xe do VLM sinh ra so với chỉ dùng ảnh thô hay không, và mức cải thiện này được định lượng ra sao?"

## 1.2. Mục tiêu nghiên cứu

Tương ứng với câu hỏi nghiên cứu cốt lõi được đặt ra tại Mục 1.1, mục tiêu tổng quát của đề tài là đề xuất, phát triển và kiểm chứng định lượng một tầng xử lý trung gian nhằm chuyển đổi dữ liệu nhận diện hạ tầng giao thông thô thành tri thức ngữ nghĩa có cấu trúc, đóng vai trò làm ngữ cảnh bổ sung cho Mô hình Ngôn ngữ Đa phương thức (VLM) trong bài toán sinh khuyến nghị lái xe bằng ngôn ngữ tự nhiên.
Bám sát phạm vi nghiên cứu đã xác định, đề tài tập trung giải quyết hai thành phần ngữ nghĩa hạ tầng cốt lõi trong tình huống giao thông:

1. **Ngữ nghĩa làn đường** (Lane Semantics): xác định tổng số làn đường, làn đường hiện tại của phương tiện (ego lane), độ lệch tâm của xe, số làn lân cận và hình thái đường (đường thẳng hay đường cong).
2. **Ngữ nghĩa biển báo giao thông** (Traffic Sign Semantics): định vị, phân loại các biển báo giao thông xuất hiện trong tầm quan sát và trích xuất quy tắc giao thông tương ứng.

Để cụ thể hóa mục tiêu tổng quát, đề tài triển khai ba mục tiêu cụ thể sau:

1. **Phát triển mô-đun chuyển đổi ngữ nghĩa**: thiết kế và cài đặt mô-đun tổng hợp dữ liệu đầu ra từ các mô hình nhận diện chuyên biệt (làn đường và biển báo) để trích xuất thành các thuộc tính ngữ nghĩa giao thông có cấu trúc (mục 3.3, 3.4).
2. **Xây dựng biểu diễn dữ liệu và phương pháp gợi ý (prompting)**: thiết kế biểu diễn ngữ nghĩa có cấu trúc hợp lý kết hợp với kỹ thuật xây dựng câu lệnh (prompt engineering) phù hợp, nhằm giúp VLM khai thác hiệu quả tri thức ngữ cảnh trong quá trình suy luận (mục 3.4, 3.5).
3. **Đánh giá và kiểm chứng định lượng**: xây dựng khung phương pháp luận đánh giá thực nghiệm đáng tin cậy — ứng dụng mô hình LLM làm giám khảo (LLM-as-a-Judge) — nhằm định lượng mức độ cải thiện về chất lượng, độ chính xác và tính căn cứ của khuyến nghị do VLM sinh ra khi có sự kết hợp của thông tin ngữ nghĩa có cấu trúc so với khi chỉ sử dụng dữ liệu ảnh thô (mục 3.7, 4.5).

Việc hoàn thành các mục tiêu cụ thể nêu trên là cơ sở thực nghiệm và luận cứ khoa học để trả lời trực tiếp cho câu hỏi nghiên cứu cốt lõi của đề tài.

## 1.3. Đóng góp chính

Đóng góp chính của đề tài là một **tầng biểu diễn ngữ nghĩa có cấu trúc** cho bài toán hỗ trợ quyết định lái xe bằng VLM, cùng bằng chứng thực nghiệm định lượng cho thấy tầng biểu diễn này có tác động tới chất lượng khuyến nghị do VLM sinh ra — một câu hỏi mà các hướng nghiên cứu liên quan (mục 2.3, 2.5) mới dừng ở việc tích hợp thông tin có cấu trúc để tối đa hóa độ chính xác, chưa tách bạch định lượng phần đóng góp riêng của thông tin đó bằng một thực nghiệm đối chứng (ablation) so với chỉ dùng ảnh thô. Ba đóng góp cụ thể:

1. **Một mô-đun biểu diễn ngữ nghĩa có cấu trúc, được kiểm chứng độc lập với ground truth** — đóng góp kỹ thuật trung tâm của đề tài: xây dựng quy trình chuyển đổi output thô của các mô hình nhận diện chuyên biệt (UFLD-v2, YOLOv8n) thành các thuộc tính ngữ nghĩa quyết định (số làn, làn ego, độ lệch tâm, làn lân cận, hình thái đường, biển báo), kiểm chứng độ chính xác bằng đối chiếu ground truth gán tay trên cả dữ liệu benchmark lẫn dữ liệu độc lập tự thu thập (Mục 3.3, 4.1–4.3).
2. **Một khung thực nghiệm để đo ảnh hưởng của biểu diễn ngữ nghĩa lên VLM**: so sánh có kiểm soát giữa ba chế độ input (chỉ ảnh / chỉ ngữ nghĩa / kết hợp) trên cùng mô hình, cùng ảnh, cùng bộ tiêu chí, kèm một công cụ đo đã được kiểm chứng độ tin cậy — quy trình đối chiếu đa giám khảo (multi-judge alignment) và đối chiếu với đánh giá của con người (Mục 3.7, 4.6) — để kết luận so sánh không phụ thuộc vào một công cụ đo chưa được xác nhận.
3. **Kết quả định lượng cho câu hỏi nghiên cứu cốt lõi**: thông tin ngữ nghĩa có cấu trúc cải thiện rõ rệt chất lượng khuyến nghị so với chỉ dùng ảnh thô, kiểm chứng nhất quán bởi ba judge độc lập trên N=200 ảnh; lợi ích của việc kết hợp thêm ảnh so với chỉ dùng thông tin ngữ nghĩa thì phụ thuộc vào judge được dùng (Mục 4.5).

Về mặt kỹ thuật, tầng suy luận theo hướng tiếp cận training-free — không huấn luyện lại mô hình lớn, khác với các kiến trúc VLM/VLA end-to-end quy mô lớn (DriveGPT4 [2], DriveLM [3]) đòi hỏi hạ tầng tính toán lớn hơn nhiều; đề tài không đề xuất một kiến trúc nhận diện mới, các mô hình nhận diện chuyên biệt (UFLD-v2, YOLOv8n) chỉ đóng vai trò tạo dữ liệu đầu vào cho tầng biểu diễn ngữ nghĩa nêu trên.

**Ý nghĩa thực tiễn**. So với các hệ thống VLM end-to-end phức tạp, đòi hỏi huấn luyện trên dữ liệu lái xe quy mô lớn, quy trình (pipeline) do đề tài đề xuất tránh được chi phí tính toán của việc huấn luyện hoặc tinh chỉnh cục bộ một VLM/LLM — tầng suy luận dùng nguyên trạng một VLM có sẵn qua API, chỉ tầng nhận diện biển báo cần một bước tinh chỉnh nhẹ (YOLOv8n). Đây là một giải pháp khả thi trong điều kiện tài nguyên tính toán hạn chế của một đề tài nghiên cứu độc lập, phù hợp làm nền tảng cho các ứng dụng camera hành trình (dashcam) thông minh, hộp đen thế hệ mới, hoặc làm tiền đề để mở rộng thích ứng với dữ liệu giao thông đặc thù tại Việt Nam (Mục 5.4); chi phí vận hành thực tế khi triển khai sản xuất (network dependency, tính sẵn sàng của API, độ trễ) chưa được đánh giá trong phạm vi đề tài này.

## 1.4. Cấu trúc luận văn

Toàn văn luận văn được tổ chức thành 5 chương chính với nội dung trình bày theo thứ tự logic như sau:

Chương 1: Giới thiệu (Introduction): Trình bày tổng quan về bối cảnh nghiên cứu, động lực đề tài, phát biểu bài toán, mục tiêu và phạm vi dữ liệu, các đóng góp chính và ý nghĩa thực tiễn của đề tài.

Chương 2: Tổng quan nghiên cứu và Cơ sở lý thuyết (Related Work & Theoretical Background): Tổng quan các công trình liên quan theo bốn trục nội dung chính bao gồm: phát hiện làn đường, phát hiện biển báo giao thông, ứng dụng Mô hình Ngôn ngữ Đa phương thức (VLM) trong lái xe tự hành, và phương pháp luận đánh giá LLM-as-a-Judge; qua đó xác định rõ khoảng trống tri thức mà đề tài hướng tới giải quyết.

Chương 3: Phương pháp đề xuất (Proposed Methodology): Mô tả chi tiết kiến trúc hệ thống tổng thể, quy trình thu thập và xử lý dữ liệu, thuật toán trích xuất ngữ nghĩa hạ tầng (làn đường và biển báo), thiết kế biểu diễn ngữ nghĩa có cấu trúc, kỹ thuật gợi ý (prompt engineering) và khung phương pháp luận đánh giá.

Chương 4: Thực nghiệm và Đánh giá (Experiments & Discussion): Trình bày chi tiết cấu hình thực nghiệm, kết quả định lượng của từng mô-đun thành phần, kết quả thực nghiệm trung tâm về tác động của thông tin ngữ nghĩa có cấu trúc đến VLM, kiểm chứng độ tin cậy của LLM-as-a-Judge, cùng các phân tích chuyên sâu làm rõ cơ chế đóng góp thực sự của thông tin đó.

Chương 5: Kết luận và Hướng phát triển (Conclusion & Future Work): Tổng kết các đóng góp chính, tổng hợp câu trả lời cho câu hỏi nghiên cứu, thảo luận khách quan về các hạn chế còn tồn tại và đề xuất các hướng mở rộng nghiên cứu trong tương lai.

Tóm tắt Chương 1. Chương 1 đã phân tích rõ bối cảnh và động lực nghiên cứu xuất phát từ khoảng trống giữa dữ liệu nhận diện hình học cấp thấp và nhu cầu diễn giải ngữ nghĩa giao thông cho người lái. Trên cơ sở đó, chương này đã xác lập mục tiêu nghiên cứu, phạm vi dữ liệu, các đóng góp cốt lõi và ý nghĩa thực tiễn của luận văn. Chương 2 tiếp theo sẽ trình bày tổng quan các nghiên cứu liên quan nhằm làm nét hơn nữa nền tảng lý thuyết và cơ sở khoa học cho phương pháp đề xuất.

---

# CHƯƠNG 2. TỔNG QUAN VÀ CÁC CÔNG TRÌNH LIÊN QUAN

Các hệ thống hỗ trợ lái xe tiên tiến (Advanced Driver Assistance Systems — ADAS) hiện là một phần gần như tiêu chuẩn trên xe hơi thương mại, với các tính năng đã phổ biến như cảnh báo chệch làn, hỗ trợ giữ làn, và nhận diện biển báo giao thông; đây cũng là nền tảng nhận thức cần thiết để tiến tới các cấp độ tự động hóa cao hơn. Nidamanuri và cộng sự [20] khảo sát tiến trình phát triển công nghệ ADAS qua các cấp độ tự động hóa, cho thấy xu hướng chuyển dịch từ hệ thống dựa trên cảm biến đơn lẻ sang các hệ đa cảm biến kết hợp học sâu nhằm tăng độ tin cậy trong điều kiện thực tế đa dạng. Song song với yêu cầu về độ chính xác, khả năng khả giải (explainability) của quyết định do AI đưa ra ngày càng được xem là một điều kiện quan trọng để ADAS được triển khai và chấp nhận ở quy mô lớn, đặc biệt trong các tình huống ranh giới (edge case): Kuznietsov và cộng sự [19] thực hiện tổng quan hệ thống đầu tiên về AI khả giải (Explainable AI — XAI) cho lái xe tự động an toàn, chỉ ra năm đóng góp chính của XAI — thiết kế khả giải, mô hình đại diện khả giải, giám sát khả giải, giải thích phụ trợ, và kiểm định khả giải. Tselentis và Papadimitriou [21] bổ sung thêm một khía cạnh nhân tố con người mà các hệ ADAS thuần cảm biến thường ít khai thác: nhận diện hồ sơ và mẫu hành vi lái xe (driver profile/pattern) như một tín hiệu đầu vào cho đánh giá an toàn giao thông. Ba hướng nghiên cứu này — công nghệ cảm biến, khả giải, và nhân tố con người — cùng phác họa bối cảnh chung mà đề tài này góp phần vào: xây dựng một tầng hỗ trợ quyết định vừa chính xác vừa có thể diễn giải bằng ngôn ngữ tự nhiên (mục 1.1).

## 2.1. Phát hiện làn đường (Lane Detection)

Phát hiện làn đường là một trong những bài toán nhận thức nền tảng và được triển khai rộng rãi nhất của ADAS, làm cơ sở trực tiếp cho các tính năng cảnh báo chệch làn và hỗ trợ giữ làn kể trên. Trong khoảng một thập kỷ qua, hướng tiếp cận cho bài toán này đã chuyển dịch rõ rệt từ các phương pháp hình học truyền thống (dò biên, biến đổi Hough, fit đa thức) sang các kiến trúc học sâu, nhờ khả năng xử lý tốt hơn các điều kiện thực tế phức tạp như bóng đổ, vạch kẻ mờ, hay ánh sáng thay đổi.

Ultra-Fast-Lane-Detection-v2 (UFLD-v2) [1] là một kiến trúc phát hiện làn đường tốc độ cao tiêu biểu của hướng tiếp cận này, biểu diễn bài toán phát hiện làn dưới dạng phân loại theo lưới hàng/cột (hybrid anchor-driven ordinal classification) thay vì hồi quy tọa độ trực tiếp hay phân đoạn ngữ nghĩa (semantic segmentation) như các phương pháp trước đó. Kiến trúc này đạt tốc độ suy luận trên 300 khung hình/giây ở phiên bản nhẹ, trong khi vẫn giữ độ chính xác cạnh tranh — F1 = 76,0% trên tập kiểm thử CULane với backbone ResNet-34, đúng biến thể pretrained được sử dụng trong đề tài (`culane_res34.pth`). CULane [6] là benchmark chuẩn cho bài toán này (88,9 nghìn ảnh huấn luyện, 9,7 nghìn ảnh kiểm định, 34,7 nghìn ảnh kiểm thử), với đặc điểm dữ liệu chủ yếu là các tình huống đường đô thị đa dạng: giao lộ, mật độ giao thông cao, điều kiện ánh sáng thay đổi.

Bên cạnh UFLD-v2, một số kiến trúc khác đại diện cho các hướng thiết kế deep learning phổ biến khác cho bài toán này. LaneATT [39] đề xuất cơ chế anchor dạng đường thẳng (line anchor) kết hợp attention để tổng hợp đặc trưng dọc theo từng anchor, cho phép dùng backbone nhẹ mà vẫn đạt tốc độ suy luận thời gian thực — phù hợp triển khai trên phần cứng hạn chế tài nguyên, cùng định hướng thực dụng với đề tài này. CLRNet [33] tiếp cận theo hướng khác: kết hợp đặc trưng từ nhiều tầng mạng (cross-layer refinement) để tận dụng cả ngữ cảnh cục bộ lẫn toàn cục, cùng hàm mất mát Line IoU (LIoU) đo trực tiếp độ khớp hình học giữa làn dự đoán và ground truth thay vì hồi quy từng điểm rời rạc, đạt độ chính xác cao trên CULane tại thời điểm công bố. Khảo sát gần đây của He và cộng sự [40] hệ thống hóa các hướng thiết kế chính của lĩnh vực theo bốn trục — mô hình hóa tác vụ, tham số hóa làn đường, tăng cường ngữ cảnh toàn cục cho làn bị che khuất, và khử hiệu ứng phối cảnh cho bài toán 3D — cho thấy lĩnh vực vẫn đang phát triển tích cực cả ở không gian 2D lẫn hướng mở rộng sang 3D gần đây.

Hai công trình khảo sát khác đã hệ thống hóa lĩnh vực này ở giai đoạn sớm hơn: [7] tổng hợp kiến trúc mạng và mục tiêu tối ưu của các phương pháp phát hiện vạch kẻ đường dựa trên deep learning; [8] là một nghiên cứu tổng quan hệ thống (systematic literature review) trên 102 công trình công bố giai đoạn 2018–2021, cho thấy xu hướng chuyển dịch từ mô hình hình học truyền thống sang deep learning trong toàn ngành.

Chỉ số F1 = 76,0% nêu trên là một metric ở tầng phát hiện điểm ảnh (point-wise localization theo IoU), khác về bản chất với các metric được sử dụng ở mục 4.1 của đề tài — Accuracy và MAE của số làn suy ra được, một đại lượng ngữ nghĩa cấp cao hơn, được tính từ output của UFLD-v2 qua một tầng xử lý hậu kỳ do đề tài tự xây dựng. Hai loại metric này không thể so sánh trực tiếp và không nên bị nhầm lẫn khi đối chiếu số liệu giữa mục 4.1 của đề tài với F1 gốc của UFLD-v2 (mục 4.1).

Bên cạnh việc cải thiện thuật toán phát hiện, việc đánh giá chất lượng của các hệ thống hỗ trợ giữ làn (Lane Keeping Assistance Systems — LKAS) khi triển khai thực tế cũng là một hướng nghiên cứu riêng. Wei và cộng sự [28] tổng hợp các phương pháp đánh giá LKAS hiện có — từ nhóm chỉ số khách quan (độ lệch làn, thời gian phản ứng) đến nhóm phương pháp có tích hợp cảm nhận chủ quan của người lái — và chỉ ra rằng nhóm phương pháp thứ hai hiện vẫn ít được chuẩn hóa hơn. Quan sát này là một phần cơ sở cho việc đề tài bổ sung một tầng đánh giá LLM-as-a-judge, mang tính "cảm nhận" hơn, bên cạnh các chỉ số Accuracy/MAE/Precision khách quan ở mục 3.7.

## 2.2. Phát hiện biển báo giao thông (Traffic Sign Detection)

Nhận diện biển báo giao thông (Traffic Sign Recognition — TSR) là một tính năng ADAS đã được thương mại hóa rộng rãi, giúp xe nhắc nhở hoặc hỗ trợ tài xế tuân thủ giới hạn tốc độ, biển cấm, biển hiệu lệnh quan sát được trên đường; đây cũng là nguồn thông tin đầu vào trực tiếp cho các quy tắc giao thông mà một hệ hỗ trợ quyết định lái xe cần cân nhắc khi sinh khuyến nghị. YOLOv8 (Ultralytics) là kiến trúc object detection một giai đoạn (single-stage) hiện được sử dụng rộng rãi cho bài toán này nhờ cân bằng tốt giữa tốc độ và độ chính xác, phù hợp cho ứng dụng thời gian thực. TT100K (Tsinghua-Tencent 100K) [9] là benchmark quy mô lớn cho bài toán phát hiện và phân loại biển báo giao thông tại Trung Quốc, gồm khoảng 100.000 ảnh và 30.000 đối tượng biển báo được gán nhãn, với hệ thống mã hóa biển báo chi tiết theo loại: biển cấm ("p"), biển hiệu lệnh ("i"), biển cảnh báo ("w"), biển giới hạn tốc độ ("pl"/"il").

Trước khi các kiến trúc một giai đoạn như YOLO trở nên phổ biến, hướng tiếp cận hai giai đoạn cũng đã chứng minh hiệu quả cho bài toán này ở quy mô lớn hơn nhiều so với vài chục lớp thường dùng cho ứng dụng lái xe: Tabernik và Skočaj [41] dùng Mask R-CNN để giải quyết đồng thời phát hiện và phân loại hàng trăm loại biển báo, phục vụ mục tiêu tự động hóa kiểm kê biển báo trên diện rộng — một minh chứng cho thấy độ khó của bài toán TSR phụ thuộc mạnh vào số lượng lớp mục tiêu, không chỉ vào kiến trúc mô hình. Gần đây, các cơ chế attention/transformer cũng được tích hợp vào pipeline phát hiện biển báo nhằm cải thiện độ chính xác trên vật thể nhỏ và điều kiện ảnh suy giảm (sương mù, độ phân giải thấp) — hướng bổ trợ cho cách cải tiến YOLOv8n bằng BoTNet/ODConv/LSKA mà Ji và cộng sự [27] áp dụng bên dưới.

Trong dòng nghiên cứu gần đây ứng dụng YOLOv8 cho bài toán này, Logeswaran và cộng sự [26] xác nhận tính khả thi của YOLOv8 khi phát hiện đồng thời người đi bộ và biển báo giao thông trong thời gian thực, thử nghiệm trên hai bộ dữ liệu chuẩn tách biệt (Penn-Fudan cho người đi bộ, GTSRB cho biển báo). Phát hiện biển báo có kích thước nhỏ trong ảnh — do khoảng cách hoặc góc chụp — vẫn là một thách thức chung của bài toán này nói riêng và của các kiến trúc một giai đoạn nói chung; Ji và cộng sự [27] đề xuất hướng giải quyết bằng cách bổ sung các mô-đun BoTNet, ODConv và LSKA vào YOLOv8n, đạt cải thiện đáng kể về độ chính xác trên đối tượng nhỏ khi kiểm thử trên chính TT100K — cùng bộ dữ liệu được đề tài này sử dụng để tinh chỉnh YOLOv8n (mục 3.2). Đây là một hướng cải tiến kiến trúc khả thi cho module biển báo của đề tài trong các nghiên cứu tiếp theo, có thể đối chiếu với quan sát về mật độ và kích thước biển báo trên CULane ở mục 4.3.

## 2.3. Mô hình ngôn ngữ lớn đa phương thức cho hỗ trợ quyết định lái xe

Các công trình ứng dụng mô hình ngôn ngữ lớn đa phương thức cho lái xe có thể chia thành ba nhóm theo mức độ tích hợp với vòng lặp điều khiển, tổng hợp ở Bảng 2.1, trước khi đi vào phân tích chi tiết từng nhóm.

**Bảng 2.1.** Tổng hợp các công trình liên quan về LLM/VLM cho lái xe.

| Nhóm | Công trình | Đặc điểm kỹ thuật chính | Kết quả nổi bật đã công bố |
|---|---|---|---|
| End-to-end quy mô lớn | DriveGPT4 [2] | Sinh giải thích ngôn ngữ tự nhiên kèm tín hiệu điều khiển, huấn luyện end-to-end | — |
| | DriveLM [3] | Đóng khung lái xe dưới dạng Graph Visual Question Answering | — |
| | LMDrive [4] | Lái xe closed-loop end-to-end bằng LLM | — |
| Tầng tương tác/suy luận gắn thêm | Drive as You Speak [22] | LLM tool-use, suy luận reasoning-acting, tương tác cá nhân hóa | — |
| | DriveVLM [23] | Kiến trúc lai DriveVLM-Dual: VLM + pipeline truyền thống cho suy luận không gian | Kiểm chứng trên nuScenes + triển khai thực tế |
| | Mô hình ngôn ngữ nhẹ confidence-aware [24] | Chưng cất từ hệ đa-agent, có nhận biết độ tin cậy | SOTA trên benchmark nuPlan, độ trễ thấp |
| | Talk2BEV [25] | VLM trên biểu diễn bird's-eye-view, không huấn luyện riêng từng tác vụ | Talk2BEV-Bench, >20.000 câu hỏi trên nuScenes |
| Hybrid deep learning + MLLM | SafeRoute [11] / Advancing-AV-Intelligence [12] | Multimodal Adapter dung hợp đặc trưng CNN với embedding EVA-CLIP | ResNet-50 99,8% / YOLOv8 98,0% / RT-DETR 96,6% (biển báo); Question Overall Accuracy 82,83% (làn đường) |
| | DSC-LLM [13] | Đặc trưng hành vi (LSTM/transformer) + ngữ cảnh ảnh, dự đoán quỹ đạo | — |

**Tiền thân trước kỷ nguyên LLM.** Hong và cộng sự [10] đã đặt nền móng cho ý tưởng mã hóa ngữ nghĩa cấp cao của tình huống giao thông thành một biểu diễn có cấu trúc (dạng lưới không gian) để mô hình học sâu suy luận hành vi lái xe. Công trình này dùng mạng convolutional thuần túy, phù hợp với công cụ AI sẵn có tại thời điểm công bố; hạn chế duy nhất là chưa sinh được giải thích bằng ngôn ngữ tự nhiên — điều mà các mô hình ngôn ngữ lớn ra đời sau đó mới giải quyết được.

**VLM cho hiểu ngữ nghĩa giao thông, không gắn trực tiếp với quyết định điều khiển.** Song song với các hệ VLM/LLM gắn liền vòng lặp điều khiển hoặc sinh khuyến nghị hành vi (Bảng 2.1), một nhánh nghiên cứu khác dùng VLM thuần túy cho mô tả và hiểu ngữ nghĩa tình huống giao thông, không nhất thiết hướng tới sinh khuyến nghị hành vi. Rivera và cộng sự [42] dùng các VLM tổng quát (GPT-4, LLaVA) để tự động phân loại và chú thích ngữ nghĩa cảnh giao thông đô thị trên BDD100K mà không cần huấn luyện lại theo từng tập nhãn mới — một minh chứng trực tiếp cho khả năng VLM tổng quát hiểu ngữ cảnh giao thông ở chế độ training-free, cùng định hướng với tầng suy luận của đề tài này (mục 1.3). Fan và cộng sự [43] (MLLM-SUL) tiến thêm một bước: kết hợp bộ mã hóa thị giác hai nhánh với một LLM đã tinh chỉnh để đồng thời sinh mô tả ngữ nghĩa tình huống và định vị vùng rủi ro trên ảnh — hướng tiếp cận tinh chỉnh MLLM chuyên biệt, gần với nhóm hybrid ở Bảng 2.1 hơn là hướng VLM tổng quát không tinh chỉnh của đề tài này. Cả hai công trình cho thấy khả năng hiểu ngữ nghĩa giao thông của VLM đang được khai thác theo nhiều hướng — từ tự động hóa gán nhãn dữ liệu đến định vị rủi ro — nhưng phần lớn tập trung vào ngữ nghĩa tổng thể của cảnh (loại tình huống, đối tượng, mức rủi ro), chưa đi sâu vào ngữ nghĩa làn đường và biển báo có cấu trúc như đề tài này.

**Các hệ VLM/LLM lái xe end-to-end quy mô lớn.** Với sự xuất hiện của các mô hình ngôn ngữ lớn đa phương thức, một hướng nghiên cứu tích cực đã hình thành nhằm tích hợp trực tiếp khả năng suy luận ngôn ngữ vào pipeline lái xe end-to-end — tiêu biểu là DriveGPT4 [2], DriveLM [3] và LMDrive [4] (Bảng 2.1). Các hệ này đạt được khả năng diễn giải tích hợp sâu ngay trong vòng lặp điều khiển, đổi lại đòi hỏi huấn luyện hoặc tinh chỉnh trên tập dữ liệu lái xe quy mô lớn (nuScenes, CARLA...) cùng hạ tầng tính toán và dữ liệu đáng kể — một yêu cầu tài nguyên vượt quá quy mô khả thi của một đề tài nghiên cứu độc lập như đề tài này.

**Các hệ LLM/VLM đóng vai trò tầng tương tác/suy luận gắn thêm.** Song song với hướng end-to-end nêu trên, một nhóm công trình gần đây dùng LLM/VLM như một tầng suy luận hoặc tương tác gắn thêm vào pipeline lái xe sẵn có — Drive as You Speak [22], DriveVLM [23], mô hình ngôn ngữ nhẹ confidence-aware [24], và Talk2BEV [25] (Bảng 2.1) — gần với cách tiếp cận kỹ thuật của đề tài này hơn. Đáng chú ý, DriveVLM [23] thừa nhận rõ hạn chế của VLM thuần túy về suy luận không gian nên phải kết hợp với một pipeline truyền thống để bù đắp — một quan sát tương đồng với phát hiện ở mục 4.7 của đề tài này, nơi VLM tự nhận diện làn đường kém chính xác hơn pipeline chuyên biệt khi ảnh có vạch kẻ rõ. Yao và cộng sự [24] giải quyết bài toán chi phí suy luận — một ràng buộc quan trọng cho triển khai thời gian thực mà đề tài này chưa tối ưu (mục 5.3) — bằng cách chưng cất (distill) một mô hình ngôn ngữ nhẹ có nhận biết độ tin cậy từ một hệ đa-agent.

Bốn công trình trên đặt trọng tâm vào những mục tiêu khác với câu hỏi nghiên cứu cốt lõi của đề tài này: cải thiện khả năng tương tác và cá nhân hóa [22], mở rộng khả năng suy luận không gian trong tình huống phức tạp [23], tối ưu chi phí/độ trễ suy luận [24], hoặc mở rộng không gian biểu diễn sang BEV [25]. Vì trọng tâm khác nhau, câu hỏi cụ thể mà đề tài này đặt ra ở mục 4.5 — tách bạch định lượng đóng góp của thông tin có cấu trúc so với ảnh thô trong cùng một mô hình cố định — chưa được đặt ra trực tiếp trong nhóm công trình này; đây là một hướng bổ trợ mà đề tài hy vọng đóng góp thêm cho dòng nghiên cứu chung.

**Các công trình gần nhất với đề tài.** Cùng hướng kết hợp deep learning chuyên biệt với multimodal LLM cho ngữ nghĩa giao thông, SafeRoute [11] và công trình tiền thân "Advancing Autonomous Vehicle Intelligence" [12] — của cùng một nhóm tác giả — xây dựng một pipeline thống nhất dung hợp đặc trưng CNN với embedding ngôn ngữ ở tầng biểu diễn (Bảng 2.1), đạt độ chính xác nhận diện biển báo và hiểu làn đường đều cao — cho thấy hướng dung hợp thông tin ở tầng embedding mang lại hiệu năng mạnh khi có đủ dữ liệu và tài nguyên để tinh chỉnh MLLM. Tương tự, DSC-LLM [13] kết hợp đặc trưng hành vi với ngữ cảnh giao thông trích xuất từ ảnh để dự đoán quỹ đạo kèm suy luận rủi ro có giải thích bằng LLM.

Đề tài này chọn một điểm thiết kế khác cho tầng dung hợp thông tin: thay vì dung hợp ở tầng embedding như SafeRoute/Advancing-AV-Intelligence, đề tài dung hợp ở tầng prompt/văn bản — thông tin ngữ nghĩa có cấu trúc được nhúng trực tiếp vào prompt của một VLM tổng quát, không tinh chỉnh. Lựa chọn này đơn giản hơn về triển khai và không đòi hỏi dữ liệu huấn luyện MLLM riêng, đổi lại phụ thuộc nhiều hơn vào chất lượng thiết kế prompt và nhiều khả năng không đạt độ chính xác nhận diện cao bằng một mô hình được tinh chỉnh chuyên biệt như SafeRoute. Ngoài khác biệt kiến trúc, mục tiêu chính của SafeRoute/Advancing-AV-Intelligence/DSC-LLM là tối đa hóa độ chính xác nhận diện và dự đoán quỹ đạo, nên các công trình này cũng chưa đặt trọng tâm vào việc tách bạch định lượng đóng góp của thông tin có cấu trúc so với ảnh thô (câu hỏi nghiên cứu cốt lõi, mục 4.5), hay kiểm chứng độ tin cậy của phương pháp đánh giá bằng đối chiếu với con người (mục 4.6) — hai khía cạnh là trọng tâm phương pháp luận riêng của đề tài này.

Nhìn chung, đề tài này khác về trọng tâm thiết kế so với cả nhóm tầng tương tác/suy luận gắn thêm và nhóm hybrid deep learning + MLLM nêu trên: thay vì huấn luyện hoặc tinh chỉnh một mô hình chuyên biệt ở tầng suy luận, đề tài tận dụng một VLM tổng quát đã huấn luyện sẵn, không tinh chỉnh (truy cập qua API theo chuẩn OpenAI-compatible của NVIDIA NIM), kết hợp với một mô-đun tiền xử lý ngữ nghĩa từ các mô hình nhận diện chuyên biệt — trong đó UFLD-v2 được dùng nguyên trạng ở dạng pretrained, còn YOLOv8n cho bài toán biển báo được tự tinh chỉnh trên TT100K (mục 3.2), một bước huấn luyện quy mô nhẹ so với việc huấn luyện lại một VLM/LLM hay thu thập dữ liệu lái xe quy mô lớn như ở các hệ end-to-end. Sự đánh đổi này tránh được chi phí huấn luyện/tinh chỉnh một VLM/LLM quy mô lớn và cho phép triển khai nhanh, phù hợp với quy mô một đề tài nghiên cứu độc lập — dù có thể đổi lại một phần độ chính xác so với các hệ được huấn luyện/tinh chỉnh chuyên biệt với đầy đủ tài nguyên.

## 2.4. Đánh giá chất lượng output ngôn ngữ tự nhiên bằng LLM-as-a-Judge

Nhu cầu đánh giá chuẩn hóa các hệ LLM và AI agent đang tăng nhanh cùng tốc độ phát triển của lĩnh vực. Một khảo sát gần đây [14] hệ thống hóa các benchmark và framework đánh giá LLM/agent công bố trong giai đoạn 2019–2025, cho thấy đây vẫn là một lĩnh vực đang định hình, chưa có phương pháp luận thống nhất — điều này càng củng cố lý do đề tài tự kiểm chứng độ tin cậy của phương pháp đánh giá thay vì áp dụng nguyên trạng mà không kiểm chứng.

Việc đánh giá chất lượng của một khuyến nghị lái xe dạng văn bản tự nhiên là bài toán khó lượng hóa bằng các metric cứng truyền thống (accuracy, F1...) vì không tồn tại một "đáp án đúng duy nhất". Phương pháp LLM-as-a-judge — sử dụng một LLM mạnh làm "giám khảo" tự động chấm điểm theo rubric cho trước — đã được áp dụng rộng rãi trong các benchmark đánh giá LLM gần đây, tiêu biểu là phương pháp luận của MT-Bench và Chatbot Arena [5], cũng như AlpacaEval. Trên MT-Bench, GPT-4 khi làm judge đạt 85% đồng thuận với chuyên gia con người (trên các cặp so sánh không hòa), một mức xấp xỉ độ đồng thuận giữa người với người (81%) — cho thấy LLM-as-a-judge có thể đạt độ tin cậy tiệm cận con người trong điều kiện phù hợp, dù vẫn tồn tại các thiên lệch cố hữu (thiên vị độ dài câu trả lời, thiên vị phong cách viết, tự thiên vị giữa các mô hình cùng họ) cần được kiểm chứng riêng cho từng bài toán ứng dụng cụ thể. Đây chính là cách tiếp cận được áp dụng trong đề tài này (mục 3.7 và 4.6), với quy mô kiểm chứng nhỏ hơn (N=20 so với hàng nghìn cặp trong MT-Bench gốc) do giới hạn nguồn lực của một đề tài cá nhân.

Việc sử dụng một mẫu kiểm chứng con người quy mô nhỏ, thay vì chấm tay toàn bộ dữ liệu, có cơ sở phương pháp luận riêng trong các nghiên cứu gần đây. Kim [15] đề xuất một khung lấy mẫu hai giai đoạn — LLM chấm toàn bộ dữ liệu, con người chỉ chấm một mẫu con được chọn có chủ đích tại những nơi dự đoán của LLM kém tin cậy nhất — và nhấn mạnh rằng y văn hiện thiếu hướng dẫn chính thức về việc cần bao nhiêu giám sát của con người là đủ khi kiểm chứng một benchmark. Saha và cộng sự [16] đề xuất phân bổ truy vấn thích ứng theo phương sai thay vì phân bổ đều, nhằm giảm sai số ước lượng trong một ngân sách tính toán cố định. Pan và cộng sự [17] phỏng vấn tám chuyên gia và nhấn mạnh nhu cầu hỗ trợ xây dựng tiêu chí đánh giá khớp với kỳ vọng của người dùng thực tế — định hướng cho cách thiết kế rubric sáu tiêu chí của đề tài (mục 3.7). Đề tài hiện sử dụng N=20 mẫu chọn ngẫu nhiên, chưa áp dụng cơ chế lấy mẫu thích ứng theo phương sai; đây là một hướng cải tiến khả thi được nêu ở mục 5.4.

Chất lượng của chính dữ liệu đánh giá — không chỉ chất lượng của công cụ đánh giá — cũng là một mối quan tâm được nêu trong y văn gần đây. Emami và cộng sự [29] tổng quan vai trò của con người trong vòng lặp huấn luyện/kiểm định (human-in-the-loop) đối với xe tự hành an toàn và có đạo đức, nhấn mạnh rằng gán nhãn dữ liệu vẫn là nút thắt cổ chai chính — phù hợp với trải nghiệm thực tế của đề tài này khi phải tự gán nhãn tay toàn bộ 200+200 ảnh CULane/real-life (mục 3.2). Fernández Llorca và cộng sự [30] đánh giá độ thiên lệch (bias) trong các bộ dữ liệu thị giác phổ biến cho xe tự hành, phát hiện mức độ đa dạng rất thấp ở nhiều thuộc tính nhân khẩu học của người đi bộ — một lời nhắc rằng ngay cả các bộ dữ liệu chuẩn như CULane/TT100K, dù được đề tài này lựa chọn vì tính phổ biến và khả năng đối sánh (mục 1.1), cũng có thể mang thiên lệch tiềm ẩn chưa được kiểm chứng trong phạm vi đề tài này.

## 2.5. Khoảng trống nghiên cứu

Trong phạm vi các công trình được khảo sát ở Chương này, năm hướng nghiên cứu liên quan để lại các khoảng trống khác nhau mà đề tài này hướng tới:

1. ADAS truyền thống (dựa trên UFLD-v2, YOLOv8...) đạt độ chính xác và tốc độ xử lý tốt ở tầng nhận diện, nhưng output dừng lại ở dạng tọa độ, bounding box, class ID — chưa có tầng suy luận ngôn ngữ tự nhiên có thể diễn giải được cho người lái.
2. Các hệ VLM lái xe end-to-end quy mô lớn (DriveGPT4, DriveLM, LMDrive) giải quyết tốt bài toán diễn giải nhờ tích hợp sâu vào vòng lặp điều khiển, nhưng đòi hỏi huấn luyện hoặc tinh chỉnh trên dữ liệu lái xe quy mô lớn — chi phí và ngưỡng gia nhập cao đối với một đề tài nghiên cứu độc lập.
3. Các hệ LLM/VLM đóng vai trò tầng tương tác/suy luận gắn thêm vào pipeline sẵn có (Drive as You Speak, DriveVLM, Talk2BEV, mô hình ngôn ngữ nhẹ có nhận biết độ tin cậy — mục 2.3) đạt nhiều kết quả mạnh trong phạm vi mục tiêu riêng của từng công trình, và gần với cách tiếp cận kỹ thuật của đề tài này nhất (VLM tổng quát, không tinh chỉnh); tuy nhiên nhóm này đặt trọng tâm vào tương tác, suy luận không gian, hoặc tối ưu độ trễ hơn là tách bạch định lượng đóng góp của thông tin có cấu trúc, và phần lớn hoạt động trên không gian biểu diễn khác (BEV, tín hiệu điều khiển) thay vì ngữ nghĩa làn đường/biển báo có cấu trúc như đề tài này.
4. Các hệ hybrid deep learning + MLLM gần đây (SafeRoute, Advancing-AV-Intelligence, DSC-LLM — mục 2.3) gần nhất về mục tiêu với đề tài này và đạt độ chính xác nhận diện rất cao nhờ dung hợp thông tin ở tầng embedding; điểm khác biệt chủ yếu là nhóm này chưa đặt trọng tâm vào việc tách bạch định lượng đóng góp của thông tin có cấu trúc so với ảnh thô, cũng như chưa kiểm chứng độ tin cậy của phương pháp đánh giá bằng đối chiếu con người — hai khía cạnh là trọng tâm phương pháp luận của đề tài này.
5. VLM tổng quát dùng nguyên trạng (không qua tiền xử lý ngữ nghĩa) có năng lực cảm nhận thị giác tốt — phù hợp quan sát của [42] rằng VLM tổng quát hiểu được ngữ cảnh giao thông đô thị mà không cần huấn luyện lại, và được đề tài này kiểm chứng lại ở mục 4.7 — nhưng không được thiết kế chuyên biệt cho ngữ nghĩa làn đường/biển báo có cấu trúc; như đề tài này cho thấy định lượng ở mục 4.5, việc thiếu một mô-đun ngữ nghĩa có cấu trúc như vậy làm giảm rõ rệt chất lượng khuyến nghị so với khi có mô-đun đó.

Đề tài định vị gần nhóm (4) nhất về mục tiêu (kết hợp deep learning chuyên biệt với LLM đa phương thức cho ngữ nghĩa giao thông), nhưng chọn hướng triển khai kỹ thuật ở tầng suy luận gần nhóm (3) và (5) hơn — dùng VLM tổng quát không tinh chỉnh thay vì huấn luyện/tinh chỉnh một mô hình chuyên biệt. Cụ thể, đề tài kết hợp: tầng nhận diện chuyên biệt đã được kiểm chứng như nhóm (1) — UFLD-v2 dùng nguyên trạng ở dạng pretrained, YOLOv8n cho biển báo được tự tinh chỉnh trên TT100K (mục 3.2), một bước huấn luyện quy mô nhẹ so với việc huấn luyện một VLM/LLM; mô-đun chuyển đổi ngữ nghĩa có cấu trúc tự thiết kế, đóng góp chính về mặt kỹ thuật, khác biệt rõ với cách biểu diễn BEV/embedding của nhóm (3)/(4); tầng suy luận VLM tổng quát không tinh chỉnh như nhóm (3)/(5); và một phương pháp luận đánh giá định lượng nghiêm ngặt, có kiểm chứng độ tin cậy của chính công cụ đánh giá bằng đối chiếu con người và đa-judge — một khoảng trống mà cả nhóm (3) lẫn nhóm (4) đều chưa lấp đầy trong các công trình đã khảo sát.

**Tóm tắt chương.** Chương này đã tổng quan các công trình liên quan theo bốn thành phần của đề tài — phát hiện làn đường, phát hiện biển báo, mô hình ngôn ngữ lớn đa phương thức cho lái xe, và phương pháp luận LLM-as-a-judge — và xác định năm khoảng trống nghiên cứu cụ thể mà đề tài này góp phần lấp đầy (mục 2.5). Chương 3 tiếp theo trình bày chi tiết phương pháp luận được xây dựng để giải quyết các khoảng trống đó, bắt đầu từ kiến trúc hệ thống tổng thể.

---

# CHƯƠNG 3. PHƯƠNG PHÁP LUẬN

Trước khi trình bày chi tiết từng thành phần, phần mở đầu này phát biểu hình thức bài toán ngữ nghĩa làn đường mà đề tài giải quyết, làm cơ sở thống nhất ký hiệu cho toàn bộ chương.

**Đầu vào.** Đơn vị xử lý của toàn bộ pipeline là một ảnh dashcam rời rạc $I$ — một khung hình tĩnh trích từ video hành trình hoặc chụp trực tiếp, không phải một luồng video được xử lý liên tục theo thời gian: hệ thống xử lý từng ảnh độc lập, không sử dụng thông tin từ khung hình trước hay sau. $I$ là ảnh màu 3 kênh (RGB); kích thước $\text{image\_width} \times \text{image\_height}$ thay đổi theo nguồn dữ liệu (1640×590 với CULane, 1280×720 với bộ real-life — mục 3.2).

Mô hình phát hiện làn đường UFLD-v2 nhận $I$ làm đầu vào và trả về một tập đường biên $B = \{b_1, b_2, \ldots, b_n\}$, mỗi đường biên $b_i$ là một danh sách điểm ảnh $\{(x, y)\}$ dọc theo vạch kẻ quan sát được — đây là đầu ra thô, cấp điểm ảnh, chưa mang ngữ nghĩa quyết định. **Nhiệm vụ** của mô-đun phân tích ngữ nghĩa (mục 3.3) là ánh xạ tập đường biên thô $B$ này thành một bộ ngữ nghĩa cấp quyết định $S = (\ell, o, c, N)$, trong đó:

- $\ell$ (ego lane) — cặp đường biên $(b_i, b_{i+1}) \subset B$ xác định làn xe đang di chuyển, kèm độ tin cậy;
- $o$ (vehicle offset) — độ lệch $\Delta x$ giữa tâm làn ego và tâm ảnh, biểu diễn dưới dạng pixel và phần trăm bề rộng làn;
- $c$ (road shape) — phân loại hình dạng đường tổng thể (thẳng/cong nhẹ/cong gắt — `straight`/`gentle`/`sharp` trong output) kèm hướng cong;
- $N$ — số làn lân cận bên trái/phải làn ego.

Song song, mô hình phát hiện biển báo YOLOv8n nhận $I$ làm đầu vào, trả về tập $D = \{(cls_j, box_j)\}$ gồm nhãn lớp và tọa độ khung bao của từng biển báo phát hiện được.

**Về định dạng biểu diễn.** Bộ ngữ nghĩa $S$ và tập $D$ tự thân là các cấu trúc dữ liệu trừu tượng — một tập giá trị và nhãn — không gắn với bất kỳ định dạng tuần tự hóa (serialization) cụ thể nào. Để đưa được vào ngữ cảnh văn bản của một mô hình ngôn ngữ, $S$ và $D$ cần được **hiện thực hóa** thành một chuỗi ký tự có cấu trúc; đề tài chọn **JSON** làm định dạng hiện thực hóa (mục 3.4).

**Lý do chính: JSON đóng vai trò kép, không chỉ là ngữ cảnh cho VLM.** Bản hiện thực hóa của $S$/$D$ không chỉ được dùng làm input cho VLM ở chế độ chỉ-ngữ-nghĩa và chế độ kết hợp — nó còn là artifact duy nhất được dùng để **so sánh tự động, theo từng trường, với ground truth gán tay** xuyên suốt Chương 4: tính Accuracy/MAE cho số làn, làn ego, hình dạng đường trên N=200+200 ảnh (mục 4.1–4.3), và đối chiếu trực tiếp với output của chính VLM trong thí nghiệm tự nhận diện (mục 4.7). Một văn bản tự do mô tả cùng nội dung sẽ cần thêm một tầng trích xuất/phân tích cú pháp riêng để so sánh tự động trên hàng trăm ảnh — một nguồn lỗi và chi phí phát triển mới. Nói cách khác, JSON được chọn trước hết vì lý do vận hành của chính pipeline đánh giá, không phải vì một ưu thế được chứng minh chắc chắn về khả năng suy luận của VLM khi đọc JSON so với đọc văn bản tự do.

Hai lý do phụ khác được cân nhắc nhưng không phải căn cứ quyết định: JSON có overhead token thấp hơn XML khoảng 14–16% theo một benchmark mã nguồn mở [45]; và bằng chứng về việc ép output theo khuôn định dạng chặt (JSON-mode) cải thiện hay làm giảm khả năng suy luận của LLM là không nhất quán trong y văn [44, 46] — đề tài không dùng đây làm căn cứ, và vì lý do tương tự, khối hướng dẫn định dạng cho output của VLM (mục 3.5) chỉ yêu cầu cấu trúc ba phần bằng ngôn ngữ tự nhiên, không ép JSON-mode.

Về nguyên tắc, $S$ và $D$ có thể được hiện thực hóa bằng bất kỳ định dạng có cấu trúc nào khác (YAML, XML, hay một đoạn văn bản mô tả theo mẫu cố định, miễn có tầng trích xuất tương ứng cho việc đánh giá tự động) mà không thay đổi bản chất phương pháp — JSON là một lựa chọn triển khai thực dụng, không phải một yêu cầu bắt buộc của phương pháp luận đề xuất.

Bộ ngữ nghĩa $S$ và tập $D$, sau khi chuẩn hóa thành hai biểu diễn JSON — đầy đủ và rút gọn (mục 3.4) — làm đầu vào cho tầng suy luận: một mô hình ngôn ngữ lớn đa phương thức $M$ nhận ảnh $I$ và/hoặc thông tin ngữ nghĩa có cấu trúc, sinh khuyến nghị lái xe $R$ dưới dạng văn bản tự nhiên có cấu trúc ba phần (mục 3.5). Câu hỏi nghiên cứu cốt lõi (mục 1.1) chính là so sánh định lượng chất lượng của $R$ khi $M$ lần lượt nhận $(I)$, $(S)$, hay $(I, S)$ làm đầu vào — luận văn gọi ba cách cấp đầu vào này là **chế độ chỉ-ảnh** $(I)$, **chế độ chỉ-ngữ-nghĩa** $(S)$, và **chế độ kết hợp** $(I,S)$. Trong mã nguồn và cấu hình gọi API, ba chế độ này được định danh lần lượt là `image_only`, `json_only`, `image_json` (hoặc `image+json`); từ đây trở đi, toàn bộ luận văn — kể cả tên cột trong các bảng số liệu ở Chương 4 — dùng tên tiếng Việt mô tả (chỉ-ảnh, chỉ-ngữ-nghĩa, kết hợp) thay cho định danh kỹ thuật này.

Các mục 3.1–3.7 tiếp theo trình bày chi tiết từng thành phần của pipeline theo đúng thứ tự xử lý: kiến trúc tổng thể, dữ liệu, thuật toán suy ra $S$ từ $B$ (mục 3.3), cấu trúc JSON cụ thể (mục 3.4), thiết kế prompt sinh $R$ (mục 3.5), lựa chọn mô hình $M$ (mục 3.6), và phương pháp luận đánh giá $R$ (mục 3.7).

## 3.1. Kiến trúc hệ thống tổng thể

Pipeline của đề tài gồm bốn giai đoạn xử lý tuần tự, minh họa ở Hình 3.1: hai tầng dựa trên mô hình học sâu (nhận diện, suy luận), nối với nhau qua một mô-đun xử lý ngữ nghĩa thuần thuật toán — không chứa tham số học được — và khép lại bằng một tầng đánh giá. Tên tiếng Anh trong ngoặc ở mỗi giai đoạn là thuật ngữ chuẩn được dùng thống nhất xuyên suốt luận văn.

![Hình 3.1. Kiến trúc tổng thể của pipeline bốn giai đoạn.](figures/hinh_3_1_kien_truc.png)

**Hình 3.1.** Kiến trúc tổng thể của pipeline bốn giai đoạn. Đường viền nét đứt của mô-đun 2 đánh dấu trực quan sự khác biệt: đây là mô-đun thuật toán/quy tắc, không phải một tầng mô hình học sâu như ba giai đoạn còn lại (chú giải ở cuối hình).

Việc gọi giai đoạn 2 là "mô-đun" thay vì "tầng" là có chủ đích: khác với ba giai đoạn còn lại — vốn đều là mô hình đã huấn luyện (UFLD-v2, YOLOv8n, VLM, LLM-as-a-judge) — mô-đun phân tích ngữ nghĩa là một chuỗi quy tắc và công thức hình học do tác giả tự thiết kế (mục 3.3), không có tham số học được, nên không nên gọi là "tầng" theo nghĩa một layer của mạng học sâu.

**Mô hình sử dụng ở tầng nhận diện.** Giai đoạn đầu tiên gồm hai mô hình phát hiện chuyên biệt, độc lập với nhau, chạy song song trên cùng một ảnh đầu vào $I$:

- *Phát hiện làn đường*: UFLD-v2, backbone ResNet-34, dùng nguyên bản pretrained trên CULane (`culane_res34.pth`), không tinh chỉnh thêm.
- *Phát hiện biển báo*: YOLOv8n (biến thể nhỏ nhất trong họ YOLOv8, khoảng 3,2 triệu tham số), được tự tinh chỉnh (fine-tune) trên tập con 50 lớp phổ biến của TT100K, khởi tạo từ checkpoint YOLOv8n gốc (pretrained trên COCO). Cấu hình huấn luyện:
  - Độ phân giải ảnh đầu vào: 640×640; batch size tự động (`batch=-1`).
  - Bộ tối ưu SGD, learning rate khởi tạo `lr0=0,01`, momentum `0,937`, weight decay `0,0005`, warm-up 3 epoch.
  - Tối đa 100 epoch, cơ chế dừng sớm `patience=30` (dừng nếu không cải thiện sau 30 epoch liên tiếp).

  Do giới hạn thời gian phiên làm việc của môi trường huấn luyện (Kaggle), quá trình bị ngắt giữa chừng ở epoch 82 và được chạy tiếp (resume) từ checkpoint gần nhất cho tới khi hoàn tất. Đây là một bước tinh chỉnh tiêu chuẩn, quy mô nhẹ so với việc huấn luyện hoặc tinh chỉnh một VLM/LLM trên dữ liệu lái xe quy mô lớn như ở các hệ end-to-end được khảo sát ở mục 2.3 (DriveGPT4, DriveLM, LMDrive, SafeRoute). Định hướng training-free của đề tài (Tóm tắt) áp dụng riêng cho tầng suy luận VLM (mục 3.6); tầng nhận diện không nằm trong phạm vi claim đó — UFLD-v2 dùng nguyên bản pretrained, còn YOLOv8n có đúng một bước tinh chỉnh nhẹ này.

## 3.2. Dữ liệu

**Bộ dữ liệu chính (CULane).** 200 ảnh được lấy ngẫu nhiên từ dataset CULane (độ phân giải 1640×590), đại diện cho các tình huống đô thị đa dạng: đường thẳng, cua nhẹ, giao lộ, mật độ giao thông khác nhau. Ground truth được gán nhãn thủ công cho toàn bộ 200/200 ảnh, gồm: số làn thực tế cùng chiều, loại đường (thẳng/cong nhẹ/cong gắt kèm hướng), số làn bị phát hiện nhầm, số làn ngược chiều bị gộp nhầm, độ chính xác xác định làn ego, số biển báo thật, số detection đúng/sai. Toàn bộ kết quả trong Chương 4 — cả các kết quả dựa trên ground truth lẫn các kết quả dựa trên LLM-as-a-judge — sử dụng đầy đủ N=200.

**Bộ dữ liệu kiểm chứng độc lập (real-life).** 200 khung hình được trích xuất từ video dashcam thực tế (độ phân giải 1280×720), gán nhãn thủ công theo cùng schema như trên. Mục đích của bộ dữ liệu này là kiểm chứng khả năng tổng quát hóa của hệ thống trên dữ liệu hoàn toàn độc lập với dữ liệu huấn luyện của mô hình phát hiện làn đường (thảo luận về rủi ro data leakage được trình bày ở mục 4.9).

## 3.3. Phân tích ngữ nghĩa làn đường

Đây là mô-đun xử lý do tác giả tự thiết kế và cài đặt — một chuỗi quy tắc và công thức hình học tường minh, không chứa tham số học được, nên không được gọi là "tầng" theo nghĩa layer của mạng học sâu (mục 3.1) — chuyển đổi danh sách điểm ảnh thô của từng đường biên (do UFLD-v2 trả về) thành bốn ngữ nghĩa cấp quyết định: làn ego, độ lệch tâm xe, hình dạng đường, và làn lân cận — cấu thành đóng góp 1 của đề tài (mục 1.3).

### Tiền xử lý: sắp xếp đường biên theo vị trí thực tế

**Đầu vào và đầu ra.** Đầu vào của bước này là tập đường biên thô $B = \{b_1, \ldots, b_n\}$ do UFLD-v2 trả về, theo thứ tự nội bộ của mô hình — thứ tự chỉ số này được UFLD-v2 gán cố định theo kiến trúc mạng (mỗi chỉ số ứng với một "lane slot" cố định của mô hình), không đảm bảo tương ứng với thứ tự trái–phải thực tế trên ảnh. Vì bước xác định làn ego ngay sau đây (mục kế tiếp) hoạt động bằng cách so sánh các cặp đường biên *liền kề về vị trí không gian*, danh sách $B$ bắt buộc phải được sắp xếp lại theo tọa độ x trước khi xử lý tiếp. Đầu ra của bước này là một danh sách đường biên đã sắp xếp trái sang phải theo tọa độ x thực tế, cùng ánh xạ giữa chỉ số gốc do UFLD-v2 gán (`original_index`) và chỉ số sau khi sắp xếp (`sorted_index`) — danh sách này là đầu vào trực tiếp cho bước xác định làn ego.

**Cách sắp xếp.** Việc sắp xếp dựa trên tọa độ x của mỗi đường biên tại một hàng ảnh tham chiếu duy nhất, để mọi đường biên được so sánh tại cùng một độ sâu ảnh:

$$y_{ref} = 0{,}95 \times \text{image\_height}$$

Hệ số 0,95 không phải một giá trị hiệu chỉnh bằng số liệu thực nghiệm, mà là một lựa chọn thực tế dựa trên đặc điểm hình học của ảnh dashcam: đây là hàng ảnh gần đáy ảnh nhất mà dashcam vẫn còn quan sát được mặt đường (các hàng sát đáy hơn thường bị nắp capo xe che khuất), đồng thời là vùng ảnh gần camera nhất nên đường biên ít bị che khuất hoặc đứt đoạn nhất — tăng khả năng UFLD-v2 đã phát hiện đủ điểm tại đó.

Tọa độ x tại $y_{ref}$ được nội suy bằng trung bình các điểm của đường biên trong khoảng $|y - y_{ref}| \le 30$ pixel; nếu không có điểm nào đủ gần (đường biên bị che khuất hoặc kết thúc sớm trước khi tới $y_{ref}$), tọa độ được ngoại suy bằng fit bậc 1 qua toàn bộ điểm sẵn có của đường biên đó. Cách này thay thế một phiên bản trước đó, vốn gán tạm $+\infty$ khi thiếu điểm gần — khiến đường biên luôn bị đẩy về cuối danh sách sắp xếp (tương đương bị coi là ở rìa phải ảnh) bất kể vị trí thực tế, làm sai phân loại làn lân cận trái/phải.

### Xác định làn ego

**Giả thiết nền tảng.** Toàn bộ thuật toán xác định làn ego — và mục "Độ lệch tâm xe" ngay sau đây — dựa trên một giả thiết về vị trí lắp đặt camera, cần được phát biểu tường minh vì mọi tính toán phía sau đều phụ thuộc vào nó: **dashcam được giả định lắp đặt tại vị trí chính giữa theo chiều ngang của xe** (ví dụ gắn trên kính chắn gió gần gương chiếu hậu trung tâm — cách lắp phổ biến nhất với dashcam tiêu dùng), không lệch trái/phải. Với giả thiết này, tâm ảnh theo chiều ngang được dùng làm xấp xỉ cho vị trí thực tế của xe trên đường:

$$x_{veh} = \text{image\_width}/2$$

Đây là một giả thiết đơn giản hóa bắt buộc: hệ thống không có dữ liệu hiệu chỉnh camera (calibration) hay thông số lắp đặt thực tế cho từng nguồn ảnh (CULane, real-life), nên không thể tính offset thật của camera so với tâm xe. Với ảnh mà camera lệch tâm đáng kể so với giả thiết này, độ lệch tâm xe suy ra được sẽ mang sai số hệ thống theo đúng chiều lệch của camera — hạn chế này được ghi nhận lại ở mục 5.3.

**Trực giác của thuật toán.** Với $n$ đường biên đã sắp xếp trái sang phải, làn ego là cặp đường biên liền kề bao quanh $x_{veh}$ hợp lý nhất. Coi mỗi cặp đường biên kề nhau $(b_i, b_{i+1})$ là một "khe" — thuật toán duyệt qua tất cả các khe và tính một điểm phạt cho từng khe (khe nào điểm phạt thấp nhất được chọn làm làn ego):

$$\text{score}_i = \underbrace{\left| \frac{x_i + x_{i+1}}{2} - x_{veh} \right|}_{\text{(a) khoảng cách tâm khe} \to \text{tâm xe}} \times \underbrace{p_{between}}_{\text{(b) ưu tiên khe chứa xe}} \times \underbrace{\left(1 + 0{,}2 \times \frac{|w_i - w_{exp}|}{w_{exp}}\right)}_{\text{(c) phạt bề rộng bất thường}}$$

- **(a) Khoảng cách tâm khe đến tâm xe** — $\left|\frac{x_i+x_{i+1}}{2} - x_{veh}\right|$: thành phần chính. Khe nào có điểm giữa gần $x_{veh}$ nhất thì càng có khả năng là làn ego.
- **(b) Ưu tiên khe thực sự chứa $x_{veh}$** — hệ số $p_{between}$ bằng 0,5 nếu $x_{veh}$ nằm giữa $x_i$ và $x_{i+1}$ (xe "đứng trong" khe này), và bằng 1 nếu $x_{veh}$ nằm ngoài khe. Vì $\text{score}_i$ càng thấp càng được ưu tiên, nhân với 0,5 làm giảm điểm phạt của khe chứa xe thật sự xuống còn một nửa — đảm bảo khe đó luôn được xếp trước các khe không chứa xe khi (a) xấp xỉ bằng nhau giữa các khe. Giá trị 0,5 chỉ mang vai trò xếp hạng ưu tiên tương đối, là một lựa chọn thiết kế thực tế để tránh chọn nhầm sang khe liền kề, không phải một xác suất hay tham số được hiệu chỉnh bằng số liệu.
- **(c) Phạt bề rộng bất thường** — $w_i = x_{i+1}-x_i$ là bề rộng thực của khe, đối chiếu với bề rộng làn "điển hình" giả định $w_{exp} = 0{,}15 \times \text{image\_width}$ (ước lượng thực tế theo tỉ lệ bề rộng làn đường thường chiếm trong ảnh dashcam ở góc chụp tiêu chuẩn của CULane và bộ real-life, không phải một giá trị đo thống kê chính thức). Khe có bề rộng lệch nhiều so với $w_{exp}$ — thường do một đường biên bị phát hiện sai — bị phạt thêm theo hệ số 0,2; trọng số này được chọn qua thử nghiệm để (c) chỉ đóng vai trò điều chỉnh phụ, chỉ đủ mạnh để phá vỡ thứ hạng khi bề rộng khe sai lệch rõ rệt, không lấn át vai trò chính của (a).

Khe có $\text{score}_i$ nhỏ nhất được chọn làm làn ego. Cách tính điểm động theo từng ảnh (thay vì giả định làn ego luôn nằm ở một vị trí cố định, ví dụ luôn là cặp đường biên thứ 2–3) cho phép xử lý cả trường hợp bất đối xứng: đường cong khiến khoảng cách giữa các đường biên không đều, hoặc UFLD-v2 chỉ phát hiện được đường biên ở một phía.

**Độ tin cậy.** Được suy trực tiếp từ khoảng cách $d$ giữa tâm làn ego đã chọn và tâm ảnh ($w$ = image_width), không suy trực tiếp từ $\text{score}_i$ (vốn không có thang đo cố định để diễn giải thành xác suất):

| Điều kiện | $d < 0{,}1w$ | $d < 0{,}25w$ | $d < 0{,}4w$ | còn lại |
|---|---|---|---|---|
| Độ tin cậy | 0,95 | 0,8 | 0,6 | 0,4 |

Bốn ngưỡng 0,1w/0,25w/0,4w và bốn mức độ tin cậy tương ứng là các mốc phân đoạn thực tế, không phải phân vị đo được từ dữ liệu — phản ánh trực giác rằng làn ego lệch tâm dưới 10% bề rộng ảnh gần như chắc chắn đúng, trong khi lệch tới 40% vẫn được chấp nhận nhưng ở độ tin cậy thấp, vì ở mức lệch lớn như vậy khả năng UFLD-v2 đã bỏ sót một đường biên gần tâm ảnh hơn tăng lên đáng kể.

Trường hợp chỉ phát hiện một đường biên ($n=1$): đường biên đó được gán làm ranh giới phải của làn ego, độ tin cậy cố định 0,5.

Trường hợp không phát hiện đường biên nào ($n=0$): toàn bộ chuỗi xử lý phía trên (sắp xếp, xác định làn ego, độ lệch tâm, phân loại độ cong) bị bỏ qua ngay từ đầu, trước khi output rỗng của UFLD-v2 được đưa vào bất kỳ bước tính toán nào — hệ thống trả về kết quả rỗng (`lane_count=0`, không có làn ego) thay vì cố suy luận từ dữ liệu không tồn tại. Đây chính là nguồn gốc của các ảnh có `pred_lane_count=0` được thảo luận ở mục 4.1 (chủ yếu rơi vào nhóm ảnh không có vạch kẻ rõ).

### Độ lệch tâm xe (vehicle offset)

Với tâm làn ego $x_{lane} = (x_{left} + x_{right})/2$ và $x_{veh}$ theo giả thiết camera gắn tâm xe (mục trên), độ lệch tâm xe được tính theo hai đơn vị song song — pixel tuyệt đối và phần trăm bề rộng làn:

$$\Delta x = x_{veh} - x_{lane} \quad \text{(pixel)}, \qquad \Delta x_{\%} = \frac{\Delta x}{w} \times 100$$

trong đó $w$ là bề rộng làn ego. Phép nhân với 100 ở $\Delta x_\%$ không phải một hằng số cần hiệu chỉnh — đây thuần túy là bước chuyển đổi tỉ lệ $\Delta x/w \in [-1,1]$ sang đơn vị phần trăm, giúp con số dễ diễn giải hơn khi trình bày và khi đưa vào JSON/prompt (mục 3.4–3.5).

Ngưỡng "centered" ($|\Delta x| < 10$ pixel) là một dung sai thực tế, không phải giá trị hiệu chỉnh bằng số liệu đo: ở độ phân giải của hai bộ dữ liệu sử dụng (1640×590 với CULane, 1280×720 với real-life), 10 pixel tương ứng khoảng 0,6–0,8% bề rộng ảnh — đủ nhỏ để nằm trong biên độ dao động tự nhiên của việc phát hiện đường biên giữa các khung hình, nên được coi là "không lệch đáng kể" thay vì đòi hỏi $\Delta x = 0$ tuyệt đối, một điều kiện phi thực tế đối với dữ liệu ảnh thật. Hướng lệch được gán "lệch phải" nếu $\Delta x > 0$, "lệch trái" nếu ngược lại.

### Ước lượng độ cong

Với mỗi đường biên có tối thiểu 4 điểm, tọa độ $y$ được chuẩn hóa $y_{norm} = (y - y_{min})/(y_{max} - y_{min})$, rồi fit hai đa thức qua $(y_{norm}, x)$: bậc 1 (sai số $\text{MSE}_1$) và bậc 2 ($\text{MSE}_2$). Hai tín hiệu độ cong được trích ra — **tỉ lệ lệch** ($\text{drift\_ratio}$ trong công thức) và **mức cải thiện khi fit cong** ($\text{fit\_improvement}$):

$$\text{drift\_ratio} = \frac{\sqrt{\text{MSE}_1}}{\text{image\_width}}, \qquad \text{fit\_improvement} = \max\!\left(0,\; \frac{\text{MSE}_1 - \text{MSE}_2}{\text{MSE}_1}\right)$$

Tỉ lệ lệch đo độ lệch quân phương so với một đường thẳng, chuẩn hóa theo chiều rộng ảnh; mức cải thiện khi fit cong đo mức cải thiện khi cho phép mô hình cong so với ép thẳng, chỉ được tin khi $\text{MSE}_1 > 4$ và đường biên có ≥10 điểm — nếu không, chênh lệch $\text{MSE}_1-\text{MSE}_2$ bị coi là nhiễu/overfit và gán bằng 0. Tín hiệu này cần thiết cho các đường cong rất nhẹ, nơi độ lệch tuyệt đối còn quá nhỏ để tỉ lệ lệch phát hiện.

Điểm hội tụ phối cảnh (vanishing point) của mỗi đường biên được ngoại suy bằng fit bậc 1, tại một mốc "chân trời" dùng chung cho mọi đường biên trong ảnh:

$$y_{horizon} = 0{,}3 \times \text{image\_height}$$

thay vì ngoại suy riêng tại $y_{norm}=0$ của từng đường biên như thiết kế ban đầu — cách cũ khiến hai đường biên thẳng song song có thể cho hai điểm hội tụ khác nhau (do được đánh giá ở hai độ sâu ảnh khác nhau), phóng đại sai độ phân tán điểm hội tụ dù đường thực sự thẳng. Neo về cùng một hàng ảnh khắc phục sai lệch này. Mốc 0,3 là một lựa chọn thực tế xấp xỉ vị trí đường chân trời thường thấy trong ảnh dashcam gắn ở độ cao mắt người lái, không phải giá trị đo trực tiếp từ dữ liệu; vai trò của nó chỉ là một mốc *dùng chung* cố định để mọi đường biên được so sánh công bằng, không nhằm mô phỏng đúng vị trí chân trời vật lý của từng ảnh cụ thể.

Bốn tín hiệu tổng hợp trên toàn ảnh — $\overline{\text{drift}}$, $\overline{\text{fit\_improvement}}$, tỉ lệ đường biên "thẳng" ($\text{MSE}_1 < 1000$), và hướng cong (so sánh x trung bình gần đáy ảnh với gần giữa ảnh, ngưỡng $\text{shift\_ratio}=0{,}08$ — một ngưỡng thực tế khác, chọn đủ nhỏ để phát hiện lệch trái/phải rõ rệt nhưng đủ lớn để không nhạy cảm với nhiễu phát hiện đường biên) — được dùng để phân loại hình dạng đường tổng thể.

### Hiệu chỉnh ngưỡng phân loại độ cong

Hai ngưỡng $\overline{\text{drift}}$ dưới đây là các giá trị được hiệu chỉnh bằng số liệu thực đo trên CULane, không đặt tùy ý: $\overline{\text{drift}}_{straight}=0{,}02$ (trên phân vị p95 đo được trên các ảnh đường thẳng, ≈0,014); $\overline{\text{drift}}_{sharp}=0{,}06$ (dưới giá trị đo được của một ảnh cua gắt đã xác nhận đúng, 0,0994). Ngưỡng thứ ba, $\text{fit\_improvement}=0{,}3$, có vai trò khác và mức độ căn cứ khác: đây là một lựa chọn thực tế bổ sung — không hiệu chỉnh bằng số liệu đo như hai ngưỡng $\overline{\text{drift}}$ ở trên — chỉ can thiệp để nâng hạng từ "thẳng" lên "cong nhẹ" trong dải giá trị mà $\overline{\text{drift}}$ còn quá nhỏ để tự phát hiện, nhưng bằng chứng cải thiện khi fit bậc 2 (so với bậc 1) vẫn rõ ràng. Quy tắc phân loại cuối cùng:

$$
\text{classification} = \begin{cases}
\texttt{straight} & \overline{\text{drift}} < 0{,}02 \text{ và } \overline{\text{fit\_improvement}} < 0{,}3 \text{ và tỉ lệ đường biên thẳng} > 50\% \\
\texttt{sharp} & \overline{\text{drift}} \ge 0{,}06 \\
\texttt{gentle} & \text{còn lại}
\end{cases}
$$

Độ phân tán tuyệt đối của điểm hội tụ ($\text{vp\_spread}$) từng được cân nhắc nhưng bị loại khỏi quy tắc phân loại: không chuẩn hóa theo kích thước ảnh nên không ổn định giữa các ảnh khác đặc trưng camera — vẫn được lưu trong JSON để tham khảo, không tham gia phân loại.

**Bảng 3.1.** Tổng hợp toàn bộ tham số cấu hình của mô-đun phân tích ngữ nghĩa (mục 3.3), phân biệt tham số hiệu chỉnh bằng số liệu thực đo và tham số chọn theo lý lẽ thực tế (heuristic). Đây là bảng tra cứu nhanh; lý lẽ chi tiết cho từng tham số được trình bày trong phần văn bản tương ứng ở trên.

| Tham số | Giá trị | Vai trò | Căn cứ |
|---|---|---|---|
| $y_{ref}$ | $0{,}95 \times \text{image\_height}$ | Hàng ảnh tham chiếu để sắp xếp đường biên trái–phải | Heuristic thực tế |
| Ngưỡng nội suy | $\pm 30$ pixel quanh $y_{ref}$ | Khoảng lấy trung bình điểm khi nội suy tọa độ x tại $y_{ref}$ | Heuristic thực tế |
| $p_{between}$ | 0,5 (trong khe) / 1 (ngoài khe) | Ưu tiên khe thực sự chứa $x_{veh}$ khi tính $\text{score}_i$ | Heuristic (xếp hạng tương đối) |
| $w_{exp}$ | $0{,}15 \times \text{image\_width}$ | Bề rộng làn "điển hình" giả định, dùng để phạt khe bất thường | Heuristic thực tế |
| Trọng số phạt bề rộng | 0,2 | Mức ảnh hưởng của thành phần (c) trong $\text{score}_i$ | Heuristic (điều chỉnh phụ) |
| Ngưỡng độ tin cậy làn ego | $d<0{,}1w/0{,}25w/0{,}4w \to 0{,}95/0{,}8/0{,}6/0{,}4$ | Suy độ tin cậy làn ego từ khoảng cách tâm $d$ | Heuristic phân đoạn |
| Độ tin cậy khi $n=1$ | 0,5 | Độ tin cậy cố định khi chỉ phát hiện 1 đường biên | Heuristic cố định |
| Ngưỡng "centered" | 10 pixel | Dung sai độ lệch tâm xe được coi là "không lệch" | Heuristic thực tế (≈0,6–0,8% bề rộng ảnh) |
| Ngưỡng tin cậy `fit_improvement` | $\text{MSE}_1>4$ và ≥10 điểm | Điều kiện để tin tín hiệu `fit_improvement`, tránh nhiễu/overfit | Heuristic |
| $y_{horizon}$ | $0{,}3 \times \text{image\_height}$ | Mốc chân trời dùng chung để ngoại suy điểm hội tụ | Heuristic thực tế |
| $\text{shift\_ratio}$ | 0,08 | Ngưỡng phát hiện hướng cong trái/phải | Heuristic thực tế |
| Ngưỡng "đường biên thẳng" | $\text{MSE}_1 < 1000$ | Xác định một đường biên là "thẳng" khi tính tỉ lệ toàn ảnh | Heuristic |
| $\overline{\text{drift}}_{straight}$ | 0,02 | Ngưỡng phân loại hình dạng "thẳng" | **Thực đo** trên CULane (p95 ≈ 0,014) |
| $\overline{\text{drift}}_{sharp}$ | 0,06 | Ngưỡng phân loại hình dạng "cua gắt" | **Thực đo** trên CULane (xác nhận 0,0994) |
| Ngưỡng `fit_improvement` | 0,3 | Nâng hạng "thẳng" → "cong nhẹ" khi drift chưa đủ rõ | Heuristic bổ sung |

### Số làn đường

Bằng số đường biên phát hiện được trừ 1, theo quy ước CULane.

![Hình 3.2. Ví dụ trực quan hóa output của mô-đun phân tích ngữ nghĩa trên một ảnh CULane thật.](figures/hinh_3_2_vi_du_pipeline.jpg)

**Hình 3.2.** Ví dụ trực quan hóa output của mô-đun phân tích ngữ nghĩa trên một ảnh CULane thật (ảnh số 129 trong tập N=200 dùng ở Chương 4). Vùng xanh lá là làn ego được xác định (độ tin cậy 0,80); vạch trắng là các đường biên còn lại sau khi sắp xếp; vạch vàng thẳng đứng đánh dấu tâm ảnh $x_{veh}$, mũi tên đỏ là điểm tham chiếu vị trí xe. Text góc trên trái là các trường ngữ nghĩa chính được suy ra: làn ego (đường biên 0–1), độ lệch tâm 168,4 px (tương đương 31,2% bề rộng làn, lệch phải), 1 làn lân cận mỗi bên, đường thẳng. Hai khung vàng là biển báo phát hiện được (`i5` — độ tin cậy 80%, `i4` — độ tin cậy 74%), tương ứng đúng hai phần tử trong trường `traffic_signs` của JSON đầy đủ cho ảnh này (mục 3.4).

## 3.4. Cấu trúc JSON ngữ nghĩa gửi cho LLM

**JSON đầy đủ (`<tên>.json`).** Đây là output trực tiếp của mô-đun phân tích ngữ nghĩa (Semantic Analysis, mục 3.3), và cũng là bản JSON được nhúng nguyên vẹn vào prompt ở chế độ chỉ-ngữ-nghĩa và chế độ kết hợp. Bảng 3.2 liệt kê từng nhóm trường và lý do đưa vào; cột "Ký hiệu" đối chiếu mỗi trường với thành phần tương ứng trong bộ ngữ nghĩa $S=(\ell,o,c,N)$ và tập biển báo $D$ đã hình thức hóa ở phần mở đầu Chương 3 — dấu "—" đánh dấu các trường nằm ngoài bộ ngữ nghĩa cốt lõi đó (siêu dữ liệu hoặc đặc trưng phụ trợ).

**Bảng 3.2.** Các nhóm trường trong JSON đầy đủ và lý do đưa vào.

| Nhóm | Trường | Ký hiệu | Ý nghĩa | Lý do đưa vào |
|---|---|---|---|---|
| Siêu dữ liệu | `scene_id`, `timestamp` | — | Định danh phiên xử lý và thời điểm | Truy vết, đối chiếu khi tổng hợp kết quả hàng loạt; không phục vụ suy luận |
| | `image_size` (`width`, `height`) | — | Kích thước ảnh gốc | Cho phép diễn giải đúng các giá trị pixel tuyệt đối (offset, spread...) mà không cần truy cập lại ảnh |
| `road` | `road_type` | — | Loại đường | Ngữ cảnh chung cho khuyến nghị |
| | `road_environment` | — | Ước lượng loại môi trường đường bằng quy tắc if-else đơn giản | Ngữ cảnh bổ sung — **đã bị loại khỏi JSON rút gọn** vì độ tin cậy thấp hơn các trường còn lại, nguy cơ khiến LLM coi là dữ kiện chắc chắn |
| | `curvature_magnitude`/`curvature_direction`/`curvature_confidence` | $c$ | Kết quả phân loại độ cong (mục 3.3) | Ngữ nghĩa cấp đường phục vụ trực tiếp đánh giá độ chính xác module hiểu đường (mục 4.1) |
| | `geometry` (`spread_pixels`, `coverage_ratio`, `convergence_ratio`, `lane_count`, `geometry_type`) | — | Đặc trưng hình học phụ trợ | Giữ lại làm dữ liệu chẩn đoán/tham khảo (ví dụ `spread_pixels` — độ phân tán điểm hội tụ — từng được cân nhắc làm tín hiệu phân loại độ cong nhưng bị loại vì không ổn định giữa các ảnh, mục 3.3); không được đưa vào phần diễn giải chính của prompt |
| `lane` | `sorted_lanes` | — | Danh sách đường biên đã sắp xếp trái–phải | Ngữ cảnh đầy đủ về cấu trúc làn quan sát được, không chỉ riêng làn ego |
| | `ego_lane` | $\ell$ | Ranh giới, tâm, bề rộng, độ tin cậy làn ego | Ngữ nghĩa cốt lõi — input trực tiếp cho khuyến nghị lái xe |
| | `lane_classification` | $N$ | Số lượng, danh sách làn lân cận trái/phải | Phục vụ khuyến nghị liên quan chuyển làn |
| | `vehicle_offset` | $o$ | Độ lệch tâm xe đầy đủ (mục 3.3) | Ngữ nghĩa cốt lõi thứ hai |
| | `curvature` | $c$ | Kết quả phân loại độ cong | Lặp lại ở cấp `lane` để LLM không cần tra cứu chéo sang `road` |
| | `lane_semantics` | — | Ngữ nghĩa từng làn: loại, có phải ego không, có đi được không, vị trí tương đối | Cho phép khuyến nghị liên quan đến các làn khác ngoài làn ego |
| `traffic_signs` | danh sách biển báo + `count` | $D$ | Nhãn lớp, tọa độ, số lượng | Ngữ nghĩa biển báo — phần còn lại của nội dung đánh giá độ chính xác nhận diện (mục 4.3) |

**JSON rút gọn (`<tên>_brief.json`).** Một schema riêng, gọn hơn nhiều, chỉ giữ lại các trường mà mục 3.3 xác định là có đủ độ tin cậy để đưa thẳng vào lý luận của LLM (Bảng 3.3).

**Bảng 3.3.** Các trường trong JSON rút gọn và lý do giữ lại. Cột "Ký hiệu" tiếp tục đối chiếu với bộ ngữ nghĩa $S=(\ell,o,c,N)$ đã hình thức hóa ở phần mở đầu Chương 3; `lane_count` là tổng số làn ($N+1$, cộng thêm làn ego), không trùng với $N$ (số làn lân cận).

| Trường | Ký hiệu | Ý nghĩa | Lý do giữ lại |
|---|---|---|---|
| `lane_count` | $N+1$ | Số làn đường | Ngữ cảnh tối thiểu cho mọi khuyến nghị liên quan đến làn |
| `ego_lane` | $\ell$ | Vị trí dạng "X/Y" và độ tin cậy | Ngữ nghĩa cốt lõi nhất, không thể lược bỏ mà vẫn còn ý nghĩa |
| `vehicle_offset` | $o$ | Hướng, mức độ, phần trăm lệch | Ngữ nghĩa cốt lõi thứ hai, phục vụ trực tiếp khuyến nghị giữ làn/căn chỉnh |
| `neighbor_lanes` | $N$ | Số làn trái/phải | Cần cho khuyến nghị chuyển làn, đủ ngắn gọn không cần danh sách chi tiết |
| `road_shape` | $c$ | Loại, mức độ, hướng cong | Ngữ nghĩa cấp đường tối thiểu, ảnh hưởng trực tiếp đến khuyến nghị tốc độ/giữ vô lăng |

Không có siêu dữ liệu, không có `traffic_signs`. Các trường bị loại khỏi bản rút gọn — toàn bộ siêu dữ liệu, `traffic_signs`, `road_environment`, và các trường hình học phụ trợ trong `geometry` — đều thuộc một trong ba nhóm: (a) không trực tiếp phục vụ suy luận về hành vi lái xe (siêu dữ liệu); (b) có độ tin cậy thấp hơn do được tính bằng heuristic đơn giản (`road_environment`, các trường hình học phụ trợ); hoặc (c) đã có một kênh thông tin song song đáng tin cậy hơn (biển báo được cấp trực tiếp qua ảnh ở chế độ chỉ-ảnh và chế độ kết hợp). Mục tiêu thiết kế là cấp cho LLM một bản dữ liệu tối giản nhất có thể mà vẫn đủ để suy luận, giảm nguy cơ LLM bị phân tán bởi các trường ít giá trị quyết định hoặc độ tin cậy thấp.

![Hình 3.3. So sánh cấu trúc trường giữa JSON đầy đủ và JSON rút gọn.](figures/hinh_3_3_cau_truc_json.png)

**Hình 3.3.** So sánh cấu trúc trường giữa JSON đầy đủ (trái) và JSON rút gọn (phải). Dấu ✓ đánh dấu trường có mặt ở cả hai bản (theo tên hoặc theo ánh xạ trực tiếp); dấu ✗ đánh dấu trường chỉ tồn tại ở JSON đầy đủ. Khung ghi chú bên dưới cột phải tóm tắt vai trò thực tế của mỗi bản trong thực nghiệm — chi tiết lý do biện luận ở đoạn kế tiếp.

**Vì sao thí nghiệm chính (mục 4.5) dùng JSON đầy đủ, không dùng JSON rút gọn.** Đoạn trên có thể gây hiểu nhầm rằng JSON rút gọn — với triết lý loại bỏ trường kém tin cậy để giảm phân tán — mới là bản được cấp cho VLM ở thí nghiệm trung tâm trả lời câu hỏi nghiên cứu cốt lõi (mục 4.5). Thực tế không phải vậy: **cả chế độ chỉ-ngữ-nghĩa lẫn chế độ kết hợp ở mục 4.5 đều dùng JSON đầy đủ**, vì lý do quyết định sau — JSON rút gọn không có trường `traffic_signs`, trong khi rubric đánh giá (mục 3.7) có hẳn một tiêu chí riêng về biển báo và quy tắc (`traffic_sign_rule`); nếu dùng JSON rút gọn làm input, chế độ chỉ-ngữ-nghĩa sẽ hoàn toàn không có thông tin biển báo để suy luận, khiến tiêu chí đó không thể chấm công bằng ở chế độ này so với hai chế độ còn lại. Với các trường bị JSON rút gọn loại bỏ vì lý do khác (siêu dữ liệu, `road_environment`, hình học phụ trợ), nguy cơ gây phân tán được xử lý bằng một cơ chế khác ngay trong JSON đầy đủ: prompt (mục 3.5) chỉ hướng dẫn VLM tập trung vào đúng bốn ngữ nghĩa cấp làn đường cốt lõi, không yêu cầu khai thác các trường phụ trợ đó — các trường này vẫn hiện diện trong payload nhưng không được prompt trỏ tới. Nói cách khác, JSON rút gọn và JSON đầy đủ xử lý cùng một mối lo (thông tin thừa/kém tin cậy gây phân tán) bằng hai cơ chế khác nhau: rút gọn xử lý ở tầng dữ liệu (loại bỏ hẳn trường khỏi payload), đầy đủ xử lý ở tầng hướng dẫn (giữ trường, nhưng prompt không trỏ sự chú ý của mô hình vào đó). Đề tài chưa có một thực nghiệm đối chứng trực tiếp so sánh hai chiến lược này với nhau (ví dụ: JSON rút gọn có bổ sung `traffic_signs` riêng, để loại trừ yếu tố gây nhiễu đó, rồi đối chiếu với JSON đầy đủ); đây là một giới hạn được ghi nhận của thiết kế thực nghiệm hiện tại, không phải một kết luận đã kiểm chứng.

Schema rút gọn này còn được sử dụng ở một vai trò khác, tách biệt với vai trò làm input cho tầng suy luận: làm định dạng output mục tiêu cho thí nghiệm kiểm chứng khả năng tự nhận diện của VLM (mục 4.7), nơi VLM được yêu cầu tự trích xuất đúng năm trường này trực tiếp từ ảnh, không kèm bất kỳ gợi ý nào, rồi so sánh với giá trị mà pipeline UFLD-v2 tính ra. Ở vai trò này, JSON rút gọn chỉ đóng vai trò khuôn mẫu cấu trúc cho output cần so sánh, không phải input được cấp cho VLM, nên không phát sinh vấn đề về công bằng hay rò rỉ thông tin.

## 3.5. Thiết kế prompt cho tầng suy luận

Prompt gửi tới VLM được ghép từ một khối nội dung chung và một trong ba khối riêng theo chế độ đang chạy (chỉ-ảnh, chỉ-ngữ-nghĩa, hoặc kết hợp). Khối chung tập trung vào bốn ngữ nghĩa cấp làn đường — số làn, làn ego, độ lệch tâm, làn lân cận — kèm hai nhóm quy tắc tường minh: quy tắc chống ảo giác (không suy diễn thông tin không có bằng chứng trực tiếp trong ảnh/JSON; không coi việc thiếu phát hiện là bằng chứng cho việc vật thể không tồn tại) và quy tắc ra quyết định khi hai nguồn có vẻ mâu thuẫn (áp dụng riêng cho chế độ kết hợp, nơi cả ảnh lẫn JSON cùng được cấp).

Khối hướng dẫn định dạng output ba phần (Tình huống, Khuyến nghị, Lưu ý an toàn) được đặt ở vị trí cuối cùng của prompt — sau khối JSON (ở các chế độ có JSON) — thay vì ở đầu như một lựa chọn trực giác thông thường. Lựa chọn này dựa trên hiệu ứng vị trí trong cách LLM sử dụng ngữ cảnh dài: Liu và cộng sự [35] cho thấy độ chính xác truy xuất thông tin của LLM đạt cao nhất khi thông tin quan trọng nằm ở đầu hoặc cuối ngữ cảnh, và giảm rõ rệt khi nằm ở giữa một ngữ cảnh dài. Đặt hướng dẫn định dạng ngay trước điểm mô hình bắt đầu sinh output — vị trí "cuối" của prompt — tận dụng hiệu ứng recency này, giảm nguy cơ hướng dẫn bị mô hình bỏ qua sau khi phải xử lý một khối JSON dài ở giữa prompt.

Trong quá trình phát triển, hai vấn đề thực nghiệm cụ thể đã được phát hiện trực tiếp trên output thật của mô hình (không phải giả định trước) và khắc phục:

- **Lặp lại vô hạn trên ảnh ít thông tin.** Với các ảnh mà cả JSON lẫn nội dung ảnh đều nghèo bằng chứng (ảnh mờ, thiếu vạch kẻ rõ ràng), một số mô hình có xu hướng lặp lại cùng một câu (ví dụ "The image does not provide enough information...") nhiều lần liên tiếp trong cùng một lượt sinh. Khắc phục bằng cách đặt `frequency_penalty=0,4` khi gọi API — tham số này phạt trực tiếp việc lặp lại token/cụm từ đã xuất hiện trong output, và giá trị 0,4 được chọn cụ thể để xử lý hiện tượng lặp lại quan sát được, không phải một siêu tham số được dò rộng bằng grid-search.
- **Trả lời quá ngắn, không tuân thủ cấu trúc bắt buộc.** Một số phản hồi bỏ qua cấu trúc ba phần hoặc chỉ nêu kết luận mà không có căn cứ đi kèm. Khắc phục bằng cách bổ sung yêu cầu tường minh trong khối nội dung chung: mỗi phần trong ba phần output phải nêu bằng chứng cụ thể trích từ ảnh và/hoặc JSON, không chỉ kết luận suông — buộc mô hình "chỉ ra" thay vì chỉ "khẳng định", đồng thời gián tiếp giảm nguy cơ ảo giác vì một bằng chứng trích dẫn sai lệch dễ bị người đọc/judge phát hiện hơn một kết luận suông sai lệch.

## 3.6. Lựa chọn mô hình cho tầng suy luận

Do giới hạn về chi phí và khả năng tái lập, phạm vi lựa chọn mô hình được giới hạn trong các VLM khả dụng miễn phí qua NVIDIA NIM API (định dạng OpenAI-compatible thống nhất). Quá trình chọn mô hình cụ thể diễn ra tuần tự theo kinh nghiệm triển khai thực tế, không phải một phép so sánh đồng thời được thiết kế sẵn từ đầu:

1. **Bắt đầu với `nemotron-nano-vl-8b`** (8 tỷ tham số) — mô hình đa phương thức nhẹ nhất do NVIDIA cung cấp qua NIM API tại thời điểm triển khai, được chọn làm điểm khởi đầu vì thời gian phản hồi nhanh, phù hợp cho giai đoạn phát triển và gỡ lỗi pipeline ban đầu.
2. **Thử nâng cấp lên `nemotron-nano-12b-v2-vl`** (12 tỷ tham số) — kỳ vọng chất lượng cao hơn nhờ quy mô lớn hơn, nhưng mô hình này cho tỉ lệ lỗi/thất bại yêu cầu rất cao trong thực nghiệm thực tế (định lượng cụ thể ở Bảng 4.4, mục 4.4: 82,9% yêu cầu thất bại), không đạt ngưỡng độ tin cậy tối thiểu để cân nhắc triển khai.
3. **Thử `ising-calibration-1.5-31b`** (31 tỷ tham số) — cho kết quả ổn định hơn hẳn `nemotron-nano-12b-v2-vl` và chất lượng nội dung tốt hơn `nemotron-nano-vl-8b`, trong khi thời gian phản hồi quan sát được trong quá trình phát triển (không đo hệ thống, không có kiểm định thống kê — mục 4.4 chỉ báo cáo độ trễ của riêng mô hình 31B) không tạo cảm giác chậm rõ rệt so với mô hình 8B ban đầu — một quan sát không hiển nhiên trước khi thử, vì quy mô tham số gấp gần bốn lần thường đi kèm độ trễ cao hơn tương ứng.

Ba ứng viên này được xác định trong quá trình phát triển ban đầu, không phải qua một bước sàng lọc có tiêu chí định trước; sau khi ba ứng viên đã được xác định, đề tài áp dụng hồi cứu (retrospectively) một giao thức so sánh chung cho cả ba, dựa trên ba tiêu chí mà cả ba đều thỏa mãn:

1. Hỗ trợ đa phương thức (nhận đồng thời ảnh và văn bản) — điều kiện bắt buộc của pipeline, loại trừ các mô hình chỉ xử lý văn bản.
2. Khả dụng miễn phí qua cùng một API thống nhất, đảm bảo chi phí triển khai bằng 0 và tính nhất quán khi thực nghiệm, đúng định hướng training-free/chi phí thấp của đề tài (mục 1.3).
3. Trải dài trên nhiều mức quy mô tham số khác nhau (8B/12B/31B), cho phép quan sát liệu quy mô mô hình có tương quan với độ tin cậy và chất lượng đầu ra hay không, phục vụ trực tiếp mục tiêu lựa chọn mô hình suy luận (mục 4.4).

Áp dụng ba tiêu chí này cho phép biến quá trình thử nghiệm tuần tự nêu trên thành một phép so sánh có kiểm soát, có thể tái lập — thay vì chỉ dừng ở nhận xét định tính "31B tốt hơn" — với tiêu chí so sánh cụ thể, theo đúng thứ tự ưu tiên: độ tin cậy — tỉ lệ hoàn thành thành công khi chạy trên toàn bộ batch thật, được xét trước và độc lập với chất lượng nội dung, vì một mô hình không phản hồi ổn định không thể triển khai cho một hệ thống hỗ trợ quyết định thời gian thực, bất kể chất lượng câu trả lời khi nó phản hồi thành công tốt tới đâu; tỉ lệ tuân thủ cấu trúc output bắt buộc; và chất lượng nội dung, chấm điểm bởi LLM-as-a-judge, chỉ áp dụng cho các mô hình đã vượt qua ngưỡng tối thiểu ở tiêu chí đầu tiên.

**Trình tự thực nghiệm.** Việc chọn mô hình LLM ở mục này (mục 4.4) và kết quả trung tâm về đóng góp của thông tin ngữ nghĩa có cấu trúc ở mục 4.5 (câu hỏi nghiên cứu cốt lõi, mục 1.1) là hai thực nghiệm tách biệt, chạy tuần tự, không phụ thuộc vòng tròn vào nhau:

1. *Giai đoạn 1 — chọn mô hình (mục 4.4)*: cả ba mô hình ứng viên được chạy ở cùng một chế độ cố định — chế độ kết hợp, chế độ cấp đầy đủ thông tin nhất, cho mỗi mô hình cơ hội thể hiện tốt nhất — và được chấm điểm bởi đúng một judge (Gemini) để xác định mô hình có độ tin cậy và chất lượng tốt nhất. Kết quả: `ising-calibration-31b` được chọn.
2. *Giai đoạn 2 — so sánh chế độ input (mục 4.5)*: mô hình đã chọn được giữ cố định, và biến số duy nhất được thay đổi là chế độ input (chỉ-ảnh/chỉ-ngữ-nghĩa/kết hợp), chấm điểm bởi cả ba judge độc lập để trả lời câu hỏi nghiên cứu cốt lõi.

Nói cách khác, chuỗi xử lý thực tế là: ảnh → detection/semantic analysis → chạy ba mô hình LLM ở chế độ kết hợp, Gemini chấm điểm, chọn mô hình thắng → cố định mô hình thắng, chạy lại ở cả ba chế độ input, cả ba judge chấm điểm, kết luận cho câu hỏi nghiên cứu cốt lõi. Bước chấm điểm để chọn mô hình và bước chấm điểm để so sánh chế độ input là hai lượt riêng biệt, phục vụ hai câu hỏi nghiên cứu khác nhau, không phải cùng một lượt chấm dùng cho cả hai mục đích.

**Giao thức thực nghiệm (cấu hình gọi API).** Cả ba mô hình ứng viên đều được gọi qua cùng một client, cùng một bộ tham số sinh (generation parameters) mặc định — không mô hình nào được ưu ái bằng cấu hình riêng — liệt kê ở Bảng 3.4.

**Bảng 3.4.** Cấu hình gọi API dùng chung cho cả ba mô hình ứng viên và cả ba chế độ input.

| Tham số | Giá trị | Lý do |
|---|---|---|
| `max_tokens` | 400 | Hạ từ 1024 xuống 400 để giới hạn thiệt hại nếu mô hình rơi vào trạng thái lặp vô hạn (đã quan sát thực tế: một output lặp cùng một câu khoảng 6 lần liên tiếp trước khi bị cắt cụt ở giới hạn 1024 cũ) |
| `temperature` | 0,2 | Giá trị thấp, ưu tiên output ổn định/tái lập được hơn là đa dạng, phù hợp một tác vụ cần độ chính xác về sự kiện (fact-based) hơn là sáng tạo văn phong |
| `top_p` | 0,7 | Kết hợp với `temperature` thấp để giới hạn thêm không gian lấy mẫu |
| `frequency_penalty` | 0,4 | Phạt lặp token, thêm để khắc phục hiện tượng lặp câu đã quan sát được (mục 3.5) |
| `timeout` | 120 giây/yêu cầu | Ngưỡng chờ trước khi coi một yêu cầu là thất bại |
| Nén ảnh trước khi mã hóa base64 | ≤150 KB | Giảm dung lượng payload gửi API, tránh bị NVIDIA NIM từ chối ảnh quá lớn |

Ba chế độ input (chỉ-ảnh/chỉ-ngữ-nghĩa/kết hợp) dùng chung nguyên vẹn bộ cấu hình trên và cùng một mô hình; biến số duy nhất thay đổi giữa ba chế độ là **khối prompt** được ghép vào (mục 3.5) và dữ liệu đính kèm theo yêu cầu của chế độ đó (ảnh, JSON, hoặc cả hai) — không có tham số sinh nào bị điều chỉnh riêng theo chế độ, đảm bảo mọi khác biệt về chất lượng output quan sát được ở Chương 4 chỉ có thể quy về sự khác biệt của thông tin đầu vào, không phải do cấu hình gọi mô hình khác nhau.

**Vì sao Giai đoạn 1 chỉ dùng một chế độ input và một judge.** Đây là một lựa chọn thiết kế thực nghiệm có chủ đích, dựa trên ba căn cứ. Thứ nhất, việc lựa chọn mô hình suy luận và câu hỏi nghiên cứu cốt lõi là hai mục tiêu trực giao: chạy toàn bộ ma trận ba mô hình × ba chế độ × ba judge sẽ tốn gấp nhiều lần chi phí và thời gian API mà không phục vụ trực tiếp việc chọn mô hình, vốn chỉ cần xác định mô hình nào đáng tin cậy và chất lượng tốt nhất, không cần biết mô hình đó tương tác thế nào với từng chế độ input cụ thể; cố định chế độ input ở chế độ kết hợp khi so sánh mô hình là cách chuẩn để đảm bảo mỗi mô hình được đánh giá trong điều kiện thuận lợi nhất có thể, tách bạch "mô hình yếu" khỏi "mô hình bị thiếu thông tin". Thứ hai, đây là một ràng buộc trong trình tự phát triển thực tế: tại thời điểm Giai đoạn 1 được thực hiện, GPT-5 Mini và DeepSeek chưa được tích hợp làm judge — Gemini là judge duy nhất tồn tại trong hệ thống ở giai đoạn đó — và việc bổ sung đối chiếu đa-judge (mục 4.6) là một bước siết chặt phương pháp luận được thêm vào sau, dành riêng cho kết quả trung tâm ở mục 4.5, nơi kết luận thực sự nhạy với lựa chọn judge (thứ hạng chế độ chỉ-ngữ-nghĩa so với chế độ kết hợp đảo chỗ tùy judge, Bảng 4.6). Thứ ba, độ lớn chênh lệch giữa các mô hình ở bước lựa chọn này không đòi hỏi kiểm chứng đa-judge để tin cậy: `nemotron-nano-12b-v2-vl` thất bại tới 82,9% số yêu cầu, và `ising-calibration-31b` vượt `nemotron-nano-8b` với Cohen's d xấp xỉ 1,04 (Bảng 4.4) — một hiệu ứng rất lớn, khó có khả năng bị đảo ngược chỉ vì đổi judge; thêm vào đó, mục 4.6 (thực hiện sau) xác nhận Gemini là judge có tương quan với con người cao nhất trong ba judge đã thử, củng cố thêm — dù không phải bằng chứng có sẵn tại thời điểm Giai đoạn 1 được thực hiện — rằng lựa chọn Gemini làm judge duy nhất cho quyết định này là hợp lý.

## 3.7. Phương pháp luận đánh giá

**Đánh giá module hiểu làn đường/biển báo.** So sánh trực tiếp với ground truth gán tay, sử dụng các metric chuẩn: Accuracy (tỉ lệ khớp chính xác), MAE (sai số tuyệt đối trung bình), Precision và Recall.

**Đánh giá chất lượng khuyến nghị lái xe.** Sử dụng LLM-as-a-judge với rubric sáu tiêu chí, trọng số bằng nhau, thang điểm 1–5: **Hiểu tình huống** (`situation_understanding` — hiểu đúng đường/giao thông/nguy cơ liên quan), **Hiểu hình học đường** (`road_understanding` — đúng hình học đường, làn, ranh giới, làn lân cận), **Vị trí làn ego** (`lane_ego_position` — đúng làn ego, vị trí, độ lệch khi có bằng chứng), **Biển báo và quy tắc** (`traffic_sign_rule` — đúng biển báo, tín hiệu, quy tắc/giới hạn tốc độ được hỗ trợ tường minh bởi bằng chứng), **Khuyến nghị lái xe** (`driving_recommendation` — hành động an toàn, phù hợp, cần thiết, cụ thể, có căn cứ), **Lưu ý an toàn** (`safety_considerations` — nêu đúng rủi ro an toàn liên quan, không nêu chung chung/không có căn cứ). Tên trong ngoặc đơn là định danh kỹ thuật dùng trong output JSON của judge (mục "Quy trình chấm điểm" bên dưới) và trong các bảng số liệu ở Chương 4; phần diễn giải dùng tên tiếng Việt ở trên.

**Căn cứ chọn đúng sáu tiêu chí này.** Bộ tiêu chí không phải một danh sách tùy ý, mà bám theo hai trục đã xác lập sẵn trong chính phương pháp luận của đề tài, không chồng lấn nhau:

- *Ba tiêu chí đầu — Hiểu hình học đường, Vị trí làn ego, Biển báo và quy tắc — đánh giá tính đúng đắn của các sự kiện nền tảng*, tương ứng trực tiếp với bộ ngữ nghĩa $S=(\ell,o,c,N)$ và tập biển báo $D$ đã hình thức hóa ở đầu Chương 3: Vị trí làn ego kiểm tra $\ell$ và $o$ (làn ego và độ lệch tâm xe); Hiểu hình học đường kiểm tra $c$ và $N$ (hình dạng đường và làn lân cận); Biển báo và quy tắc kiểm tra $D$. Đây cũng chính là ba nhóm ngữ nghĩa được đánh giá định lượng độc lập với ground truth ở mục 4.1–4.3 — rubric LLM-as-a-judge nhờ vậy đo cùng một không gian ngữ nghĩa, chỉ khác ở việc đọc trực tiếp từ văn bản khuyến nghị thay vì từ output có cấu trúc của pipeline.
- *Ba tiêu chí còn lại — Hiểu tình huống, Khuyến nghị lái xe, Lưu ý an toàn — đánh giá chất lượng của chính văn bản đầu ra*, tương ứng trực tiếp với cấu trúc ba phần bắt buộc của prompt (Tình huống/Khuyến nghị/Lưu ý an toàn, mục 3.5): mỗi tiêu chí chấm đúng một phần trong ba phần đó.

Cách chia này buộc rubric phải tách bạch đúng-sai ở tầng sự kiện (ba tiêu chí đầu) khỏi chất lượng trình bày/hành động ở tầng đầu ra (ba tiêu chí sau) — hai khía cạnh có thể lệch nhau (ví dụ một khuyến nghị nghe hợp lý nhưng dựa trên nhận diện sai vị trí làn vẫn phải bị trừ điểm ở tiêu chí Vị trí làn ego, dù tiêu chí Khuyến nghị lái xe có thể vẫn cao) — thay vì chỉ đo cảm nhận tổng quát "câu trả lời có nghe hợp lý không", vốn dễ bị judge chấm theo văn phong hơn là tính đúng đắn (mục 2.4, 4.9).

Mỗi mức điểm trong thang 1–5 được neo bằng một mô tả cố định, áp dụng thống nhất cho cả sáu tiêu chí (Bảng 3.5) — đây là căn cứ để judge (và người đọc luận văn) phân biệt "điểm 3" khác "điểm 4" ở đâu, thay vì một con số không có ngữ nghĩa tường minh.

**Bảng 3.5.** Mô tả từng mức điểm trong thang đánh giá 1–5, áp dụng cho cả sáu tiêu chí.

| Điểm | Mô tả |
|---|---|
| 5 | Đúng và có căn cứ rõ ràng; không có lỗi đáng kể |
| 4 | Phần lớn đúng; chỉ có lỗi/thiếu sót nhỏ, không trọng yếu |
| 3 | Đúng một phần; có lỗi/thiếu sót đáng chú ý, nhưng phần hiểu chính vẫn dùng được |
| 2 | Lỗi nghiêm trọng, ảnh hưởng đến việc hiểu tình huống hoặc quyết định lái xe |
| 1 | Sai, không có căn cứ, hoặc không dùng được |

Đây là một hạn chế đã biết của rubric: mô tả 1–5 ở Bảng 3.5 dùng chung cho cả sáu tiêu chí, chưa có anchor cụ thể riêng cho từng tiêu chí (ví dụ "điểm 4 ở Vị trí làn ego" khác "điểm 4 ở Lưu ý an toàn" như thế nào). Xây dựng anchor riêng theo từng tiêu chí là một hướng cải tiến khả thi cho rubric, nêu ở mục 5.4.

**Quy trình chấm điểm.** Với mỗi ảnh, judge nhận đồng thời trong một lệnh gọi API duy nhất: (a) ảnh gốc, dùng làm tham chiếu thị giác duy nhất để xác minh tính đúng đắn của sự kiện; (b) văn bản khuyến nghị do VLM sinh ra ở cả ba chế độ (chỉ-ảnh, chỉ-ngữ-nghĩa, kết hợp) của cùng một ảnh đó, đánh giá độc lập với nhau — judge được yêu cầu tường minh không so sánh ba chế độ khi chấm từng điểm, và không phạt một chế độ vì thiếu thông tin mà chế độ đó vốn dĩ không được cấp (ví dụ không phạt chế độ chỉ-ngữ-nghĩa vì không mô tả chi tiết hình ảnh). Output yêu cầu là một cấu trúc JSON, với mỗi tiêu chí × mỗi chế độ là một cặp `{"score": <1-5>, "reason": "<một câu giải thích ngắn>"}` — bắt buộc có lý do đi kèm điểm số để tăng khả năng kiểm tra chéo và giảm rủi ro chấm điểm ngẫu nhiên không có căn cứ. Các quy tắc chấm điểm bổ sung, áp dụng nhất quán cho toàn bộ rubric: chấm theo tính đúng đắn và bằng chứng, không chấm theo văn phong hay độ dài câu trả lời; các khẳng định không có bằng chứng (ảo giác) bị trừ điểm ở đúng tiêu chí liên quan; không thưởng điểm cho lời khuyên an toàn chung chung không gắn với tình huống cụ thể trong ảnh; không suy diễn giới hạn tốc độ khi không có bằng chứng tường minh; không coi việc thiếu phát hiện là bằng chứng cho việc vật thể không tồn tại; đánh giá độc lập từng tiêu chí — một khuyến nghị lái xe đúng không đồng nghĩa phần hiểu tình huống đúng, và ngược lại. Gộp cả ba chế độ vào cùng một lệnh gọi API cho mỗi ảnh (thay vì gọi riêng từng chế độ) vừa tiết kiệm chi phí, vừa đảm bảo cả ba chế độ được đánh giá trong cùng một ngữ cảnh nhất quán.

**Vì sao Gemini được chọn làm judge chính.** Lựa chọn ban đầu dựa trên đánh giá thực tế của nhóm nghiên cứu qua trải nghiệm sử dụng trực tiếp, kết hợp với uy tín chung của Gemini về khả năng diễn giải nội dung đa phương thức tại thời điểm triển khai — được hỗ trợ một phần bởi tài liệu kỹ thuật chính thức của Google về năng lực suy luận đa phương thức của họ mô hình Gemini [36], và một số đánh giá ứng dụng nhấn mạnh khả năng diễn giải chi tiết, dễ hiểu của Gemini trong các ngữ cảnh cụ thể như giáo dục [37]. Cần nói rõ đây không phải một kết luận đồng thuận tuyệt đối trong tài liệu: một số nghiên cứu so sánh trực tiếp Gemini với GPT-4V trên các tác vụ suy luận thị giác khác cho thấy GPT-4V có xu hướng đưa ra giải thích chi tiết, nhiều bước trung gian hơn, trong khi Gemini thiên về câu trả lời ngắn gọn, trực tiếp hơn [38] — tùy tác vụ cụ thể, mô hình này có thể vượt hoặc kém mô hình kia. Do đó, lựa chọn Gemini ở đây cần được nhìn nhận đúng bản chất là một quyết định thực dụng ban đầu (dựa trên đánh giá thực tế và uy tín chung), không phải một kết luận đã được kiểm chứng thực nghiệm từ trước cho riêng bài toán của đề tài — và chính vì vậy, việc kiểm chứng độc lập bằng dữ liệu chấm tay của con người (trình bày ngay bên dưới, định lượng đầy đủ ở mục 4.6) là một bước bắt buộc trong phương pháp luận, không phải thủ tục hình thức: kết quả mục 4.6 sau đó xác nhận Gemini có tương quan với đánh giá của con người cao nhất trong ba judge đã thử, củng cố hậu nghiệm cho lựa chọn ban đầu.

Sau khi Gemini được đưa vào vận hành làm judge duy nhất, GPT-5 Mini và DeepSeek được bổ sung ở giai đoạn phát triển sau — khi ngân sách API cho phép mở rộng — nhằm mục đích đối chiếu đa-judge, không phải để thay thế Gemini; trình tự bổ sung này cũng chính là lý do Giai đoạn 1 chọn mô hình LLM ở mục 3.6 chỉ có Gemini khả dụng làm judge tại thời điểm đó.

**Kiểm chứng độ tin cậy của judge.** Gồm hai bước: so sánh điểm của Gemini với điểm chấm tay của con người trên một mẫu ngẫu nhiên N=20; và đối chiếu với hai judge độc lập khác (GPT-5 Mini, DeepSeek) trên cùng bộ dữ liệu, dùng nguyên văn cùng một rubric để đảm bảo so sánh công bằng. Mốc chuẩn để đánh giá "judge nào chính xác hơn" là độ đồng thuận với con người, không phải độ đồng thuận giữa các judge với nhau, vì hai judge AI có thể đồng ý với nhau nhưng vẫn cùng chia sẻ một thiên lệch giống nhau so với con người.

**Tóm tắt chương.** Chương này đã trình bày đầy đủ phương pháp luận của đề tài: kiến trúc pipeline bốn giai đoạn, dữ liệu sử dụng, thuật toán suy ra ngữ nghĩa làn đường $S$ từ output UFLD-v2, cấu trúc JSON gửi cho VLM, thiết kế prompt, tiêu chí và trình tự lựa chọn mô hình suy luận, và phương pháp luận đánh giá. Chương 4 tiếp theo trình bày kết quả thực nghiệm định lượng cho từng thành phần này, bắt đầu từ độ chính xác của module hiểu làn đường.

---

# CHƯƠNG 4. KẾT QUẢ VÀ BÀN LUẬN

## 4.1. Độ chính xác module hiểu làn đường (CULane)

Ở giai đoạn đầu, 26 ảnh thuộc các tình huống khó xác định — sảnh/quảng trường không vạch kẻ, hầm gửi xe, đang nhập làn, giao lộ phức tạp — được gán tạm `lane_count=0` để loại khỏi thống kê. Quá trình rà soát sau đó phát hiện cách làm này che giấu một sai lệch: phần lớn các ảnh đó, mô hình cũng dự đoán giá trị 0 do không thấy vạch kẻ, nên vô tình được tính là "khớp chính xác", dù thực chất mô hình đã thất bại hoàn toàn chứ không phải đoán đúng "0 làn". Toàn bộ 200 ảnh sau đó được gán nhãn lại bằng số làn ước lượng thực tế — dựa vào bề rộng đường, vị trí xe khác, dải phân cách vật lý — kèm theo nhãn phân loại lý do khó (`hard_reason`), cho phép tách riêng nhóm ảnh có vạch kẻ rõ ("Normal") khỏi nhóm không có vạch kẻ rõ.

**Bảng 4.1.** Độ chính xác module hiểu làn đường trên CULane (N=200).

| Chỉ số | Giá trị (N=200) |
|---|---|
| Lane count – Accuracy (khớp chính xác) | **69,0%** |
| Lane count – MAE | **0,475** |
| Lane count – Precision | **96,6%** |
| Road type – Accuracy (khớp chính xác) | **76,5%** |
| Road type – Accuracy (khớp nhóm thẳng/cong nhẹ/cong gắt) | **78,5%** |
| Road type – Recall của cua nhẹ | **57,1%** (4/7) |
| Ego lane – Accuracy | **86,0%** |
| Làn bị phát hiện nhầm | **0,8%** |

Các chỉ số ở Bảng 4.1 được tính trực tiếp từ đối chiếu `image_labels.xlsx` với output của pipeline trên N=200 ảnh:

- Lane count Accuracy = tỉ lệ ảnh có số làn dự đoán khớp đúng số làn thực tế = 138/200 = 69,0%.
- Lane count MAE = trung bình trị tuyệt đối của hiệu số làn thực tế và dự đoán = 95/200 = 0,475.
- Lane count Precision = tổng số làn thực tế chia cho tổng số làn thực tế cộng số làn phát hiện nhầm và số làn ngược chiều bị gộp nhầm = 477/(477+5+12) = 96,6%.
- Road type Accuracy (khớp chính xác) = 153/200 = 76,5%; khớp theo nhóm thẳng/nhẹ/gắt = 157/200 = 78,5%.
- Ego lane Accuracy = tỉ lệ ảnh có làn ego được xác định đúng = 172/200 = 86,0%.

Sau khi gán nhãn lại 26 ảnh khó nêu trên, việc tách riêng theo lý do khó cho thấy hiệu năng của mô hình phụ thuộc rất mạnh vào sự hiện diện của vạch kẻ đường: nhóm ảnh có vạch kẻ rõ đạt Accuracy 77,3%, trong khi nhóm không có vạch kẻ rõ chỉ còn 8,3% — chênh lệch gần 70 điểm phần trăm giữa hai nhóm, phân tích chi tiết ở Bảng 4.2.

**Bảng 4.2.** So sánh hiệu năng module hiểu làn đường theo nhóm có/không vạch kẻ đường rõ.

| Nhóm | N | Lane count Accuracy | Lane count MAE | Precision | Ego lane Accuracy |
|---|---|---|---|---|---|
| Có vạch kẻ rõ ("Normal") | 176 | **77,3%** | 0,273 | 96,2% | **96,6%** |
| Không vạch kẻ rõ (quảng trường/hầm gửi xe/nhập làn/giao lộ phức tạp) | 24 | **8,3%** | 1,958 | 100,0% | **8,3%** |

Số liệu thô làm cơ sở cho Bảng 4.2: nhóm Normal có 136/176 ảnh khớp chính xác, tổng trị tuyệt đối sai số 48 (MAE = 48/176 = 0,273), tổng số làn thực tế/nhầm/ngược chiều lần lượt 427/5/12 (Precision = 427/444 = 96,2%), 170/176 ảnh xác định đúng làn ego (96,6%). Nhóm Hard có 2/24 ảnh khớp chính xác, tổng trị tuyệt đối sai số 47 (MAE = 47/24 = 1,958), tổng số làn thực tế/nhầm/ngược chiều lần lượt 50/0/0 (Precision = 50/50 = 100%), 2/24 ảnh xác định đúng làn ego (8,3%).

Đáng chú ý, Precision vẫn đạt 100% ngay cả trên nhóm khó, dù Accuracy chỉ 8,3%. Lý do nằm ở chính công thức: Precision đo tỉ lệ những gì mô hình *dám khẳng định* là chính xác, không đo mức độ đầy đủ. Với 19/24 ảnh trong nhóm này, pipeline trả về số làn dự đoán bằng 0 — không phát hiện được gì — nên không có làn nào để đếm là "sai" hay "bịa"; Σfalse và Σopposite vì vậy đều bằng 0, và Precision = 50/(50+0+0) = 100% một cách gần như tất yếu. Điều này thể hiện rõ nhất ở hai lý do "không có vạch kẻ" (`no_markings`) và "đang nhập làn" (`merging`), nơi số làn dự đoán trung bình bằng 0,00 trong khi số làn thực tế trung bình khoảng 1,7–2,5: mô hình không "bịa" làn giả, mà đơn giản là im lặng khi thiếu vạch kẻ. Đây là hạn chế cố hữu của một detector dựa trên vạch kẻ đường — UFLD-v2 được huấn luyện trên CULane, vốn chủ yếu là ảnh có vạch kẻ rõ — không phải lỗi logic của tầng xử lý ngữ nghĩa phía sau, và được bàn thêm ở mục 5.3. Precision 100% ở nhóm này được báo cáo vì tính đầy đủ của số liệu, không nên được đọc như bằng chứng cho thấy mô hình hiểu làn đường tốt trong điều kiện thiếu vạch kẻ — con số này chỉ phản ánh việc mô hình im lặng thay vì bịa đặt, không phản ánh khả năng nhận diện thực tế.

**So sánh với công trình cùng hướng (hybrid deep learning + MLLM).** Công trình [12] (mục 2.3) báo cáo Frame Overall Accuracy 53,87% và Question Overall Accuracy 82,83% cho module hiểu làn đường dạng hỏi–đáp bằng MLLM. Kết quả của đề tài — 69,0% tổng thể, 77,3% trên nhóm ảnh có vạch kẻ rõ — nằm giữa hai con số đó. Điều này hợp lý vì hai nghiên cứu định nghĩa "accuracy" theo cách khác nhau (Frame Overall Accuracy đo trên toàn khung hình bao gồm cả điều kiện thời tiết và ánh sáng bất lợi, Question Overall Accuracy đo theo từng câu hỏi VQA cụ thể), nên không thể coi là so sánh trực tiếp một-một; tuy nhiên, kết quả cho thấy độ chính xác đạt được nằm trong khoảng hợp lý so với mặt bằng chung của hướng nghiên cứu hybrid deep learning + MLLM cho ngữ nghĩa làn đường.

## 4.2. Kiểm chứng độc lập trên dữ liệu real-life

**Bảng 4.3.** Đối chiếu module hiểu làn đường và biển báo giữa CULane và dữ liệu real-life độc lập (N=200 mỗi bộ).

| Chỉ số | CULane | Real-life độc lập |
|---|---|---|
| Lane count – Accuracy | 69,0% | 50,5% |
| Lane count – MAE | 0,475 | 0,715 |
| Lane count – Precision | 96,6% | **99,4%** |
| Road type – Accuracy | 76,5% | 53,0% |
| Ego lane – Accuracy | 86,0% | **86,5%** |
| Biển báo – Precision | Không đo được (dữ liệu quá thưa) | **60,9%** |
| Biển báo – Recall | Không đo được (dữ liệu quá thưa) | **60,9%** |

Precision số làn và Accuracy làn ego giữ nguyên hoặc cao hơn trên dữ liệu hoàn toàn độc lập — bằng chứng cho thấy thuật toán cốt lõi (ghép cặp làn ego, công thức đếm làn) tổng quát hóa tốt, không overfit vào đặc thù của CULane. Ngược lại, tỉ lệ khớp chính xác (exact match) giảm rõ rệt, do mô hình có xu hướng bỏ sót làn cùng chiều (under-detect) trong điều kiện camera và ánh sáng khác CULane, chứ không phải hiện tượng bịa làn giả — Precision vẫn rất cao. Đây cũng là lần đầu tiên Precision/Recall của module biển báo được đo lường, điều không thực hiện được trên CULane do dữ liệu quá thưa biển báo (mục 4.3).

## 4.3. Module biển báo giao thông trên CULane

Sử dụng mô hình YOLOv8n đã tự tinh chỉnh trên TT100K (mục 3.2), một phát hiện quan trọng là dataset CULane có mật độ biển báo và đèn tín hiệu rất thấp: chỉ 6% ảnh CULane (12/200) có detection ở ngưỡng chuẩn 0,5, và 20% ảnh không có detection nào dù đã hạ ngưỡng xuống 0,01. Đây là hạn chế của dữ liệu benchmark — CULane vốn được thiết kế cho bài toán phát hiện làn đường — không phải hạn chế của mô hình, điều này được xác nhận qua kết quả tốt hơn hẳn trên dữ liệu dashcam thực tế tự thu thập (mục 4.2, Precision/Recall 60,9%).

**So sánh với công trình cùng hướng.** SafeRoute và Advancing-AV-Intelligence [11], [12] báo cáo accuracy phân loại biển báo từ 96,6% đến 99,8% (YOLOv8 đạt 98,0%) — cao hơn đáng kể so với Precision/Recall 60,9% của đề tài. Chênh lệch này chủ yếu đến từ khác biệt về độ khó bài toán: các con số 96,6–99,8% là accuracy phân loại trên biển báo đã được khoanh vùng sẵn, trong khi Precision/Recall 60,9% của đề tài đo trên bài toán phát hiện từ đầu — vừa phải định vị vừa phải phân loại trên toàn khung hình, không có gợi ý vị trí trước — một bài toán khó hơn về bản chất.

## 4.4. So sánh mô hình LLM cho tầng suy luận

Toàn bộ so sánh trong mục này (Giai đoạn 1, mục 3.6) được chạy ở cùng một chế độ cố định — chế độ kết hợp — và chấm điểm bởi đúng một judge (Gemini), nhằm chọn ra mô hình LLM sẽ được giữ cố định cho Giai đoạn 2 — so sánh chế độ input, mục 4.5 — chứ không phải một phần của thực nghiệm ba-judge/ba-chế-độ trả lời câu hỏi nghiên cứu cốt lõi.

**Độ tin cậy và tốc độ.** `ising-calibration-31b` đạt tỉ lệ thành công 200/200 (0% lỗi), thời gian trung bình 3,80 giây/ảnh. `nemotron-nano-12b-v2-vl` chỉ đạt 34/200 (83% yêu cầu nhận lỗi 500 Internal Server Error từ phía máy chủ NVIDIA NIM).

Mô hình `nemotron-nano-12b-v2-vl` bị loại khỏi vòng so sánh chất lượng vì hai lý do độc lập, không phải vì bản thân câu trả lời — khi có — kém chất lượng. Thứ nhất, áp dụng đúng tiêu chí loại trừ về độ tin cậy đã đặt ra ở mục 3.6: chỉ 17,1% yêu cầu phản hồi thành công (lỗi 500 từ hạ tầng máy chủ NVIDIA NIM, không phản ánh trực tiếp năng lực mô hình, nhưng vẫn khiến mô hình không thể triển khai trên thực tế). Thứ hai, ngay cả khi bỏ qua tiêu chí loại trừ trên, 34 câu trả lời thành công còn lại không tạo thành một mẫu so sánh công bằng: đây là tập con tự chọn lọc bởi chính cơ chế gây lỗi của máy chủ, nhiều khả năng thiên lệch về phía các ảnh hoặc yêu cầu đơn giản hơn, ít tốn thời gian xử lý hơn, chứ không phải một mẫu ngẫu nhiên đại diện cho toàn bộ 200 ảnh như hai mô hình còn lại đạt được ở phép so sánh này. So sánh chất lượng giữa 34 mẫu thiên lệch với 200 mẫu đầy đủ của các mô hình khác sẽ vi phạm nguyên tắc so sánh công bằng đã đặt ra cho toàn bộ phương pháp luận đánh giá của đề tài (mục 3.7).

**Tuân thủ cấu trúc output.** Trên N=200, đếm số output có độ dài dưới 80 ký tự — tương đương bỏ qua cấu trúc ba phần bắt buộc — cho thấy `nemotron-nano-8b` có 99/200 (49,5%) output bị cắt cụt, trong khi `ising-calibration-31b` có 0/200 (0%) trên đúng tập đối chứng này. Xét trên độ dài toàn bộ output, `nemotron-nano-8b` sinh trung bình 95 ký tự/câu trả lời (SD = 78), trong khi `ising-calibration-31b` sinh trung bình 876 ký tự/câu trả lời (SD = 198) — gấp hơn 9 lần, đủ để trình bày trọn vẹn ba phần Tình huống/Khuyến nghị/Lưu ý an toàn theo đúng yêu cầu prompt (mục 3.5), thay vì một câu trả lời rút gọn không đạt cấu trúc tối thiểu.

**Chất lượng nội dung** (so với `nemotron-nano-8b`, N=200, cùng ảnh, cùng judge Gemini, cùng rubric sáu tiêu chí). Đây là phép so sánh trực tiếp và công bằng nhất trong ba mô hình, vì cả hai đều vượt qua tiêu chí loại trừ về độ tin cậy — `nemotron-nano-8b` hoàn thành 200/200, không bị loại vì lý do thiên lệch mẫu như `nemotron-nano-12b-v2-vl`. Áp dụng đúng phương pháp thống kê đã dùng ở mục 4.5 — tính điểm trung bình sáu tiêu chí theo từng ảnh trước, rồi kiểm định bắt cặp trên 200 cặp điểm-trên-ảnh — kết quả ở Bảng 4.4 cho thấy khoảng cách không chỉ lớn mà còn có ý nghĩa thống kê rất mạnh. (Nhắc lại: mỗi tiêu chí chấm trên thang 1–5 theo mô tả cố định ở Bảng 3.5, mục 3.7 — điểm càng cao càng đúng và có căn cứ.)

**Bảng 4.4.** So sánh chi tiết chất lượng nội dung giữa `nemotron-nano-8b` và `ising-calibration-31b` (Mean ± SD, N=200, kiểm định Wilcoxon signed-rank bắt cặp theo ảnh).

| Tiêu chí | nemotron-nano-8b | ising-calibration-31b | Wilcoxon p |
|---|---|---|---|
| Hiểu tình huống | 1,97 ± 1,15 | 3,48 ± 1,24 | p < 0,001 |
| Hiểu hình học đường | 2,08 ± 1,27 | 3,77 ± 0,92 | p < 0,001 |
| Vị trí làn ego | 2,03 ± 1,13 | 3,77 ± 1,24 | p < 0,001 |
| Biển báo và quy tắc | 2,17 ± 1,42 | 3,18 ± 1,32 | p < 0,001 |
| Khuyến nghị lái xe | 3,98 ± 1,13 | 4,16 ± 1,20 | p = 0,066 |
| Lưu ý an toàn | 1,69 ± 0,98 | 3,74 ± 1,19 | p < 0,001 |
| **Trung bình 6 tiêu chí (điểm/ảnh)** | **2,32 ± 0,99** | **3,68 ± 0,96** | paired t: t = −14,68, p < 0,001; Cohen's d = −1,04 (rất lớn) |

`ising-calibration-31b` vượt trội có ý nghĩa thống kê ở năm trên sáu tiêu chí (p < 0,001), với kích thước hiệu ứng tổng thể rất lớn (Cohen's d ≈ 1,04, tức chênh lệch trung bình vượt quá một độ lệch chuẩn). Riêng tiêu chí Khuyến nghị lái xe, chênh lệch 3,98 so với 4,16 không đạt ý nghĩa thống kê (p = 0,066) — hai mô hình được đánh giá tương đương nhau ở đúng tiêu chí này, không phải `ising-calibration-31b` thắng tuyệt đối ở toàn bộ sáu tiêu chí. Điều này không làm suy yếu quyết định chọn mô hình: năm trên sáu tiêu chí còn lại, cùng với chênh lệch rất lớn về độ tin cậy và về độ dài/tính đầy đủ cấu trúc output (876 so với 95 ký tự), đã là căn cứ đủ mạnh và đủ toàn diện.

Tổng hợp cả ba tiêu chí theo đúng thứ tự ưu tiên đã đặt ra ở mục 3.6 — độ tin cậy, tuân thủ cấu trúc, chất lượng nội dung — `ising-calibration-31b` là lựa chọn tốt nhất trong ba mô hình, và được chọn làm mô hình chính cho toàn bộ thực nghiệm còn lại của đề tài.

## 4.5. Kết quả chính: đóng góp của thông tin ngữ nghĩa có cấu trúc

Đây là kết quả trung tâm trả lời câu hỏi nghiên cứu cốt lõi, đo trên mô hình chính (`ising-calibration-31b`), ba chế độ input, chấm điểm bởi ba judge độc lập (Gemini, GPT-5 Mini, DeepSeek) dùng nguyên văn cùng một rubric, trên toàn bộ N=200 ảnh. Ở hai chế độ có thông tin ngữ nghĩa, dữ liệu được cấp dưới dạng **JSON đầy đủ**, không phải JSON rút gọn (lý do lựa chọn: mục 3.4).

Với mỗi ảnh, điểm tổng hợp của một chế độ được tính bằng trung bình cộng của sáu điểm tiêu chí trên chính ảnh đó (thang 1–5); từ đó thu được, với mỗi judge, ba dãy 200 điểm bắt cặp theo ảnh — một dãy cho mỗi chế độ. Điểm trung bình toàn mẫu của một chế độ, dùng để báo cáo ở Bảng 4.5, là trung bình cộng của dãy 200 điểm-trên-ảnh đó:

$$\text{Điểm(chế độ)} = \frac{1}{200} \sum_{j=1}^{200} \left[ \frac{1}{6} \sum_{i=1}^{6} \text{điểm}(\text{ảnh } j, \text{tiêu chí } i, \text{chế độ}) \right]$$

Việc tính điểm theo từng ảnh trước, rồi mới lấy trung bình, giúp mỗi ảnh đóng góp đúng một lần vào kết quả cuối và cho phép thực hiện kiểm định thống kê bắt cặp (paired) giữa các chế độ trên cùng một ảnh, thay vì chỉ so sánh hai giá trị trung bình đơn lẻ.

**Bảng 4.5.** Điểm chất lượng khuyến nghị lái xe (Mean ± SD trên 200 ảnh) theo ba chế độ input, chấm bởi ba judge độc lập (thang 1–5).

| Judge | Chỉ ảnh | Chỉ ngữ nghĩa | Kết hợp | Xếp hạng |
|---|---|---|---|---|
| Gemini | 3,32 ± 0,95 | **4,53 ± 0,77** | 3,97 ± 0,95 | Ngữ nghĩa > Kết hợp > Ảnh |
| GPT-5 Mini | 3,13 ± 0,75 | 3,55 ± 1,14 | **3,96 ± 0,86** | Kết hợp > Ngữ nghĩa > Ảnh |
| DeepSeek | 3,11 ± 0,96 | **3,41 ± 1,17** | 3,40 ± 1,02 | Ngữ nghĩa ≈ Kết hợp > Ảnh |

Kết quả điểm trung bình này gần như không đổi so với lần đo trước đó ở N=200 (chênh lệch chỉ ở chữ số thập phân thứ ba), cho thấy kết luận ổn định, không nhạy với việc thêm hoặc bớt một vài mẫu. Độ lệch chuẩn tương đối lớn ở cả ba chế độ (0,75–1,17 trên thang 1–5) phản ánh mức độ đa dạng tự nhiên giữa các ảnh: có ảnh dễ — đường thẳng, ít vật cản — cho điểm cao ở mọi chế độ, có ảnh khó — giao lộ, thiếu vạch kẻ — cho điểm thấp ở mọi chế độ. Vì vậy, khoảng cách trung bình giữa các chế độ cần được kiểm định thống kê thay vì chỉ so sánh trực quan hai con số, trình bày ở Bảng 4.6.

**Bảng 4.6.** Kiểm định ý nghĩa thống kê khi so sánh cặp giữa ba chế độ input, theo từng judge (N=200, dữ liệu bắt cặp theo ảnh; kiểm định t bắt cặp và Wilcoxon signed-rank; d là Cohen's d cho hiệu số bắt cặp).

| Judge | Cặp so sánh | t bắt cặp (df=199) | p (t-test) | Wilcoxon p | Cohen's d |
|---|---|---|---|---|---|
| Gemini | Chỉ ảnh vs Chỉ ngữ nghĩa | −13,62 | p < 0,001 | p < 0,001 | −0,96 (lớn) |
| Gemini | Chỉ ảnh vs Kết hợp | −8,37 | p < 0,001 | p < 0,001 | −0,59 (trung bình–lớn) |
| Gemini | Chỉ ngữ nghĩa vs Kết hợp | 7,28 | p < 0,001 | p < 0,001 | 0,51 (trung bình) |
| GPT-5 Mini | Chỉ ảnh vs Chỉ ngữ nghĩa | −4,33 | p < 0,001 | p < 0,001 | −0,31 (nhỏ) |
| GPT-5 Mini | Chỉ ảnh vs Kết hợp | −11,16 | p < 0,001 | p < 0,001 | −0,79 (lớn) |
| GPT-5 Mini | Chỉ ngữ nghĩa vs Kết hợp | −4,93 | p < 0,001 | p < 0,001 | −0,35 (nhỏ) |
| DeepSeek | Chỉ ảnh vs Chỉ ngữ nghĩa | −2,83 | p = 0,005 | p = 0,003 | −0,20 (nhỏ) |
| DeepSeek | Chỉ ảnh vs Kết hợp | −3,19 | p = 0,002 | p < 0,001 | −0,23 (nhỏ) |
| DeepSeek | Chỉ ngữ nghĩa vs Kết hợp | 0,09 | p = 0,930 | p = 0,625 | 0,01 (không đáng kể) |

Kết quả kiểm định củng cố kết luận ở Bảng 4.5: trong sáu phép so sánh liên quan trực tiếp đến chế độ chỉ-ảnh — ba judge nhân hai cặp so sánh — đều có ý nghĩa thống kê ở mức p < 0,01, xác nhận chế độ chỉ-ảnh thấp hơn hai chế độ còn lại không phải do ngẫu nhiên. Với chín kiểm định đồng thời trong Bảng 4.6, ngưỡng Bonferroni tương ứng là p < 0,0056; toàn bộ sáu phép so sánh có ý nghĩa nêu trên vẫn thỏa ngưỡng này (kể cả cặp sát ngưỡng nhất — DeepSeek, chỉ-ảnh vs chỉ-ngữ-nghĩa, p = 0,005), riêng phép so sánh duy nhất không có ý nghĩa (chỉ-ngữ-nghĩa vs kết hợp của DeepSeek) giữ nguyên kết luận không đổi. Kích thước hiệu ứng dao động từ nhỏ ở DeepSeek (d ≈ 0,20–0,23) đến lớn ở Gemini (d ≈ 0,59–0,96), phù hợp với việc Gemini đồng thời là judge có độ tin cậy cao nhất khi đối chiếu với con người (mục 4.6) — gợi ý rằng khoảng cách điểm số lớn hơn ở Gemini không chỉ là nhiễu thống kê mà phản ánh một tín hiệu thật rõ ràng hơn. Riêng phép so sánh chỉ-ngữ-nghĩa với kết hợp của DeepSeek không có ý nghĩa thống kê (p = 0,930, d ≈ 0,01), xác nhận định lượng cho nhận định "ngữ nghĩa ≈ kết hợp" đã nêu ở Bảng 4.5: đây không phải hai chế độ có điểm số ngẫu nhiên gần nhau, mà thực sự không khác biệt theo đánh giá của judge này.

Bảng 4.7 minh họa cách tính điểm trung bình tiêu chí bằng ví dụ chi tiết của judge Gemini, kèm độ lệch chuẩn của từng tiêu chí và kết quả kiểm định Wilcoxon cho hai so sánh chính.

**Bảng 4.7.** Điểm trung bình (Mean ± SD, N=200/tiêu chí) sáu tiêu chí đánh giá của judge Gemini theo từng chế độ input, kèm kiểm định Wilcoxon so với chế độ chỉ-ảnh.

| Tiêu chí | Chỉ ảnh | Chỉ ngữ nghĩa | Kết hợp | Wilcoxon p (ảnh vs ngữ nghĩa) | Wilcoxon p (ảnh vs kết hợp) |
|---|---|---|---|---|---|
| Hiểu tình huống | 2,76 ± 1,12 | 4,38 ± 0,95 | 3,51 ± 1,31 | p < 0,001 | p < 0,001 |
| Hiểu hình học đường | 3,27 ± 1,00 | 4,47 ± 0,87 | 4,04 ± 1,02 | p < 0,001 | p < 0,001 |
| Vị trí làn ego | 3,27 ± 1,25 | 4,64 ± 0,76 | 4,21 ± 1,17 | p < 0,001 | p < 0,001 |
| Biển báo và quy tắc | 3,84 ± 1,51 | 4,72 ± 0,75 | 4,24 ± 1,24 | p < 0,001 | p < 0,001 |
| Khuyến nghị lái xe | 3,50 ± 1,41 | 4,58 ± 0,87 | 3,97 ± 1,38 | p < 0,001 | p < 0,001 |
| Lưu ý an toàn | 3,31 ± 1,21 | 4,39 ± 0,95 | 3,85 ± 1,30 | p < 0,001 | p < 0,001 |
| **Trung bình 6 tiêu chí** | **3,32 ± 0,95** | **4,53 ± 0,77** | **3,97 ± 0,95** | — | — |

Cả sáu tiêu chí đều cho khác biệt có ý nghĩa thống kê mạnh (p < 0,001) khi so chế độ chỉ-ảnh với chế độ chỉ-ngữ-nghĩa hoặc với chế độ kết hợp; với sáu kiểm định đồng thời, ngưỡng Bonferroni tương ứng là p < 0,0083, vẫn được thỏa mãn ở tất cả sáu tiêu chí. Độ lệch chuẩn cao nhất rơi vào tiêu chí biển báo/quy tắc (`traffic_sign_rule`) ở chế độ chỉ-ảnh (± 1,51) — hợp lý vì đây là tiêu chí phụ thuộc nhiều vào việc ảnh có hay không có biển báo dễ nhận biết bằng mắt, một yếu tố dao động mạnh giữa các ảnh; độ lệch chuẩn thấp nhất rơi vào tiêu chí vị trí làn ego (`lane_ego_position`) ở chế độ chỉ-ngữ-nghĩa (± 0,76), phù hợp với việc thông tin vị trí làn ego được cấp sẵn dưới dạng số liệu chính xác trong thông tin ngữ nghĩa có cấu trúc, ít phụ thuộc vào khả năng suy luận thị giác vốn dao động nhiều hơn giữa các ảnh.

Kết luận nhất quán nhất — chế độ chỉ-ảnh luôn đạt điểm thấp nhất — giữ nguyên không ngoại lệ ở cả ba judge được áp dụng độc lập (cùng rubric, cùng ảnh, cùng output, chỉ khác model chấm điểm). Trên nền tảng module hiểu làn đường/biển báo đã kiểm chứng (mục 4.1–4.3) và mô hình suy luận đã lựa chọn (mục 4.4), thông tin ngữ nghĩa có cấu trúc cải thiện rõ rệt chất lượng khuyến nghị lái xe so với chỉ dùng ảnh.

Tuy nhiên, kết luận cần được nêu có sắc thái ở một điểm: thứ hạng giữa chế độ chỉ-ngữ-nghĩa và chế độ kết hợp phụ thuộc vào judge được sử dụng — một judge nghiêng về chỉ-ngữ-nghĩa, một judge nghiêng về kết hợp, một judge coi hai chế độ là ngang nhau — nên không có câu trả lời tuyệt đối cho câu hỏi "kết hợp ảnh và ngữ nghĩa có tốt hơn chỉ dùng ngữ nghĩa hay không". Đây chính là giá trị của phương pháp luận đa-judge: nếu chỉ sử dụng một judge duy nhất, nghiên cứu có nguy cơ báo cáo nhầm một kết luận "chắc chắn" trong khi thực chất đó chỉ là đặc thù riêng của judge đó.

## 4.6. Kiểm chứng độ tin cậy của phương pháp đánh giá

Với 120 cặp điểm — 20 ảnh nhân 6 tiêu chí, mỗi cặp gồm một điểm của con người và một điểm của judge trên cùng ảnh/tiêu chí — ba chỉ số đồng thuận được định nghĩa như sau: Đồng thuận tuyệt đối bằng tỉ lệ số cặp có |điểm người − điểm judge| = 0; Đồng thuận trong sai số ≤1 bằng tỉ lệ số cặp có |điểm người − điểm judge| ≤ 1; Tương quan Pearson r được tính trên hai dãy 120 điểm tương ứng của người và của judge.

**Giới hạn của cỡ mẫu khi diễn giải tương quan.** 120 cặp điểm không phải 120 quan sát độc lập: cả sáu điểm mỗi ảnh đều chịu ảnh hưởng chung của cùng một đơn vị độc lập thực sự — chính bức ảnh đó (một ảnh "khó" có xu hướng kéo điểm thấp ở cả sáu tiêu chí cùng lúc, kể cả khi chấm bởi người lẫn judge). Coi 120 cặp là độc lập khi tính kiểm định ý nghĩa (df=118) cho ra p < 0,0001 (Gemini, r=0,427), p ≈ 0,03 (GPT-5 Mini, r=0,194), và p ≈ 0,12 (DeepSeek, r=0,143) — nhưng đây là các giá trị p lạc quan, vì đơn vị độc lập thực chất chỉ có N=20 ảnh, không phải 120 cặp điểm. Hạn chế này không đảo ngược thứ hạng giữa ba judge (khoảng cách r giữa Gemini và hai judge còn lại đủ lớn để không phụ thuộc vào cách tính), nhưng có nghĩa là mức độ tin cậy tuyệt đối của từng hệ số tương quan — đặc biệt r=0,194 của GPT-5 Mini, vốn chỉ vừa đạt ý nghĩa dưới giả định (sai) rằng 120 cặp độc lập — cần được diễn giải thận trọng hơn con số p nêu trên gợi ý.

**Gemini so với con người** (N=20, 120 cặp điểm): đồng thuận tuyệt đối 44/120 = 36,7%, đồng thuận trong sai số ≤1 điểm 95/120 = 79,2%, tương quan Pearson 0,427.

Cần thận trọng khi đối chiếu con số này với MT-Bench: nghiên cứu đó báo cáo GPT-4 đạt 85% đồng thuận với con người trên một tác vụ so sánh cặp nhị phân, chỉ tính trên các cặp không hòa [5] — khác về bản chất so với việc chấm điểm tuyệt đối trên thang 1–5 của đề tài này. Một quyết định nhị phân đúng/sai không cùng độ khó với một mức độ khoan dung ±1 điểm trên thang 5 mức, vốn có baseline ngẫu nhiên cao hơn hẳn. Do khác loại tác vụ, khác định nghĩa đồng thuận, và khác quy mô kiểm chứng (N=20 so với hàng nghìn cặp), 79,2% và 85% không phải hai con số đối sánh trực tiếp được — việc chúng gần nhau về mặt số học không tự nó là bằng chứng cho độ tin cậy của Gemini, và luận văn không dùng đây làm căn cứ chính.

Bằng chứng vững chắc hơn, và là căn cứ chính cho quyết định dùng Gemini làm judge chính của đề tài, đến từ chính nội bộ nghiên cứu: Gemini đạt mức đồng thuận và tương quan cao hơn rõ rệt so với hai judge còn lại, được kiểm chứng theo đúng cùng phương pháp, cùng thang đo, cùng mẫu N=20 (Bảng 4.8) — một phép so sánh công bằng, cùng đơn vị đo, không phụ thuộc vào việc đối chiếu với một nghiên cứu khác dùng tác vụ khác.

**GPT-5 Mini so với con người** (cùng N=20): đồng thuận tuyệt đối 23,3%, trong sai số ≤1 điểm 62,5%, tương quan 0,194 — thấp hơn Gemini ở cả ba chỉ số, củng cố quyết định dùng Gemini làm judge chính.

**DeepSeek so với con người** (cùng N=20, 120 cặp điểm): đồng thuận tuyệt đối 25,8%, trong sai số ≤1 điểm 55,0%, tương quan 0,143 — thấp nhất trong ba judge, với tương quan Pearson gần như không có ý nghĩa thống kê thực tế trên cỡ mẫu này. Điểm đáng chú ý là DeepSeek có xu hướng chấm thấp hơn con người một cách hệ thống — chênh lệch trung bình người trừ DeepSeek là +1,21, lớn hơn nhiều so với Gemini và GPT — với nhiều trường hợp con người chấm 4–5 điểm nhưng DeepSeek chỉ chấm 1–2 điểm, đặc biệt ở hai tiêu chí Biển báo và quy tắc, Vị trí làn ego. Có thể DeepSeek diễn giải rubric khắt khe hơn, hoặc ít khoan dung hơn với các suy luận gián tiếp không có bằng chứng tường minh trong thông tin ngữ nghĩa có cấu trúc.

**Bảng 4.8.** Xếp hạng độ tin cậy của ba judge khi đối chiếu với đánh giá của con người (N=20).

| Judge | Đồng thuận tuyệt đối | Trong sai số ≤1 | Tương quan Pearson |
|---|---|---|---|
| Gemini | **36,7%** | **79,2%** | **0,427** |
| DeepSeek | 25,8% | 55,0% | 0,143 |
| GPT-5 Mini | 23,3% | 62,5% | 0,194 |

Gemini vượt trội rõ rệt ở cả ba chỉ số so với hai judge còn lại, củng cố quyết định dùng Gemini làm judge chính cho toàn bộ các kết luận trọng tâm của đề tài (mục 4.4, 4.5); GPT-5 Mini và DeepSeek chỉ đóng vai trò tham khảo và đối chiếu chéo (mục 4.5).

Một phát hiện phương pháp luận đáng chú ý là tương quan giữa GPT và Gemini với nhau (0,511) còn cao hơn tương quan của mỗi judge với con người (0,427 và 0,194) — minh chứng trực tiếp rằng hai judge AI có xu hướng đồng ý với nhau nhiều hơn đồng ý với con người, có thể do cùng chia sẻ một mức độ nghiêm khắc nhất định khác với người chấm không chuyên. Tương quan giữa DeepSeek và Gemini cũng đạt 0,395, vẫn cao hơn tương quan DeepSeek-người (0,143), củng cố thêm cùng một phát hiện. Đây là lý do phương pháp luận của đề tài dùng đúng một judge cố định (Gemini) cho các so sánh chính, và dùng độ đồng thuận với con người — không phải độ đồng thuận giữa các judge — làm mốc chuẩn.

## 4.7. Kiểm chứng khả năng tự nhận diện làn đường của VLM

Một câu hỏi đặt ra là: nếu không đi qua tầng UFLD-v2 và xử lý ngữ nghĩa, bản thân VLM (`ising-calibration-31b`) tự quan sát ảnh có nhận diện được ngữ nghĩa làn đường chính xác tới đâu? Để trả lời, một thực nghiệm bổ sung được thực hiện: gửi cho VLM duy nhất bức ảnh, không kèm bất kỳ thông tin ngữ nghĩa có cấu trúc hay gợi ý nào, yêu cầu trả về JSON đúng schema `_brief.json` hiện tại (`lane_count`, `ego_lane`, `vehicle_offset`, `neighbor_lanes`, `road_shape`), trên cả hai bộ dữ liệu (CULane N=200, real-life N=200). Toàn bộ 200/200 ảnh ở cả hai bộ đều nhận được JSON hợp lệ.

**Bảng 4.9.** So sánh khả năng tự nhận diện ngữ nghĩa làn đường giữa pipeline UFLD-v2 và VLM.

| Bộ dữ liệu / Nhóm | Lane count Accuracy (Pipeline) | Lane count Accuracy (VLM) | Lane count MAE (Pipeline) | Lane count MAE (VLM) | Road shape bucket match (Pipeline) | Road shape bucket match (VLM) |
|---|---|---|---|---|---|---|
| CULane – Normal (N=176, có vạch kẻ) | **77,3%** | 54,5% | **0,273** | 0,477 | 84,1% | **95,5%** |
| CULane – Hard (N=24, không vạch kẻ) | 8,3% | **37,5%** | 1,958 | **0,792** | 20,8% | **91,7%** |
| CULane – Toàn bộ (N=200) | **69,0%** | 52,5% | **0,475** | 0,515 | 76,5% | **95,0%** |
| Real-life độc lập (N=200) | 50,5% | **53,5%** | 0,715 | **0,510** | 53,0% | **69,5%** |

Phát hiện chính từ Bảng 4.9 là pipeline chuyên biệt (UFLD-v2) chỉ vượt trội rõ rệt VLM ở đúng một điều kiện: ảnh CULane có vạch kẻ, đúng domain mà nó được pretrain. Ở hai điều kiện còn lại — CULane không vạch kẻ, và toàn bộ dữ liệu real-life thuộc domain khác CULane — VLM tự nhận diện đạt hoặc vượt pipeline ở mọi chỉ số, đặc biệt rõ ở road shape (phân loại thẳng/cong), nơi VLM vượt trội pipeline ở cả bốn dòng của bảng. Điều này gợi ý rằng ưu thế của pipeline một phần đến từ việc cùng domain với dữ liệu huấn luyện, không chỉ từ bản chất kiến trúc của một detector chuyên biệt: pipeline trở nên giòn và dễ vỡ khi ra khỏi đúng vùng an toàn đó, trong khi VLM tổng quát — không được tinh chỉnh riêng cho bài toán làn đường — lại ổn định hơn.

## 4.8. Bàn luận: giả thuyết về cơ chế đóng góp của thông tin ngữ nghĩa có cấu trúc

Mục 4.7 cho thấy VLM tự nhận diện làn đường không hề yếu — vậy vì sao chế độ chỉ-ngữ-nghĩa/kết hợp vẫn vượt chế độ chỉ-ảnh rõ rệt ở mục 4.5? Giả thuyết được đề tài đề xuất: thông tin ngữ nghĩa có cấu trúc không chỉ bù đắp năng lực thị giác còn thiếu, mà chủ yếu đóng vai trò **khung đỡ (scaffolding)** cho suy luận và trình bày trong một tác vụ ghép nhiều bước. Ba căn cứ ủng hộ giả thuyết này:

- **Độ phức tạp tác vụ khác nhau.** Mục 4.7 chỉ yêu cầu một việc — trích xuất số liệu theo schema cứng; chế độ chỉ-ảnh ở mục 4.5 dồn ba việc vào một lượt sinh duy nhất (tự nhận diện, tự suy luận, tự viết đúng cấu trúc ba phần theo một prompt dài — mục 3.5). Năng lực tốt ở một tác vụ hẹp không đảm bảo chất lượng khi tác vụ đó chỉ là một bước ẩn trong chuỗi phức tạp hơn.
- **Prompt không tương đương.** Chế độ chỉ-ngữ-nghĩa cấp sẵn dữ liệu có cấu trúc để tham chiếu trực tiếp khi viết câu trả lời; chế độ chỉ-ảnh chỉ yêu cầu quan sát ảnh chung chung, ít khung đỡ hơn hẳn.
- **Judge chấm văn phong, không đối chiếu ground truth.** Một câu trả lời trích số liệu cụ thể ("làn 2/3, lệch 19,3%") dễ được đánh giá là có căn cứ và tự tin hơn, dù độ chính xác thực tế của con số đó chưa chắc cao hơn — đúng thiên vị phong cách viết mà MT-Bench đã ghi nhận như hạn chế cố hữu của LLM-as-judge [5] (mục 2.4), lý do đề tài kiểm chứng bằng đối chiếu con người thay vì tin tuyệt đối vào judge (mục 4.6).

Các phát hiện trên **phù hợp với** giả thuyết khung đỡ, chứ chưa phải bằng chứng trực tiếp chứng minh nó: đây là suy luận dựa trên bằng chứng gián tiếp — hai thực nghiệm dùng hai prompt khác độ phức tạp — chưa qua một thực nghiệm đối chứng trực tiếp (cùng độ phức tạp prompt, chỉ khác có/không thông tin ngữ nghĩa có cấu trúc); đây là một hướng mở rộng ở mục 5.4. Cách diễn giải này không làm suy yếu kết luận của câu hỏi nghiên cứu cốt lõi — thông tin ngữ nghĩa có cấu trúc vẫn cải thiện chất lượng khuyến nghị, kiểm chứng bởi ba judge độc lập — mà làm rõ hơn một cách thận trọng về cơ chế có thể có phía sau kết quả đó.

## 4.9. Hạn chế: rủi ro trùng lặp dữ liệu (data leakage) và hiệu chỉnh tham số

200 ảnh đánh giá ở mục 4.1 được lấy ngẫu nhiên từ CULane, cùng nguồn dữ liệu mà mô hình phát hiện làn đường (`culane_res34.pth`) được pretrain, mà không đối chiếu với danh sách phân chia train/val/test chính thức, do bản dữ liệu cục bộ sử dụng không có sẵn thông tin này. Do đó, không loại trừ khả năng một phần ảnh đánh giá trùng với dữ liệu mà mô hình đã học qua, có thể khiến Accuracy và Precision tuyệt đối ở mục 4.1 lạc quan hơn khả năng tổng quát hóa thực tế. Hạn chế này không ảnh hưởng tới các so sánh tương đối — mức cải thiện trước/sau sửa lỗi, toàn bộ kết quả mục 4.4–4.6 — vì các so sánh này dùng chung một lần detect, chỉ khác ở bước xử lý hoặc mô hình phía sau. Kết quả ở mục 4.2, kiểm chứng trên dữ liệu real-life, được thực hiện chính là để giảm thiểu rủi ro này.

Một rủi ro cùng bản chất, tuy quy mô nhỏ hơn, tồn tại ở bước hiệu chỉnh ngưỡng phân loại độ cong (mục 3.3, Bảng 3.1): các ngưỡng $\overline{\text{drift}}_{straight}$/$\overline{\text{drift}}_{sharp}$ được hiệu chỉnh bằng cách đối chiếu avg_drift do thuật toán tính ra với hình dạng đường xác nhận bằng nhãn tay trên một tập ảnh CULane riêng (199 ảnh, kết hợp thêm 200 ảnh Tusimple, chạy qua một script hiệu chỉnh riêng biệt với quy trình đánh giá chính thức). Đề tài không có bản ghi lưu vết đủ chi tiết để xác nhận tập 199 ảnh CULane dùng hiệu chỉnh này có trùng, có giao, hay hoàn toàn tách biệt với 200 ảnh CULane dùng đánh giá ở mục 4.1 — nên không loại trừ được khả năng ngưỡng phân loại độ cong đã được hiệu chỉnh một phần trên chính dữ liệu dùng để báo cáo Accuracy của road type ở Bảng 4.1. Rủi ro này, nếu có, chỉ ảnh hưởng tới chỉ số phân loại hình dạng đường (road type), không ảnh hưởng tới số làn, làn ego, hay độ lệch tâm xe — vốn không phụ thuộc vào các ngưỡng này.

**Tóm tắt chương.** Chương này đã trình bày kết quả thực nghiệm cho câu hỏi nghiên cứu cốt lõi: độ chính xác của module hiểu làn đường và biển báo (mục 4.1–4.3), lựa chọn mô hình suy luận (mục 4.4), đóng góp của thông tin ngữ nghĩa có cấu trúc cùng kiểm chứng độ tin cậy của phương pháp đánh giá (mục 4.5–4.6), một thực nghiệm bổ sung và giả thuyết về cơ chế đóng góp của thông tin đó (mục 4.7–4.8), và các hạn chế về dữ liệu/hiệu chỉnh tham số cần lưu ý khi diễn giải kết quả (mục 4.9). Chương 5 tiếp theo tổng kết các đóng góp, trả lời trực tiếp từng câu hỏi nghiên cứu, thảo luận hạn chế và đề xuất hướng phát triển tiếp theo.

---

# CHƯƠNG 5. KẾT LUẬN

## 5.1. Trả lời câu hỏi nghiên cứu

**Câu hỏi nghiên cứu cốt lõi** (mục 1.1): thông tin ngữ nghĩa có cấu trúc cải thiện chất lượng khuyến nghị lái xe so với chỉ dùng ảnh — kết luận có kiểm chứng vững chắc (mục 4.5), với cơ chế đóng góp được làm rõ thêm ở mục 4.7–4.8.

Ba kết quả thực nghiệm sau đây là căn cứ trực tiếp cho kết luận trên:

- **Độ chính xác các module trích xuất ngữ nghĩa**: đã được trả lời định lượng đầy đủ ở mục 4.1–4.3 (module hiểu làn đường và biển báo).
- **Lựa chọn mô hình suy luận**: `ising-calibration-31b` là lựa chọn phù hợp nhất trong phạm vi mô hình khảo sát, dựa trên độ tin cậy, tuân thủ cấu trúc và chất lượng nội dung (mục 4.4).
- **Độ tin cậy của phương pháp đánh giá**: LLM-as-a-judge (Gemini) đạt độ tin cậy chấp nhận được khi đối chiếu với con người, tốt hơn hai judge thay thế đã thử nghiệm — GPT-5 Mini, DeepSeek — ở cả ba chỉ số đồng thuận (mục 4.6).

## 5.2. Tóm tắt đóng góp

Đề tài xây dựng và kiểm chứng định lượng một pipeline hoàn chỉnh cho bài toán hiểu ngữ nghĩa làn đường và biển báo giao thông hỗ trợ ra quyết định lái xe bằng LLM, trên hai bộ dữ liệu chuẩn phổ biến (CULane, TT100K). Tầng suy luận theo hướng tiếp cận training-free — khác với các hệ VLM lái xe end-to-end (DriveGPT4 [2], DriveLM [3], LMDrive [4]) vốn đòi hỏi huấn luyện quy mô lớn (mục 2.3, 2.5) — trong khi tầng nhận diện biển báo có một bước tinh chỉnh YOLOv8n quy mô nhẹ trên TT100K (mục 3.2). Các kết quả chính, có số liệu định lượng cụ thể, gồm:

1. **Module hiểu làn đường** đạt Accuracy 77,3% trên ảnh có vạch kẻ rõ (N=176/200), tổng quát hóa tốt sang dữ liệu độc lập tự thu thập (Precision 99,4%, Ego lane Accuracy 86,5%, N=200), nhưng giảm mạnh còn 8,3% trên 24 ảnh không có vạch kẻ rõ — một giới hạn cố hữu của detector dựa trên vạch kẻ (mục 4.1).
2. **Module biển báo** đạt hiệu quả thực sự khi dữ liệu đủ dày (Precision/Recall 60,9% trên dữ liệu real-life), nhưng bị giới hạn trên CULane do đặc thù dataset thưa biển báo (6% ảnh có detection).
3. **Thông tin ngữ nghĩa có cấu trúc cải thiện rõ rệt chất lượng khuyến nghị lái xe** — đóng góp trung tâm của đề tài: Gemini 3,32 → 4,53/5, tương đương +36%, có kiểm chứng nhất quán bởi ba judge độc lập trên N=200 (mục 4.5).
4. **Làm rõ cơ chế đóng góp của thông tin ngữ nghĩa có cấu trúc**: một kiểm chứng bổ sung cho thấy VLM tự nhận diện làn đường từ ảnh thô không hề yếu, thậm chí vượt pipeline UFLD-v2 khi thiếu vạch kẻ hoặc trên dữ liệu ngoài domain (mục 4.7) — phát hiện này phù hợp với giả thuyết rằng thông tin ngữ nghĩa có cấu trúc đóng vai trò khung đỡ cho suy luận và trình bày trong một tác vụ ghép nhiều bước, hơn là chỉ đơn thuần bù đắp năng lực cảm nhận thị giác còn thiếu (mục 4.8) — đây là suy luận dựa trên bằng chứng gián tiếp, chưa qua thực nghiệm đối chứng trực tiếp.
5. **Bằng chứng bước đầu về độ tin cậy của phương pháp đánh giá LLM-as-a-judge**: đối chiếu với con người trên một mẫu N=20 đạt 79,2% đồng thuận trong sai số ≤1, và đối chiếu chéo ba judge cùng phương pháp cho thấy Gemini vượt trội rõ rệt GPT-5 Mini và DeepSeek ở cả ba chỉ số đồng thuận với con người (mục 4.6) — căn cứ chính cho việc chọn Gemini làm judge chính, thay vì đối sánh trực tiếp với các nghiên cứu LLM-as-a-judge khác vốn dùng tác vụ và thang đo khác biệt về bản chất [5].

**Ý nghĩa thực tiễn.** Các kết quả trên cho thấy một hệ hỗ trợ quyết định lái xe có khả năng diễn giải bằng ngôn ngữ tự nhiên có thể được xây dựng mà không cần huấn luyện lại một VLM/LLM quy mô lớn: tầng suy luận dùng nguyên trạng một VLM có sẵn qua API; tầng nhận diện biển báo chỉ cần một bước tinh chỉnh nhẹ trên một mô hình nhỏ (YOLOv8n, khoảng 3,2 triệu tham số) thay vì thu thập dữ liệu và huấn luyện một hệ end-to-end quy mô lớn. Kết quả này phù hợp làm nền tảng cho các ứng dụng dashcam hoặc hộp đen thông minh, hoặc làm điểm khởi đầu để mở rộng sang dữ liệu giao thông Việt Nam mà không cần xây dựng lại từ đầu — chỉ cần tinh chỉnh nhẹ ở tầng nhận diện làn đường và biển báo (mục 5.4); chi phí vận hành thực tế khi triển khai sản xuất chưa được đánh giá trong phạm vi đề tài này.

## 5.3. Hạn chế

- **Module hiểu làn đường ở tầng pipeline thị giác máy tính phụ thuộc mạnh vào vạch kẻ đường và vào việc cùng domain với dữ liệu huấn luyện.** Trên 24/200 ảnh CULane thuộc các tình huống không có vạch kẻ rõ, Accuracy số làn giảm từ 77,3% xuống còn 8,3%, dù Precision vẫn đạt 100% (mục 4.1). Kiểm chứng bổ sung ở mục 4.7 cho thấy đây là hạn chế của riêng pipeline thị giác máy tính, không phải của cách tiếp cận nói chung: VLM tự nhận diện trực tiếp từ ảnh không chia sẻ đúng điểm yếu này, thậm chí vượt trội pipeline ở chính hai điều kiện đó — mở ra hướng thiết kế hybrid (mục 5.4).
- Rủi ro trùng lặp dữ liệu (data leakage) trên dữ liệu CULane, và rủi ro tương tự chưa loại trừ được ở bước hiệu chỉnh ngưỡng phân loại độ cong (mục 4.9), giảm thiểu một phần bằng kiểm chứng độc lập trên dữ liệu real-life.
- So sánh mô hình LLM và judge giới hạn trong các lựa chọn miễn phí, chi phí thấp, chưa mở rộng sang các phiên bản thương mại lớn hơn hoặc mới hơn của các họ mô hình đã thử (Gemini, GPT, DeepSeek) hay các mô hình khác như Claude.
- Module biển báo trên CULane bị giới hạn bởi mật độ dữ liệu thưa của bản thân dataset.

## 5.4. Hướng phát triển tiếp theo

Ba hướng sau được sắp xếp theo mức độ ưu tiên, từ tác động thực tiễn cao nhất đến các cải tiến kỹ thuật bổ sung.

**1. Mở rộng sang dữ liệu Việt Nam, kết hợp kiến trúc hybrid.** Hướng ưu tiên cao nhất là áp dụng và đánh giá lại pipeline trên dữ liệu giao thông Việt Nam thực tế — vạch kẻ đường và biển báo theo quy chuẩn QCVN, mật độ xe máy cao, hành vi giao thông khác biệt; bước đầu đã có tín hiệu tích cực qua bộ dữ liệu real-life tự thu thập (mục 4.2). Vì giao thông Việt Nam có nhiều tình huống thiếu vạch kẻ rõ — đúng điểm yếu của pipeline UFLD-v2 (mục 4.1, 5.3) — hướng này nên đi kèm một kiến trúc hybrid: giữ UFLD-v2 làm nguồn chính, tự động chuyển sang kết quả tự nhận diện của VLM (mục 4.7) khi pipeline trả về tín hiệu thấp (`lane_count=0`, độ tin cậy thấp).

**2. Củng cố phương pháp luận đánh giá.** Ba việc cụ thể: (a) một thực nghiệm đối chứng trực tiếp cho giả thuyết "khung đỡ" ở mục 4.8 — chạy chế độ chỉ-ảnh với một prompt hai bước, buộc VLM tự trích xuất thông tin ngữ nghĩa có cấu trúc trước khi viết khuyến nghị, rồi so sánh với chế độ chỉ-ngữ-nghĩa gốc; nếu khoảng cách thu hẹp, giả thuyết được củng cố; (b) mở rộng kiểm chứng đồng thuận người–AI vượt quy mô N=20 hiện tại, có thể áp dụng khung lấy mẫu thích ứng của Kim [15] thay vì chọn mẫu ngẫu nhiên; (c) xây dựng anchor mô tả riêng cho từng tiêu chí trong rubric sáu tiêu chí (mục 3.7), thay vì dùng chung một thang mô tả 1–5 cho cả sáu tiêu chí như hiện tại.

**3. Cải thiện kỹ thuật tầng suy luận và perception.** Gồm: áp dụng cấu trúc tư duy có kiểm chứng như RATT [18] (lập kế hoạch, xác minh sự kiện qua RAG) để giảm rủi ro ảo giác ở các tình huống phức tạp — giao lộ, nhập làn (mục 5.3); bổ sung khả năng phân biệt làn ngược chiều và đường một chiều/hai chiều; cải thiện module biển báo bằng dữ liệu mật độ cao hơn; và thử nghiệm các mô hình LLM thương mại tiên tiến hơn.

---

# TÀI LIỆU THAM KHẢO

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

[19] A. Kuznietsov, B. Gyevnar, C. Wang, S. Peters, and S. V. Albrecht, "Explainable AI for safe and trustworthy autonomous driving: A systematic review," *IEEE Trans. Intell. Transp. Syst.*, vol. 25, no. 12, pp. 19342–19364, Dec. 2024.

[20] J. Nidamanuri, C. Nibhanupudi, R. Assfalg, and H. Venkataraman, "A progressive review: Emerging technologies for ADAS driven solutions," *IEEE Trans. Intell. Veh.*, vol. 7, no. 2, pp. 326–341, 2022.

[21] D. I. Tselentis and E. Papadimitriou, "Driver profile and driving pattern recognition for road safety assessment: Main challenges and future directions," *IEEE Open J. Intell. Transp. Syst.*, vol. 4, pp. 83–100, 2023.

[22] C. Cui, Y. Ma, X. Cao, W. Ye, and Z. Wang, "Drive as you speak: Enabling human-like interaction with large language models in autonomous vehicles," in *Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis. Workshops (WACVW)*, 2024, pp. 902–909.

[23] X. Tian, J. Gu, B. Li, Y. Liu, Y. Wang, Z. Zhao, K. Zhan, P. Jia, X. Lang, and H. Zhao, "DriveVLM: The convergence of autonomous driving and large vision-language models," *arXiv:2402.12289*, 2024.

[24] R. Yao, R. Zhong, P. Liu, M. Peng, R. Yang, and J. Ma, "Decision-making with lightweight confidence-aware language model for autonomous driving," in *Proc. IEEE Int. Conf. Intell. Transp. Syst. (ITSC)*, 2026.

[25] T. Choudhary, V. Dewangan, S. Chandhok, S. Priyadarshan, A. Jain, A. K. Singh, S. Srivastava, K. M. Jatavallabhula, and K. M. Krishna, "Talk2BEV: Language-enhanced bird's-eye view maps for autonomous driving," in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, 2024.

[26] I. Logeswaran, H. Eissa, and R. Almadhoun, "Autonomous vehicle pedestrian detection & traffic sign recognition using YOLOv8," in *Proc. 29th Int. Conf. Autom. Comput. (ICAC)*, 2024.

[27] B. Ji, J. Xu, Y. Liu, P. Fan, and M. Wang, "Improved YOLOv8 for small traffic sign detection under complex environmental conditions," *Franklin Open*, vol. 8, 2024.

[28] S. Wei, P. E. Pfeffer, and J. Edelmann, "State of the art: Ongoing research in assessment methods for lane keeping assistance systems," *IEEE Trans. Intell. Veh.*, vol. 9, pp. 5853–5875, 2024.

[29] Y. Emami, M. Homaei, M. Gutiérrez Gaitán, L. Almeida, K. Li, H. Huang, and Z. Han, "Human-in-the-loop machine learning for safe and ethical autonomous vehicles: Principles, challenges, and opportunities," *arXiv:2408.12548*, 2024.

[30] D. Fernández Llorca, P. Frau, I. Parra, R. Izquierdo, and E. Gómez, "Attribute annotation and bias evaluation in visual datasets for autonomous driving," *J. Big Data*, vol. 11, 2024.

[31] World Health Organization, *Global Status Report on Road Safety 2023*. Geneva, Switzerland: WHO, 2023.

[32] Insurance Institute for Highway Safety (IIHS), "Stay within the lines: Lane departure warning, blind spot detection help drivers avoid trouble," IIHS News, Aug. 2017. [Online]. Available: https://www.iihs.org/news/detail/stay-within-the-lines-lane-departure-warning-blind-spot-detection-help-drivers-avoid-trouble

[33] T. Zheng, Y. Huang, Y. Liu, W. Tang, Z. Yang, D. Cai, and X. He, "CLRNet: Cross layer refinement network for lane detection," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2022.

[34] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)*, 2020.

[35] N. F. Liu, K. Lin, J. Hewitt, A. Paranjape, M. Bevilacqua, F. Petroni, and P. Liang, "Lost in the middle: How language models use long contexts," *Trans. Assoc. Comput. Linguist.*, vol. 12, pp. 157–173, 2024, doi: 10.1162/tacl_a_00638.

[36] Gemini Team, Google, "Gemini: A family of highly capable multimodal models," *arXiv:2312.11805*, 2023.

[37] M. Imran and N. Almusharraf, "Google Gemini as a next generation AI educational tool: A review of emerging educational technology," *Smart Learn. Environ.*, vol. 11, 2024, doi: 10.1186/s40561-024-00310-z.

[38] Z. Qi, Y. Fang, M. Zhang, Z. Sun, T. Wu, Z. Liu, D. Lin, J. Wang, and H. Zhao, "Gemini vs GPT-4V: A preliminary comparison and combination of vision-language models through qualitative cases," *arXiv:2312.15011*, 2023.

[39] L. Tabelini, R. Berriel, T. M. Paixão, C. Badue, A. F. De Souza, and T. Oliveira-Santos, "Keep your eyes on the lane: Real-time attention-guided lane detection," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2021.

[40] X. He, H. Guo, K. Zhu, B. Zhu, X. Zhao, J. Fang, and J. Wang, "Monocular lane detection based on deep learning: A survey," *arXiv:2411.16316*, 2024.

[41] D. Tabernik and D. Skočaj, "Deep learning for large-scale traffic-sign detection and recognition," *IEEE Trans. Intell. Transp. Syst.*, vol. 21, no. 4, pp. 1427–1440, 2020.

[42] E. Rivera, J. Lübberstedt, N. Uhlemann, and M. Lienkamp, "Scenario understanding of traffic scenes through large visual language models," in *Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis. (WACV)*, 2025.

[43] J. Fan, J. Wu, J. Gao, J. Yu, Y. Wang, H. Chu, and B. Gao, "MLLM-SUL: Multimodal large language model for semantic scene understanding and localization in traffic scenarios," *arXiv:2412.19406*, 2024.

[44] Z. R. Tam, C.-K. Wu, Y.-L. Tsai, C.-Y. Lin, H. Lee, and Y.-N. Chen, "Let me speak freely? A study on the impact of format restrictions on performance of large language models," in *Proc. Conf. Empir. Methods Nat. Lang. Process. (EMNLP), Ind. Track*, 2024.

[45] J. Schopplich et al., "TOON: Token-oriented object notation — benchmarks," GitHub repository, 2026. [Online]. Available: https://github.com/toon-format/toon

[46] S. Zerhoudi, M. Granitzer, and J. Mitrovic, "Metadata, structure, or strategy? A decomposition of RAG context enrichment," *arXiv:2606.29645*, 2026.
