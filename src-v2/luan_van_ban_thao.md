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
  - 1.3. Phạm vi dữ liệu
  - 1.4. Câu hỏi nghiên cứu
  - 1.5. Đóng góp chính
  - 1.6. Cấu trúc luận văn
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
  - 4.5. Kết quả chính: đóng góp của JSON ngữ nghĩa
  - 4.6. Kiểm chứng độ tin cậy của phương pháp đánh giá
  - 4.7. Hạn chế: rủi ro trùng lặp dữ liệu (data leakage)
  - 4.8. Kiểm chứng khả năng tự nhận diện làn đường của VLM
  - 4.9. Bàn luận: cơ chế đóng góp thực sự của JSON ngữ nghĩa
- CHƯƠNG 5. KẾT LUẬN
  - 5.1. Tóm tắt đóng góp
  - 5.2. Trả lời các câu hỏi nghiên cứu
  - 5.3. Hạn chế
  - 5.4. Hướng phát triển tiếp theo
- TÀI LIỆU THAM KHẢO

## DANH MỤC TỪ VIẾT TẮT

| Từ viết tắt | Tiếng Anh | Giải thích |
|---|---|---|
| ADAS | Advanced Driver Assistance System | Hệ thống hỗ trợ lái xe tiên tiến |
| VLM | Vision-Language Model | Mô hình ngôn ngữ đa phương thức (thị giác + ngôn ngữ) |
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
| RQ | Research Question | Câu hỏi nghiên cứu |
| QCVN | Quy chuẩn Việt Nam | Hệ thống quy chuẩn kỹ thuật quốc gia (áp dụng cho biển báo Việt Nam) |

## DANH MỤC BẢNG

| STT | Ký hiệu | Tên bảng |
|---|---|---|
| 1 | Bảng 4.1 | Độ chính xác module hiểu làn đường trước và sau khi sửa lỗi off-by-one (N=200) |
| 2 | Bảng 4.2 | So sánh hiệu năng module hiểu làn đường theo nhóm có/không vạch kẻ đường rõ |
| 3 | Bảng 4.3 | Đối chiếu module hiểu làn đường và biển báo giữa CULane và dữ liệu real-life độc lập |
| 4 | Bảng 4.4 | So sánh chi tiết chất lượng nội dung giữa nemotron-nano-8b và ising-calibration-31b (Mean ± SD, kiểm định thống kê) |
| 5 | Bảng 4.5 | Điểm chất lượng khuyến nghị lái xe (Mean ± SD) theo 3 chế độ input, chấm bởi 3 judge độc lập |
| 6 | Bảng 4.6 | Kiểm định ý nghĩa thống kê khi so sánh cặp giữa 3 chế độ input, theo từng judge (N=200, dữ liệu bắt cặp theo ảnh) |
| 7 | Bảng 4.7 | Điểm trung bình (Mean ± SD) 6 tiêu chí đánh giá của judge Gemini theo từng chế độ input |
| 8 | Bảng 4.8 | Xếp hạng độ tin cậy của 3 judge khi đối chiếu với đánh giá của con người |
| 9 | Bảng 4.9 | So sánh khả năng tự nhận diện ngữ nghĩa làn đường giữa pipeline UFLD-v2 và VLM |

## DANH MỤC HÌNH

| STT | Ký hiệu | Tên hình |
|---|---|---|
| 1 | Hình 3.1 | Kiến trúc tổng thể của pipeline 4 tầng: Perception – Semantic Analysis – LLM Reasoning – Evaluation |

---

## TÓM TẮT

Các hệ thống hỗ trợ lái xe (ADAS) hiện nay thường dừng lại ở tầng nhận diện cấp thấp (tọa độ điểm ảnh, bounding box), chưa chuyển hóa được thành ngữ nghĩa giao thông mà con người có thể hiểu và tin tưởng. Luận văn này xây dựng và kiểm chứng định lượng một pipeline bốn tầng (Perception – Semantic Analysis – LLM Reasoning – Evaluation), kết hợp mô hình phát hiện làn đường UFLD-v2 (dùng nguyên trạng ở dạng pretrained), mô hình phát hiện biển báo YOLOv8n (tự tinh chỉnh trên TT100K), một tầng chuyển đổi ngữ nghĩa có cấu trúc (JSON) tự thiết kế, và một mô hình ngôn ngữ lớn đa phương thức (VLM) để sinh khuyến nghị lái xe bằng ngôn ngữ tự nhiên. Tầng suy luận theo hướng tiếp cận training-free, không tinh chỉnh lại mô hình; chi phí huấn luyện của toàn hệ thống do đó chỉ giới hạn ở một bước tinh chỉnh YOLOv8n quy mô nhẹ, thay vì huấn luyện một VLM hoặc LLM chuyên biệt.

Trên bộ dữ liệu CULane (N=200 ảnh, gán nhãn tay đầy đủ), module hiểu làn đường đạt Accuracy 69,0% tổng thể và 77,3% trên nhóm ảnh có vạch kẻ đường rõ, sau khi phát hiện và khắc phục một lỗi lệch đơn vị (off-by-one) từng khiến Accuracy ban đầu chỉ đạt 11,1%. Kết quả tổng quát hóa tốt sang một bộ dữ liệu real-life độc lập tự thu thập (N=200), với Precision số làn đạt 99,4%. Câu hỏi nghiên cứu trung tâm — liệu thông tin ngữ nghĩa có cấu trúc (JSON) có cải thiện chất lượng khuyến nghị lái xe của VLM so với chỉ dùng ảnh hay không — được trả lời bằng thực nghiệm định lượng trên N=200 ảnh, chấm điểm độc lập bởi ba mô hình judge (Gemini, GPT-5 Mini, DeepSeek) trên cùng một rubric sáu tiêu chí. Cả ba judge đồng thuận rằng chế độ chỉ dùng ảnh luôn đạt điểm thấp nhất, trong khi chế độ có JSON cải thiện điểm số tới 36% (Gemini: 3,32 → 4,53/5). Độ tin cậy của phương pháp LLM-as-a-judge được kiểm chứng bằng đối chiếu với đánh giá của con người (N=20), đạt mức đồng thuận 79,2% trong sai số ≤1 điểm — một mức đồng thuận cao, vượt trội rõ rệt so với hai judge thay thế được kiểm chứng theo cùng phương pháp.

Một thực nghiệm bổ sung, yêu cầu VLM tự nhận diện ngữ nghĩa làn đường trực tiếp từ ảnh mà không qua tầng UFLD-v2, cho thấy năng lực cảm nhận thị giác của VLM không hề yếu — thậm chí vượt trội pipeline chuyên biệt khi thiếu vạch kẻ đường hoặc trên dữ liệu ngoài domain huấn luyện. Phát hiện này dẫn tới một điều chỉnh quan trọng trong cách diễn giải kết quả trung tâm: JSON ngữ nghĩa cải thiện chất lượng khuyến nghị chủ yếu nhờ vai trò khung đỡ (scaffolding) cho việc suy luận và trình bày trong một tác vụ ghép nhiều bước, không đơn thuần vì bù đắp năng lực cảm nhận thị giác còn thiếu của VLM. Luận văn cũng thảo luận các hạn chế đã kiểm chứng — rủi ro trùng lặp dữ liệu, giới hạn dữ liệu biển báo trên CULane — và đề xuất hướng phát triển: kiến trúc hybrid kết hợp pipeline thị giác máy tính với cơ chế fallback sang VLM, và mở rộng sang dữ liệu giao thông Việt Nam.

**Từ khóa**: hiểu ngữ nghĩa giao thông, mô hình ngôn ngữ lớn đa phương thức, phát hiện làn đường, phát hiện biển báo, LLM-as-a-judge, hỗ trợ ra quyết định lái xe.

---

# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh và động lực

ADAS (Advanced Driver Assistance Systems) là các hệ thống điện tử trên xe, dùng cảm biến (camera, radar, LiDAR...) để tự động phát hiện tình huống giao thông và hỗ trợ hành vi lái xe — ví dụ cảnh báo chệch làn, hỗ trợ giữ làn, phanh khẩn cấp tự động [20]. Nhu cầu này gắn liền với quy mô vấn đề an toàn giao thông toàn cầu: tai nạn đường bộ gây khoảng 1,19 triệu ca tử vong mỗi năm [31], trong khi hệ thống cảnh báo chệch làn đã được chứng minh giảm 11% tỉ lệ va chạm và 21% tỉ lệ thương tích liên quan [32].

Phần lớn nghiên cứu ADAS hiện nay tập trung vào tầng nhận diện, với các mô-đun phát hiện làn đường, biển báo ngày càng nhanh và chính xác (mục 2.1, 2.2). Tuy nhiên, đầu ra của các mô-đun này — tọa độ điểm ảnh, bounding box, class ID — được thiết kế cho thuật toán điều khiển, không phải để con người trực tiếp đọc hiểu; đây là khoảng trống về tính khả giải đã được ghi nhận như một điều kiện an toàn còn thiếu ở nhiều hệ ADAS dựa trên AI [19], đòi hỏi một tầng trung gian chuyển thông tin nhận diện thô thành ngữ nghĩa giao thông — làn đường, độ lệch tâm, hình dạng đường, biển báo cần tuân thủ — trước khi trình bày cho người lái bằng ngôn ngữ tự nhiên.

Sự phát triển gần đây của mô hình ngôn ngữ đa phương thức (Vision-Language Model — VLM) mở ra hướng tiếp cận lấp đầy khoảng trống này, nhờ khả năng tổng hợp ảnh quan sát và dữ liệu ngữ nghĩa có cấu trúc (JSON) để sinh khuyến nghị bằng ngôn ngữ tự nhiên. Nguyên lý cấp thêm ngữ cảnh có cấu trúc để tăng độ chính xác và giảm ảo giác cho mô hình sinh đã được kiểm chứng cả ở LLM nói chung (Retrieval-Augmented Generation [34]) lẫn trong lái xe cụ thể: DriveVLM [23] kết hợp VLM với thông tin không gian có cấu trúc để bù hạn chế suy luận không gian, còn Talk2BEV [25] cho thấy đặt VLM vào biểu diễn bản đồ có cấu trúc cải thiện rõ chất lượng suy luận so với chỉ dùng ảnh. Kế thừa nguyên lý này, đề tài đặt giả thuyết trung tâm — kết hợp ảnh với JSON ngữ nghĩa sẽ cải thiện khuyến nghị lái xe của VLM so với chỉ dùng ảnh thô — và kiểm chứng định lượng ở mục 4.5.

Do không gian ngữ nghĩa giao thông đầy đủ bao quát rất nhiều yếu tố (hạ tầng đường bộ, phương tiện xung quanh, chướng ngại vật động...), để đảm bảo tính khả thi, đề tài thu hẹp phạm vi vào hai thành phần hạ tầng cố định nền tảng nhất — làn đường và biển báo giao thông — quyết định trực tiếp việc định vị không gian và quy tắc bắt buộc đối với phương tiện.

Trên cơ sở đó, đề tài hướng tới câu hỏi nghiên cứu cốt lõi:

"Việc tích hợp thông tin ngữ nghĩa có cấu trúc (JSON) có cải thiện chất lượng, độ chính xác và tính căn cứ của khuyến nghị lái xe do VLM sinh ra so với chỉ dùng ảnh thô hay không, và mức cải thiện này được định lượng ra sao?"

## 1.2. Mục tiêu nghiên cứu

Đề tài tập trung vào hai thành phần ngữ nghĩa cốt lõi của tình huống giao thông:

1. Hiểu làn đường (lane understanding): số làn, làn ego, độ lệch tâm xe, làn lân cận, hình dạng đường (thẳng/cong).
2. Hiểu biển báo giao thông (traffic sign understanding): phát hiện và phân loại biển báo giao thông.

Hai thành phần này được chuyển hóa thành ngữ nghĩa có cấu trúc, kết hợp với ảnh gốc, đưa vào mô hình ngôn ngữ lớn để sinh khuyến nghị lái xe, và được đánh giá bằng phương pháp luận định lượng đáng tin cậy.

## 1.3. Phạm vi dữ liệu

Để đảm bảo tính khách quan, khả năng tái lập, và có thể đối sánh với các nghiên cứu khác, đề tài sử dụng hai bộ dữ liệu công khai, phổ biến, đã được cộng đồng nghiên cứu kiểm chứng và có chung một đặc điểm giao thông — giao thông đô thị Trung Quốc:

- **CULane** — benchmark chuẩn cho bài toán phát hiện làn đường, dùng để đánh giá module hiểu làn đường và làm dữ liệu chính cho toàn bộ pipeline.
- **TT100K** (Tsinghua-Tencent 100K) — benchmark chuẩn cho bài toán phát hiện biển báo giao thông, dùng để huấn luyện và đánh giá module biển báo.

Việc lựa chọn hai bộ dữ liệu phổ biến, có sẵn này — thay vì thu thập riêng dữ liệu Việt Nam ngay từ đầu — nhằm kiểm chứng tính hiệu quả của pipeline trên dữ liệu đã được chuẩn hóa, có thể đối sánh khách quan với các công trình khác, trước khi mở rộng sang bối cảnh giao thông Việt Nam. Hướng mở rộng này được trình bày ở Chương 5 (mục 5.4).

## 1.4. Câu hỏi nghiên cứu

- **RQ1**: Module hiểu làn đường (dựa trên UFLD-v2 và xử lý ngữ nghĩa) đạt độ chính xác bao nhiêu khi đối chiếu với nhãn tay, và độ chính xác này có tổng quát hóa được sang dữ liệu độc lập không?
- **RQ2**: Module hiểu biển báo (dựa trên YOLOv8 và TT100K) đạt hiệu quả thế nào, và những giới hạn nào cần lưu ý khi áp dụng trên các bộ dữ liệu khác nhau?
- **RQ3**: Thông tin JSON ngữ nghĩa có cải thiện chất lượng khuyến nghị lái xe của VLM so với chỉ dùng ảnh hay không?
- **RQ4**: Trong các mô hình VLM có thể tiếp cận được (miễn phí, chi phí thấp), mô hình nào phù hợp nhất cho bài toán này, xét trên độ tin cậy, chất lượng và khả năng vận hành?
- **RQ5**: Phương pháp đánh giá bằng LLM-as-a-judge có đáng tin cậy không, và có thể định lượng độ tin cậy đó như thế nào?

## 1.5. Đóng góp chính

Các hệ VLM lái xe end-to-end quy mô lớn như DriveGPT4 [2], DriveLM [3] hay LMDrive [4] đã cho thấy khả năng tích hợp sâu suy luận ngôn ngữ vào vòng lặp điều khiển, nhưng đòi hỏi tài nguyên huấn luyện và dữ liệu lái xe quy mô lớn vượt quá phạm vi khả thi của một đề tài nghiên cứu độc lập (mục 2.3). Đề tài này vì vậy không đặt mục tiêu đề xuất một kiến trúc phát hiện làn đường/biển báo mới hay một hệ VLM end-to-end tương tự, mà tập trung đóng góp ở tầng tích hợp, chuyển đổi ngữ nghĩa và phương pháp luận đánh giá, với tầng suy luận theo hướng training-free — sử dụng VLM miễn phí qua API, không tinh chỉnh lại mô hình (mục 3.6); tầng perception biển báo có một bước tinh chỉnh YOLOv8n quy mô nhẹ trên TT100K (mục 3.2). Cụ thể, đề tài có bốn đóng góp:

1. **Tầng chuyển đổi ngữ nghĩa được kiểm chứng định lượng**: chuyển output thô của UFLD-v2 sang ngữ nghĩa cấp quyết định (số làn, làn ego, độ lệch tâm, hình dạng đường), đạt Accuracy 77,3% trên ảnh có vạch kẻ rõ (N=176/200) và tổng quát hóa tốt sang dữ liệu độc lập tự thu thập (N=200, Precision 99,4%, Ego lane Accuracy 86,5%).
2. **Minh chứng cho tầm quan trọng của tầng diễn giải ngữ nghĩa**: quá trình xây dựng tầng trên phát hiện một lỗi lệch đơn vị (off-by-one) khiến Accuracy ban đầu chỉ đạt 11,1%, dù UFLD-v2 đã đạt F1 = 76,0% ở tầng phát hiện. Bản thân việc sửa lỗi không phải một đóng góp thuật toán, nhưng là bằng chứng thực nghiệm cho luận điểm rằng chất lượng detector không tự động đảm bảo chất lượng hệ hỗ trợ quyết định — sai số có thể nằm ở tầng diễn giải ngữ nghĩa phía sau, một tầng thường ít được đầu tư kiểm chứng khi trọng tâm nghiên cứu đặt vào cải thiện độ chính xác của detector.
3. **Phương pháp luận đánh giá LLM-as-a-judge được kiểm chứng độ tin cậy**, thay vì áp dụng "nguyên trạng" như các benchmark tổng quát: đối chiếu với đánh giá của con người (N=20) và đối chiếu đa-judge (Gemini, GPT-5 Mini, DeepSeek) trên cùng một rubric. Gemini đạt mức đồng thuận cao nhất trong ba judge (79,2% trong sai số ≤1 điểm), phù hợp với tiền lệ rằng LLM-as-a-judge có thể đạt độ tin cậy tiệm cận con người trong điều kiện phù hợp [5] (mục 2.4, 4.6).
4. **Kết quả thực nghiệm định lượng cho RQ3** (N=200, ba judge độc lập): JSON ngữ nghĩa cải thiện chất lượng khuyến nghị lái xe so với chỉ dùng ảnh (Gemini: 3,32 → 4,53/5, tương đương +36%), nhất quán ở cả ba judge.

**Ý nghĩa thực tiễn**. So với các hệ VLM/VLA end-to-end — vốn mang lại khả năng tích hợp sâu nhưng đòi hỏi dữ liệu lái xe quy mô lớn và hạ tầng huấn luyện đáng kể — pipeline trong đề tài này là một lựa chọn thay thế phù hợp khi nguồn lực hạn chế: một hệ hỗ trợ quyết định có khả năng diễn giải bằng ngôn ngữ tự nhiên, chi phí triển khai thấp, có thể được xây dựng từ các mô hình VLM sẵn có — phù hợp làm nền tảng cho ứng dụng dashcam/hộp đen thông minh, hoặc điểm khởi đầu để mở rộng sang dữ liệu giao thông Việt Nam (mục 5.4).

## 1.6. Cấu trúc luận văn

Chương 2 trình bày tổng quan các công trình liên quan, gồm các hướng nghiên cứu về phát hiện làn đường, phát hiện biển báo, mô hình ngôn ngữ lớn đa phương thức cho lái xe, và phương pháp luận LLM-as-a-judge. Chương 3 trình bày phương pháp luận: kiến trúc hệ thống, dữ liệu, thuật toán phân tích ngữ nghĩa, thiết kế prompt và phương pháp luận đánh giá. Chương 4 trình bày kết quả thực nghiệm và bàn luận, gồm chín mục — từ độ chính xác của từng module, kết quả trung tâm về đóng góp của JSON ngữ nghĩa, kiểm chứng độ tin cậy của phương pháp đánh giá, cho tới một thực nghiệm bổ sung và bàn luận làm rõ cơ chế đóng góp thực sự của JSON. Chương 5 tổng kết đóng góp, trả lời các câu hỏi nghiên cứu, thảo luận hạn chế và đề xuất hướng phát triển tiếp theo.

**Tóm tắt chương.** Chương này đã trình bày động lực nghiên cứu — khoảng trống giữa nhận diện cấp thấp và ngữ nghĩa giao thông có thể diễn giải — cùng mục tiêu, phạm vi dữ liệu, năm câu hỏi nghiên cứu và bốn đóng góp chính của đề tài. Chương 2 tiếp theo tổng quan các công trình liên quan theo bốn hướng: phát hiện làn đường, phát hiện biển báo, mô hình ngôn ngữ lớn đa phương thức cho lái xe, và phương pháp luận LLM-as-a-judge, làm cơ sở xác định các khoảng trống nghiên cứu cụ thể mà đề tài này góp phần lấp đầy.

---

# CHƯƠNG 2. TỔNG QUAN VÀ CÁC CÔNG TRÌNH LIÊN QUAN

Các hệ thống hỗ trợ lái xe tiên tiến (Advanced Driver Assistance Systems — ADAS) hiện là một phần gần như tiêu chuẩn trên xe hơi thương mại, với các tính năng đã phổ biến như cảnh báo chệch làn, hỗ trợ giữ làn, và nhận diện biển báo giao thông; đây cũng là nền tảng nhận thức cần thiết để tiến tới các cấp độ tự động hóa cao hơn. Nidamanuri và cộng sự [20] khảo sát tiến trình phát triển công nghệ ADAS qua các cấp độ tự động hóa, cho thấy xu hướng chuyển dịch từ hệ thống dựa trên cảm biến đơn lẻ sang các hệ đa cảm biến kết hợp học sâu nhằm tăng độ tin cậy trong điều kiện thực tế đa dạng. Song song với yêu cầu về độ chính xác, khả năng khả giải (explainability) của quyết định do AI đưa ra ngày càng được xem là một điều kiện quan trọng để ADAS được triển khai và chấp nhận ở quy mô lớn, đặc biệt trong các tình huống ranh giới (edge case): Kuznietsov và cộng sự [19] thực hiện tổng quan hệ thống đầu tiên về AI khả giải (Explainable AI — XAI) cho lái xe tự động an toàn, chỉ ra năm đóng góp chính của XAI — thiết kế khả giải, mô hình đại diện khả giải, giám sát khả giải, giải thích phụ trợ, và kiểm định khả giải. Tselentis và Papadimitriou [21] bổ sung thêm một khía cạnh nhân tố con người mà các hệ ADAS thuần cảm biến thường ít khai thác: nhận diện hồ sơ và mẫu hành vi lái xe (driver profile/pattern) như một tín hiệu đầu vào cho đánh giá an toàn giao thông. Ba hướng nghiên cứu này — công nghệ cảm biến, khả giải, và nhân tố con người — cùng phác họa bối cảnh chung mà đề tài này góp phần vào: xây dựng một tầng hỗ trợ quyết định vừa chính xác vừa có thể diễn giải bằng ngôn ngữ tự nhiên (mục 1.1).

## 2.1. Phát hiện làn đường (Lane Detection)

Phát hiện làn đường là một trong những bài toán nhận thức nền tảng và được triển khai rộng rãi nhất của ADAS, làm cơ sở trực tiếp cho các tính năng cảnh báo chệch làn và hỗ trợ giữ làn kể trên. Trong khoảng một thập kỷ qua, hướng tiếp cận cho bài toán này đã chuyển dịch rõ rệt từ các phương pháp hình học truyền thống (dò biên, biến đổi Hough, fit đa thức) sang các kiến trúc học sâu, nhờ khả năng xử lý tốt hơn các điều kiện thực tế phức tạp như bóng đổ, vạch kẻ mờ, hay ánh sáng thay đổi.

Ultra-Fast-Lane-Detection-v2 (UFLD-v2) [1] là một kiến trúc phát hiện làn đường tốc độ cao tiêu biểu của hướng tiếp cận này, biểu diễn bài toán phát hiện làn dưới dạng phân loại theo lưới hàng/cột (hybrid anchor-driven ordinal classification) thay vì hồi quy tọa độ trực tiếp hay phân đoạn ngữ nghĩa (semantic segmentation) như các phương pháp trước đó. Kiến trúc này đạt tốc độ suy luận trên 300 khung hình/giây ở phiên bản nhẹ, trong khi vẫn giữ độ chính xác cạnh tranh — F1 = 76,0% trên tập kiểm thử CULane với backbone ResNet-34, đúng biến thể pretrained được sử dụng trong đề tài (`culane_res34.pth`). CULane [6] là benchmark chuẩn cho bài toán này (88,9 nghìn ảnh huấn luyện, 9,7 nghìn ảnh kiểm định, 34,7 nghìn ảnh kiểm thử), với đặc điểm dữ liệu chủ yếu là các tình huống đường đô thị đa dạng: giao lộ, mật độ giao thông cao, điều kiện ánh sáng thay đổi.

Hai công trình khảo sát gần đây đã hệ thống hóa lĩnh vực này: [7] tổng hợp kiến trúc mạng và mục tiêu tối ưu của các phương pháp phát hiện vạch kẻ đường dựa trên deep learning; [8] là một nghiên cứu tổng quan hệ thống (systematic literature review) trên 102 công trình công bố giai đoạn 2018–2021, cho thấy xu hướng chuyển dịch từ mô hình hình học truyền thống sang deep learning trong toàn ngành.

Chỉ số F1 = 76,0% nêu trên là một metric ở tầng phát hiện điểm ảnh (point-wise localization theo IoU), khác về bản chất với các metric được sử dụng ở mục 4.1 của đề tài — Accuracy và MAE của số làn suy ra được, một đại lượng ngữ nghĩa cấp cao hơn, được tính từ output của UFLD-v2 qua một tầng xử lý hậu kỳ do đề tài tự xây dựng. Hai loại metric này không thể so sánh trực tiếp; điểm mấu chốt mà đề tài muốn làm rõ là: ngay cả khi tầng phát hiện đã đạt F1 cạnh tranh theo benchmark gốc, tầng diễn giải ngữ nghĩa phía sau vẫn có thể chứa lỗi nghiêm trọng, độc lập với chất lượng của bản thân detector (mục 4.1, 1.5).

Bên cạnh việc cải thiện thuật toán phát hiện, việc đánh giá chất lượng của các hệ thống hỗ trợ giữ làn (Lane Keeping Assistance Systems — LKAS) khi triển khai thực tế cũng là một hướng nghiên cứu riêng. Wei và cộng sự [28] tổng hợp các phương pháp đánh giá LKAS hiện có — từ nhóm chỉ số khách quan (độ lệch làn, thời gian phản ứng) đến nhóm phương pháp có tích hợp cảm nhận chủ quan của người lái — và chỉ ra rằng nhóm phương pháp thứ hai hiện vẫn ít được chuẩn hóa hơn. Quan sát này là một phần cơ sở cho việc đề tài bổ sung một tầng đánh giá LLM-as-a-judge, mang tính "cảm nhận" hơn, bên cạnh các chỉ số Accuracy/MAE/Precision khách quan ở mục 3.7.

## 2.2. Phát hiện biển báo giao thông (Traffic Sign Detection)

Nhận diện biển báo giao thông (Traffic Sign Recognition — TSR) là một tính năng ADAS đã được thương mại hóa rộng rãi, giúp xe nhắc nhở hoặc hỗ trợ tài xế tuân thủ giới hạn tốc độ, biển cấm, biển hiệu lệnh quan sát được trên đường; đây cũng là nguồn thông tin đầu vào trực tiếp cho các quy tắc giao thông mà một hệ hỗ trợ quyết định lái xe cần cân nhắc khi sinh khuyến nghị. YOLOv8 (Ultralytics) là kiến trúc object detection một giai đoạn (single-stage) hiện được sử dụng rộng rãi cho bài toán này nhờ cân bằng tốt giữa tốc độ và độ chính xác, phù hợp cho ứng dụng thời gian thực. TT100K (Tsinghua-Tencent 100K) [9] là benchmark quy mô lớn cho bài toán phát hiện và phân loại biển báo giao thông tại Trung Quốc, gồm khoảng 100.000 ảnh và 30.000 đối tượng biển báo được gán nhãn, với hệ thống mã hóa biển báo chi tiết theo loại: biển cấm ("p"), biển hiệu lệnh ("i"), biển cảnh báo ("w"), biển giới hạn tốc độ ("pl"/"il").

Trong dòng nghiên cứu gần đây ứng dụng YOLOv8 cho bài toán này, Logeswaran và cộng sự [26] xác nhận tính khả thi của YOLOv8 khi phát hiện đồng thời người đi bộ và biển báo giao thông trong thời gian thực, thử nghiệm trên hai bộ dữ liệu chuẩn tách biệt (Penn-Fudan cho người đi bộ, GTSRB cho biển báo). Phát hiện biển báo có kích thước nhỏ trong ảnh — do khoảng cách hoặc góc chụp — vẫn là một thách thức chung của bài toán này nói riêng và của các kiến trúc một giai đoạn nói chung; Ji và cộng sự [27] đề xuất hướng giải quyết bằng cách bổ sung các mô-đun BoTNet, ODConv và LSKA vào YOLOv8n, đạt cải thiện đáng kể về độ chính xác trên đối tượng nhỏ khi kiểm thử trên chính TT100K — cùng bộ dữ liệu được đề tài này sử dụng để tinh chỉnh YOLOv8n (mục 3.2). Đây là một hướng cải tiến kiến trúc khả thi cho module biển báo của đề tài trong các nghiên cứu tiếp theo, có thể đối chiếu với quan sát về mật độ và kích thước biển báo trên CULane ở mục 4.3.

## 2.3. Mô hình ngôn ngữ lớn đa phương thức cho hỗ trợ quyết định lái xe

**Tiền thân trước kỷ nguyên LLM.** Hong và cộng sự [10] đã đặt nền móng cho ý tưởng mã hóa ngữ nghĩa cấp cao của tình huống giao thông thành một biểu diễn có cấu trúc (dạng lưới không gian) để mô hình học sâu suy luận hành vi lái xe. Công trình này dùng mạng convolutional thuần túy, phù hợp với công cụ AI sẵn có tại thời điểm công bố; hạn chế duy nhất là chưa sinh được giải thích bằng ngôn ngữ tự nhiên — điều mà các mô hình ngôn ngữ lớn ra đời sau đó mới giải quyết được.

**Các hệ VLM/LLM lái xe end-to-end quy mô lớn.** Với sự xuất hiện của các mô hình ngôn ngữ lớn đa phương thức, một hướng nghiên cứu tích cực đã hình thành nhằm tích hợp trực tiếp khả năng suy luận ngôn ngữ vào pipeline lái xe end-to-end. DriveGPT4 [2] sinh giải thích ngôn ngữ tự nhiên kèm dự đoán tín hiệu điều khiển theo hướng end-to-end; DriveLM [3] đóng khung bài toán lái xe dưới dạng Graph Visual Question Answering; LMDrive [4] thực hiện lái xe closed-loop end-to-end bằng LLM. Các hệ này đạt được khả năng diễn giải tích hợp sâu ngay trong vòng lặp điều khiển, đổi lại đòi hỏi huấn luyện hoặc tinh chỉnh trên tập dữ liệu lái xe quy mô lớn (nuScenes, CARLA...) cùng hạ tầng tính toán và dữ liệu đáng kể — một yêu cầu tài nguyên vượt quá quy mô khả thi của một đề tài nghiên cứu độc lập như đề tài này.

**Các hệ LLM/VLM đóng vai trò tầng tương tác/suy luận gắn thêm.** Song song với hướng end-to-end nêu trên, một nhóm công trình gần đây dùng LLM/VLM như một tầng suy luận hoặc tương tác gắn thêm vào pipeline lái xe sẵn có, gần với cách tiếp cận kỹ thuật của đề tài này hơn. Cui và cộng sự [22] (Drive as You Speak) xây dựng một framework LLM có khả năng gọi công cụ (tool-use) và suy luận theo chu trình reasoning-acting, cho phép xe tương tác với người lái bằng ngôn ngữ tự nhiên một cách cá nhân hóa và liên tục học hỏi. Tian và cộng sự [23] (DriveVLM) đề xuất kiến trúc lai DriveVLM-Dual, kết hợp VLM cho suy luận cảnh phức tạp (long-tail) với pipeline lái xe truyền thống cho các tác vụ đòi hỏi suy luận không gian chính xác, và xác nhận bằng thực nghiệm trên nuScenes cùng dữ liệu triển khai thực tế rằng cách kết hợp này quản lý tốt các tình huống lái xe khó lường; quan sát của nhóm tác giả về giới hạn suy luận không gian của VLM thuần túy tương đồng với phát hiện ở mục 4.8 của đề tài này, nơi VLM tự nhận diện làn đường kém chính xác hơn pipeline chuyên biệt khi ảnh có vạch kẻ rõ. Yao và cộng sự [24] giải quyết bài toán chi phí suy luận — một ràng buộc quan trọng cho triển khai thời gian thực — bằng cách chưng cất (distill) một mô hình ngôn ngữ nhẹ có nhận biết độ tin cậy (confidence-aware) từ một hệ đa-agent, đạt trạng thái tốt nhất (SOTA) trên benchmark nuPlan với độ trễ suy luận thấp. Choudhary và cộng sự [25] (Talk2BEV) đưa mô hình thị giác–ngôn ngữ lớn vào không gian biểu diễn nhìn từ trên xuống (bird's-eye-view — BEV), cho phép truy vấn ngôn ngữ tự nhiên trực tiếp trên bản đồ BEV mà không cần huấn luyện riêng cho từng tác vụ, được kiểm chứng trên benchmark Talk2BEV-Bench với hơn 20.000 câu hỏi trên dữ liệu nuScenes — một quy mô kiểm chứng lớn hơn đáng kể so với N=200 của đề tài này.

Bốn công trình trên đặt trọng tâm vào những mục tiêu khác với RQ3 của đề tài này: cải thiện khả năng tương tác và cá nhân hóa [22], mở rộng khả năng suy luận không gian trong tình huống phức tạp [23], tối ưu chi phí/độ trễ suy luận [24], hoặc mở rộng không gian biểu diễn sang BEV [25]. Vì trọng tâm khác nhau, câu hỏi cụ thể mà đề tài này đặt ra ở RQ3/mục 4.5 — tách bạch định lượng đóng góp của thông tin có cấu trúc so với ảnh thô trong cùng một mô hình cố định — chưa được đặt ra trực tiếp trong nhóm công trình này; đây là một hướng bổ trợ mà đề tài hy vọng đóng góp thêm cho dòng nghiên cứu chung.

**Các công trình gần nhất với đề tài.** Cùng hướng kết hợp deep learning chuyên biệt với multimodal LLM cho ngữ nghĩa giao thông, SafeRoute [11] và công trình tiền thân "Advancing Autonomous Vehicle Intelligence" [12] — của cùng một nhóm tác giả — xây dựng một pipeline thống nhất: ba kiến trúc phát hiện biển báo (ResNet-50 đạt 99,8%, YOLOv8 đạt 98,0%, RT-DETR đạt 96,6% accuracy) kết hợp với một MLLM được tinh chỉnh bằng instruction-tuning cho làn đường, sử dụng cơ chế Multimodal Adapter để dung hợp đặc trưng CNN với embedding EVA-CLIP; công trình này báo cáo Frame Overall Accuracy 53,87% và Question Overall Accuracy 82,83% cho phần hiểu làn đường dạng hỏi–đáp — mức độ chính xác nhận diện biển báo và hiểu làn đường đều cao, cho thấy hướng dung hợp thông tin ở tầng embedding mang lại hiệu năng mạnh khi có đủ dữ liệu và tài nguyên để tinh chỉnh MLLM. Tương tự, DSC-LLM [13] kết hợp đặc trưng hành vi (mô hình hóa bằng LSTM/transformer) với ngữ cảnh giao thông trích xuất từ ảnh để dự đoán quỹ đạo kèm suy luận rủi ro có giải thích bằng LLM.

Đề tài này chọn một điểm thiết kế khác cho tầng dung hợp thông tin: thay vì dung hợp ở tầng embedding như SafeRoute/Advancing-AV-Intelligence, đề tài dung hợp ở tầng prompt/văn bản — JSON ngữ nghĩa được nhúng trực tiếp vào prompt của một VLM tổng quát, không tinh chỉnh. Lựa chọn này đơn giản hơn về triển khai và không đòi hỏi dữ liệu huấn luyện MLLM riêng, đổi lại phụ thuộc nhiều hơn vào chất lượng thiết kế prompt và nhiều khả năng không đạt độ chính xác nhận diện cao bằng một mô hình được tinh chỉnh chuyên biệt như SafeRoute. Ngoài khác biệt kiến trúc, mục tiêu chính của SafeRoute/Advancing-AV-Intelligence/DSC-LLM là tối đa hóa độ chính xác nhận diện và dự đoán quỹ đạo, nên các công trình này cũng chưa đặt trọng tâm vào việc tách bạch định lượng đóng góp của thông tin có cấu trúc so với ảnh thô (RQ3/mục 4.5), hay kiểm chứng độ tin cậy của phương pháp đánh giá bằng đối chiếu với con người (mục 4.6) — hai khía cạnh là trọng tâm phương pháp luận riêng của đề tài này.

Nhìn chung, đề tài này khác về trọng tâm thiết kế so với cả hai nhóm công trình liên quan nêu trên: thay vì huấn luyện hoặc tinh chỉnh một mô hình chuyên biệt ở tầng suy luận, đề tài tận dụng một VLM tổng quát đã huấn luyện sẵn, không tinh chỉnh (truy cập qua API theo chuẩn OpenAI-compatible của NVIDIA NIM), kết hợp với một tầng tiền xử lý ngữ nghĩa từ các mô-đun perception chuyên biệt — trong đó UFLD-v2 được dùng nguyên trạng ở dạng pretrained, còn YOLOv8n cho bài toán biển báo được tự tinh chỉnh trên TT100K (mục 3.2), một bước huấn luyện quy mô nhẹ so với việc huấn luyện lại một VLM/LLM hay thu thập dữ liệu lái xe quy mô lớn như ở các hệ end-to-end. Sự đánh đổi này mang lại tính đơn giản, chi phí thấp và khả năng triển khai nhanh, phù hợp với quy mô một đề tài nghiên cứu độc lập — dù có thể đổi lại một phần độ chính xác so với các hệ được huấn luyện/tinh chỉnh chuyên biệt với đầy đủ tài nguyên.

## 2.4. Đánh giá chất lượng output ngôn ngữ tự nhiên bằng LLM-as-a-Judge

Nhu cầu đánh giá chuẩn hóa các hệ LLM và AI agent đang tăng nhanh cùng tốc độ phát triển của lĩnh vực. Một khảo sát gần đây [14] hệ thống hóa các benchmark và framework đánh giá LLM/agent công bố trong giai đoạn 2019–2025, cho thấy đây vẫn là một lĩnh vực đang định hình, chưa có phương pháp luận thống nhất — điều này càng củng cố lý do đề tài tự kiểm chứng độ tin cậy của phương pháp đánh giá thay vì áp dụng nguyên trạng mà không kiểm chứng.

Việc đánh giá chất lượng của một khuyến nghị lái xe dạng văn bản tự nhiên là bài toán khó lượng hóa bằng các metric cứng truyền thống (accuracy, F1...) vì không tồn tại một "đáp án đúng duy nhất". Phương pháp LLM-as-a-judge — sử dụng một LLM mạnh làm "giám khảo" tự động chấm điểm theo rubric cho trước — đã được áp dụng rộng rãi trong các benchmark đánh giá LLM gần đây, tiêu biểu là phương pháp luận của MT-Bench và Chatbot Arena [5], cũng như AlpacaEval. Trên MT-Bench, GPT-4 khi làm judge đạt 85% đồng thuận với chuyên gia con người (trên các cặp so sánh không hòa), một mức xấp xỉ độ đồng thuận giữa người với người (81%) — cho thấy LLM-as-a-judge có thể đạt độ tin cậy tiệm cận con người trong điều kiện phù hợp, dù vẫn tồn tại các thiên lệch cố hữu (thiên vị độ dài câu trả lời, thiên vị phong cách viết, tự thiên vị giữa các mô hình cùng họ) cần được kiểm chứng riêng cho từng bài toán ứng dụng cụ thể. Đây chính là cách tiếp cận được áp dụng trong đề tài này (mục 3.7 và 4.6), với quy mô kiểm chứng nhỏ hơn (N=20 so với hàng nghìn cặp trong MT-Bench gốc) do giới hạn nguồn lực của một đề tài cá nhân.

Việc sử dụng một mẫu kiểm chứng con người quy mô nhỏ, thay vì chấm tay toàn bộ dữ liệu, có cơ sở phương pháp luận riêng trong các nghiên cứu gần đây. Kim [15] đề xuất một khung lấy mẫu hai giai đoạn — LLM chấm toàn bộ dữ liệu, con người chỉ chấm một mẫu con được chọn có chủ đích tại những nơi dự đoán của LLM kém tin cậy nhất — và nhấn mạnh rằng y văn hiện thiếu hướng dẫn chính thức về việc cần bao nhiêu giám sát của con người là đủ khi kiểm chứng một benchmark. Saha và cộng sự [16] đề xuất phân bổ truy vấn thích ứng theo phương sai thay vì phân bổ đều, nhằm giảm sai số ước lượng trong một ngân sách tính toán cố định. Pan và cộng sự [17] phỏng vấn tám chuyên gia và nhấn mạnh nhu cầu hỗ trợ xây dựng tiêu chí đánh giá khớp với kỳ vọng của người dùng thực tế — định hướng cho cách thiết kế rubric sáu tiêu chí của đề tài (mục 3.7). Đề tài hiện sử dụng N=20 mẫu chọn ngẫu nhiên, chưa áp dụng cơ chế lấy mẫu thích ứng theo phương sai; đây là một hướng cải tiến khả thi được nêu ở mục 5.4.

Chất lượng của chính dữ liệu đánh giá — không chỉ chất lượng của công cụ đánh giá — cũng là một mối quan tâm được nêu trong y văn gần đây. Emami và cộng sự [29] tổng quan vai trò của con người trong vòng lặp huấn luyện/kiểm định (human-in-the-loop) đối với xe tự hành an toàn và có đạo đức, nhấn mạnh rằng gán nhãn dữ liệu vẫn là nút thắt cổ chai chính — phù hợp với trải nghiệm thực tế của đề tài này khi phải tự gán nhãn tay toàn bộ 200+200 ảnh CULane/real-life (mục 3.2). Fernández Llorca và cộng sự [30] đánh giá độ thiên lệch (bias) trong các bộ dữ liệu thị giác phổ biến cho xe tự hành, phát hiện mức độ đa dạng rất thấp ở nhiều thuộc tính nhân khẩu học của người đi bộ — một lời nhắc rằng ngay cả các bộ dữ liệu chuẩn như CULane/TT100K, dù được đề tài này lựa chọn vì tính phổ biến và khả năng đối sánh (mục 1.3), cũng có thể mang thiên lệch tiềm ẩn chưa được kiểm chứng trong phạm vi đề tài này.

## 2.5. Khoảng trống nghiên cứu

Năm hướng nghiên cứu liên quan để lại các khoảng trống khác nhau mà đề tài này hướng tới:

1. ADAS truyền thống (dựa trên UFLD-v2, YOLOv8...) đạt độ chính xác và tốc độ xử lý tốt ở tầng nhận diện, nhưng output dừng lại ở dạng tọa độ, bounding box, class ID — chưa có tầng suy luận ngôn ngữ tự nhiên có thể diễn giải được cho người lái.
2. Các hệ VLM lái xe end-to-end quy mô lớn (DriveGPT4, DriveLM, LMDrive) giải quyết tốt bài toán diễn giải nhờ tích hợp sâu vào vòng lặp điều khiển, nhưng đòi hỏi huấn luyện hoặc tinh chỉnh trên dữ liệu lái xe quy mô lớn — chi phí và ngưỡng gia nhập cao đối với một đề tài nghiên cứu độc lập.
3. Các hệ LLM/VLM đóng vai trò tầng tương tác/suy luận gắn thêm vào pipeline sẵn có (Drive as You Speak, DriveVLM, Talk2BEV, mô hình ngôn ngữ nhẹ có nhận biết độ tin cậy — mục 2.3) đạt nhiều kết quả mạnh trong phạm vi mục tiêu riêng của từng công trình, và gần với cách tiếp cận kỹ thuật của đề tài này nhất (VLM tổng quát, không tinh chỉnh); tuy nhiên nhóm này đặt trọng tâm vào tương tác, suy luận không gian, hoặc tối ưu độ trễ hơn là tách bạch định lượng đóng góp của thông tin có cấu trúc, và phần lớn hoạt động trên không gian biểu diễn khác (BEV, tín hiệu điều khiển) thay vì ngữ nghĩa làn đường/biển báo dạng JSON như đề tài này.
4. Các hệ hybrid deep learning + MLLM gần đây (SafeRoute, Advancing-AV-Intelligence, DSC-LLM — mục 2.3) gần nhất về mục tiêu với đề tài này và đạt độ chính xác nhận diện rất cao nhờ dung hợp thông tin ở tầng embedding; điểm khác biệt chủ yếu là nhóm này chưa đặt trọng tâm vào việc tách bạch định lượng đóng góp của thông tin có cấu trúc so với ảnh thô, cũng như chưa kiểm chứng độ tin cậy của phương pháp đánh giá bằng đối chiếu con người — hai khía cạnh là trọng tâm phương pháp luận của đề tài này.
5. VLM tổng quát dùng nguyên trạng (không qua tiền xử lý ngữ nghĩa) có năng lực cảm nhận thị giác tốt (mục 4.8) nhưng không được thiết kế chuyên biệt cho ngữ nghĩa giao thông; như đề tài này cho thấy định lượng ở mục 4.5, việc thiếu một tầng ngữ nghĩa có cấu trúc làm giảm rõ rệt chất lượng khuyến nghị so với khi có tầng đó.

Đề tài định vị gần nhóm (4) nhất về mục tiêu (kết hợp deep learning chuyên biệt với LLM đa phương thức cho ngữ nghĩa giao thông), nhưng chọn hướng triển khai kỹ thuật ở tầng suy luận gần nhóm (3) và (5) hơn — dùng VLM tổng quát không tinh chỉnh thay vì huấn luyện/tinh chỉnh một mô hình chuyên biệt. Cụ thể, đề tài kết hợp: tầng perception chuyên biệt đã được kiểm chứng như nhóm (1) — UFLD-v2 dùng nguyên trạng ở dạng pretrained, YOLOv8n cho biển báo được tự tinh chỉnh trên TT100K (mục 3.2), một bước huấn luyện quy mô nhẹ so với việc huấn luyện một VLM/LLM; tầng chuyển đổi ngữ nghĩa có cấu trúc tự thiết kế, đóng góp chính về mặt kỹ thuật, khác biệt rõ với cách biểu diễn BEV/embedding của nhóm (3)/(4); tầng suy luận VLM tổng quát không tinh chỉnh như nhóm (3)/(5); và một phương pháp luận đánh giá định lượng nghiêm ngặt, có kiểm chứng độ tin cậy của chính công cụ đánh giá bằng đối chiếu con người và đa-judge — một khoảng trống mà cả nhóm (3) lẫn nhóm (4) đều chưa lấp đầy trong các công trình đã khảo sát.

**Tóm tắt chương.** Chương này đã tổng quan các công trình liên quan theo bốn thành phần của đề tài — phát hiện làn đường, phát hiện biển báo, mô hình ngôn ngữ lớn đa phương thức cho lái xe, và phương pháp luận LLM-as-a-judge — và xác định năm khoảng trống nghiên cứu cụ thể mà đề tài này góp phần lấp đầy (mục 2.5). Chương 3 tiếp theo trình bày chi tiết phương pháp luận được xây dựng để giải quyết các khoảng trống đó, bắt đầu từ kiến trúc hệ thống tổng thể.

---

# CHƯƠNG 3. PHƯƠNG PHÁP LUẬN

Trước khi trình bày chi tiết từng thành phần, phần mở đầu này phát biểu hình thức bài toán ngữ nghĩa làn đường mà đề tài giải quyết, làm cơ sở thống nhất ký hiệu cho toàn bộ chương.

Cho một ảnh dashcam đầu vào $I$ có kích thước $\text{image\_width} \times \text{image\_height}$, mô hình phát hiện làn đường UFLD-v2 trả về một tập đường biên $B = \{b_1, b_2, \ldots, b_n\}$, mỗi đường biên $b_i$ là một danh sách điểm ảnh $\{(x, y)\}$ dọc theo vạch kẻ quan sát được. Nhiệm vụ của tầng phân tích ngữ nghĩa (mục 3.3) là ánh xạ tập đường biên thô $B$ này thành một bộ ngữ nghĩa cấp quyết định $S = (\ell, o, c, N)$, trong đó:

- $\ell$ (ego lane) — cặp đường biên $(b_i, b_{i+1}) \subset B$ xác định làn xe đang di chuyển, kèm độ tin cậy;
- $o$ (vehicle offset) — độ lệch $\Delta x$ giữa tâm làn ego và tâm ảnh, biểu diễn dưới dạng pixel và phần trăm bề rộng làn;
- $c$ (road shape) — phân loại hình dạng đường tổng thể (`straight`/`gentle`/`sharp`) kèm hướng cong;
- $N$ — số làn lân cận bên trái/phải làn ego.

Song song, mô hình phát hiện biển báo YOLOv8n trả về tập $D = \{(cls_j, box_j)\}$ gồm nhãn lớp và tọa độ khung bao của từng biển báo phát hiện được. Bộ ngữ nghĩa $S$ và tập $D$ sau đó được chuẩn hóa thành hai biểu diễn JSON — đầy đủ và rút gọn (mục 3.4) — làm đầu vào cho tầng suy luận: một mô hình ngôn ngữ lớn đa phương thức $M$ nhận ảnh $I$ và/hoặc JSON ngữ nghĩa, sinh khuyến nghị lái xe $R$ dưới dạng văn bản tự nhiên có cấu trúc ba phần (mục 3.5). RQ3 (mục 1.4) — câu hỏi nghiên cứu trung tâm của đề tài — chính là so sánh định lượng chất lượng của $R$ khi $M$ lần lượt nhận $(I)$, $(S)$, hay $(I, S)$ làm đầu vào.

Các mục 3.1–3.7 tiếp theo trình bày chi tiết từng thành phần của pipeline theo đúng thứ tự xử lý: kiến trúc tổng thể, dữ liệu, thuật toán suy ra $S$ từ $B$ (mục 3.3), cấu trúc JSON cụ thể (mục 3.4), thiết kế prompt sinh $R$ (mục 3.5), lựa chọn mô hình $M$ (mục 3.6), và phương pháp luận đánh giá $R$ (mục 3.7).

## 3.1. Kiến trúc hệ thống tổng thể

Pipeline của đề tài gồm bốn tầng xử lý tuần tự, minh họa ở Hình 3.1.

**Hình 3.1.** Kiến trúc tổng thể của pipeline bốn tầng.

```
Ảnh dashcam
    │
    ▼
[1. PERCEPTION]  UFLD-v2 (làn đường) + YOLOv8/TT100K (biển báo)
    │
    ▼
[2. SEMANTIC ANALYSIS]  Chuyển tọa độ thô → ngữ nghĩa (số làn, làn ego, độ lệch tâm,
                          làn lân cận, hình dạng đường) → JSON đầy đủ + JSON rút gọn
    │
    ▼
[3. LLM REASONING]  VLM (qua NVIDIA NIM API) sinh khuyến nghị lái xe bằng
                      ngôn ngữ tự nhiên - 3 chế độ input độc lập: chỉ ảnh /
                      chỉ JSON / ảnh + JSON
    │
    ▼
[4. EVALUATION]  LLM-as-a-judge (6 tiêu chí) + kiểm chứng độ tin cậy bằng
                   người và đa-judge
```

## 3.2. Dữ liệu

**Bộ dữ liệu chính (CULane).** 200 ảnh được lấy ngẫu nhiên từ dataset CULane (độ phân giải 1640×590), đại diện cho các tình huống đô thị đa dạng: đường thẳng, cua nhẹ, giao lộ, mật độ giao thông khác nhau. Ground truth được gán nhãn thủ công cho toàn bộ 200/200 ảnh, gồm: số làn thực tế cùng chiều, loại đường (thẳng/cong nhẹ/cong gắt kèm hướng), số làn bị phát hiện nhầm, số làn ngược chiều bị gộp nhầm, độ chính xác xác định làn ego, số biển báo thật, số detection đúng/sai. Toàn bộ kết quả trong Chương 4 — cả các kết quả dựa trên ground truth lẫn các kết quả dựa trên LLM-as-a-judge — sử dụng đầy đủ N=200.

**Bộ dữ liệu kiểm chứng độc lập (real-life).** 200 khung hình được trích xuất từ video dashcam thực tế (độ phân giải 1280×720), gán nhãn thủ công theo cùng schema như trên. Mục đích của bộ dữ liệu này là kiểm chứng khả năng tổng quát hóa của hệ thống trên dữ liệu hoàn toàn độc lập với dữ liệu huấn luyện của mô hình phát hiện làn đường (thảo luận về rủi ro data leakage được trình bày ở mục 4.7).

**Mô hình phát hiện làn đường.** UFLD-v2, backbone ResNet-34, pretrained trên CULane (`culane_res34.pth`).

**Mô hình phát hiện biển báo.** YOLOv8n (biến thể nhỏ nhất trong họ YOLOv8, khoảng 3,2 triệu tham số), được tự tinh chỉnh (fine-tune) trên tập con 50 lớp phổ biến của TT100K, khởi tạo từ checkpoint YOLOv8n gốc (pretrained trên COCO). Cấu hình huấn luyện:

- Độ phân giải ảnh đầu vào: 640×640; batch size tự động (`batch=-1`).
- Bộ tối ưu SGD, learning rate khởi tạo `lr0=0,01`, momentum `0,937`, weight decay `0,0005`, warm-up 3 epoch.
- Tối đa 100 epoch, cơ chế dừng sớm `patience=30` (dừng nếu không cải thiện sau 30 epoch liên tiếp).

Do giới hạn thời gian phiên làm việc của môi trường huấn luyện (Kaggle), quá trình bị ngắt giữa chừng ở epoch 82 và được chạy tiếp (resume) từ checkpoint gần nhất cho tới khi hoàn tất. Đây là một bước tinh chỉnh tiêu chuẩn, quy mô nhẹ so với việc huấn luyện hoặc tinh chỉnh một VLM/LLM trên dữ liệu lái xe quy mô lớn như ở các hệ end-to-end được khảo sát ở mục 2.3 (DriveGPT4, DriveLM, LMDrive, SafeRoute) — không mâu thuẫn với định hướng training-free của đề tài, vốn chỉ áp dụng cho riêng tầng suy luận VLM (mục 3.6), không áp dụng cho tầng perception.

## 3.3. Phân tích ngữ nghĩa làn đường

Đây là tầng xử lý do tác giả tự thiết kế và cài đặt, chuyển đổi danh sách điểm ảnh thô của từng đường biên (do UFLD-v2 trả về) thành bốn ngữ nghĩa cấp quyết định: làn ego, độ lệch tâm xe, hình dạng đường, và làn lân cận — cấu thành đóng góp 1 của đề tài (mục 1.5).

### Tiền xử lý: sắp xếp đường biên theo vị trí thực tế

UFLD-v2 không đảm bảo trả về các đường biên theo đúng thứ tự trái–phải trên ảnh. Do đó, trước khi xác định làn ego, các đường biên được sắp xếp lại theo tọa độ x tại một hàng ảnh tham chiếu gần đáy ảnh:

$$y_{ref} = 0{,}95 \times \text{image\_height}$$

Tọa độ x tại $y_{ref}$ được nội suy bằng trung bình các điểm trong khoảng $|y - y_{ref}| \le 30$ pixel; nếu không có điểm nào đủ gần (đường biên bị che khuất hoặc kết thúc sớm), tọa độ được ngoại suy bằng fit bậc 1 qua toàn bộ điểm sẵn có của đường biên. Cách này thay thế một phiên bản trước đó, vốn gán tạm $+\infty$ khi thiếu điểm gần và khiến đường biên bị đẩy sai lệch về bên phải, làm sai phân loại làn lân cận trái/phải.

### Xác định làn ego

Với $n$ đường biên đã sắp xếp trái sang phải và $x_{veh} = \text{image\_width}/2$ (giả định camera gắn tâm xe), thuật toán tính điểm cho mỗi cặp đường biên kề nhau $(i, i+1)$:

$$\text{score}_i = \left| \frac{x_i + x_{i+1}}{2} - x_{veh} \right| \times p_{between} \times \left(1 + 0{,}2 \times \frac{|w_i - w_{exp}|}{w_{exp}}\right)$$

trong đó $w_i = x_{i+1} - x_i$ là bề rộng cặp làn, $w_{exp} = 0{,}15 \times \text{image\_width}$ là bề rộng làn "điển hình" giả định, và

$$
p_{between} = \begin{cases} 0{,}5 & \text{nếu xe nằm giữa hai đường biên} \\ 1 & \text{ngược lại} \end{cases}
$$

Cặp có $\text{score}_i$ nhỏ nhất được chọn làm làn ego — chọn động theo từng ảnh thay vì giả định vị trí cố định, chấp nhận cả trường hợp bất đối xứng (đường cong, hoặc thiếu đường biên ở một phía).

Độ tin cậy được suy trực tiếp từ khoảng cách $d$ giữa tâm làn ego và tâm ảnh ($w$ = image_width):

| Điều kiện | $d < 0{,}1w$ | $d < 0{,}25w$ | $d < 0{,}4w$ | còn lại |
|---|---|---|---|---|
| Độ tin cậy | 0,95 | 0,8 | 0,6 | 0,4 |

Trường hợp chỉ phát hiện một đường biên ($n=1$): đường biên đó được gán làm ranh giới phải của làn ego, độ tin cậy cố định 0,5.

### Độ lệch tâm xe (vehicle offset)

Với tâm làn ego $x_{lane} = (x_{left} + x_{right})/2$:

$$\Delta x = x_{veh} - x_{lane} \quad \text{(pixel)}, \qquad \Delta x_{\%} = \frac{\Delta x}{w} \times 100$$

trong đó $w$ là bề rộng làn ego. Gán "centered" nếu $|\Delta x| < 10$ pixel, "lệch phải" nếu $\Delta x > 0$, "lệch trái" nếu ngược lại.

### Ước lượng độ cong

Với mỗi đường biên có tối thiểu 4 điểm, tọa độ $y$ được chuẩn hóa $y_{norm} = (y - y_{min})/(y_{max} - y_{min})$, rồi fit hai đa thức qua $(y_{norm}, x)$: bậc 1 (sai số $\text{MSE}_1$) và bậc 2 ($\text{MSE}_2$). Hai tín hiệu độ cong được trích ra:

$$\text{drift\_ratio} = \frac{\sqrt{\text{MSE}_1}}{\text{image\_width}}, \qquad \text{fit\_improvement} = \max\!\left(0,\; \frac{\text{MSE}_1 - \text{MSE}_2}{\text{MSE}_1}\right)$$

`drift_ratio` đo độ lệch quân phương so với một đường thẳng, chuẩn hóa theo chiều rộng ảnh; `fit_improvement` đo mức cải thiện khi cho phép mô hình cong so với ép thẳng, chỉ được tin khi $\text{MSE}_1 > 4$ và đường biên có ≥10 điểm — nếu không, chênh lệch $\text{MSE}_1-\text{MSE}_2$ bị coi là nhiễu/overfit và gán bằng 0. Tín hiệu này cần thiết cho các đường cong rất nhẹ, nơi độ lệch tuyệt đối còn quá nhỏ để `drift_ratio` phát hiện.

Điểm hội tụ phối cảnh (vanishing point) của mỗi đường biên được ngoại suy bằng fit bậc 1, tại một mốc "chân trời" dùng chung cho mọi đường biên trong ảnh:

$$y_{horizon} = 0{,}3 \times \text{image\_height}$$

thay vì ngoại suy riêng tại $y_{norm}=0$ của từng đường biên như thiết kế ban đầu — cách cũ khiến hai đường biên thẳng song song có thể cho hai điểm hội tụ khác nhau (do được đánh giá ở hai độ sâu ảnh khác nhau), phóng đại sai độ phân tán điểm hội tụ dù đường thực sự thẳng. Neo về cùng một hàng ảnh khắc phục sai lệch này.

Bốn tín hiệu tổng hợp trên toàn ảnh — $\overline{\text{drift}}$, $\overline{\text{fit\_improvement}}$, tỉ lệ đường biên "thẳng" ($\text{MSE}_1 < 1000$), và hướng cong (so sánh x trung bình gần đáy ảnh với gần giữa ảnh, ngưỡng $\text{shift\_ratio}=0{,}08$) — được dùng để phân loại hình dạng đường tổng thể.

### Hiệu chỉnh ngưỡng phân loại độ cong

Ba ngưỡng được hiệu chỉnh bằng số liệu thực đo trên CULane, không đặt tùy ý: $\overline{\text{drift}}_{straight}=0{,}02$ (trên phân vị p95 của ảnh đường thẳng, ≈0,014); $\overline{\text{drift}}_{sharp}=0{,}06$ (dưới giá trị đo của một ảnh cua gắt đã xác nhận đúng, 0,0994); $\text{fit\_improvement}=0{,}3$, dùng để nâng hạng từ "thẳng" lên "cong nhẹ" khi $\overline{\text{drift}}$ quá nhỏ để tự phát hiện nhưng bằng chứng cong vẫn rõ ràng. Quy tắc phân loại cuối cùng:

$$
\text{classification} = \begin{cases}
\texttt{straight} & \overline{\text{drift}} < 0{,}02 \text{ và } \overline{\text{fit\_improvement}} < 0{,}3 \text{ và tỉ lệ đường biên thẳng} > 50\% \\
\texttt{sharp} & \overline{\text{drift}} \ge 0{,}06 \\
\texttt{gentle} & \text{còn lại}
\end{cases}
$$

Độ phân tán tuyệt đối của điểm hội tụ ($\text{vp\_spread}$) từng được cân nhắc nhưng bị loại khỏi quy tắc phân loại: không chuẩn hóa theo kích thước ảnh nên không ổn định giữa các ảnh khác đặc trưng camera — vẫn được lưu trong JSON để tham khảo, không tham gia phân loại.

### Số làn đường

Bằng số đường biên phát hiện được trừ 1, theo quy ước CULane — công thức từng chứa lỗi lệch đơn vị (off-by-one), thảo luận định lượng ở mục 4.1.

## 3.4. Cấu trúc JSON ngữ nghĩa gửi cho LLM

**JSON đầy đủ (`<tên>.json`).** Đây là output trực tiếp của tầng Semantic Analysis (mục 3.3), và cũng là bản JSON được nhúng nguyên vẹn vào prompt ở hai chế độ `json_only`/`image_json`. Cấu trúc gồm bốn nhóm trường:

1. **Siêu dữ liệu**: `scene_id` (định danh phiên xử lý), `timestamp`, `image_size` (`width`, `height`).
2. **`road`** (tổng hợp cấp đường): `road_type`, `road_environment` (ước lượng heuristic loại môi trường đường bằng quy tắc if-else đơn giản — độ tin cậy thấp, đã bị loại khỏi bản rút gọn vì lý do này), `curvature_magnitude`/`curvature_direction`/`curvature_confidence` (kết quả từ mục 3.3), và `geometry` (`spread_pixels`, `coverage_ratio`, `convergence_ratio`, `lane_count`, `geometry_type`).
3. **`lane`** (chi tiết cấp làn, đầu ra chính của mục 3.3): `sorted_lanes` (danh sách đường biên đã sắp xếp trái sang phải); `ego_lane` (ranh giới, tâm làn, bề rộng, độ tin cậy); `lane_classification` (số lượng và danh sách làn lân cận trái/phải); `vehicle_offset` (đầy đủ các trường mô tả ở mục 3.3); `curvature` (kết quả phân loại độ cong); `lane_semantics` (ngữ nghĩa từng làn: loại, có phải làn ego không, có đi được không, vị trí tương đối); và kích thước ảnh.
4. **`traffic_signs`**: danh sách biển báo phát hiện được kèm nhãn lớp và tọa độ, cùng số lượng.

**JSON rút gọn (`<tên>_brief.json`).** Một schema riêng, gọn hơn nhiều, chỉ gồm năm trường cấp quyết định: `lane_count`, `ego_lane` (vị trí dạng "X/Y" và độ tin cậy), `vehicle_offset` (hướng, mức độ, phần trăm lệch), `neighbor_lanes` (số làn trái/phải), `road_shape` (loại, mức độ, hướng cong) — không có siêu dữ liệu, không có `traffic_signs`. Thiết kế nhằm cấp cho LLM một bản dữ liệu tối giản, loại bỏ các trường thiếu bằng chứng đủ tin cậy khỏi ngữ cảnh của LLM. Schema này được sử dụng đúng mục đích ở một thí nghiệm khác của đề tài: làm định dạng output mục tiêu cho thí nghiệm kiểm chứng khả năng tự nhận diện của VLM (mục 4.8), nơi VLM được yêu cầu tự trích xuất đúng năm trường này trực tiếp từ ảnh, không kèm bất kỳ gợi ý nào, rồi so sánh với giá trị mà pipeline UFLD-v2 tính ra. Ở vai trò này, `_brief.json` chỉ đóng vai trò khuôn mẫu cấu trúc cho output cần so sánh, không phải input được cấp cho VLM, nên không phát sinh vấn đề về công bằng hay rò rỉ thông tin.

## 3.5. Thiết kế prompt cho tầng suy luận

Prompt được thiết kế qua nhiều vòng lặp thực nghiệm, tập trung vào bốn ngữ nghĩa cấp làn đường — số làn, làn ego, độ lệch tâm, làn lân cận — kèm các quy tắc chống ảo giác (không suy diễn thông tin không có bằng chứng, không coi thiếu phát hiện là bằng chứng cho việc vật thể không tồn tại) và yêu cầu cấu trúc output cố định gồm ba phần: Tình huống, Khuyến nghị, Lưu ý an toàn, nhằm đảm bảo tính nhất quán giữa các lần sinh. Trong quá trình phát triển, hai vấn đề đã được phát hiện và khắc phục: hiện tượng mô hình lặp lại vô hạn cùng một câu trả lời trên ảnh ít thông tin, khắc phục bằng tham số frequency penalty; và hiện tượng mô hình trả lời quá ngắn, không tuân thủ cấu trúc bắt buộc, khắc phục bằng yêu cầu nêu bằng chứng cụ thể cho từng phần.

## 3.6. Lựa chọn mô hình cho tầng suy luận

Do giới hạn về chi phí và khả năng tái lập, phạm vi lựa chọn mô hình được giới hạn trong các VLM khả dụng miễn phí qua NVIDIA NIM API (định dạng OpenAI-compatible thống nhất). Ba mô hình cụ thể được chọn để so sánh dựa trên ba tiêu chí:

1. Hỗ trợ đa phương thức (nhận đồng thời ảnh và văn bản) — điều kiện bắt buộc của pipeline, loại trừ các mô hình chỉ xử lý văn bản.
2. Khả dụng miễn phí qua cùng một API thống nhất, đảm bảo chi phí triển khai bằng 0 và tính nhất quán khi thực nghiệm, đúng định hướng training-free/chi phí thấp của đề tài (mục 1.5).
3. Trải dài trên nhiều mức quy mô tham số khác nhau trong phạm vi các mô hình khả dụng, cho phép quan sát liệu quy mô mô hình có tương quan với độ tin cậy và chất lượng đầu ra hay không, phục vụ trực tiếp RQ4.

Ba mô hình thỏa mãn đồng thời cả ba tiêu chí là: `nemotron-nano-vl-8b` (8 tỷ tham số), `nemotron-nano-12b-v2-vl` (12 tỷ tham số), `ising-calibration-1.5-31b` (31 tỷ tham số).

Tiêu chí so sánh giữa ba mô hình gồm, theo đúng thứ tự ưu tiên: độ tin cậy — tỉ lệ hoàn thành thành công khi chạy trên toàn bộ batch thật, được xét trước và độc lập với chất lượng nội dung, vì một mô hình không phản hồi ổn định không thể triển khai cho một hệ thống hỗ trợ quyết định thời gian thực, bất kể chất lượng câu trả lời khi nó phản hồi thành công tốt tới đâu; tỉ lệ tuân thủ cấu trúc output bắt buộc; và chất lượng nội dung, chấm điểm bởi LLM-as-a-judge, chỉ áp dụng cho các mô hình đã vượt qua ngưỡng tối thiểu ở tiêu chí đầu tiên.

**Trình tự thực nghiệm.** Việc chọn mô hình LLM ở mục này (RQ4) và kết quả trung tâm về đóng góp của JSON ngữ nghĩa ở mục 4.5 (RQ3) là hai thực nghiệm tách biệt, chạy tuần tự, không phụ thuộc vòng tròn vào nhau:

1. *Giai đoạn 1 — chọn mô hình (mục 4.4)*: cả ba mô hình ứng viên được chạy ở cùng một chế độ input cố định — `image+json`, chế độ cấp đầy đủ thông tin nhất, cho mỗi mô hình cơ hội thể hiện tốt nhất — và được chấm điểm bởi đúng một judge (Gemini) để xác định mô hình có độ tin cậy và chất lượng tốt nhất. Kết quả: `ising-calibration-31b` được chọn.
2. *Giai đoạn 2 — so sánh chế độ input (mục 4.5)*: mô hình đã chọn được giữ cố định, và biến số duy nhất được thay đổi là chế độ input (`image_only`/`json_only`/`image+json`), chấm điểm bởi cả ba judge độc lập để trả lời RQ3.

Nói cách khác, chuỗi xử lý thực tế là: ảnh → detection/semantic analysis → chạy ba mô hình LLM ở chế độ `image+json`, Gemini chấm điểm, chọn mô hình thắng → cố định mô hình thắng, chạy lại ở cả ba chế độ input, cả ba judge chấm điểm, kết luận RQ3. Bước chấm điểm để chọn mô hình và bước chấm điểm để so sánh chế độ input là hai lượt riêng biệt, phục vụ hai câu hỏi nghiên cứu khác nhau, không phải cùng một lượt chấm dùng cho cả hai mục đích.

**Vì sao Giai đoạn 1 chỉ dùng một chế độ input và một judge.** Đây là một lựa chọn thiết kế thực nghiệm có chủ đích, dựa trên ba căn cứ. Thứ nhất, RQ4 và RQ3 là hai câu hỏi trực giao: chạy toàn bộ ma trận ba mô hình × ba chế độ × ba judge sẽ tốn gấp nhiều lần chi phí và thời gian API mà không phục vụ trực tiếp RQ4, vốn chỉ cần xác định mô hình nào đáng tin cậy và chất lượng tốt nhất, không cần biết mô hình đó tương tác thế nào với từng chế độ input cụ thể; cố định chế độ input ở `image+json` khi so sánh mô hình là cách chuẩn để đảm bảo mỗi mô hình được đánh giá trong điều kiện thuận lợi nhất có thể, tách bạch "mô hình yếu" khỏi "mô hình bị thiếu thông tin". Thứ hai, đây là một ràng buộc trong trình tự phát triển thực tế: tại thời điểm Giai đoạn 1 được thực hiện, GPT-5 Mini và DeepSeek chưa được tích hợp làm judge — Gemini là judge duy nhất tồn tại trong hệ thống ở giai đoạn đó — và việc bổ sung đối chiếu đa-judge (mục 4.6) là một bước siết chặt phương pháp luận được thêm vào sau, dành riêng cho kết quả trung tâm ở mục 4.5, nơi kết luận thực sự nhạy với lựa chọn judge (thứ hạng `json_only` so với `image+json` đảo chỗ tùy judge, Bảng 4.6). Thứ ba, độ lớn chênh lệch giữa các mô hình ở RQ4 không đòi hỏi kiểm chứng đa-judge để tin cậy: `nemotron-nano-12b-v2-vl` thất bại tới 82,9% số yêu cầu, và `ising-calibration-31b` vượt `nemotron-nano-8b` với Cohen's d xấp xỉ 1,04 (Bảng 4.4) — một hiệu ứng rất lớn, khó có khả năng bị đảo ngược chỉ vì đổi judge; thêm vào đó, mục 4.6 (thực hiện sau) xác nhận Gemini là judge có tương quan với con người cao nhất trong ba judge đã thử, củng cố thêm — dù không phải bằng chứng có sẵn tại thời điểm Giai đoạn 1 được thực hiện — rằng lựa chọn Gemini làm judge duy nhất cho quyết định này là hợp lý.

## 3.7. Phương pháp luận đánh giá

**Đánh giá module hiểu làn đường/biển báo.** So sánh trực tiếp với ground truth gán tay, sử dụng các metric chuẩn: Accuracy (tỉ lệ khớp chính xác), MAE (sai số tuyệt đối trung bình), Precision và Recall.

**Đánh giá chất lượng khuyến nghị lái xe.** Sử dụng LLM-as-a-judge với rubric sáu tiêu chí, thang điểm 1–5: `situation_understanding`, `road_understanding`, `lane_ego_position`, `traffic_sign_rule`, `driving_recommendation`, `safety_considerations`. Mỗi ảnh được đánh giá bằng một lệnh gọi API duy nhất, gộp cả ba thí nghiệm cần so sánh trong cùng một ngữ cảnh, vừa tiết kiệm chi phí, vừa đảm bảo tính nhất quán trong đánh giá.

**Kiểm chứng độ tin cậy của judge.** Gồm hai bước: so sánh điểm của Gemini với điểm chấm tay của con người trên một mẫu ngẫu nhiên N=20; và đối chiếu với hai judge độc lập khác (GPT-5 Mini, DeepSeek) trên cùng bộ dữ liệu, dùng nguyên văn cùng một rubric để đảm bảo so sánh công bằng. Mốc chuẩn để đánh giá "judge nào chính xác hơn" là độ đồng thuận với con người, không phải độ đồng thuận giữa các judge với nhau, vì hai judge AI có thể đồng ý với nhau nhưng vẫn cùng chia sẻ một thiên lệch giống nhau so với con người.

**Tóm tắt chương.** Chương này đã trình bày đầy đủ phương pháp luận của đề tài: kiến trúc pipeline bốn tầng, dữ liệu sử dụng, thuật toán suy ra ngữ nghĩa làn đường $S$ từ output UFLD-v2, cấu trúc JSON gửi cho VLM, thiết kế prompt, tiêu chí và trình tự lựa chọn mô hình suy luận, và phương pháp luận đánh giá. Chương 4 tiếp theo trình bày kết quả thực nghiệm định lượng cho từng thành phần này, bắt đầu từ độ chính xác của module hiểu làn đường.

---

# CHƯƠNG 4. KẾT QUẢ VÀ BÀN LUẬN

## 4.1. Độ chính xác module hiểu làn đường (CULane)

Ở giai đoạn đầu, 26 ảnh thuộc các tình huống khó xác định — sảnh/quảng trường không vạch kẻ, hầm gửi xe, đang nhập làn, giao lộ phức tạp — được gán tạm `lane_count=0` để loại khỏi thống kê. Quá trình rà soát sau đó phát hiện cách làm này che giấu một sai lệch: phần lớn các ảnh đó, mô hình cũng dự đoán giá trị 0 do không thấy vạch kẻ, nên vô tình được tính là "khớp chính xác", dù thực chất mô hình đã thất bại hoàn toàn chứ không phải đoán đúng "0 làn". Toàn bộ 200 ảnh sau đó được gán nhãn lại bằng số làn ước lượng thực tế — dựa vào bề rộng đường, vị trí xe khác, dải phân cách vật lý — kèm theo nhãn phân loại lý do khó (`hard_reason`), cho phép tách riêng nhóm ảnh có vạch kẻ rõ ("Normal") khỏi nhóm không có vạch kẻ rõ.

**Bảng 4.1.** Độ chính xác module hiểu làn đường trước và sau khi sửa lỗi off-by-one (N=200).

| Chỉ số | Trước khi sửa lỗi off-by-one | Sau khi sửa lỗi (N=200) |
|---|---|---|
| Lane count – Accuracy (khớp chính xác) | 11,1% | **69,0%** |
| Lane count – MAE | 1,056 | **0,475** |
| Lane count – Precision | – | **96,6%** |
| Road type – Accuracy (khớp chính xác) | Không đo được (luôn "straight") | **76,5%** |
| Road type – Accuracy (khớp nhóm thẳng/cong nhẹ/cong gắt) | – | **78,5%** |
| Road type – Recall của cua nhẹ | 0% | **57,1%** (4/7) |
| Ego lane – Accuracy | – | **86,0%** |
| Làn bị phát hiện nhầm | – | **0,8%** |

Các chỉ số ở Bảng 4.1 được tính trực tiếp từ đối chiếu `image_labels.xlsx` với output của pipeline trên N=200 ảnh:

- Lane count Accuracy = tỉ lệ ảnh có số làn dự đoán khớp đúng số làn thực tế = 138/200 = 69,0%.
- Lane count MAE = trung bình trị tuyệt đối của hiệu số làn thực tế và dự đoán = 95/200 = 0,475.
- Lane count Precision = tổng số làn thực tế chia cho tổng số làn thực tế cộng số làn phát hiện nhầm và số làn ngược chiều bị gộp nhầm = 477/(477+5+12) = 96,6%.
- Road type Accuracy (khớp chính xác) = 153/200 = 76,5%; khớp theo nhóm thẳng/nhẹ/gắt = 157/200 = 78,5%.
- Ego lane Accuracy = tỉ lệ ảnh có làn ego được xác định đúng = 172/200 = 86,0%.

Kết quả đáng chú ý nhất ở giai đoạn này không nằm ở bản thân việc sửa lỗi, mà ở ý nghĩa phương pháp luận mà nó bộc lộ về tầng diễn giải ngữ nghĩa. Hệ thống ban đầu chứa một lỗi lệch đơn vị (off-by-one) trong công thức tính số làn — đếm số đường biên thay vì số làn thực tế — khiến hầu hết ảnh bị báo thừa một làn. Do giá trị này được nhúng trực tiếp vào ngữ cảnh JSON gửi cho LLM, lỗi này là nguyên nhân trực tiếp gây ra hiện tượng "ảo giác" số làn trong khuyến nghị của LLM ở giai đoạn đầu nghiên cứu. Sau khi sửa, Accuracy tăng từ 11,1% lên 69,0%, đo trên cùng một lần detect và chỉ khác công thức xử lý phía sau — cho thấy mức cải thiện này đến từ tầng diễn giải ngữ nghĩa, không phụ thuộc vào chất lượng của bản thân mô hình phát hiện. Nói cách khác, đây không phải một đóng góp thuật toán, mà là bằng chứng thực nghiệm cho thấy tầng diễn giải ngữ nghĩa, nếu không được xây dựng và kiểm chứng cẩn thận, có thể trở thành điểm nghẽn quyết định chất lượng toàn hệ thống, dù tầng phát hiện phía trước đã đạt chất lượng tốt.

Sau khi gán nhãn lại 26 ảnh khó nêu trên, việc tách riêng theo `hard_reason` cho thấy hiệu năng của mô hình phụ thuộc rất mạnh vào sự hiện diện của vạch kẻ đường.

**Bảng 4.2.** So sánh hiệu năng module hiểu làn đường theo nhóm có/không vạch kẻ đường rõ.

| Nhóm | N | Lane count Accuracy | Lane count MAE | Precision | Ego lane Accuracy |
|---|---|---|---|---|---|
| Có vạch kẻ rõ ("Normal") | 176 | **77,3%** | 0,273 | 96,2% | **96,6%** |
| Không vạch kẻ rõ (quảng trường/hầm gửi xe/nhập làn/giao lộ phức tạp) | 24 | **8,3%** | 1,958 | 100,0% | **8,3%** |

Số liệu thô làm cơ sở cho Bảng 4.2: nhóm Normal có 136/176 ảnh khớp chính xác, tổng trị tuyệt đối sai số 48 (MAE = 48/176 = 0,273), tổng số làn thực tế/nhầm/ngược chiều lần lượt 427/5/12 (Precision = 427/444 = 96,2%), 170/176 ảnh xác định đúng làn ego (96,6%). Nhóm Hard có 2/24 ảnh khớp chính xác, tổng trị tuyệt đối sai số 47 (MAE = 47/24 = 1,958), tổng số làn thực tế/nhầm/ngược chiều lần lượt 50/0/0 (Precision = 50/50 = 100%), 2/24 ảnh xác định đúng làn ego (8,3%).

Đáng chú ý, Precision vẫn đạt 100% ngay cả trên nhóm khó, dù Accuracy chỉ 8,3%. Lý do nằm ở chính công thức: Precision đo tỉ lệ những gì mô hình *dám khẳng định* là chính xác, không đo mức độ đầy đủ. Với 19/24 ảnh trong nhóm này, pipeline trả về `pred_lane_count = 0` — không phát hiện được gì — nên không có làn nào để đếm là "sai" hay "bịa"; Σfalse và Σopposite vì vậy đều bằng 0, và Precision = 50/(50+0+0) = 100% một cách gần như tất yếu. Điều này thể hiện rõ nhất ở hai lý do `no_markings` và `merging`, nơi số làn dự đoán trung bình bằng 0,00 trong khi số làn thực tế trung bình khoảng 1,7–2,5: mô hình không "bịa" làn giả, mà đơn giản là im lặng khi thiếu vạch kẻ. Đây là hạn chế cố hữu của một detector dựa trên vạch kẻ đường — UFLD-v2 được huấn luyện trên CULane, vốn chủ yếu là ảnh có vạch kẻ rõ — không phải lỗi logic của tầng xử lý ngữ nghĩa phía sau, và được bàn thêm ở mục 5.3.

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

Toàn bộ so sánh trong mục này (Giai đoạn 1, mục 3.6) được chạy ở cùng một chế độ input cố định `image+json` và chấm điểm bởi đúng một judge (Gemini), nhằm chọn ra mô hình LLM sẽ được giữ cố định cho Giai đoạn 2 — so sánh chế độ input, mục 4.5 — chứ không phải một phần của thực nghiệm ba-judge/ba-chế-độ trả lời RQ3.

**Độ tin cậy và tốc độ.** `ising-calibration-31b` đạt tỉ lệ thành công 200/200 (0% lỗi), thời gian trung bình 3,80 giây/ảnh. `nemotron-nano-12b-v2-vl` chỉ đạt 34/200 (83% yêu cầu nhận lỗi 500 Internal Server Error từ phía máy chủ NVIDIA NIM).

Mô hình `nemotron-nano-12b-v2-vl` bị loại khỏi vòng so sánh chất lượng vì hai lý do độc lập, không phải vì bản thân câu trả lời — khi có — kém chất lượng. Thứ nhất, như đã nêu ở mục 3.6, độ tin cậy được xét như một tiêu chí có tính loại trừ, đứng trước và độc lập với chất lượng nội dung: một mô hình chỉ phản hồi thành công 17,1% số yêu cầu không thể triển khai cho một hệ thống hỗ trợ quyết định thời gian thực, bất kể chất lượng của 17% câu trả lời còn lại tốt tới đâu. Lỗi 500 xuất phát từ phía hạ tầng máy chủ NVIDIA NIM lưu trữ mô hình, không phản ánh trực tiếp năng lực của bản thân mô hình, nhưng từ góc độ triển khai thực tế, một mô hình không thể truy cập ổn định thì không sử dụng được, bất kể nguyên nhân kỹ thuật đến từ đâu. Thứ hai, ngay cả khi bỏ qua tiêu chí loại trừ trên, 34 câu trả lời thành công còn lại không tạo thành một mẫu so sánh công bằng: đây là tập con tự chọn lọc bởi chính cơ chế gây lỗi của máy chủ, nhiều khả năng thiên lệch về phía các ảnh hoặc yêu cầu đơn giản hơn, ít tốn thời gian xử lý hơn, chứ không phải một mẫu ngẫu nhiên đại diện cho toàn bộ 200 ảnh như hai mô hình còn lại đạt được ở phép so sánh này. So sánh chất lượng giữa 34 mẫu thiên lệch với 200 mẫu đầy đủ của các mô hình khác sẽ vi phạm nguyên tắc so sánh công bằng đã đặt ra cho toàn bộ phương pháp luận đánh giá của đề tài (mục 3.7).

**Tuân thủ cấu trúc output.** Trên N=200, đếm số output có độ dài dưới 80 ký tự — tương đương bỏ qua cấu trúc ba phần bắt buộc — cho thấy `nemotron-nano-8b` có 99/200 (49,5%) output bị cắt cụt, trong khi `ising-calibration-31b` có 0/200 (0%) trên đúng tập đối chứng này. Xét trên độ dài toàn bộ output, `nemotron-nano-8b` sinh trung bình 95 ký tự/câu trả lời (SD = 78), trong khi `ising-calibration-31b` sinh trung bình 876 ký tự/câu trả lời (SD = 198) — gấp hơn 9 lần, đủ để trình bày trọn vẹn ba phần Tình huống/Khuyến nghị/Lưu ý an toàn theo đúng yêu cầu prompt (mục 3.5), thay vì một câu trả lời rút gọn không đạt cấu trúc tối thiểu.

**Chất lượng nội dung** (so với `nemotron-nano-8b`, N=200, cùng ảnh, cùng judge Gemini, cùng rubric sáu tiêu chí). Đây là phép so sánh trực tiếp và công bằng nhất trong ba mô hình, vì cả hai đều vượt qua tiêu chí loại trừ về độ tin cậy — `nemotron-nano-8b` hoàn thành 200/200, không bị loại vì lý do thiên lệch mẫu như `nemotron-nano-12b-v2-vl`. Áp dụng đúng phương pháp thống kê đã dùng ở mục 4.5 — tính điểm trung bình sáu tiêu chí theo từng ảnh trước, rồi kiểm định bắt cặp trên 200 cặp điểm-trên-ảnh — kết quả ở Bảng 4.4 cho thấy khoảng cách không chỉ lớn mà còn có ý nghĩa thống kê rất mạnh.

**Bảng 4.4.** So sánh chi tiết chất lượng nội dung giữa `nemotron-nano-8b` và `ising-calibration-31b` (Mean ± SD, N=200, kiểm định Wilcoxon signed-rank bắt cặp theo ảnh).

| Tiêu chí | nemotron-nano-8b | ising-calibration-31b | Wilcoxon p |
|---|---|---|---|
| situation_understanding | 1,97 ± 1,15 | 3,48 ± 1,24 | p < 0,001 |
| road_understanding | 2,08 ± 1,27 | 3,77 ± 0,92 | p < 0,001 |
| lane_ego_position | 2,03 ± 1,13 | 3,77 ± 1,24 | p < 0,001 |
| traffic_sign_rule | 2,17 ± 1,42 | 3,18 ± 1,32 | p < 0,001 |
| driving_recommendation | 3,98 ± 1,13 | 4,16 ± 1,20 | p = 0,066 |
| safety_considerations | 1,69 ± 0,98 | 3,74 ± 1,19 | p < 0,001 |
| **Trung bình 6 tiêu chí (điểm/ảnh)** | **2,32 ± 0,99** | **3,68 ± 0,96** | paired t: t = −14,68, p < 0,001; Cohen's d = −1,04 (rất lớn) |

`ising-calibration-31b` vượt trội có ý nghĩa thống kê ở năm trên sáu tiêu chí (p < 0,001), với kích thước hiệu ứng tổng thể rất lớn (Cohen's d ≈ 1,04, tức chênh lệch trung bình vượt quá một độ lệch chuẩn). Riêng tiêu chí `driving_recommendation`, chênh lệch 3,98 so với 4,16 không đạt ý nghĩa thống kê (p = 0,066) — hai mô hình được đánh giá tương đương nhau ở đúng tiêu chí này, không phải `ising-calibration-31b` thắng tuyệt đối ở toàn bộ sáu tiêu chí. Điều này không làm suy yếu quyết định chọn mô hình: năm trên sáu tiêu chí còn lại, cùng với chênh lệch rất lớn về độ tin cậy và về độ dài/tính đầy đủ cấu trúc output (876 so với 95 ký tự), đã là căn cứ đủ mạnh và đủ toàn diện.

Tổng hợp cả ba tiêu chí theo đúng thứ tự ưu tiên đã đặt ra ở mục 3.6 — độ tin cậy, tuân thủ cấu trúc, chất lượng nội dung — `ising-calibration-31b` là lựa chọn tốt nhất trong ba mô hình, và được chọn làm mô hình chính cho toàn bộ thực nghiệm còn lại của đề tài.

## 4.5. Kết quả chính: đóng góp của JSON ngữ nghĩa

Đây là kết quả trung tâm trả lời RQ3, đo trên mô hình chính (`ising-calibration-31b`), ba chế độ input, chấm điểm bởi ba judge độc lập (Gemini, GPT-5 Mini, DeepSeek) dùng nguyên văn cùng một rubric, trên toàn bộ N=200 ảnh.

Với mỗi ảnh, điểm tổng hợp của một chế độ được tính bằng trung bình cộng của sáu điểm tiêu chí trên chính ảnh đó (thang 1–5); từ đó thu được, với mỗi judge, ba dãy 200 điểm bắt cặp theo ảnh — một dãy cho mỗi chế độ. Điểm trung bình toàn mẫu của một chế độ, dùng để báo cáo ở Bảng 4.5, là trung bình cộng của dãy 200 điểm-trên-ảnh đó:

$$\text{Điểm(chế độ)} = \frac{1}{200} \sum_{j=1}^{200} \left[ \frac{1}{6} \sum_{i=1}^{6} \text{điểm}(\text{ảnh } j, \text{tiêu chí } i, \text{chế độ}) \right]$$

Việc tính điểm theo từng ảnh trước, rồi mới lấy trung bình, giúp mỗi ảnh đóng góp đúng một lần vào kết quả cuối và cho phép thực hiện kiểm định thống kê bắt cặp (paired) giữa các chế độ trên cùng một ảnh, thay vì chỉ so sánh hai giá trị trung bình đơn lẻ.

**Bảng 4.5.** Điểm chất lượng khuyến nghị lái xe (Mean ± SD trên 200 ảnh) theo ba chế độ input, chấm bởi ba judge độc lập (thang 1–5).

| Judge | image_only | json_only | image+json | Xếp hạng |
|---|---|---|---|---|
| Gemini | 3,32 ± 0,95 | **4,53 ± 0,77** | 3,97 ± 0,95 | json > image+json > image |
| GPT-5 Mini | 3,13 ± 0,75 | 3,55 ± 1,14 | **3,96 ± 0,86** | image+json > json > image |
| DeepSeek | 3,11 ± 0,96 | **3,41 ± 1,17** | 3,40 ± 1,02 | json ≈ image+json > image |

Kết quả điểm trung bình này gần như không đổi so với lần đo trước đó ở N=200 (chênh lệch chỉ ở chữ số thập phân thứ ba), cho thấy kết luận ổn định, không nhạy với việc thêm hoặc bớt một vài mẫu. Độ lệch chuẩn tương đối lớn ở cả ba chế độ (0,75–1,17 trên thang 1–5) phản ánh mức độ đa dạng tự nhiên giữa các ảnh: có ảnh dễ — đường thẳng, ít vật cản — cho điểm cao ở mọi chế độ, có ảnh khó — giao lộ, thiếu vạch kẻ — cho điểm thấp ở mọi chế độ. Vì vậy, khoảng cách trung bình giữa các chế độ cần được kiểm định thống kê thay vì chỉ so sánh trực quan hai con số, trình bày ở Bảng 4.6.

**Bảng 4.6.** Kiểm định ý nghĩa thống kê khi so sánh cặp giữa ba chế độ input, theo từng judge (N=200, dữ liệu bắt cặp theo ảnh; kiểm định t bắt cặp và Wilcoxon signed-rank; d là Cohen's d cho hiệu số bắt cặp).

| Judge | Cặp so sánh | t bắt cặp (df=199) | p (t-test) | Wilcoxon p | Cohen's d |
|---|---|---|---|---|---|
| Gemini | image_only vs json_only | −13,62 | p < 0,001 | p < 0,001 | −0,96 (lớn) |
| Gemini | image_only vs image+json | −8,37 | p < 0,001 | p < 0,001 | −0,59 (trung bình–lớn) |
| Gemini | json_only vs image+json | 7,28 | p < 0,001 | p < 0,001 | 0,51 (trung bình) |
| GPT-5 Mini | image_only vs json_only | −4,33 | p < 0,001 | p < 0,001 | −0,31 (nhỏ) |
| GPT-5 Mini | image_only vs image+json | −11,16 | p < 0,001 | p < 0,001 | −0,79 (lớn) |
| GPT-5 Mini | json_only vs image+json | −4,93 | p < 0,001 | p < 0,001 | −0,35 (nhỏ) |
| DeepSeek | image_only vs json_only | −2,83 | p = 0,005 | p = 0,003 | −0,20 (nhỏ) |
| DeepSeek | image_only vs image+json | −3,19 | p = 0,002 | p < 0,001 | −0,23 (nhỏ) |
| DeepSeek | json_only vs image+json | 0,09 | p = 0,930 | p = 0,625 | 0,01 (không đáng kể) |

Kết quả kiểm định củng cố kết luận ở Bảng 4.5: trong sáu phép so sánh liên quan trực tiếp đến `image_only` — ba judge nhân hai cặp so sánh — đều có ý nghĩa thống kê ở mức p < 0,01, xác nhận `image_only` thấp hơn hai chế độ còn lại không phải do ngẫu nhiên. Kích thước hiệu ứng dao động từ nhỏ ở DeepSeek (d ≈ 0,20–0,23) đến lớn ở Gemini (d ≈ 0,59–0,96), phù hợp với việc Gemini đồng thời là judge có độ tin cậy cao nhất khi đối chiếu với con người (mục 4.6) — gợi ý rằng khoảng cách điểm số lớn hơn ở Gemini không chỉ là nhiễu thống kê mà phản ánh một tín hiệu thật rõ ràng hơn. Riêng phép so sánh `json_only` với `image+json` của DeepSeek không có ý nghĩa thống kê (p = 0,930, d ≈ 0,01), xác nhận định lượng cho nhận định "json ≈ image+json" đã nêu ở Bảng 4.5: đây không phải hai chế độ có điểm số ngẫu nhiên gần nhau, mà thực sự không khác biệt theo đánh giá của judge này.

Bảng 4.7 minh họa cách tính điểm trung bình tiêu chí bằng ví dụ chi tiết của judge Gemini, kèm độ lệch chuẩn của từng tiêu chí và kết quả kiểm định Wilcoxon cho hai so sánh chính.

**Bảng 4.7.** Điểm trung bình (Mean ± SD, N=200/tiêu chí) sáu tiêu chí đánh giá của judge Gemini theo từng chế độ input, kèm kiểm định Wilcoxon so với `image_only`.

| Tiêu chí | image_only | json_only | image+json | Wilcoxon p (image vs json) | Wilcoxon p (image vs image+json) |
|---|---|---|---|---|---|
| situation_understanding | 2,76 ± 1,12 | 4,38 ± 0,95 | 3,51 ± 1,31 | p < 0,001 | p < 0,001 |
| road_understanding | 3,27 ± 1,00 | 4,47 ± 0,87 | 4,04 ± 1,02 | p < 0,001 | p < 0,001 |
| lane_ego_position | 3,27 ± 1,25 | 4,64 ± 0,76 | 4,21 ± 1,17 | p < 0,001 | p < 0,001 |
| traffic_sign_rule | 3,84 ± 1,51 | 4,72 ± 0,75 | 4,24 ± 1,24 | p < 0,001 | p < 0,001 |
| driving_recommendation | 3,50 ± 1,41 | 4,58 ± 0,87 | 3,97 ± 1,38 | p < 0,001 | p < 0,001 |
| safety_considerations | 3,31 ± 1,21 | 4,39 ± 0,95 | 3,85 ± 1,30 | p < 0,001 | p < 0,001 |
| **Trung bình 6 tiêu chí** | **3,32 ± 0,95** | **4,53 ± 0,77** | **3,97 ± 0,95** | — | — |

Cả sáu tiêu chí đều cho khác biệt có ý nghĩa thống kê mạnh (p < 0,001) khi so `image_only` với `json_only` hoặc với `image+json`; với sáu kiểm định đồng thời, ngưỡng Bonferroni tương ứng là p < 0,0083, vẫn được thỏa mãn ở tất cả sáu tiêu chí. Độ lệch chuẩn cao nhất rơi vào `traffic_sign_rule` ở chế độ `image_only` (± 1,51) — hợp lý vì đây là tiêu chí phụ thuộc nhiều vào việc ảnh có hay không có biển báo dễ nhận biết bằng mắt, một yếu tố dao động mạnh giữa các ảnh; độ lệch chuẩn thấp nhất rơi vào `lane_ego_position` ở chế độ `json_only` (± 0,76), phù hợp với việc thông tin vị trí làn ego được cấp sẵn dưới dạng số liệu chính xác trong JSON, ít phụ thuộc vào khả năng suy luận thị giác vốn dao động nhiều hơn giữa các ảnh.

Kết luận nhất quán nhất, được cả ba judge độc lập đồng thuận không ngoại lệ, là chế độ `image_only` luôn đạt điểm thấp nhất. Sau khi khắc phục các lỗi hệ thống ở tầng perception (mục 4.1) và hoàn thiện tầng reasoning (mục 4.4), JSON ngữ nghĩa cải thiện rõ rệt chất lượng khuyến nghị lái xe so với chỉ dùng ảnh.

Tuy nhiên, kết luận cần được nêu có sắc thái ở một điểm: thứ hạng giữa `json_only` và `image+json` phụ thuộc vào judge được sử dụng — một judge nghiêng về JSON đơn thuần, một judge nghiêng về kết hợp, một judge coi hai chế độ là ngang nhau — nên không có câu trả lời tuyệt đối cho câu hỏi "kết hợp ảnh và JSON có tốt hơn chỉ dùng JSON hay không". Đây chính là giá trị của phương pháp luận đa-judge: nếu chỉ sử dụng một judge duy nhất, nghiên cứu có nguy cơ báo cáo nhầm một kết luận "chắc chắn" trong khi thực chất đó chỉ là đặc thù riêng của judge đó.

## 4.6. Kiểm chứng độ tin cậy của phương pháp đánh giá

Với 120 cặp điểm — 20 ảnh nhân 6 tiêu chí, mỗi cặp gồm một điểm của con người và một điểm của judge trên cùng ảnh/tiêu chí — ba chỉ số đồng thuận được định nghĩa như sau: Đồng thuận tuyệt đối bằng tỉ lệ số cặp có |điểm người − điểm judge| = 0; Đồng thuận trong sai số ≤1 bằng tỉ lệ số cặp có |điểm người − điểm judge| ≤ 1; Tương quan Pearson r được tính trên hai dãy 120 điểm tương ứng của người và của judge.

**Gemini so với con người** (N=20, 120 cặp điểm): đồng thuận tuyệt đối 44/120 = 36,7%, đồng thuận trong sai số ≤1 điểm 95/120 = 79,2%, tương quan Pearson 0,427.

Cần thận trọng khi đối chiếu con số này với MT-Bench: nghiên cứu đó báo cáo GPT-4 đạt 85% đồng thuận với con người trên một tác vụ so sánh cặp nhị phân, chỉ tính trên các cặp không hòa [5] — khác về bản chất so với việc chấm điểm tuyệt đối trên thang 1–5 của đề tài này. Một quyết định nhị phân đúng/sai không cùng độ khó với một mức độ khoan dung ±1 điểm trên thang 5 mức, vốn có baseline ngẫu nhiên cao hơn hẳn. Do khác loại tác vụ, khác định nghĩa đồng thuận, và khác quy mô kiểm chứng (N=20 so với hàng nghìn cặp), 79,2% và 85% không phải hai con số đối sánh trực tiếp được — việc chúng gần nhau về mặt số học không tự nó là bằng chứng cho độ tin cậy của Gemini, và luận văn không dùng đây làm căn cứ chính.

Bằng chứng vững chắc hơn, và là căn cứ chính cho quyết định dùng Gemini làm judge chính của đề tài, đến từ chính nội bộ nghiên cứu: Gemini đạt mức đồng thuận và tương quan cao hơn rõ rệt so với hai judge còn lại, được kiểm chứng theo đúng cùng phương pháp, cùng thang đo, cùng mẫu N=20 (Bảng 4.8) — một phép so sánh công bằng, cùng đơn vị đo, không phụ thuộc vào việc đối chiếu với một nghiên cứu khác dùng tác vụ khác.

**GPT-5 Mini so với con người** (cùng N=20): đồng thuận tuyệt đối 23,3%, trong sai số ≤1 điểm 62,5%, tương quan 0,194 — thấp hơn Gemini ở cả ba chỉ số, củng cố quyết định dùng Gemini làm judge chính.

**DeepSeek so với con người** (cùng N=20, 120 cặp điểm): đồng thuận tuyệt đối 25,8%, trong sai số ≤1 điểm 55,0%, tương quan 0,143 — thấp nhất trong ba judge, với tương quan Pearson gần như không có ý nghĩa thống kê thực tế trên cỡ mẫu này. Điểm đáng chú ý là DeepSeek có xu hướng chấm thấp hơn con người một cách hệ thống — chênh lệch trung bình người trừ DeepSeek là +1,21, lớn hơn nhiều so với Gemini và GPT — với nhiều trường hợp con người chấm 4–5 điểm nhưng DeepSeek chỉ chấm 1–2 điểm, đặc biệt ở hai tiêu chí `traffic_sign_rule` và `lane_ego_position`. Có thể DeepSeek diễn giải rubric khắt khe hơn, hoặc ít khoan dung hơn với các suy luận gián tiếp không có bằng chứng tường minh trong JSON.

**Bảng 4.8.** Xếp hạng độ tin cậy của ba judge khi đối chiếu với đánh giá của con người (N=20).

| Judge | Đồng thuận tuyệt đối | Trong sai số ≤1 | Tương quan Pearson |
|---|---|---|---|
| Gemini | **36,7%** | **79,2%** | **0,427** |
| DeepSeek | 25,8% | 55,0% | 0,143 |
| GPT-5 Mini | 23,3% | 62,5% | 0,194 |

Gemini vượt trội rõ rệt ở cả ba chỉ số so với hai judge còn lại, củng cố quyết định dùng Gemini làm judge chính cho toàn bộ các kết luận trọng tâm của đề tài (mục 4.4, 4.5); GPT-5 Mini và DeepSeek chỉ đóng vai trò tham khảo và đối chiếu chéo (mục 4.5).

Một phát hiện phương pháp luận đáng chú ý là tương quan giữa GPT và Gemini với nhau (0,511) còn cao hơn tương quan của mỗi judge với con người (0,427 và 0,194) — minh chứng trực tiếp rằng hai judge AI có xu hướng đồng ý với nhau nhiều hơn đồng ý với con người, có thể do cùng chia sẻ một mức độ nghiêm khắc nhất định khác với người chấm không chuyên. Tương quan giữa DeepSeek và Gemini cũng đạt 0,395, vẫn cao hơn tương quan DeepSeek-người (0,143), củng cố thêm cùng một phát hiện. Đây là lý do phương pháp luận của đề tài dùng đúng một judge cố định (Gemini) cho các so sánh chính, và dùng độ đồng thuận với con người — không phải độ đồng thuận giữa các judge — làm mốc chuẩn.

## 4.7. Hạn chế: rủi ro trùng lặp dữ liệu (data leakage)

200 ảnh đánh giá ở mục 4.1 được lấy ngẫu nhiên từ CULane, cùng nguồn dữ liệu mà mô hình phát hiện làn đường (`culane_res34.pth`) được pretrain, mà không đối chiếu với danh sách phân chia train/val/test chính thức, do bản dữ liệu cục bộ sử dụng không có sẵn thông tin này. Do đó, không loại trừ khả năng một phần ảnh đánh giá trùng với dữ liệu mà mô hình đã học qua, có thể khiến Accuracy và Precision tuyệt đối ở mục 4.1 lạc quan hơn khả năng tổng quát hóa thực tế. Hạn chế này không ảnh hưởng tới các so sánh tương đối — mức cải thiện trước/sau sửa lỗi, toàn bộ kết quả mục 4.4–4.6 — vì các so sánh này dùng chung một lần detect, chỉ khác ở bước xử lý hoặc mô hình phía sau. Kết quả ở mục 4.2, kiểm chứng trên dữ liệu real-life hoàn toàn độc lập, được thực hiện chính là để giảm thiểu rủi ro này.

## 4.8. Kiểm chứng khả năng tự nhận diện làn đường của VLM

Một câu hỏi đặt ra là: nếu không đi qua tầng UFLD-v2 và xử lý ngữ nghĩa, bản thân VLM (`ising-calibration-31b`) tự quan sát ảnh có nhận diện được ngữ nghĩa làn đường chính xác tới đâu? Để trả lời, một thực nghiệm bổ sung được thực hiện: gửi cho VLM duy nhất bức ảnh, không kèm bất kỳ JSON hay gợi ý nào, yêu cầu trả về JSON đúng schema `_brief.json` hiện tại (`lane_count`, `ego_lane`, `vehicle_offset`, `neighbor_lanes`, `road_shape`), trên cả hai bộ dữ liệu (CULane N=200, real-life N=200). Toàn bộ 200/200 ảnh ở cả hai bộ đều nhận được JSON hợp lệ.

**Bảng 4.9.** So sánh khả năng tự nhận diện ngữ nghĩa làn đường giữa pipeline UFLD-v2 và VLM.

| Bộ dữ liệu / Nhóm | Lane count Accuracy (Pipeline) | Lane count Accuracy (VLM) | Lane count MAE (Pipeline) | Lane count MAE (VLM) | Road shape bucket match (Pipeline) | Road shape bucket match (VLM) |
|---|---|---|---|---|---|---|
| CULane – Normal (N=176, có vạch kẻ) | **77,3%** | 54,5% | **0,273** | 0,477 | 84,1% | **95,5%** |
| CULane – Hard (N=24, không vạch kẻ) | 8,3% | **37,5%** | 1,958 | **0,792** | 20,8% | **91,7%** |
| CULane – Toàn bộ (N=200) | **69,0%** | 52,5% | **0,475** | 0,515 | 76,5% | **95,0%** |
| Real-life độc lập (N=200) | 50,5% | **53,5%** | 0,715 | **0,510** | 53,0% | **69,5%** |

Phát hiện chính từ Bảng 4.9 là pipeline chuyên biệt (UFLD-v2) chỉ vượt trội rõ rệt VLM ở đúng một điều kiện: ảnh CULane có vạch kẻ, đúng domain mà nó được pretrain. Ở hai điều kiện còn lại — CULane không vạch kẻ, và toàn bộ dữ liệu real-life thuộc domain khác CULane — VLM tự nhận diện đạt hoặc vượt pipeline ở mọi chỉ số, đặc biệt rõ ở road shape (phân loại thẳng/cong), nơi VLM vượt trội pipeline ở cả bốn dòng của bảng. Điều này gợi ý rằng ưu thế của pipeline một phần đến từ việc cùng domain với dữ liệu huấn luyện, không chỉ từ bản chất kiến trúc của một detector chuyên biệt: pipeline trở nên giòn và dễ vỡ khi ra khỏi đúng vùng an toàn đó, trong khi VLM tổng quát — không được tinh chỉnh riêng cho bài toán làn đường — lại ổn định hơn.

## 4.9. Bàn luận: cơ chế đóng góp thực sự của JSON ngữ nghĩa

Mục 4.8 cho thấy VLM tự nhận diện làn đường không hề yếu — vậy vì sao `json_only`/`image+json` vẫn vượt `image_only` rõ rệt ở mục 4.5? Giả thuyết được đề tài đề xuất: JSON không chỉ bù đắp năng lực thị giác còn thiếu, mà chủ yếu đóng vai trò **khung đỡ (scaffolding)** cho suy luận và trình bày trong một tác vụ ghép nhiều bước. Ba căn cứ ủng hộ giả thuyết này:

- **Độ phức tạp tác vụ khác nhau.** Mục 4.8 chỉ yêu cầu một việc — trích xuất số liệu theo schema cứng; `image_only` ở mục 4.5 dồn ba việc vào một lượt sinh duy nhất (tự nhận diện, tự suy luận, tự viết đúng cấu trúc ba phần theo một prompt dài — mục 3.5). Năng lực tốt ở một tác vụ hẹp không đảm bảo chất lượng khi tác vụ đó chỉ là một bước ẩn trong chuỗi phức tạp hơn.
- **Prompt không tương đương.** `json_only` cấp sẵn dữ liệu có cấu trúc để tham chiếu trực tiếp khi viết câu trả lời; `image_only` chỉ yêu cầu quan sát ảnh chung chung, ít khung đỡ hơn hẳn.
- **Judge chấm văn phong, không đối chiếu ground truth.** Một câu trả lời trích số liệu cụ thể ("làn 2/3, lệch 19,3%") dễ được đánh giá là có căn cứ và tự tin hơn, dù độ chính xác thực tế của con số đó chưa chắc cao hơn — đúng thiên vị phong cách viết mà MT-Bench đã ghi nhận như hạn chế cố hữu của LLM-as-judge [5] (mục 2.4), lý do đề tài kiểm chứng bằng đối chiếu con người thay vì tin tuyệt đối vào judge (mục 4.6).

Cách diễn giải này không làm suy yếu kết luận RQ3 — JSON vẫn cải thiện chất lượng khuyến nghị, kiểm chứng bởi ba judge độc lập — mà làm rõ hơn cơ chế: JSON giúp câu trả lời mạch lạc và có căn cứ hơn trong một tác vụ ghép nhiều bước, không đơn thuần vì VLM "không nhìn được đường". Đây là suy luận dựa trên bằng chứng gián tiếp — hai thực nghiệm dùng hai prompt khác độ phức tạp — chưa qua một thực nghiệm đối chứng trực tiếp (cùng độ phức tạp prompt, chỉ khác có/không JSON); đây là một hướng mở rộng ở mục 5.4.

**Tóm tắt chương.** Chương này đã trình bày kết quả thực nghiệm cho cả năm câu hỏi nghiên cứu: độ chính xác của module hiểu làn đường và biển báo (RQ1, RQ2), lựa chọn mô hình suy luận (RQ4), đóng góp của JSON ngữ nghĩa cùng kiểm chứng độ tin cậy của phương pháp đánh giá (RQ3, RQ5), và một thực nghiệm bổ sung làm rõ cơ chế đóng góp thực sự của JSON. Chương 5 tiếp theo tổng kết các đóng góp, trả lời trực tiếp từng câu hỏi nghiên cứu, thảo luận hạn chế và đề xuất hướng phát triển tiếp theo.

---

# CHƯƠNG 5. KẾT LUẬN

## 5.1. Tóm tắt đóng góp

Đề tài xây dựng và kiểm chứng định lượng một pipeline hoàn chỉnh cho bài toán hiểu ngữ nghĩa làn đường và biển báo giao thông hỗ trợ ra quyết định lái xe bằng LLM, trên hai bộ dữ liệu chuẩn phổ biến (CULane, TT100K). Tầng suy luận theo hướng tiếp cận training-free — khác với các hệ VLM lái xe end-to-end (DriveGPT4 [2], DriveLM [3], LMDrive [4]) vốn đòi hỏi huấn luyện quy mô lớn (mục 2.3, 2.5) — trong khi tầng perception biển báo có một bước tinh chỉnh YOLOv8n quy mô nhẹ trên TT100K (mục 3.2). Các kết quả chính, có số liệu định lượng cụ thể, gồm:

1. **Module hiểu làn đường** đạt Accuracy 77,3% trên ảnh có vạch kẻ rõ (N=176/200), tổng quát hóa tốt sang dữ liệu độc lập tự thu thập (Precision 99,4%, Ego lane Accuracy 86,5%, N=200), nhưng giảm mạnh còn 8,3% trên 24 ảnh không có vạch kẻ rõ — một giới hạn cố hữu của detector dựa trên vạch kẻ (mục 4.1).
2. **Minh chứng cho tầm quan trọng của tầng diễn giải ngữ nghĩa**: lỗi off-by-one phát hiện trong quá trình xây dựng tầng chuyển đổi ngữ nghĩa khiến Accuracy ban đầu chỉ đạt 11,1%, dù bản thân UFLD-v2 đã đạt F1 = 76,0% ở tầng phát hiện [1]. Việc sửa lỗi này tự nó không phải một đóng góp thuật toán, nhưng là bằng chứng thực nghiệm cho luận điểm rằng chất lượng của một detector không tự động đảm bảo chất lượng của hệ hỗ trợ quyết định — cho thấy giá trị của việc đầu tư kiểm chứng kỹ lưỡng tầng diễn giải ngữ nghĩa (mục 2.1, 4.1).
3. **Module biển báo** đạt hiệu quả thực sự khi dữ liệu đủ dày (Precision/Recall 60,9% trên dữ liệu real-life), nhưng bị giới hạn trên CULane do đặc thù dataset thưa biển báo (6% ảnh có detection).
4. **JSON ngữ nghĩa cải thiện rõ rệt chất lượng khuyến nghị lái xe**: Gemini 3,32 → 4,53/5, tương đương +36%, có kiểm chứng nhất quán bởi ba judge độc lập trên N=200 (mục 4.5).
5. **Phương pháp đánh giá LLM-as-a-judge có kiểm chứng**: đối chiếu với con người đạt 79,2% đồng thuận trong sai số ≤1 (N=20), và đối chiếu chéo ba judge cùng phương pháp xác định Gemini vượt trội rõ rệt GPT-5 Mini và DeepSeek ở cả ba chỉ số đồng thuận với con người (mục 4.6) — căn cứ chính cho việc chọn Gemini làm judge chính, thay vì đối sánh trực tiếp với các nghiên cứu LLM-as-a-judge khác vốn dùng tác vụ và thang đo khác biệt về bản chất [5].
6. **Làm rõ cơ chế đóng góp của JSON ngữ nghĩa**: một kiểm chứng bổ sung cho thấy VLM tự nhận diện làn đường từ ảnh thô không hề yếu, thậm chí vượt pipeline UFLD-v2 khi thiếu vạch kẻ hoặc trên dữ liệu ngoài domain (mục 4.8), nên JSON cải thiện chất lượng khuyến nghị chủ yếu nhờ vai trò khung đỡ cho suy luận và trình bày trong một tác vụ ghép nhiều bước, không chỉ vì bù đắp năng lực cảm nhận thị giác còn thiếu (mục 4.9).

**Ý nghĩa thực tiễn.** Các kết quả trên cho thấy một hệ hỗ trợ quyết định lái xe có khả năng diễn giải bằng ngôn ngữ tự nhiên có thể được xây dựng với chi phí thấp: tầng suy luận dùng VLM miễn phí qua API, không cần huấn luyện lại; tầng perception biển báo chỉ cần một bước tinh chỉnh nhẹ trên một mô hình nhỏ (YOLOv8n, khoảng 3,2 triệu tham số) thay vì thu thập dữ liệu và huấn luyện một hệ end-to-end quy mô lớn. Kết quả này phù hợp làm nền tảng cho các ứng dụng dashcam hoặc hộp đen thông minh chi phí thấp, hoặc làm điểm khởi đầu để mở rộng sang dữ liệu giao thông Việt Nam mà không cần xây dựng lại từ đầu — chỉ cần tinh chỉnh nhẹ ở tầng perception làn đường và biển báo (mục 5.4).

## 5.2. Trả lời các câu hỏi nghiên cứu

- **RQ1–RQ2**: đã được trả lời định lượng đầy đủ ở mục 4.1–4.3.
- **RQ3**: JSON ngữ nghĩa cải thiện chất lượng khuyến nghị lái xe so với chỉ dùng ảnh — kết luận có kiểm chứng vững chắc (mục 4.5), với cơ chế đóng góp được làm rõ thêm ở mục 4.8–4.9.
- **RQ4**: `ising-calibration-31b` là lựa chọn phù hợp nhất trong phạm vi mô hình khảo sát, dựa trên độ tin cậy, tuân thủ cấu trúc và chất lượng nội dung (mục 4.4).
- **RQ5**: LLM-as-a-judge (Gemini) đạt độ tin cậy chấp nhận được khi đối chiếu với con người, tốt hơn hai judge thay thế đã thử nghiệm — GPT-5 Mini, DeepSeek — ở cả ba chỉ số đồng thuận (mục 4.6).

## 5.3. Hạn chế

- **Module hiểu làn đường ở tầng pipeline thị giác máy tính phụ thuộc mạnh vào vạch kẻ đường và vào việc cùng domain với dữ liệu huấn luyện.** Trên 24/200 ảnh CULane thuộc các tình huống không có vạch kẻ rõ, Accuracy số làn giảm từ 77,3% xuống còn 8,3%, dù Precision vẫn đạt 100% (mục 4.1). Kiểm chứng bổ sung ở mục 4.8 cho thấy đây là hạn chế của riêng pipeline thị giác máy tính, không phải của cách tiếp cận nói chung: VLM tự nhận diện trực tiếp từ ảnh không chia sẻ đúng điểm yếu này, thậm chí vượt trội pipeline ở chính hai điều kiện đó — mở ra hướng thiết kế hybrid (mục 5.4).
- Rủi ro trùng lặp dữ liệu (data leakage) trên dữ liệu CULane (mục 4.7), giảm thiểu một phần bằng kiểm chứng độc lập trên dữ liệu real-life.
- So sánh mô hình LLM và judge giới hạn trong các lựa chọn miễn phí, chi phí thấp, chưa mở rộng sang các phiên bản thương mại lớn hơn hoặc mới hơn của các họ mô hình đã thử (Gemini, GPT, DeepSeek) hay các mô hình khác như Claude.
- Module biển báo trên CULane bị giới hạn bởi mật độ dữ liệu thưa của bản thân dataset.

## 5.4. Hướng phát triển tiếp theo

Ba hướng sau được sắp xếp theo mức độ ưu tiên, từ tác động thực tiễn cao nhất đến các cải tiến kỹ thuật bổ sung.

**1. Mở rộng sang dữ liệu Việt Nam, kết hợp kiến trúc hybrid.** Hướng ưu tiên cao nhất là áp dụng và đánh giá lại pipeline trên dữ liệu giao thông Việt Nam thực tế — vạch kẻ đường và biển báo theo quy chuẩn QCVN, mật độ xe máy cao, hành vi giao thông khác biệt; bước đầu đã có tín hiệu tích cực qua bộ dữ liệu real-life tự thu thập (mục 4.2). Vì giao thông Việt Nam có nhiều tình huống thiếu vạch kẻ rõ — đúng điểm yếu của pipeline UFLD-v2 (mục 4.1, 5.3) — hướng này nên đi kèm một kiến trúc hybrid: giữ UFLD-v2 làm nguồn chính, tự động chuyển sang kết quả tự nhận diện của VLM (mục 4.8) khi pipeline trả về tín hiệu thấp (`lane_count=0`, độ tin cậy thấp).

**2. Củng cố phương pháp luận đánh giá.** Hai việc cụ thể: (a) một thực nghiệm đối chứng trực tiếp cho giả thuyết "khung đỡ" ở mục 4.9 — chạy `image_only` với một prompt hai bước, buộc VLM tự trích xuất JSON có cấu trúc trước khi viết khuyến nghị, rồi so sánh với `json_only` gốc; nếu khoảng cách thu hẹp, giả thuyết được củng cố; (b) mở rộng kiểm chứng đồng thuận người–AI vượt quy mô N=20 hiện tại, có thể áp dụng khung lấy mẫu thích ứng của Kim [15] thay vì chọn mẫu ngẫu nhiên.

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

[34] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)*, 2020.
