# [TÊN TRƯỜNG] — [TÊN KHOA]

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

Để hoàn thành chương trình đào tạo Thạc sĩ và hoàn thiện công trình nghiên cứu này, bên cạnh những nỗ lực của bản thân, tôi đã nhận được sự dạy giỗ, hướng dẫn và động viên vô cùng to lớn của các thầy, cô, nhà trường, bạn bè và gia đình.
Trước tiên, tôi xin bày tỏ lòng biết ơn chân thành đến giảng viên hướng dẫn luận văn của mình - Tiến sĩ Đoàn Nhật Quang, thầy là người đã truyền cảm hứng và định hướng cho tôi hình thành nên ý tưởng của đề tài nghiên cứu này. Thầy đã dành nhiều thời gian chỉ dẫn, truyền tải kiến thức đồng thời đánh giá, góp ý trong suốt quá trình thực hiện đề tài. Những chỉ bảo tâm huyết của thầy không chỉ giúp tôi hoàn thiện bài luận văn mà còn là hành trang quý giá cho con đường phát triển chuyên môn của tôi sau này.
Tôi xin chân thành cảm ơn đội ngũ giảng viên, nhân viên tại Trường Kinh doanh và Công nghệ FPT (FSB) vì đã tạo ra một môi trường giáo dục chuyên nghiệp, cởi mở để tôi có thể theo học những kiến thức chuyên môn vững chắc và tham gia những buổi hội thảo hữu ích. Tôi cũng xin gửi lời cảm ơn đến các bạn bè, đồng nghiệp đã luôn sẵn sàng chia sẻ kiến thức, thảo luận và đồng hành cùng tôi trong suốt quá trình học tập.
Cuối cùng tôi xin dành trọn tình cảm và lòng biết ơn vô hạn tới cha mẹ, anh chị em trong gia đình. Gia đình luôn là điểm tựa vững chắc nhất, mang lại sự bình yên, niềm tin và luôn tạo điều kiện tốt nhất để tôi kiên trì nỗ lực vượt qua khó khăn, hoàn thành ước mơ học tập của mình.
Mặc dù đã có nhiều cố gắng trong quá trình nghiên cứu và trình bày, song công việc này của tôi không tránh khỏi những hạn chế nhất định. Tôi rất mong nhận được những ý kiến đóng góp quý báu từ Quý Thầy/Cô trong Hội đồng để công trình nghiên cứu này được hoàn thiện hơn.

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

*(Số trang sẽ được bổ sung khi chuyển bản thảo sang định dạng trình bày cuối cùng (.docx/.pdf) theo đúng biểu mẫu của cơ sở đào tạo.)*

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
| 4 | Bảng 4.4 | So sánh chi tiết chất lượng nội dung giữa `nemotron-nano-8b` và `ising-calibration-31b` (Mean ± SD, kiểm định thống kê) |
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

Các hệ thống hỗ trợ lái xe (ADAS) hiện nay thường dừng lại ở tầng nhận diện cấp thấp (tọa độ điểm ảnh, bounding box), chưa chuyển hóa được thành ngữ nghĩa giao thông mà con người có thể hiểu và tin tưởng. Luận văn này xây dựng và kiểm chứng định lượng một pipeline bốn tầng (Perception – Semantic Analysis – LLM Reasoning – Evaluation) kết hợp mô hình phát hiện làn đường UFLD-v2 (dùng nguyên trạng ở dạng pretrained), mô hình phát hiện biển báo YOLOv8n (tự tinh chỉnh trên TT100K), một tầng chuyển đổi ngữ nghĩa có cấu trúc (JSON) tự thiết kế, và một mô hình ngôn ngữ lớn đa phương thức (VLM) để sinh khuyến nghị lái xe bằng ngôn ngữ tự nhiên. Tầng suy luận (VLM) theo hướng tiếp cận training-free, không tinh chỉnh lại mô hình; chi phí huấn luyện của toàn hệ thống do đó chỉ giới hạn ở một bước tinh chỉnh YOLOv8n quy mô nhẹ, thay vì huấn luyện một VLM/LLM chuyên biệt.

Trên bộ dữ liệu CULane (N=200 ảnh, gán nhãn tay đầy đủ), module hiểu làn đường đạt Accuracy 69,0% tổng thể và 77,3% trên nhóm ảnh có vạch kẻ đường rõ, sau khi phát hiện và khắc phục một lỗi lệch đơn vị (off-by-one) từng khiến Accuracy ban đầu chỉ đạt 11,1%. Kết quả tổng quát hóa tốt sang một bộ dữ liệu real-life độc lập tự thu thập (N=200), với Precision số làn đạt 99,4%. Câu hỏi nghiên cứu trung tâm — liệu thông tin ngữ nghĩa có cấu trúc (JSON) có cải thiện chất lượng khuyến nghị lái xe của VLM so với chỉ dùng ảnh hay không — được trả lời bằng thực nghiệm định lượng trên N=200 ảnh, chấm điểm độc lập bởi ba mô hình judge (Gemini, GPT-5 Mini, DeepSeek) trên cùng một rubric sáu tiêu chí: cả ba judge đồng thuận rằng chế độ chỉ dùng ảnh luôn đạt điểm thấp nhất, trong khi chế độ có JSON cải thiện điểm số tới 36% (Gemini: 3,32 → 4,53/5). Độ tin cậy của phương pháp LLM-as-a-judge được kiểm chứng bằng đối chiếu với đánh giá của con người (N=20), đạt mức đồng thuận 79,2% trong sai số ≤1 điểm — một mức đồng thuận cao, và vượt trội rõ rệt so với hai judge thay thế được kiểm chứng theo cùng phương pháp (GPT-5 Mini, DeepSeek).

Một thực nghiệm bổ sung yêu cầu VLM tự nhận diện ngữ nghĩa làn đường trực tiếp từ ảnh (không qua tầng UFLD-v2) cho thấy năng lực cảm nhận thị giác của VLM không hề yếu — thậm chí vượt trội pipeline chuyên biệt khi thiếu vạch kẻ đường hoặc trên dữ liệu ngoài domain huấn luyện. Phát hiện này dẫn tới một điều chỉnh quan trọng trong cách diễn giải kết quả trung tâm: JSON ngữ nghĩa cải thiện chất lượng khuyến nghị chủ yếu nhờ vai trò khung đỡ (scaffolding) cho việc suy luận và trình bày trong một tác vụ ghép nhiều bước, không đơn thuần vì bù đắp năng lực cảm nhận thị giác còn thiếu của VLM. Luận văn cũng thảo luận các hạn chế đã kiểm chứng (rủi ro trùng lặp dữ liệu, một điểm không nhất quán nhỏ giữa thiết kế và triển khai JSON gửi cho LLM, giới hạn dữ liệu biển báo trên CULane) và đề xuất hướng phát triển: kiến trúc hybrid kết hợp pipeline CV với cơ chế fallback sang VLM, và mở rộng sang dữ liệu giao thông Việt Nam.

**Từ khóa**: hiểu ngữ nghĩa giao thông, mô hình ngôn ngữ lớn đa phương thức, phát hiện làn đường, phát hiện biển báo, LLM-as-a-judge, hỗ trợ ra quyết định lái xe.

---

# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh và động lực

Các hệ thống hỗ trợ lái xe hiện đại (ADAS) thường dựa vào các mô-đun nhận diện cấp thấp (low-level perception) như phát hiện làn đường, phát hiện biển báo và đèn tín hiệu. Tuy nhiên, đầu ra của các mô-đun này — tọa độ điểm ảnh, bounding box, class ID — chưa đủ để hỗ trợ ra quyết định lái xe theo cách con người có thể hiểu và tin tưởng được. Cần một tầng trung gian chuyển đổi thông tin nhận diện thô thành **ngữ nghĩa giao thông** (semantic understanding): xe đang ở làn nào, có bị lệch tâm không, còn bao nhiêu làn lân cận, đường đang thẳng hay cong, có biển báo hay luật nào cần tuân thủ.

Sự phát triển gần đây của mô hình ngôn ngữ lớn đa phương thức (Vision-Language Model — VLM) mở ra một khả năng mới: kết hợp thông tin thị giác (ảnh) và thông tin có cấu trúc (JSON ngữ nghĩa) để sinh ra khuyến nghị lái xe bằng ngôn ngữ tự nhiên, có giải thích, có căn cứ. Câu hỏi nghiên cứu cốt lõi của đề tài là: *thông tin ngữ nghĩa có cấu trúc (JSON) có thực sự cải thiện chất lượng kết quả đầu ra của VLM so với chỉ dùng ảnh thô hay không, và cải thiện tới mức nào?*

## 1.2. Mục tiêu nghiên cứu

Đề tài tập trung vào hai thành phần ngữ nghĩa cốt lõi của tình huống giao thông:

1. **Hiểu làn đường** (lane understanding): số làn, làn ego, độ lệch tâm xe, làn lân cận, hình dạng đường (thẳng/cong).
2. **Hiểu biển báo giao thông** (traffic sign understanding): phát hiện và phân loại biển báo giao thông.

Hai thành phần này được chuyển hóa thành ngữ nghĩa có cấu trúc, kết hợp với ảnh gốc, đưa vào mô hình ngôn ngữ lớn để sinh khuyến nghị lái xe, và được đánh giá bằng phương pháp luận định lượng đáng tin cậy.

## 1.3. Phạm vi dữ liệu

Để đảm bảo tính khách quan, khả năng tái lập, và có thể đối sánh với các nghiên cứu khác, đề tài sử dụng hai bộ dữ liệu công khai, phổ biến, đã được cộng đồng nghiên cứu kiểm chứng và có chung một đặc điểm giao thông - giao thông đô thị Trung Quốc:

- **CULane** — benchmark chuẩn cho bài toán phát hiện làn đường, dùng để đánh giá module hiểu làn đường và làm dữ liệu chính cho toàn bộ pipeline.
- **TT100K** (Tsinghua-Tencent 100K) — benchmark chuẩn cho bài toán phát hiện biển báo giao thông, dùng để huấn luyện và đánh giá module biển báo.

Việc lựa chọn hai bộ dữ liệu phổ biến, có sẵn này — thay vì thu thập riêng dữ liệu Việt Nam ngay từ đầu — nhằm chứng minh tính hiệu quả và đúng đắn của pipeline trên dữ liệu đã được chuẩn hóa, có thể đối sánh khách quan với các công trình khác, trước khi mở rộng sang bối cảnh giao thông Việt Nam. Hướng mở rộng này được trình bày ở Chương 5 (mục 5.4).

## 1.4. Câu hỏi nghiên cứu

- **RQ1**: Module hiểu làn đường (dựa trên UFLD-v2 và xử lý ngữ nghĩa) đạt độ chính xác bao nhiêu khi đối chiếu với nhãn tay, và độ chính xác này có tổng quát hóa được sang dữ liệu độc lập không?
- **RQ2**: Module hiểu biển báo (dựa trên YOLOv8 và TT100K) đạt hiệu quả thế nào, và những giới hạn nào cần lưu ý khi áp dụng trên các bộ dữ liệu khác nhau?
- **RQ3**: Thông tin JSON ngữ nghĩa có cải thiện chất lượng khuyến nghị lái xe của VLM so với chỉ dùng ảnh hay không?
- **RQ4**: Trong các mô hình VLM có thể tiếp cận được (miễn phí, chi phí thấp), mô hình nào phù hợp nhất cho bài toán này, xét trên độ tin cậy, chất lượng và khả năng vận hành?
- **RQ5**: Phương pháp đánh giá bằng LLM-as-a-judge có đáng tin cậy không, và có thể định lượng độ tin cậy đó như thế nào?

## 1.5. Đóng góp chính

Cần làm rõ trước phạm vi đóng góp: đề tài không đề xuất một kiến trúc phát hiện làn đường hay biển báo mới để cạnh tranh với UFLD-v2 (F1 = 76,0% trên CULane, backbone ResNet-34) [1], cũng không đề xuất một hệ VLM lái xe end-to-end quy mô lớn như DriveGPT4 [2], DriveLM [3] hay LMDrive [4] — các hệ này đòi hỏi huấn luyện hoặc tinh chỉnh (fine-tune) trên tập dữ liệu lái xe quy mô lớn (nuScenes, CARLA...) cùng hạ tầng tính toán đáng kể. Đóng góp của đề tài nằm ở tầng tích hợp, chuyển đổi ngữ nghĩa và phương pháp luận đánh giá. Riêng tầng suy luận (LLM Reasoning) theo hướng tiếp cận training-free, chi phí thấp — sử dụng VLM miễn phí qua API, không tinh chỉnh lại mô hình (mục 3.6); tầng perception biển báo có một bước tinh chỉnh YOLOv8n quy mô nhẹ trên TT100K (mục 3.2), nhỏ hơn nhiều bậc về chi phí tính toán so với việc huấn luyện/tinh chỉnh một VLM hoặc LLM trên dữ liệu lái xe quy mô lớn như ở các hệ so sánh. Cụ thể:

1. **Một tầng chuyển đổi ngữ nghĩa được kiểm chứng định lượng đầy đủ**: chuyển đổi từ output thô của mô hình phát hiện làn đường (UFLD-v2) sang ngữ nghĩa cấp quyết định (số làn, làn ego, độ lệch tâm, hình dạng đường), đạt Accuracy 77,3% trên ảnh có vạch kẻ rõ (N=176/200) và tổng quát hóa tốt sang dữ liệu độc lập tự thu thập (N=200, Precision 99,4%, Ego lane Accuracy 86,5%) — không dừng lại ở kiểm chứng trên một bộ dữ liệu duy nhất.
2. **Minh chứng định lượng cho tầm quan trọng của tầng diễn giải ngữ nghĩa**: quá trình xây dựng và kiểm chứng tầng chuyển đổi ngữ nghĩa (đóng góp 1) đã phát hiện một lỗi tích hợp cụ thể — lệch đơn vị (off-by-one) trong công thức suy ra số làn từ số đường biên — khiến Accuracy ban đầu chỉ đạt 11,1%, dù bản thân UFLD-v2 đã đạt F1 = 76,0% ở tầng phát hiện. Bản thân việc sửa lỗi này không phải một đóng góp về mặt thuật toán, nhưng là bằng chứng thực nghiệm cụ thể cho một luận điểm phương pháp luận quan trọng: một mô hình phát hiện tốt không tự động đảm bảo một hệ thống hỗ trợ quyết định đúng — sai số hoàn toàn có thể nằm ở tầng diễn giải ngữ nghĩa phía sau, tầng mà các nghiên cứu tập trung cải thiện detector thường bỏ qua. Đây chính là lý do việc xây dựng và kiểm chứng kỹ lưỡng tầng chuyển đổi ngữ nghĩa (đóng góp 1) có giá trị thực tiễn, không thể xem là một bước phụ trợ hiển nhiên đúng.
3. **Một phương pháp luận đánh giá LLM-as-a-judge được kiểm chứng độ tin cậy cao** cho một bài toán ứng dụng cụ thể, thay vì áp dụng "nguyên trạng" như các benchmark tổng quát: đối chiếu với đánh giá của con người (N=20) và đối chiếu đa-judge (Gemini, GPT-5 Mini, DeepSeek) trên cùng một rubric. Gemini đạt mức đồng thuận cao nhất trong ba judge (79,2% trong sai số ≤1 điểm), phù hợp với tiền lệ trong y văn rằng LLM-as-a-judge có thể đạt độ tin cậy tiệm cận con người trong điều kiện phù hợp [5] (mục 2.4 và 4.6 thảo luận chi tiết hơn về vấn đề này).
4. **Kết quả thực nghiệm định lượng cho RQ3** (N=200, đối chiếu bởi ba judge độc lập): JSON ngữ nghĩa cải thiện chất lượng khuyến nghị lái xe rõ rệt so với chỉ dùng ảnh (Gemini: 3,32 → 4,53/5, tương đương +36%; cả 3 judge đều nhất quán kết quả chỉ dùng ảnh luôn thấp nhất).

**Ý nghĩa thực tiễn**. Khác với các hệ VLM/VLA end-to-end đòi hỏi dữ liệu lái xe quy mô lớn và hạ tầng huấn luyện — khó khả thi đối với một đề tài thạc sĩ hoặc một đơn vị nghiên cứu vừa và nhỏ — pipeline được xây dựng trong luận văn này chứng minh rằng một hệ hỗ trợ quyết định có khả năng diễn giải bằng ngôn ngữ tự nhiên, chi phí triển khai thấp, có thể được xây dựng ngay từ các mô hình VLM sẵn có. Kết quả này phù hợp làm nền tảng cho các ứng dụng dashcam hoặc hộp đen thông minh chi phí thấp, hoặc làm điểm khởi đầu để mở rộng sang dữ liệu giao thông Việt Nam (mục 5.4) mà không cần thu thập và huấn luyện lại từ đầu.

## 1.6. Cấu trúc luận văn

Chương 2 trình bày tổng quan các công trình liên quan, gồm các hướng nghiên cứu về phát hiện làn đường, phát hiện biển báo, mô hình ngôn ngữ lớn đa phương thức cho lái xe, và phương pháp luận LLM-as-a-judge. Chương 3 trình bày phương pháp luận: kiến trúc hệ thống, dữ liệu, thuật toán phân tích ngữ nghĩa, thiết kế prompt và phương pháp luận đánh giá. Chương 4 trình bày kết quả thực nghiệm và bàn luận, gồm chín mục — từ độ chính xác của từng module, kết quả trung tâm về đóng góp của JSON ngữ nghĩa, kiểm chứng độ tin cậy của phương pháp đánh giá, cho tới một thực nghiệm bổ sung và bàn luận làm rõ cơ chế đóng góp thực sự của JSON. Chương 5 tổng kết đóng góp, trả lời các câu hỏi nghiên cứu, thảo luận hạn chế và đề xuất hướng phát triển tiếp theo.

---

# CHƯƠNG 2. TỔNG QUAN VÀ CÁC CÔNG TRÌNH LIÊN QUAN

## 2.1. Phát hiện làn đường (Lane Detection)

Ultra-Fast-Lane-Detection-v2 (UFLD-v2) [1] là kiến trúc phát hiện làn đường tốc độ cao, biểu diễn bài toán phát hiện làn dưới dạng phân loại theo lưới hàng/cột (hybrid anchor-driven ordinal classification) thay vì hồi quy tọa độ trực tiếp hay phân đoạn ngữ nghĩa (semantic segmentation) như các phương pháp trước đó. Kiến trúc này đạt tốc độ suy luận trên 300 khung hình/giây ở phiên bản nhẹ, trong khi vẫn giữ độ chính xác cạnh tranh — F1 = 76,0% trên tập kiểm thử CULane với backbone ResNet-34, đúng biến thể pretrained được sử dụng trong đề tài (`culane_res34.pth`). CULane [6] là benchmark chuẩn cho bài toán này (88,9 nghìn ảnh huấn luyện, 9,7 nghìn ảnh kiểm định, 34,7 nghìn ảnh kiểm thử), với đặc điểm dữ liệu chủ yếu là các tình huống đường đô thị đa dạng: giao lộ, mật độ giao thông cao, điều kiện ánh sáng thay đổi.

Hai công trình khảo sát gần đây hệ thống hóa lĩnh vực này: [7] tổng hợp kiến trúc mạng và mục tiêu tối ưu của các phương pháp phát hiện vạch kẻ đường dựa trên deep learning; và [8], một nghiên cứu tổng quan hệ thống (systematic literature review) trên 102 công trình công bố giai đoạn 2018–2021, cho thấy xu hướng chuyển dịch từ mô hình hình học truyền thống sang deep learning trong toàn ngành.

Cần lưu ý rằng chỉ số F1 = 76,0% nêu trên là một metric ở tầng phát hiện điểm ảnh (point-wise localization theo IoU), khác về bản chất với các metric được sử dụng ở mục 4.1 của đề tài — Accuracy và MAE của số làn suy ra được, một đại lượng ngữ nghĩa cấp cao hơn, được tính từ output của UFLD-v2 qua một tầng xử lý hậu kỳ do đề tài tự xây dựng. Hai loại metric này không thể so sánh trực tiếp; điểm mấu chốt mà đề tài muốn làm rõ là: ngay cả khi tầng phát hiện đã đạt F1 cạnh tranh theo benchmark gốc, tầng diễn giải ngữ nghĩa phía sau vẫn có thể chứa lỗi nghiêm trọng, độc lập với chất lượng của bản thân detector (mục 4.1, 1.5).

## 2.2. Phát hiện biển báo giao thông (Traffic Sign Detection)

YOLOv8 (Ultralytics) là kiến trúc object detection một giai đoạn (single-stage), cân bằng tốt giữa tốc độ và độ chính xác, phù hợp cho ứng dụng thời gian thực. TT100K (Tsinghua-Tencent 100K) [9] là benchmark quy mô lớn cho bài toán phát hiện và phân loại biển báo giao thông tại Trung Quốc, gồm khoảng 100.000 ảnh và 30.000 đối tượng biển báo được gán nhãn, với hệ thống mã hóa biển báo chi tiết theo loại (biển cấm — "p", biển hiệu lệnh — "i", biển cảnh báo — "w", biển giới hạn tốc độ — "pl"/"il").

## 2.3. Mô hình ngôn ngữ lớn đa phương thức cho hỗ trợ quyết định lái xe

**Tiền thân trước kỷ nguyên LLM**. Hong và cộng sự [10] đã đặt nền móng cho ý tưởng mã hóa ngữ nghĩa cấp cao của tình huống giao thông thành một biểu diễn có cấu trúc (dạng lưới không gian) để mô hình học sâu suy luận hành vi lái xe — tuy nhiên công trình này dùng mạng convolutional thuần túy, không sinh được giải thích bằng ngôn ngữ tự nhiên.

**Các hệ VLM/LLM lái xe end-to-end quy mô lớn**. DriveGPT4 [2] sinh giải thích ngôn ngữ tự nhiên kèm dự đoán tín hiệu điều khiển theo hướng end-to-end; DriveLM [3] đóng khung bài toán lái xe dưới dạng Graph Visual Question Answering; LMDrive [4] thực hiện lái xe closed-loop end-to-end bằng LLM. Điểm chung của các hệ này là đòi hỏi huấn luyện hoặc tinh chỉnh trên tập dữ liệu lái xe quy mô lớn (nuScenes, CARLA...), cùng hạ tầng tính toán và dữ liệu đáng kể.

**Các công trình gần nhất với đề tài này**. Cùng hướng kết hợp deep learning chuyên biệt với multimodal LLM cho ngữ nghĩa giao thông, SafeRoute [11] và công trình tiền thân "Advancing Autonomous Vehicle Intelligence" [12] — của cùng một nhóm tác giả — xây dựng một pipeline thống nhất: ba kiến trúc phát hiện biển báo (ResNet-50 đạt 99,8%, YOLOv8 đạt 98,0%, RT-DETR đạt 96,6% accuracy) kết hợp với một MLLM được tinh chỉnh bằng instruction-tuning cho làn đường, sử dụng cơ chế Multimodal Adapter để dung hợp đặc trưng CNN với embedding EVA-CLIP; công trình này báo cáo Frame Overall Accuracy 53,87% và Question Overall Accuracy 82,83% cho phần hiểu làn đường dạng hỏi–đáp. Tương tự, DSC-LLM [13] kết hợp đặc trưng hành vi (mô hình hóa bằng LSTM/transformer) với ngữ cảnh cảnh giao thông trích xuất từ ảnh để dự đoán quỹ đạo kèm suy luận rủi ro có giải thích bằng LLM.

Điểm khác biệt giữa các công trình trên và đề tài này nằm ở hai khía cạnh. Thứ nhất, SafeRoute và Advancing-AV-Intelligence dung hợp thông tin ở tầng embedding (Multimodal Adapter, đòi hỏi tinh chỉnh MLLM), trong khi đề tài này dung hợp ở tầng prompt/văn bản (JSON ngữ nghĩa được nhúng trực tiếp vào prompt của một VLM tổng quát, không tinh chỉnh) — đơn giản hơn về triển khai, đổi lại phụ thuộc nhiều hơn vào chất lượng thiết kế prompt. Thứ hai, và quan trọng hơn, các công trình nêu trên đều không thực hiện một bước ablation tách riêng đóng góp của thông tin có cấu trúc so với ảnh thô — đây chính là RQ3 và mục 4.5, câu hỏi nghiên cứu trung tâm của đề tài — và cũng không kiểm chứng độ tin cậy của phương pháp đánh giá bằng đối chiếu với con người như mục 4.6 của đề tài.

Nhìn chung, hướng tiếp cận của đề tài này khác về bản chất so với cả hai nhóm công trình liên quan: thay vì huấn luyện hoặc tinh chỉnh một mô hình chuyên biệt ở tầng suy luận, đề tài tận dụng một VLM tổng quát đã huấn luyện sẵn, không tinh chỉnh (truy cập qua API theo chuẩn OpenAI-compatible của NVIDIA NIM), kết hợp với một tầng tiền xử lý ngữ nghĩa từ các mô-đun perception chuyên biệt — trong đó UFLD-v2 được dùng nguyên trạng ở dạng pretrained, còn YOLOv8n cho bài toán biển báo được tác giả tự tinh chỉnh trên TT100K (mục 3.2), một bước huấn luyện quy mô nhẹ, khác hẳn về chi phí so với việc huấn luyện lại một VLM/LLM hay thu thập dữ liệu lái xe quy mô lớn như ở các hệ end-to-end. Nhờ đó, hệ thống hỗ trợ quyết định có khả năng diễn giải được xây dựng mà không cần dữ liệu huấn luyện lái xe quy mô lớn hay tài nguyên tính toán để huấn luyện lại tầng suy luận. Sự đánh đổi này mang lại tính đơn giản, chi phí thấp và khả năng triển khai nhanh, phù hợp với quy mô một đề tài nghiên cứu độc lập.

## 2.4. Đánh giá chất lượng output ngôn ngữ tự nhiên bằng LLM-as-a-Judge

Nhu cầu đánh giá chuẩn hóa các hệ LLM và AI agent đang tăng nhanh cùng tốc độ phát triển của lĩnh vực. Một khảo sát gần đây [14] hệ thống hóa các benchmark và framework đánh giá LLM/agent công bố trong giai đoạn 2019–2025, cho thấy đây vẫn là một lĩnh vực đang định hình, chưa có phương pháp luận thống nhất — điều này càng củng cố lý do đề tài tự kiểm chứng độ tin cậy của phương pháp đánh giá thay vì áp dụng nguyên trạng mà không kiểm chứng.

Việc đánh giá chất lượng của một khuyến nghị lái xe dạng văn bản tự nhiên là bài toán khó lượng hóa bằng các metric cứng truyền thống (accuracy, F1...) vì không tồn tại một "đáp án đúng duy nhất". Phương pháp LLM-as-a-judge — sử dụng một LLM mạnh làm "giám khảo" tự động chấm điểm theo rubric cho trước — đã được áp dụng rộng rãi trong các benchmark đánh giá LLM gần đây, tiêu biểu là phương pháp luận của MT-Bench và Chatbot Arena [5], cũng như AlpacaEval. Trên MT-Bench, GPT-4 khi làm judge đạt 85% đồng thuận với chuyên gia con người (trên các cặp so sánh không hòa), một mức xấp xỉ độ đồng thuận giữa người với người (81%) — cho thấy LLM-as-a-judge có thể đạt độ tin cậy tiệm cận con người trong điều kiện phù hợp, dù vẫn tồn tại các thiên lệch cố hữu (thiên vị độ dài câu trả lời, thiên vị phong cách viết, tự thiên vị giữa các mô hình cùng họ) cần được kiểm chứng riêng cho từng bài toán ứng dụng cụ thể. Đây chính là cách tiếp cận được áp dụng trong đề tài này (mục 3.7 và 4.6), với quy mô kiểm chứng nhỏ hơn (N=20 so với hàng nghìn cặp trong MT-Bench gốc) do giới hạn nguồn lực của một đề tài cá nhân.

Việc sử dụng một mẫu kiểm chứng con người quy mô nhỏ, thay vì chấm tay toàn bộ dữ liệu, có cơ sở phương pháp luận riêng trong các nghiên cứu gần đây. [15] đề xuất một khung lấy mẫu hai giai đoạn — LLM chấm toàn bộ dữ liệu, con người chỉ chấm một mẫu con được chọn có chủ đích tại những nơi dự đoán của LLM kém tin cậy nhất — và nhấn mạnh rằng y văn hiện thiếu hướng dẫn chính thức về việc cần bao nhiêu giám sát của con người là đủ khi kiểm chứng một benchmark. [16] đề xuất phân bổ truy vấn thích ứng theo phương sai thay vì phân bổ đều, nhằm giảm sai số ước lượng trong một ngân sách tính toán cố định. [17] phỏng vấn tám chuyên gia và nhấn mạnh nhu cầu hỗ trợ xây dựng tiêu chí đánh giá khớp với kỳ vọng của người dùng thực tế — định hướng cho cách thiết kế rubric sáu tiêu chí của đề tài này (mục 3.7). Đề tài hiện sử dụng N=20 mẫu chọn ngẫu nhiên, chưa áp dụng cơ chế lấy mẫu thích ứng theo phương sai; đây là một hướng cải tiến khả thi được nêu ở mục 5.4.

## 2.5. Khoảng trống nghiên cứu

Bốn hướng nghiên cứu liên quan để lại các khoảng trống khác nhau mà đề tài này hướng tới:

1. **ADAS truyền thống** (dựa trên UFLD-v2, YOLOv8...) dừng lại ở tầng nhận diện — tọa độ, bounding box, class ID — không có tầng suy luận ngôn ngữ tự nhiên có thể diễn giải được cho người lái.
2. **Các hệ VLM lái xe end-to-end quy mô lớn** (DriveGPT4, DriveLM, LMDrive) giải quyết được bài toán diễn giải, nhưng đòi hỏi huấn luyện hoặc tinh chỉnh trên dữ liệu lái xe quy mô lớn — chi phí và ngưỡng gia nhập cao.
3. **Các hệ hybrid deep learning + MLLM gần đây** (SafeRoute, Advancing-AV-Intelligence, DSC-LLM — mục 2.3) là nhóm gần nhất về ý tưởng với đề tài này, kết hợp deep learning chuyên biệt với LLM đa phương thức, nhưng khác ở hai điểm cụ thể: (a) dung hợp thông tin ở tầng embedding, đòi hỏi tinh chỉnh, thay vì ở tầng prompt/văn bản; (b) không có bước ablation định lượng tách riêng đóng góp của thông tin có cấu trúc so với ảnh thô, và không kiểm chứng độ tin cậy của phương pháp đánh giá bằng đối chiếu con người.
4. **VLM tổng quát dùng nguyên trạng** (không qua tiền xử lý ngữ nghĩa) không được thiết kế chuyên biệt cho ngữ nghĩa giao thông; như đề tài này chứng minh định lượng ở mục 4.5, việc thiếu một tầng ngữ nghĩa có cấu trúc làm giảm rõ rệt chất lượng khuyến nghị so với khi có tầng đó.

Đề tài định vị gần nhóm (3) nhất về mục tiêu, nhưng chọn hướng triển khai gần nhóm (1) và (4) hơn về mặt kỹ thuật ở tầng suy luận (không tinh chỉnh VLM): kết hợp (a) tầng perception chuyên biệt đã được kiểm chứng — UFLD-v2 dùng nguyên trạng ở dạng pretrained, YOLOv8n cho biển báo được tự tinh chỉnh trên TT100K (mục 3.2), một bước huấn luyện quy mô nhẹ so với việc huấn luyện một VLM/LLM; (b) tầng chuyển đổi ngữ nghĩa có cấu trúc tự thiết kế — đóng góp chính về mặt kỹ thuật; (c) tầng suy luận VLM tổng quát không tinh chỉnh; và (d) một phương pháp luận đánh giá định lượng nghiêm ngặt, có kiểm chứng độ tin cậy của chính công cụ đánh giá bằng đối chiếu con người và đa-judge — một khoảng trống mà cả nhóm (2) và (3) đều chưa lấp đầy trong các công trình đã khảo sát.

---

# CHƯƠNG 3. PHƯƠNG PHÁP LUẬN

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

**Bộ dữ liệu chính (CULane)**. 200 ảnh được lấy ngẫu nhiên từ dataset CULane (độ phân giải 1640×590), đại diện cho các tình huống đô thị đa dạng: đường thẳng, cua nhẹ, giao lộ, mật độ giao thông khác nhau. Ground truth được gán nhãn thủ công cho toàn bộ 200/200 ảnh, gồm: số làn thực tế cùng chiều, loại đường (thẳng/cong nhẹ/cong gắt kèm hướng), số làn bị phát hiện nhầm, số làn ngược chiều bị gộp nhầm, độ chính xác xác định làn ego, số biển báo thật, số detection đúng/sai. Toàn bộ kết quả trong Chương 4 — cả các kết quả dựa trên ground truth lẫn các kết quả dựa trên LLM-as-a-judge — sử dụng đầy đủ N=200.

**Bộ dữ liệu kiểm chứng độc lập (real-life)**. 200 khung hình được trích xuất từ video dashcam thực tế (độ phân giải 1280 x 720), gán nhãn thủ công theo cùng schema như trên. Mục đích của bộ dữ liệu này là kiểm chứng khả năng tổng quát hóa của hệ thống trên dữ liệu hoàn toàn độc lập với dữ liệu huấn luyện của mô hình phát hiện làn đường (thảo luận về rủi ro data leakage được trình bày ở mục 4.7).

**Mô hình phát hiện làn đường**: UFLD-v2, backbone ResNet-34, pretrained trên CULane (`culane_res34.pth`).

**Mô hình phát hiện biển báo**: YOLOv8n (biến thể nhỏ nhất trong họ YOLOv8, ~3,2 triệu tham số), được tác giả tự tinh chỉnh (fine-tune) trên tập con 50 lớp phổ biến của TT100K — không dùng checkpoint pretrained nguyên trạng. Cấu hình huấn luyện: độ phân giải ảnh đầu vào 640×640, batch size tự động (`batch=-1`), tối ưu hóa bằng SGD (learning rate khởi tạo `lr0=0,01`, momentum `0,937`, weight decay `0,0005`, warm-up 3 epoch), cấu hình cho tối đa 100 epoch với cơ chế dừng sớm `patience=30` (dừng nếu không cải thiện sau 30 epoch liên tiếp). Đây là một bước tinh chỉnh tiêu chuẩn, quy mô nhẹ so với việc huấn luyện hoặc tinh chỉnh một VLM/LLM trên dữ liệu lái xe quy mô lớn như ở các hệ end-to-end được khảo sát ở mục 2.3 (DriveGPT4, DriveLM, LMDrive, SafeRoute) — không mâu thuẫn với định hướng training-free của đề tài, vốn áp dụng cho riêng tầng suy luận VLM ở LLM Reasoning (mục 3.6), không áp dụng cho tầng perception.

## 3.3. Phân tích ngữ nghĩa làn đường

Đây là tầng xử lý do tác giả tự thiết kế và cài đặt, chuyển đổi danh sách điểm ảnh thô của từng đường biên (do UFLD-v2 trả về) thành bốn ngữ nghĩa cấp quyết định: làn ego, độ lệch tâm xe, hình dạng đường, và làn lân cận — cấu thành đóng góp 1 của đề tài (mục 1.5).

**Bước tiền xử lý — sắp xếp đường biên theo vị trí thực tế**. UFLD-v2 không đảm bảo trả về các đường biên theo đúng thứ tự trái–phải trên ảnh (thứ tự trả về phụ thuộc nội bộ mô hình, không phải quy ước hình học), nên trước khi xác định làn ego, toàn bộ đường biên được sắp xếp lại theo tọa độ x thực tế tại một hàng ảnh tham chiếu $y_{ref} = 0{,}95 \times \text{image\_height}$ (gần đáy ảnh, nơi camera dashcam "nhìn thấy" mép capo xe). Với mỗi đường biên, tọa độ x tại $y_{ref}$ được nội suy bằng trung bình các điểm nằm trong khoảng $|y - y_{ref}| \le 30$ pixel; nếu không có điểm nào đủ gần (đường biên bị che khuất hoặc kết thúc sớm), tọa độ được ngoại suy bằng cách fit một đường thẳng bậc 1 qua toàn bộ điểm sẵn có của đường biên đó rồi tính giá trị tại $y_{ref}$ — thay cho cách làm trước đó (gán tạm giá trị $+\infty$ khi thiếu điểm gần), vốn khiến đường biên bị đẩy sai lệch về tận cùng bên phải bất kể vị trí thực tế, làm sai toàn bộ phân loại làn lân cận trái/phải phía sau.

**Xác định làn ego**. Với $n$ đường biên đã sắp xếp trái→phải (chỉ số $0$ đến $n-1$) và giả định camera gắn ở tâm xe (nên vị trí xe trên ảnh luôn là $x_{veh} = \text{image\_width}/2$), thuật toán xét toàn bộ $n-1$ cặp đường biên kề nhau $(i, i+1)$, tính điểm số cho mỗi cặp:

$$\text{score}_i = \left| \frac{x_i + x_{i+1}}{2} - x_{veh} \right| \times p_{between} \times \left(1 + 0{,}2 \times \frac{|w_i - w_{exp}|}{w_{exp}}\right)$$

trong đó $w_i = x_{i+1} - x_i$ là bề rộng cặp làn đang xét, $w_{exp} = 0{,}15 \times \text{image\_width}$ là bề rộng làn "điển hình" giả định, và $p_{between} = 0{,}5$ nếu xe thực sự nằm giữa hai đường biên ($x_i < x_{veh} < x_{i+1}$, ưu tiên mạnh cho trường hợp hình học hợp lý nhất) hoặc $p_{between} = 1$ trong trường hợp còn lại. Cặp có $\text{score}_i$ nhỏ nhất được chọn làm làn ego — tức thuật toán không giả định vị trí làn ego cố định (ví dụ "luôn là cặp ở giữa"), mà chọn động theo từng ảnh, chấp nhận cả trường hợp bất đối xứng (ví dụ đường cong, hoặc UFLD-v2 phát hiện thiếu đường biên ở một phía).

Độ tin cậy của kết quả được suy ra trực tiếp từ khoảng cách tâm làn ego tới tâm ảnh ($d = \text{score}_i$ của cặp thắng, trước khi nhân hệ số phạt): $d < 0{,}1 \times \text{image\_width}$ cho độ tin cậy $0{,}95$; $d < 0{,}25\times$ cho $0{,}8$; $d < 0{,}4\times$ cho $0{,}6$; còn lại $0{,}4$. Trường hợp đặc biệt chỉ phát hiện được đúng 1 đường biên ($n=1$) được xử lý riêng: gán đường biên đó làm ranh giới phải của làn ego, độ tin cậy cố định $0{,}5$.

**Độ lệch tâm xe (vehicle offset)**. Với tâm làn ego $x_{lane} = (x_{left} + x_{right})/2$ đã xác định ở bước trên, độ lệch được tính bằng $\Delta x = x_{veh} - x_{lane}$ (pixel), quy đổi theo tỉ lệ bề rộng làn thành $\Delta x_{\%} = (\Delta x / w) \times 100$. Hướng lệch được gán "centered" nếu $|\Delta x| < 10$ pixel, "lệch phải" nếu $\Delta x > 0$ (tâm làn nằm bên trái tâm xe), "lệch trái" nếu ngược lại.

**Ước lượng độ cong**. Với mỗi đường biên riêng lẻ (tối thiểu 4 điểm hợp lệ), tọa độ $y$ được chuẩn hóa về $[0,1]$ theo chính khoảng $[y_{min}, y_{max}]$ quan sát được của đường biên đó: $y_{norm} = (y - y_{min})/(y_{max} - y_{min})$. Hai đa thức được fit qua các điểm $(y_{norm}, x)$: bậc 1 (đường thẳng, hệ số $c_1$, sai số bình phương trung bình $\text{MSE}_1$) và bậc 2 (parabol, $\text{MSE}_2$). Hai tín hiệu độ cong được trích ra:

- $\text{drift\_ratio} = \sqrt{\text{MSE}_1} \, / \, \text{image\_width}$ — độ lệch quân phương so với một đường thẳng lý tưởng, chuẩn hóa theo chiều rộng ảnh để so sánh được giữa các ảnh có độ phân giải khác nhau.
- $\text{fit\_improvement} = \max\!\left(0, \dfrac{\text{MSE}_1 - \text{MSE}_2}{\text{MSE}_1}\right)$ — mức cải thiện TƯƠNG ĐỐI khi cho phép mô hình cong so với ép thẳng, chỉ được tin cậy khi $\text{MSE}_1 > 4$ (tương đương sai số quân phương $>2$ pixel) và đường biên có $\ge 10$ điểm; nếu không, chênh lệch $\text{MSE}_1 - \text{MSE}_2$ được coi là nhiễu đo đạc hoặc hiện tượng overfit (đa thức bậc 2 có thêm 1 bậc tự do, dễ "khớp hoàn hảo" giả tạo khi quá ít điểm) và $\text{fit\_improvement}$ được gán 0. Tín hiệu này đặc biệt cần thiết cho các đường cong rất nhẹ, chỉ quan sát được ở cự ly gần: độ lệch tuyệt đối so với đường thẳng khi đó vẫn rất nhỏ (vài pixel), khiến $\text{drift\_ratio}$ không đủ nhạy, dù hình dạng thực sự đã cong — $\text{fit\_improvement}$ trả lời một câu hỏi khác và nhạy hơn: "cho phép mô hình cong có giải thích hình dạng đường biên này tốt hơn hẳn không?", không phụ thuộc độ lớn lệch tuyệt đối.

Điểm hội tụ phối cảnh (vanishing point) của mỗi đường biên được ngoại suy bằng CHÍNH fit bậc 1 (không dùng bậc 2), tại một mốc "chân trời" $y_{horizon} = 0{,}3 \times \text{image\_height}$ DÙNG CHUNG cho mọi đường biên trong cùng một ảnh — thay vì ngoại suy tại $y_{norm}=0$ của riêng từng đường biên như thiết kế ban đầu. Lựa chọn này dựa trên hai lý do: (1) về hình học, phép chiếu phối cảnh (pinhole camera) luôn biến một đường thẳng trong không gian ba chiều thành một đường thẳng trên ảnh (tính đồng quy được bảo toàn), nên fit bậc 1 vừa đúng bản chất của một đường biên thẳng, vừa ổn định hơn fit bậc 2 khi ngoại suy ra ngoài khoảng điểm quan sát được; (2) mỗi đường biên có thể chỉ hiển thị rõ ở một đoạn $y$ khác nhau (do bị che khuất hoặc đặc thù model), nên nếu ngoại suy tại $y_{norm}=0$ riêng của từng đường biên, hai đường biên thẳng song song vẫn có thể cho hai điểm hội tụ khác nhau do đang được đánh giá ở hai độ sâu ảnh khác nhau — gây phóng đại sai độ phân tán điểm hội tụ (vanishing-point spread) dù đường thực sự thẳng. Neo tất cả về cùng một hàng ảnh "chân trời" khắc phục được sai lệch này.

Bốn tín hiệu tổng hợp trên toàn ảnh — $\overline{\text{drift}}$ (trung bình $\text{drift\_ratio}$ của mọi đường biên), $\overline{\text{fit\_improvement}}$ (trung bình $\text{fit\_improvement}$), tỉ lệ đường biên riêng lẻ được gán "thẳng" ($\text{MSE}_1 < 1000$), và hướng cong — được dùng để phân loại hình dạng đường tổng thể. Hướng cong (trái/phải) được ước lượng độc lập, bằng cách so sánh tọa độ x trung bình của các điểm gần đáy ảnh ($y \approx 0{,}85 \times \text{image\_height}$) với các điểm gần giữa ảnh ($y \approx 0{,}35\times$): tỉ lệ dịch chuyển $\text{shift\_ratio}$ (chuẩn hóa theo chiều rộng ảnh) dưới $0{,}08$ được coi là "thẳng"; ngược lại, hướng được gán theo dấu của độ dịch chuyển.

**Hiệu chỉnh ngưỡng phân loại độ cong**. Ba ngưỡng phân loại được hiệu chỉnh bằng số liệu thống kê thực đo trên ảnh CULane (không đặt tùy ý): $\overline{\text{drift}}_{straight} = 0{,}02$ (đặt trên phân vị p95 quan sát được của các ảnh đường thẳng, $\approx 0{,}014$, chừa biên độ cho nhiễu), $\overline{\text{drift}}_{sharp} = 0{,}06$ (đặt dưới giá trị đo được của một ảnh cua gắt đã xác nhận đúng bằng mắt, $0{,}0994$, để chắc chắn bắt được), và ngưỡng $\text{fit\_improvement} = 0{,}3$ dùng để "nâng hạng" từ "thẳng" lên "cong nhẹ" khi $\overline{\text{drift}}$ quá nhỏ để tự phát hiện nhưng $\overline{\text{fit\_improvement}}$ cho thấy bằng chứng cong rõ ràng. Quy tắc phân loại cuối cùng: `straight` nếu $\overline{\text{drift}} < 0{,}02$ VÀ $\overline{\text{fit\_improvement}} < 0{,}3$ VÀ tỉ lệ đường biên thẳng $> 50\%$; `sharp` nếu $\overline{\text{drift}} \ge 0{,}06$; còn lại là `gentle`. Một tín hiệu hình học khác (độ phân tán tuyệt đối của điểm hội tụ theo pixel, $\text{vp\_spread}$) từng được cân nhắc đưa vào quy tắc phân loại nhưng bị loại bỏ: quan sát thực nghiệm trong quá trình phát triển cho thấy giá trị này không ổn định giữa các ảnh có đặc trưng camera/độ phân giải khác nhau (không chuẩn hóa theo kích thước ảnh), nên không đáng tin cậy để đặt một ngưỡng cố định duy nhất — khác với $\overline{\text{drift}}$ (đã chuẩn hóa theo chiều rộng ảnh); $\text{vp\_spread}$ vẫn được lưu lại trong JSON để tham khảo/debug nhưng không tham gia quy tắc phân loại.

**Số làn đường**. Được tính bằng số đường biên phát hiện được trừ 1, do một làn nằm giữa hai đường biên kề nhau — đúng theo quy ước của CULane.

## 3.4. Cấu trúc JSON ngữ nghĩa gửi cho LLM

**JSON đầy đủ (`<tên>.json`)**. Đây là output trực tiếp của tầng Semantic Analysis (mục 3.3), và cũng là bản JSON được nhúng nguyên vẹn vào prompt ở hai chế độ `json_only`/`image_json`. Cấu trúc gồm bốn nhóm trường:

1. **Siêu dữ liệu**: `scene_id` (UUID định danh phiên xử lý), `timestamp`, `image_size` (`width`, `height`).
2. **`road`** (tổng hợp cấp đường): `road_type` (nhãn phân loại, ví dụ `"straight"`), `road_environment` (ước lượng heuristic loại môi trường đường bằng quy tắc if-else đơn giản, ví dụ `"urban_marketplace"` — độ tin cậy thấp, đã bị loại khỏi bản rút gọn vì lý do này, xem bên dưới), `curvature_magnitude`/`curvature_direction`/`curvature_confidence` (kết quả từ mục 3.3), và `geometry` (`spread_pixels`, `coverage_ratio`, `convergence_ratio`, `lane_count`, `geometry_type`).
3. **`lane`** (chi tiết cấp làn, đầu ra chính của mục 3.3): `sorted_lanes` (danh sách đường biên đã sắp xếp trái→phải, mỗi phần tử gồm `original_index`, `sorted_index`, `x_at_reference`, `point_count`); `ego_lane` (`left_boundary_index`, `right_boundary_index`, `ego_lane_center_x`, `lane_width`, `confidence`, `reason`); `lane_classification` (danh sách và số lượng làn lân cận trái/phải); `vehicle_offset` (`offset_pixels`, `offset_ratio_percent`, `direction`, `vehicle_x`, `lane_center_x`, `lane_width`, khoảng cách tới từng biên, cờ `is_vehicle_between_boundaries`); `curvature` (`curvature_magnitude`, `direction`, `classification`, `confidence`, `vanishing_point_spread`, `avg_drift`, `avg_fit_improvement`); `lane_semantics` (danh sách ngữ nghĩa từng làn: `lane_type`, `is_ego_lane`, `is_drivable`, `lateral_position`); và `image_width`/`image_height`.
4. **`traffic_signs`**: `detected` (danh sách biển báo phát hiện được, mỗi phần tử gồm nhãn lớp và tọa độ), `count`.

**JSON rút gọn (`<tên>_brief.json`)**. Một schema riêng, gọn hơn nhiều, chỉ gồm năm trường cấp quyết định: `lane_count` (số nguyên), `ego_lane` (`position` dạng "X/Y", `confidence`), `vehicle_offset` (`direction`, `magnitude`, `offset_percent`), `neighbor_lanes` (`left_count`, `right_count`), `road_shape` (`type`, `severity`, `direction`) — không có siêu dữ liệu, không có `traffic_signs`. Thiết kế nhằm cấp cho LLM một bản dữ liệu tối giản, loại bỏ các trường thiếu bằng chứng đủ tin cậy (như `road_environment` heuristic) khỏi ngữ cảnh của LLM. Schema này được sử dụng đúng mục đích ở một thí nghiệm khác của đề tài: làm định dạng output mục tiêu cho thí nghiệm kiểm chứng khả năng tự nhận diện của VLM (mục 4.8) — nơi VLM được yêu cầu tự trích xuất đúng năm trường này trực tiếp từ ảnh, không kèm bất kỳ gợi ý nào, rồi so sánh với giá trị mà pipeline UFLD-v2 tính ra. Ở vai trò này, `_brief.json` chỉ đóng vai trò khuôn mẫu cấu trúc cho output cần so sánh, không phải input được cấp cho VLM, nên không phát sinh vấn đề về công bằng hay rò rỉ thông tin.

## 3.5. Thiết kế prompt cho tầng suy luận

Prompt được thiết kế qua nhiều vòng lặp thực nghiệm, tập trung vào bốn ngữ nghĩa cấp làn đường (số làn, làn ego, độ lệch tâm, làn lân cận), kèm các quy tắc chống ảo giác (không suy diễn thông tin không có bằng chứng, không coi thiếu phát hiện là bằng chứng cho việc vật thể không tồn tại) và yêu cầu cấu trúc output cố định gồm ba phần — Tình huống, Khuyến nghị, Lưu ý an toàn — để đảm bảo tính nhất quán giữa các lần sinh. Trong quá trình phát triển, hai vấn đề đã được phát hiện và khắc phục: hiện tượng mô hình lặp lại vô hạn cùng một câu trả lời trên ảnh ít thông tin (khắc phục bằng tham số frequency penalty), và hiện tượng mô hình trả lời quá ngắn, không tuân thủ cấu trúc bắt buộc (khắc phục bằng yêu cầu nêu bằng chứng cụ thể cho từng phần).

## 3.6. Lựa chọn mô hình cho tầng suy luận

Do giới hạn về chi phí và khả năng tái lập, phạm vi lựa chọn mô hình được giới hạn trong các VLM khả dụng miễn phí qua NVIDIA NIM API (định dạng OpenAI-compatible thống nhất). Ba mô hình cụ thể được chọn để so sánh dựa trên ba tiêu chí: (1) hỗ trợ đa phương thức (nhận đồng thời ảnh và văn bản) — điều kiện bắt buộc của pipeline, loại trừ các mô hình chỉ xử lý văn bản; (2) khả dụng miễn phí qua cùng một API thống nhất, đảm bảo chi phí triển khai bằng 0 và tính nhất quán khi thực nghiệm, đúng định hướng training-free/chi phí thấp của đề tài (mục 1.5); (3) trải dài trên nhiều mức quy mô tham số khác nhau trong phạm vi các mô hình khả dụng đó, cho phép quan sát liệu quy mô mô hình có tương quan với độ tin cậy và chất lượng đầu ra hay không — phục vụ trực tiếp RQ4. Ba mô hình thỏa mãn đồng thời cả ba tiêu chí này là: `nemotron-nano-vl-8b` (8 tỷ tham số), `nemotron-nano-12b-v2-vl` (12 tỷ tham số), `ising-calibration-1.5-31b` (31 tỷ tham số).

Tiêu chí so sánh giữa ba mô hình gồm, theo đúng thứ tự ưu tiên: (1) độ tin cậy — tỉ lệ hoàn thành thành công khi chạy trên toàn bộ batch thật, được xét TRƯỚC và độc lập với chất lượng nội dung, vì một mô hình không phản hồi ổn định không thể triển khai cho một hệ thống hỗ trợ quyết định thời gian thực, bất kể chất lượng câu trả lời khi nó phản hồi thành công tốt tới đâu; (2) tỉ lệ tuân thủ cấu trúc output bắt buộc; (3) chất lượng nội dung, chấm điểm bởi LLM-as-a-judge — chỉ áp dụng cho các mô hình đã vượt qua ngưỡng tối thiểu ở tiêu chí (1).

**Trình tự thực nghiệm (tránh nhầm lẫn vòng lặp giữa việc chọn mô hình và việc chấm điểm bởi judge)**. Việc chọn mô hình LLM ở mục này (RQ4) và kết quả trung tâm về đóng góp của JSON ngữ nghĩa ở mục 4.5 (RQ3) là hai thực nghiệm tách biệt, chạy tuần tự, không phụ thuộc vòng tròn vào nhau:

1. **Giai đoạn 1 — chọn mô hình (mục 4.4)**: cả ba mô hình ứng viên (8B, 12B, 31B) được chạy ở CÙNG MỘT chế độ input cố định — `image+json` (chế độ cấp đầy đủ thông tin nhất, cho mỗi mô hình cơ hội thể hiện tốt nhất) — và được chấm điểm bởi đúng một judge (Gemini) để xác định mô hình có độ tin cậy và chất lượng tốt nhất. Kết quả: `ising-calibration-31b` được chọn.
2. **Giai đoạn 2 — so sánh chế độ input (mục 4.5)**: sau khi đã chốt mô hình LLM ở Giai đoạn 1, mô hình đó được GIỮ CỐ ĐỊNH, và biến số duy nhất được thay đổi là chế độ input (`image_only`/`json_only`/`image+json`) — chấm điểm bởi cả ba judge độc lập để trả lời RQ3.

Nói cách khác, chuỗi xử lý thực tế là: ảnh → detection/semantic analysis → **[chạy 3 mô hình LLM ở chế độ image+json → Gemini chấm điểm → chọn mô hình thắng]** → **[cố định mô hình thắng, chạy lại ở cả 3 chế độ input → cả 3 judge chấm điểm → kết luận RQ3]**. Bước chấm điểm để chọn mô hình (Giai đoạn 1) và bước chấm điểm để so sánh chế độ input (Giai đoạn 2) là hai lượt chấm điểm riêng biệt, phục vụ hai câu hỏi nghiên cứu khác nhau (RQ4 và RQ3), không phải cùng một lượt chấm dùng cho cả hai mục đích.

**Vì sao Giai đoạn 1 chỉ dùng một chế độ input và một judge, không dùng đầy đủ 3×3 tổ hợp như Giai đoạn 2**. Đây là một lựa chọn thiết kế thực nghiệm có chủ đích, dựa trên ba căn cứ:

1. **Hai câu hỏi trực giao, độ phức tạp cần thiết khác nhau**. RQ4 (chọn mô hình) và RQ3 (so sánh chế độ input) là hai biến số độc lập của cùng một hệ thống. Việc chạy toàn bộ ma trận 3 mô hình × 3 chế độ × 3 judge (thiết kế factorial đầy đủ) sẽ tốn gấp nhiều lần chi phí/thời gian API mà không phục vụ trực tiếp RQ4 — vốn chỉ cần xác định "mô hình nào đáng tin cậy và chất lượng tốt nhất", không cần biết mô hình đó tương tác thế nào với từng chế độ input cụ thể. Cố định chế độ input ở `image+json` — chế độ cấp nhiều thông tin nhất — khi so sánh mô hình là cách chuẩn để đảm bảo mỗi mô hình được đánh giá trong điều kiện thuận lợi nhất có thể, tách bạch rõ "mô hình yếu" khỏi "mô hình bị thiếu thông tin".
2. **Ràng buộc trình tự phát triển thực tế**: tại thời điểm Giai đoạn 1 được thực hiện, GPT-5 Mini và DeepSeek chưa được tích hợp làm judge — Gemini là judge duy nhất tồn tại trong hệ thống ở giai đoạn đó. Việc bổ sung đối chiếu đa-judge (mục 4.6) là một bước siết chặt phương pháp luận được thêm vào SAU, dành riêng cho kết quả trung tâm (RQ3, mục 4.5) — nơi kết luận thực sự nhạy với lựa chọn judge (thứ hạng `json_only` so với `image+json` đảo chỗ tùy judge, Bảng 4.5). Việc chạy lại toàn bộ Giai đoạn 1 với 3 judge sau khi đã có kết quả không được thực hiện vì không cần thiết cho quyết định đã đủ rõ ràng (xem điểm 3).
3. **Độ lớn chênh lệch không đòi hỏi kiểm chứng đa-judge để tin cậy**. Khác với RQ3 — nơi khoảng cách giữa `json_only` và `image+json` đủ hẹp để thứ hạng đổi chiều theo judge, biện minh cho việc cần đối chiếu nhiều judge — chênh lệch giữa các mô hình ở RQ4 lớn hơn nhiều bậc: `nemotron-nano-12b-v2-vl` thất bại 83% số yêu cầu (không phải một chênh lệch điểm số cần judge tinh vi mới phân biệt được), và `ising-calibration-31b` vượt `nemotron-nano-8b` với Cohen's d ≈ 1,04 (Bảng 4.4) — một hiệu ứng rất lớn, khó có khả năng bị đảo ngược chỉ vì đổi judge. Thêm vào đó, mục 4.6 (thực hiện sau) xác nhận Gemini là judge có tương quan với con người cao nhất trong ba judge đã thử — củng cố thêm, dù không phải bằng chứng có sẵn tại thời điểm Giai đoạn 1 được thực hiện, rằng lựa chọn Gemini làm judge duy nhất cho quyết định này là hợp lý.

## 3.7. Phương pháp luận đánh giá

**Đánh giá module hiểu làn đường/biển báo**. So sánh trực tiếp với ground truth gán tay, sử dụng các metric chuẩn: Accuracy (tỉ lệ khớp chính xác), MAE (sai số tuyệt đối trung bình), Precision và Recall.

**Đánh giá chất lượng khuyến nghị lái xe**. Sử dụng LLM-as-a-judge với rubric sáu tiêu chí, thang điểm 1–5: `situation_understanding`, `road_understanding`, `lane_ego_position`, `traffic_sign_rule`, `driving_recommendation`, `safety_considerations`. Mỗi ảnh được đánh giá bằng một lệnh gọi API duy nhất, gộp cả ba thí nghiệm cần so sánh trong cùng một ngữ cảnh — vừa tiết kiệm chi phí, vừa đảm bảo tính nhất quán trong đánh giá.

**Kiểm chứng độ tin cậy của judge**. Gồm hai bước: (1) so sánh điểm của Gemini với điểm chấm tay của con người trên một mẫu ngẫu nhiên N=20; (2) đối chiếu với hai judge độc lập khác (GPT-5 Mini, DeepSeek) trên cùng bộ dữ liệu, sử dụng nguyên văn cùng một rubric để đảm bảo so sánh công bằng. Mốc chuẩn để đánh giá "judge nào chính xác hơn" là độ đồng thuận với con người, không phải độ đồng thuận giữa các judge với nhau — vì hai judge AI có thể đồng ý với nhau nhưng vẫn cùng chia sẻ một thiên lệch giống nhau so với con người.

---

# CHƯƠNG 4. KẾT QUẢ VÀ BÀN LUẬN

## 4.1. Độ chính xác module hiểu làn đường (CULane)

Ở giai đoạn đầu, 26 ảnh thuộc các tình huống khó xác định (sảnh/quảng trường không vạch kẻ, hầm gửi xe, đang nhập làn, giao lộ phức tạp...) được gán tạm `lane_count=0` để loại khỏi thống kê. Quá trình rà soát sau đó phát hiện cách làm này che giấu một sai lệch: phần lớn các ảnh đó, mô hình cũng dự đoán giá trị `0` (do không thấy vạch kẻ), nên vô tình được tính là "khớp chính xác", dù thực chất mô hình đã thất bại hoàn toàn chứ không phải đoán đúng "0 làn". Toàn bộ 200 ảnh sau đó được gán nhãn lại bằng số làn ước lượng thực tế (dựa vào bề rộng đường, vị trí xe khác, dải phân cách vật lý...), kèm theo nhãn phân loại lý do khó (`hard_reason`), cho phép tách riêng nhóm ảnh có vạch kẻ rõ ("Normal") khỏi nhóm không có vạch kẻ rõ.

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

Các chỉ số ở Bảng 4.1 được tính trực tiếp từ đối chiếu `image_labels.xlsx` với output của pipeline trên N=200 ảnh, theo các công thức sau: Lane count Accuracy bằng tỉ lệ ảnh có số làn dự đoán khớp đúng số làn thực tế (138/200 = 69,0%); Lane count MAE bằng trung bình trị tuyệt đối của hiệu số làn thực tế và dự đoán (95/200 = 0,475); Lane count Precision bằng tổng số làn thực tế chia cho tổng số làn thực tế cộng số làn phát hiện nhầm và số làn ngược chiều bị gộp nhầm (477/(477+5+12) = 96,6%); Road type Accuracy khớp chính xác bằng 153/200 = 76,5%, khớp theo nhóm thẳng/nhẹ/gắt bằng 157/200 = 78,5%; Ego lane Accuracy bằng tỉ lệ ảnh có làn ego được xác định đúng (172/200 = 86,0%).

Kết quả đáng chú ý nhất ở giai đoạn này không nằm ở bản thân việc sửa lỗi, mà ở ý nghĩa phương pháp luận mà nó bộc lộ về tầng diễn giải ngữ nghĩa: hệ thống ban đầu chứa một lỗi lệch đơn vị (off-by-one) trong công thức tính số làn — đếm số đường biên thay vì số làn thực tế — khiến hầu hết ảnh bị báo thừa một làn. Do giá trị này được nhúng trực tiếp vào ngữ cảnh JSON gửi cho LLM, lỗi này là nguyên nhân trực tiếp gây ra hiện tượng "ảo giác" số làn trong khuyến nghị của LLM ở giai đoạn đầu nghiên cứu. Sau khi sửa, Accuracy tăng từ 11,1% lên 69,0%, đo trên cùng một lần detect và chỉ khác công thức xử lý phía sau — chứng minh rằng mức cải thiện này đến hoàn toàn từ tầng diễn giải ngữ nghĩa, không phụ thuộc vào chất lượng của bản thân mô hình phát hiện. Nói cách khác, đây không phải một đóng góp thuật toán, mà là bằng chứng thực nghiệm cho thấy tầng diễn giải ngữ nghĩa — nếu không được xây dựng và kiểm chứng cẩn thận — có thể trở thành điểm nghẽn quyết định chất lượng toàn hệ thống, dù tầng phát hiện phía trước đã đạt chất lượng tốt.

Sau khi gán nhãn lại 26 ảnh khó nêu trên, việc tách riêng theo `hard_reason` cho thấy hiệu năng của mô hình phụ thuộc rất mạnh vào sự hiện diện của vạch kẻ đường.

**Bảng 4.2.** So sánh hiệu năng module hiểu làn đường theo nhóm có/không vạch kẻ đường rõ.

| Nhóm | N | Lane count Accuracy | Lane count MAE | Precision | Ego lane Accuracy |
|---|---|---|---|---|---|
| Có vạch kẻ rõ ("Normal") | 176 | **77,3%** | 0,273 | 96,2% | **96,6%** |
| Không vạch kẻ rõ (quảng trường/hầm gửi xe/nhập làn/giao lộ phức tạp) | 24 | **8,3%** | 1,958 | 100,0% | **8,3%** |

Số liệu thô làm cơ sở cho Bảng 4.2: nhóm Normal có 136/176 ảnh khớp chính xác, tổng trị tuyệt đối sai số 48 (MAE = 48/176 = 0,273), tổng số làn thực tế/nhầm/ngược chiều lần lượt 427/5/12 (Precision = 427/444 = 96,2%), 170/176 ảnh xác định đúng làn ego (96,6%). Nhóm Hard có 2/24 ảnh khớp chính xác, tổng trị tuyệt đối sai số 47 (MAE = 47/24 = 1,958), tổng số làn thực tế/nhầm/ngược chiều lần lượt 50/0/0 (Precision = 50/50 = 100%), 2/24 ảnh xác định đúng làn ego (8,3%).

Đáng chú ý, Precision vẫn đạt 100% ngay cả trên nhóm khó — tức mô hình không "bịa" làn giả, mà chỉ đơn giản không phát hiện được gì khi thiếu vạch kẻ (thể hiện rõ ở hai lý do `no_markings` và `merging`: số làn dự đoán trung bình bằng 0,00, trong khi số làn thực tế trung bình khoảng 1,7–2,5). Đây là hạn chế cố hữu của một detector dựa trên vạch kẻ đường (UFLD-v2, huấn luyện trên CULane vốn chủ yếu là ảnh có vạch kẻ rõ), không phải lỗi logic của tầng xử lý ngữ nghĩa phía sau — được bàn thêm ở mục 5.3.

**So sánh với công trình cùng hướng (hybrid deep learning + MLLM)**. Công trình [12] (mục 2.3) báo cáo Frame Overall Accuracy 53,87% và Question Overall Accuracy 82,83% cho module hiểu làn đường dạng hỏi–đáp bằng MLLM. Kết quả của đề tài này — 69,0% tổng thể, 77,3% trên nhóm ảnh có vạch kẻ rõ — nằm giữa hai con số đó. Điều này hợp lý vì hai nghiên cứu định nghĩa "accuracy" theo cách khác nhau (Frame Overall Accuracy đo trên toàn khung hình bao gồm cả điều kiện thời tiết và ánh sáng bất lợi, Question Overall Accuracy đo theo từng câu hỏi VQA cụ thể), nên không thể coi là so sánh trực tiếp một-một; tuy nhiên, kết quả cho thấy độ chính xác đạt được nằm trong khoảng hợp lý so với mặt bằng chung của hướng nghiên cứu hybrid deep learning + MLLM cho ngữ nghĩa làn đường.

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

Sử dụng mô hình YOLOv8n đã tự tinh chỉnh trên TT100K (mục 3.2), một phát hiện quan trọng là dataset CULane có mật độ biển báo và đèn tín hiệu rất thấp: chỉ 6% ảnh CULane (12/200) có detection ở ngưỡng chuẩn 0,5, và 20% ảnh không có detection nào dù đã hạ ngưỡng xuống 0,01. Đây là hạn chế của dữ liệu benchmark (CULane vốn được thiết kế cho bài toán phát hiện làn đường), không phải hạn chế của mô hình — điều này được xác nhận qua kết quả tốt hơn hẳn trên dữ liệu dashcam thực tế tự thu thập (mục 4.2, Precision/Recall 60,9%).

**So sánh với công trình cùng hướng**. SafeRoute và Advancing-AV-Intelligence [11], [12] báo cáo accuracy phân loại biển báo từ 96,6% đến 99,8% (YOLOv8 đạt 98,0%) — cao hơn đáng kể so với Precision/Recall 60,9% của đề tài này. Chênh lệch này chủ yếu đến từ khác biệt về độ khó bài toán: các con số 96,6–99,8% là accuracy phân loại trên biển báo đã được khoanh vùng sẵn (given a cropped/localized sign, classify it), trong khi Precision/Recall 60,9% của đề tài đo trên bài toán phát hiện từ đầu — vừa phải định vị vừa phải phân loại trên toàn khung hình, không có gợi ý vị trí trước — một bài toán khó hơn về bản chất.

## 4.4. So sánh mô hình LLM cho tầng suy luận

Toàn bộ so sánh trong mục này (Giai đoạn 1, xem mục 3.6) được chạy ở CÙNG MỘT chế độ input cố định `image+json` và chấm điểm bởi đúng một judge (Gemini), nhằm chọn ra mô hình LLM sẽ được giữ cố định cho Giai đoạn 2 (so sánh chế độ input, mục 4.5) — không phải một phần của thực nghiệm ba-judge/ba-chế-độ trả lời RQ3.

**Độ tin cậy và tốc độ**. `ising-calibration-31b` đạt tỉ lệ thành công 200/200 (0% lỗi, N=200), thời gian trung bình 3,80 giây/ảnh. `nemotron-nano-12b-v2-vl` chỉ đạt 34/200 (83% yêu cầu nhận lỗi 500 Internal Server Error từ phía máy chủ NVIDIA NIM).

Mô hình này bị loại khỏi vòng so sánh chất lượng vì hai lý do độc lập, không phải vì bản thân câu trả lời (khi có) kém chất lượng. Thứ nhất, như đã nêu ở mục 3.6, độ tin cậy được xét như một tiêu chí có tính loại trừ (gating), đứng trước và độc lập với chất lượng nội dung: một mô hình chỉ phản hồi thành công 17% số yêu cầu không thể triển khai cho một hệ thống hỗ trợ quyết định thời gian thực, bất kể chất lượng của 17% câu trả lời còn lại tốt tới đâu — lỗi 500 xuất phát từ phía hạ tầng máy chủ NVIDIA NIM lưu trữ mô hình, không phản ánh trực tiếp năng lực của bản thân mô hình, nhưng từ góc độ triển khai thực tế, một mô hình không thể truy cập ổn định thì không sử dụng được, bất kể nguyên nhân kỹ thuật đến từ đâu. Thứ hai, ngay cả khi bỏ qua tiêu chí gating trên, 34 câu trả lời thành công còn lại không tạo thành một mẫu so sánh công bằng: đây là tập con tự chọn lọc (self-selected) bởi chính cơ chế gây lỗi của máy chủ — nhiều khả năng thiên lệch về phía các ảnh/yêu cầu đơn giản hơn, ít tốn thời gian xử lý hơn — chứ không phải một mẫu ngẫu nhiên đại diện cho toàn bộ 200 ảnh như hai mô hình còn lại đạt được ở phép so sánh này. So sánh chất lượng giữa 34 mẫu thiên lệch với 200 mẫu đầy đủ của các mô hình khác sẽ vi phạm nguyên tắc so sánh công bằng đã đặt ra cho toàn bộ phương pháp luận đánh giá của đề tài (mục 3.7).

**Tuân thủ cấu trúc output**. Trên N=200 (`nemotron-nano-8b`/`ising-calibration-31b`; đếm số output có độ dài dưới 80 ký tự — tương đương bỏ qua cấu trúc ba phần bắt buộc — cho thấy `nemotron-nano-8b` có 99/200 (49,5%) output bị cắt cụt, trong khi `ising-calibration-31b` có 0/200 (0%) trên đúng tập 200 ảnh đối chứng này (0/200 trên toàn bộ tập, mục 4.5). Xét trên độ dài toàn bộ output (không chỉ ngưỡng cắt cụt), `nemotron-nano-8b` sinh trung bình 95 ký tự/câu trả lời (SD = 78), trong khi `ising-calibration-31b` sinh trung bình 876 ký tự/câu trả lời (SD = 198) — gấp hơn 9 lần, đủ để trình bày trọn vẹn ba phần Tình huống/Khuyến nghị/Lưu ý an toàn theo đúng yêu cầu prompt (mục 3.5), thay vì một câu trả lời rút gọn không đạt cấu trúc tối thiểu.

**Chất lượng nội dung** (so với `nemotron-nano-8b`, N=200, cùng ảnh, cùng judge Gemini, cùng rubric sáu tiêu chí). Đây là phép so sánh trực tiếp và công bằng nhất trong ba mô hình, vì cả hai đều vượt qua tiêu chí gating về độ tin cậy (`nemotron-nano-8b` hoàn thành 200/200, không bị loại vì lý do thiên lệch mẫu như `nemotron-nano-12b-v2-vl`). Áp dụng đúng phương pháp thống kê đã dùng ở mục 4.5 — tính điểm trung bình sáu tiêu chí theo từng ảnh trước, rồi kiểm định bắt cặp trên 200 cặp điểm-trên-ảnh — kết quả ở Bảng 4.4 cho thấy khoảng cách không chỉ lớn mà còn có ý nghĩa thống kê rất mạnh.

**Bảng 4.4.** So sánh chi tiết chất lượng nội dung giữa `nemotron-nano-8b` và `ising-calibration-31b` (Mean ± SD, N=200, kiểm định Wilcoxon signed-rank bắt cặp theo ảnh).

| Tiêu chí | nemotron-nano-8b | ising-calibration-31b | Wilcoxon p |
|---|---|---|---|
| situation_understanding | 1,97 ± 1,15 | 3,48 ± 1,24 | p < 0,001 |
| road_understanding | 2,08 ± 1,27 | 3,77 ± 0,92 | p < 0,001 |
| lane_ego_position | 2,03 ± 1,13 | 3,77 ± 1,24 | p < 0,001 |
| traffic_sign_rule | 2,17 ± 1,42 | 3,18 ± 1,32 | p < 0,001 |
| driving_recommendation | 3,98 ± 1,13 | 4,16 ± 1,20 | p = 0,066 (không có ý nghĩa) |
| safety_considerations | 1,69 ± 0,98 | 3,74 ± 1,19 | p < 0,001 |
| **Trung bình 6 tiêu chí (điểm/ảnh)** | **2,32 ± 0,99** | **3,68 ± 0,96** | **paired t: t = −14,68, p < 0,001; Cohen's d = −1,04 (rất lớn)** |

`ising-calibration-31b` vượt trội có ý nghĩa thống kê ở năm trên sáu tiêu chí (p < 0,001), với kích thước hiệu ứng tổng thể rất lớn (Cohen's d ≈ 1,04 — chênh lệch trung bình vượt quá một độ lệch chuẩn). Tiêu chí `driving_recommendation`, chênh lệch (3,98 so với 4,16) không đạt ý nghĩa thống kê (p = 0,066) — tức hai mô hình được đánh giá tương đương nhau ở đúng tiêu chí này, không phải `ising-calibration-31b` thắng tuyệt đối ở toàn bộ sáu tiêu chí. Điều này không làm suy yếu quyết định chọn mô hình: 5/6 tiêu chí còn lại, cùng với chênh lệch rất lớn về độ tin cậy (100% so với việc không bị loại do gating) và độ dài/tính đầy đủ cấu trúc output (876 so với 95 ký tự), đã là căn cứ đủ mạnh và đủ toàn diện.

Tổng hợp cả ba tiêu chí theo đúng thứ tự ưu tiên đã đặt ra ở mục 3.6 — độ tin cậy, tuân thủ cấu trúc, chất lượng nội dung — `ising-calibration-31b` là lựa chọn tốt nhất trong 3 mô hình, và được chọn làm mô hình chính cho toàn bộ thực nghiệm còn lại của đề tài.

## 4.5. Kết quả chính: đóng góp của JSON ngữ nghĩa

Đây là kết quả trung tâm trả lời RQ3, đo trên mô hình chính (`ising-calibration-31b`), ba chế độ input, chấm điểm bởi ba judge độc lập (Gemini, GPT-5 Mini, DeepSeek) dùng nguyên văn cùng một rubric, trên toàn bộ N=200 ảnh.

Với mỗi ảnh, điểm tổng hợp của một chế độ được tính bằng trung bình cộng của sáu điểm tiêu chí trên chính ảnh đó (thang 1–5); từ đó thu được, với mỗi judge, ba dãy 200 điểm bắt cặp theo ảnh — một dãy cho mỗi chế độ. Điểm trung bình toàn mẫu của một chế độ, dùng để báo cáo ở Bảng 4.5, là trung bình cộng của dãy 200 điểm-trên-ảnh đó, tức:

Điểm(chế độ) = (1/200) × Σ²⁰⁰ⱼ₌₁ [ (1/6) × Σ₆ᵢ₌₁ điểm(ảnh j, tiêu chí i, chế độ) ]

Việc tính điểm theo từng ảnh trước, rồi mới lấy trung bình, giúp mỗi ảnh đóng góp đúng một lần vào kết quả cuối và cho phép thực hiện kiểm định thống kê bắt cặp (paired) giữa các chế độ trên cùng một ảnh — thay vì chỉ so sánh hai giá trị trung bình đơn lẻ.

**Bảng 4.5.** Điểm chất lượng khuyến nghị lái xe (Mean ± SD trên 200 ảnh) theo ba chế độ input, chấm bởi ba judge độc lập (thang 1–5).

| Judge | image_only | json_only | image+json | Xếp hạng |
|---|---|---|---|---|
| Gemini | 3,32 ± 0,95 | **4,53 ± 0,77** | 3,97 ± 0,95 | json > image+json > image |
| GPT-5 Mini | 3,13 ± 0,75 | 3,55 ± 1,14 | **3,96 ± 0,86** | image+json > json > image |
| DeepSeek | 3,11 ± 0,96 | **3,41 ± 1,17** | 3,40 ± 1,02 | json ≈ image+json > image |

Kết quả điểm trung bình này gần như không đổi so với lần đo trước đó ở N=200 (chênh lệch chỉ ở chữ số thập phân thứ ba), cho thấy kết luận ổn định, không nhạy với việc thêm hoặc bớt một vài mẫu. Độ lệch chuẩn (SD) tương đối lớn ở cả ba chế độ (0,75–1,17 trên thang 1–5) phản ánh mức độ đa dạng tự nhiên giữa các ảnh — có ảnh dễ (đường thẳng, ít vật cản) cho điểm cao ở mọi chế độ, có ảnh khó (giao lộ, thiếu vạch kẻ) cho điểm thấp ở mọi chế độ — nên khoảng cách trung bình giữa các chế độ cần được kiểm định thống kê thay vì chỉ so sánh trực quan hai con số, trình bày ở Bảng 4.6.

**Bảng 4.6.** Kiểm định ý nghĩa thống kê khi so sánh cặp giữa ba chế độ input, theo từng judge (N=200, dữ liệu bắt cặp theo ảnh; kiểm định t bắt cặp và Wilcoxon signed-rank; d = Cohen's d cho hiệu số bắt cặp).

| Judge | Cặp so sánh | t bắt cặp (df=200) | p (t-test) | Wilcoxon p | Cohen's d |
|---|---|---|---|---|---|
| Gemini | image_only vs json_only | t = −13,62 | **p < 0,001** | p < 0,001 | −0,96 (lớn) |
| Gemini | image_only vs image+json | t = −8,37 | **p < 0,001** | p < 0,001 | −0,59 (trung bình–lớn) |
| Gemini | json_only vs image+json | t = 7,28 | **p < 0,001** | p < 0,001 | 0,51 (trung bình) |
| GPT-5 Mini | image_only vs json_only | t = −4,33 | **p < 0,001** | p < 0,001 | −0,31 (nhỏ) |
| GPT-5 Mini | image_only vs image+json | t = −11,16 | **p < 0,001** | p < 0,001 | −0,79 (lớn) |
| GPT-5 Mini | json_only vs image+json | t = −4,93 | **p < 0,001** | p < 0,001 | −0,35 (nhỏ) |
| DeepSeek | image_only vs json_only | t = −2,83 | **p = 0,005** | p = 0,003 | −0,20 (nhỏ) |
| DeepSeek | image_only vs image+json | t = −3,19 | **p = 0,002** | p < 0,001 | −0,23 (nhỏ) |
| DeepSeek | json_only vs image+json | t = 0,09 | p = 0,930 | p = 0,625 | 0,01 (không đáng kể) |

Kết quả kiểm định củng cố mạnh mẽ kết luận ở Bảng 4.5: cả chín phép so sánh liên quan đến `image_only` (ba judge × hai cặp so sánh với `image_only`) đều có ý nghĩa thống kê ở mức p < 0,01, xác nhận `image_only` thấp hơn hai chế độ còn lại không phải do ngẫu nhiên. Kích thước hiệu ứng (Cohen's d) dao động từ nhỏ (DeepSeek, d ≈ 0,20–0,23) đến lớn (Gemini, d ≈ 0,59–0,96), phù hợp với việc Gemini đồng thời là judge có độ tin cậy cao nhất khi đối chiếu với con người (mục 4.6) — gợi ý rằng khoảng cách điểm số lớn hơn ở Gemini không chỉ là nhiễu thống kê mà phản ánh một tín hiệu thật rõ ràng hơn. Riêng phép so sánh `json_only` với `image+json` của DeepSeek không có ý nghĩa thống kê (p = 0,930, d ≈ 0,01) — xác nhận định lượng cho nhận định "json ≈ image+json" đã nêu ở Bảng 4.5, đây không phải hai chế độ có điểm số ngẫu nhiên gần nhau mà thực sự không khác biệt theo đánh giá của judge này.

Bảng 4.7 minh họa cách tính điểm trung bình tiêu chí bằng ví dụ chi tiết của judge Gemini, kèm độ lệch chuẩn của từng tiêu chí và kết quả kiểm định Wilcoxon cho hai so sánh chính (`image_only` với `json_only`, và `image_only` với `image+json`).

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

Cả sáu tiêu chí đều cho khác biệt có ý nghĩa thống kê mạnh (p < 0,001, chưa hiệu chỉnh cho so sánh bội — với sáu kiểm định đồng thời, ngưỡng Bonferroni tương ứng là p < 0,0083, vẫn được thỏa mãn ở tất cả sáu tiêu chí) khi so `image_only` với `json_only` hoặc với `image+json`. Độ lệch chuẩn cao nhất rơi vào `traffic_sign_rule` ở chế độ `image_only` (± 1,51) — hợp lý vì đây là tiêu chí phụ thuộc nhiều vào việc ảnh có hay không có biển báo dễ nhận biết bằng mắt, một yếu tố dao động mạnh giữa các ảnh; độ lệch chuẩn thấp nhất rơi vào `lane_ego_position` ở chế độ `json_only` (± 0,76) — phù hợp với việc thông tin vị trí làn ego được cấp sẵn dưới dạng số liệu chính xác trong JSON, ít phụ thuộc vào khả năng suy luận thị giác vốn dao động nhiều hơn giữa các ảnh.

Kết luận chắc chắn nhất, được cả ba judge độc lập đồng thuận không ngoại lệ, là chế độ `image_only` luôn đạt điểm thấp nhất. Sau khi khắc phục các lỗi hệ thống ở tầng perception (mục 4.1) và hoàn thiện tầng reasoning (mục 4.4), JSON ngữ nghĩa cải thiện rõ rệt chất lượng khuyến nghị lái xe so với chỉ dùng ảnh.

Tuy nhiên, kết luận cần được nêu có sắc thái ở một điểm: thứ hạng giữa `json_only` và `image+json` phụ thuộc vào judge được sử dụng — một phần ba số judge nghiêng về JSON đơn thuần, một phần ba nghiêng về kết hợp, một phần ba coi hai chế độ là ngang nhau — nên không có câu trả lời tuyệt đối cho câu hỏi "kết hợp ảnh và JSON có tốt hơn chỉ dùng JSON hay không". Đây chính là giá trị của phương pháp luận đa-judge: nếu chỉ sử dụng một judge duy nhất, nghiên cứu có nguy cơ báo cáo nhầm một kết luận "chắc chắn" trong khi thực chất đó chỉ là đặc thù riêng của judge đó.

## 4.6. Kiểm chứng độ tin cậy của phương pháp đánh giá

Với 120 cặp điểm (20 ảnh × 6 tiêu chí, mỗi cặp gồm một điểm của con người và một điểm của judge trên cùng ảnh/tiêu chí), ba chỉ số đồng thuận được định nghĩa như sau: Đồng thuận tuyệt đối bằng tỉ lệ số cặp có |điểm người − điểm judge| = 0; Đồng thuận trong sai số ≤1 bằng tỉ lệ số cặp có |điểm người − điểm judge| ≤ 1; Tương quan Pearson r được tính trên hai dãy 120 điểm tương ứng của người và của judge.

**Gemini so với con người** (N=20, 120 cặp điểm): đồng thuận tuyệt đối 44/120 = 36,7%, đồng thuận trong sai số ≤1 điểm 95/120 = 79,2%, tương quan Pearson 0,427.

Cần thận trọng khi đối chiếu con số này với MT-Bench: nghiên cứu đó báo cáo GPT-4 đạt 85% đồng thuận với con người trên một tác vụ so sánh cặp nhị phân, chỉ tính trên các cặp không hòa [5] — khác về bản chất so với việc chấm điểm tuyệt đối trên thang 1–5 của đề tài này (một quyết định nhị phân đúng/sai so với một mức độ khoan dung ±1 điểm trên thang 5 mức có baseline ngẫu nhiên cao hơn hẳn). Do khác loại tác vụ, khác định nghĩa đồng thuận, và khác quy mô kiểm chứng (N=20 so với hàng nghìn cặp), 79,2% và 85% không phải hai con số đối sánh trực tiếp được — việc chúng gần nhau về mặt số học không tự nó là bằng chứng cho độ tin cậy của Gemini, và luận văn không dùng đây làm căn cứ chính.

Bằng chứng vững chắc hơn, và là căn cứ chính cho quyết định dùng Gemini làm judge chính của đề tài, đến từ chính nội bộ nghiên cứu: Gemini đạt mức đồng thuận và tương quan cao hơn rõ rệt so với hai judge còn lại (GPT-5 Mini, DeepSeek), được kiểm chứng theo đúng cùng phương pháp, cùng thang đo, cùng mẫu N=20 (Bảng 4.8) — đây là một phép so sánh công bằng, cùng đơn vị đo, không phụ thuộc vào việc đối chiếu với một nghiên cứu khác dùng tác vụ khác.

**GPT-5 Mini so với con người** (cùng N=20): đồng thuận tuyệt đối 23,3%, trong sai số ≤1 điểm 62,5%, tương quan 0,194 — thấp hơn Gemini ở cả ba chỉ số, củng cố quyết định dùng Gemini làm judge chính.

**DeepSeek so với con người** (cùng N=20, 120 cặp điểm): đồng thuận tuyệt đối 25,8%, trong sai số ≤1 điểm 55,0%, tương quan 0,143 — thấp nhất trong ba judge, với tương quan Pearson gần như không có ý nghĩa thống kê thực tế trên cỡ mẫu này. Điểm đáng chú ý là DeepSeek có xu hướng chấm thấp hơn con người một cách hệ thống (chênh lệch trung bình người − DeepSeek = +1,21, lớn hơn nhiều so với Gemini và GPT), với nhiều trường hợp con người chấm 4–5 điểm nhưng DeepSeek chỉ chấm 1–2 điểm, đặc biệt ở hai tiêu chí `traffic_sign_rule` và `lane_ego_position` — có thể do DeepSeek diễn giải rubric khắt khe hơn, hoặc ít khoan dung hơn với các suy luận gián tiếp không có bằng chứng tường minh trong JSON.

**Bảng 4.8.** Xếp hạng độ tin cậy của ba judge khi đối chiếu với đánh giá của con người (N=20).

| Judge | Đồng thuận tuyệt đối | Trong sai số ≤1 | Tương quan Pearson |
|---|---|---|---|
| Gemini | **36,7%** | **79,2%** | **0,427** |
| DeepSeek | 25,8% | 55,0% | 0,143 |
| GPT-5 Mini | 23,3% | 62,5% | 0,194 |

Gemini vượt trội rõ rệt ở cả ba chỉ số so với hai judge còn lại, củng cố quyết định dùng Gemini làm judge chính cho toàn bộ các kết luận trọng tâm của đề tài (mục 4.4, 4.5); GPT-5 Mini và DeepSeek chỉ đóng vai trò tham khảo và đối chiếu chéo (mục 4.5).

Một phát hiện phương pháp luận đáng chú ý là tương quan giữa GPT và Gemini với nhau (0,511) còn cao hơn tương quan của mỗi judge với con người (0,427 và 0,194) — minh chứng trực tiếp rằng hai judge AI có xu hướng đồng ý với nhau nhiều hơn đồng ý với con người, có thể do cùng chia sẻ một mức độ nghiêm khắc nhất định khác với người chấm không chuyên. Tương quan giữa DeepSeek và Gemini cũng đạt 0,395 — vẫn cao hơn tương quan DeepSeek-người (0,143) — củng cố thêm cùng một phát hiện. Đây là lý do phương pháp luận của đề tài dùng đúng một judge cố định (Gemini) cho các so sánh chính, và dùng độ đồng thuận với con người — không phải độ đồng thuận giữa các judge — làm mốc chuẩn.

## 4.7. Hạn chế: rủi ro trùng lặp dữ liệu (data leakage)

200 ảnh đánh giá ở mục 4.1 được lấy ngẫu nhiên từ CULane — cùng nguồn dữ liệu mà mô hình phát hiện làn đường (`culane_res34.pth`) được pretrain — mà không đối chiếu với danh sách phân chia train/val/test chính thức, do bản dữ liệu cục bộ sử dụng không có sẵn thông tin này. Do đó, không loại trừ khả năng một phần ảnh đánh giá trùng với dữ liệu mà mô hình đã học qua, có thể khiến Accuracy và Precision tuyệt đối ở mục 4.1 lạc quan hơn khả năng tổng quát hóa thực tế. Hạn chế này không ảnh hưởng tới các so sánh tương đối (mức cải thiện trước/sau sửa lỗi, toàn bộ kết quả mục 4.4–4.6), vì các so sánh này dùng chung một lần detect, chỉ khác ở bước xử lý hoặc mô hình phía sau. Kết quả ở mục 4.2 — kiểm chứng trên dữ liệu real-life hoàn toàn độc lập — được thực hiện chính là để giảm thiểu rủi ro này.

## 4.8. Kiểm chứng khả năng tự nhận diện làn đường của VLM

Một câu hỏi đặt ra là: nếu không đi qua tầng UFLD-v2 và xử lý ngữ nghĩa, bản thân VLM (`ising-calibration-31b`) tự quan sát ảnh có nhận diện được ngữ nghĩa làn đường chính xác tới đâu? Để trả lời, một thực nghiệm bổ sung được thực hiện: gửi cho VLM duy nhất bức ảnh, không kèm bất kỳ JSON hay gợi ý nào, yêu cầu trả về JSON đúng schema `_brief.json` hiện tại (`lane_count`, `ego_lane`, `vehicle_offset`, `neighbor_lanes`, `road_shape`), trên cả hai bộ dữ liệu (CULane N=200, real-life N=200). Toàn bộ 200/200 ảnh ở cả hai bộ đều nhận được JSON hợp lệ.

**Bảng 4.9.** So sánh khả năng tự nhận diện ngữ nghĩa làn đường giữa pipeline UFLD-v2 và VLM.

| Bộ dữ liệu / Nhóm | Lane count Accuracy (Pipeline) | Lane count Accuracy (VLM) | Lane count MAE (Pipeline) | Lane count MAE (VLM) | Road shape bucket match (Pipeline) | Road shape bucket match (VLM) |
|---|---|---|---|---|---|---|
| CULane – Normal (N=176, có vạch kẻ) | **77,3%** | 54,5% | **0,273** | 0,477 | 84,1% | **95,5%** |
| CULane – Hard (N=24, không vạch kẻ) | 8,3% | **37,5%** | 1,958 | **0,792** | 20,8% | **91,7%** |
| CULane – Toàn bộ (N=200) | **69,0%** | 52,5% | **0,475** | 0,515 | 76,5% | **95,0%** |
| Real-life độc lập (N=200) | 50,5% | **53,5%** | 0,715 | **0,510** | 53,0% | **69,5%** |

Phát hiện chính từ Bảng 4.9 là: pipeline chuyên biệt (UFLD-v2) chỉ vượt trội rõ rệt VLM ở đúng một điều kiện — ảnh CULane có vạch kẻ, đúng domain mà nó được pretrain. Ở hai điều kiện còn lại — CULane không vạch kẻ, và toàn bộ dữ liệu real-life (domain khác CULane) — VLM tự nhận diện đạt hoặc vượt pipeline ở mọi chỉ số, đặc biệt rõ ở road shape (phân loại thẳng/cong), nơi VLM vượt trội pipeline ở cả bốn dòng của bảng. Điều này gợi ý rằng ưu thế của pipeline một phần đến từ việc cùng domain với dữ liệu huấn luyện, không chỉ từ bản chất kiến trúc của một detector chuyên biệt: pipeline trở nên giòn và dễ vỡ khi ra khỏi đúng vùng an toàn đó, trong khi VLM tổng quát — không được tinh chỉnh riêng cho bài toán làn đường — lại ổn định hơn.

## 4.9. Bàn luận: cơ chế đóng góp thực sự của JSON ngữ nghĩa

Phát hiện ở mục 4.8 đặt ra một câu hỏi hợp lý: nếu VLM tự nhận diện làn đường không hề yếu — thậm chí vượt pipeline ở nhiều điều kiện — thì tại sao `json_only` và `image+json` vẫn được chấm điểm cao hơn rõ rệt so với `image_only` ở mục 4.5? Đây không phải là một mâu thuẫn về số liệu, vì cả hai kết quả đều đã được kiểm chứng độc lập và vững chắc, mà là một điểm cần diễn giải lại chính xác hơn so với cách hiểu ngầm định ban đầu, theo đó "JSON thắng vì VLM không tự nhìn được làn đường".

Ba yếu tố hợp lý hơn để giải thích khoảng cách này được đề xuất như sau. Thứ nhất, hai thực nghiệm khác nhau về độ phức tạp tác vụ: thực nghiệm ở mục 4.8 yêu cầu VLM thực hiện đúng một việc — trích xuất số liệu theo schema cứng — trong khi chế độ `image_only` ở mục 4.5 yêu cầu VLM thực hiện ba việc dồn vào một lượt sinh duy nhất: tự nhận diện, tự suy luận, và tự viết đúng cấu trúc ba phần theo một prompt dài, nhiều ràng buộc (mục 3.5). Năng lực tốt ở một tác vụ hẹp không đảm bảo chất lượng tương đương khi tác vụ đó chỉ là một bước ẩn trong một chuỗi tác vụ ghép phức tạp hơn. Thứ hai, prompt của hai thực nghiệm không tương đương nhau: prompt `json_only` cấp sẵn dữ liệu đã trích xuất, có cấu trúc, để mô hình tham chiếu trực tiếp khi viết câu trả lời, trong khi prompt `image_only` chỉ yêu cầu chung chung việc quan sát ảnh khi có thể xác định đáng tin cậy, ít khung đỡ (scaffolding) hơn hẳn. Chênh lệch điểm số một phần có thể đến từ việc JSON cấp sẵn một khung viết mạch lạc và tự tin hơn, không chỉ từ việc bù đắp năng lực cảm nhận thị giác. Thứ ba, judge chấm chất lượng văn bản chứ không đối chiếu với ground truth: rubric sáu tiêu chí được chấm bởi một LLM đọc câu trả lời, không kiểm tra số liệu trong câu trả lời có đúng thực tế hay không. Một câu trả lời trích dẫn số liệu cụ thể ("làn 2/3, lệch 19,3%") có thể được judge đánh giá là có căn cứ và tự tin hơn, dù độ chính xác thực tế của con số đó chưa chắc cao hơn — đúng như thiên vị phong cách viết mà MT-Bench [5] đã ghi nhận là hạn chế cố hữu của LLM-as-judge (mục 2.4), và đề tài này đã chủ động kiểm chứng bằng đối chiếu con người thay vì tin tuyệt đối vào judge (mục 4.6).

Từ ba yếu tố trên, kết luận được điều chỉnh như sau: JSON ngữ nghĩa cải thiện chất lượng khuyến nghị lái xe không (chỉ) vì VLM "không tự nhìn được làn đường", mà nhiều khả năng hơn là vì JSON có cấu trúc đóng vai trò khung đỡ cho việc suy luận và trình bày trong một tác vụ ghép nhiều bước, giúp câu trả lời trở nên mạch lạc và tự tin hơn, ngay cả khi năng lực cảm nhận thị giác thô của VLM là chấp nhận được. Cách diễn giải này phù hợp hơn với toàn bộ bằng chứng hiện có, và không làm suy yếu kết luận của RQ3 — JSON vẫn cải thiện chất lượng khuyến nghị, đã được kiểm chứng bởi ba judge độc lập — mà chỉ làm rõ hơn cơ chế đằng sau kết luận đó.

Cần nhìn nhận rõ giới hạn của lập luận này: hai thực nghiệm ở mục 4.5 và 4.8 sử dụng hai prompt khác nhau về độ phức tạp và yêu cầu output, nên đây là cách giải thích hợp lý nhất dựa trên bằng chứng gián tiếp hiện có, chưa phải là kết quả của một thực nghiệm đối chứng trực tiếp (cùng một mức độ phức tạp prompt, chỉ khác nhau ở việc có hay không có JSON). Một thiết kế thực nghiệm như vậy được đề xuất như một hướng mở rộng ở mục 5.4.

---

# CHƯƠNG 5. KẾT LUẬN

## 5.1. Tóm tắt đóng góp

Đề tài xây dựng và kiểm chứng định lượng một pipeline hoàn chỉnh cho bài toán hiểu ngữ nghĩa làn đường và biển báo giao thông hỗ trợ ra quyết định lái xe bằng LLM, trên hai bộ dữ liệu chuẩn phổ biến (CULane, TT100K). Tầng suy luận theo hướng tiếp cận training-free — khác với các hệ VLM lái xe end-to-end (DriveGPT4 [2], DriveLM [3], LMDrive [4]) vốn đòi hỏi huấn luyện quy mô lớn (mục 2.3, 2.5) — trong khi tầng perception biển báo có một bước tinh chỉnh YOLOv8n quy mô nhẹ trên TT100K (mục 3.2). Các kết quả chính, có số liệu định lượng cụ thể, gồm:

1. **Module hiểu làn đường** đạt Accuracy 77,3% trên ảnh có vạch kẻ rõ (N=176/200), tổng quát hóa tốt sang dữ liệu độc lập tự thu thập (Precision 99,4%, Ego lane Accuracy 86,5%, N=200), nhưng giảm mạnh còn 8,3% trên 24 ảnh không có vạch kẻ rõ — một giới hạn cố hữu của detector dựa trên vạch kẻ (mục 4.1).
2. **Minh chứng cho tầm quan trọng của tầng diễn giải ngữ nghĩa**: lỗi off-by-one phát hiện trong quá trình xây dựng tầng chuyển đổi ngữ nghĩa khiến Accuracy ban đầu chỉ đạt 11,1%, dù bản thân UFLD-v2 đã đạt F1 = 76,0% ở tầng phát hiện [1]. Việc sửa lỗi này tự nó không phải một đóng góp thuật toán, nhưng là bằng chứng thực nghiệm cho luận điểm: chất lượng của một detector không tự động đảm bảo chất lượng của hệ hỗ trợ quyết định — khẳng định giá trị của việc đầu tư kiểm chứng kỹ lưỡng tầng diễn giải ngữ nghĩa (mục 2.1, 4.1).
3. **Module biển báo** đạt hiệu quả thực sự khi dữ liệu đủ dày (Precision/Recall 60,9% trên dữ liệu real-life), nhưng bị giới hạn trên CULane do đặc thù dataset thưa biển báo (6% ảnh có detection).
4. **JSON ngữ nghĩa cải thiện rõ rệt chất lượng khuyến nghị lái xe**: Gemini 3,32 → 4,53/5, tương đương +36%, có kiểm chứng nhất quán bởi ba judge độc lập (Gemini, GPT-5 Mini, DeepSeek) trên N=200 (mục 4.5).
5. **Phương pháp đánh giá LLM-as-a-judge có kiểm chứng**: đối chiếu với con người đạt 79,2% đồng thuận trong sai số ≤1 (N=20), và đối chiếu chéo ba judge cùng phương pháp xác định Gemini vượt trội rõ rệt GPT-5 Mini và DeepSeek ở cả ba chỉ số đồng thuận với con người (mục 4.6) — đây là căn cứ chính cho việc chọn Gemini làm judge chính, thay vì đối sánh trực tiếp với các nghiên cứu LLM-as-a-judge khác vốn dùng tác vụ và thang đo khác biệt về bản chất [5].
6. **Làm rõ cơ chế đóng góp của JSON ngữ nghĩa**: một kiểm chứng bổ sung cho thấy VLM tự nhận diện làn đường từ ảnh thô không hề yếu — thậm chí vượt pipeline UFLD-v2 khi thiếu vạch kẻ hoặc trên dữ liệu ngoài domain (mục 4.8) — nên JSON cải thiện chất lượng khuyến nghị chủ yếu nhờ vai trò khung đỡ cho suy luận và trình bày trong một tác vụ ghép nhiều bước, không (chỉ) vì bù đắp năng lực cảm nhận thị giác còn thiếu (mục 4.9).

**Ý nghĩa thực tiễn**. Các kết quả trên cho thấy một hệ hỗ trợ quyết định lái xe có khả năng diễn giải bằng ngôn ngữ tự nhiên có thể được xây dựng với chi phí thấp: tầng suy luận dùng VLM miễn phí qua API, không cần huấn luyện lại (training-free); tầng perception biển báo chỉ cần một bước tinh chỉnh nhẹ trên một mô hình nhỏ (YOLOv8n, ~3,2 triệu tham số) thay vì thu thập dữ liệu và huấn luyện một hệ end-to-end quy mô lớn. Kết quả này phù hợp làm nền tảng cho các ứng dụng dashcam hoặc hộp đen thông minh chi phí thấp, hoặc làm điểm khởi đầu để mở rộng sang dữ liệu giao thông Việt Nam mà không cần xây dựng lại từ đầu, chỉ cần tinh chỉnh nhẹ ở tầng perception làn đường và biển báo (mục 5.4).

## 5.2. Trả lời các câu hỏi nghiên cứu

- **RQ1–RQ2**: đã được trả lời định lượng đầy đủ ở mục 4.1–4.3.
- **RQ3**: JSON ngữ nghĩa cải thiện chất lượng khuyến nghị lái xe so với chỉ dùng ảnh — kết luận có kiểm chứng vững chắc (mục 4.5), với cơ chế đóng góp được làm rõ thêm ở mục 4.8–4.9.
- **RQ4**: `ising-calibration-31b` là lựa chọn phù hợp nhất trong phạm vi mô hình khảo sát, dựa trên độ tin cậy, tuân thủ cấu trúc và chất lượng nội dung (mục 4.4).
- **RQ5**: LLM-as-a-judge (Gemini) đạt độ tin cậy chấp nhận được khi đối chiếu với con người, tốt hơn hai judge thay thế đã thử nghiệm — GPT-5 Mini, DeepSeek — ở cả ba chỉ số đồng thuận (mục 4.6).

## 5.3. Hạn chế

- **Module hiểu làn đường ở tầng pipeline thị giác máy tính phụ thuộc mạnh vào vạch kẻ đường và vào việc cùng domain với dữ liệu huấn luyện**: trên 24/200 ảnh CULane thuộc các tình huống không có vạch kẻ rõ, Accuracy số làn giảm từ 77,3% xuống còn 8,3%, dù Precision vẫn đạt 100% (mục 4.1). Kiểm chứng bổ sung ở mục 4.8 cho thấy đây là hạn chế của riêng pipeline thị giác máy tính, không phải của cách tiếp cận nói chung: VLM tự nhận diện trực tiếp từ ảnh không chia sẻ đúng điểm yếu này, thậm chí vượt trội pipeline ở chính hai điều kiện đó — mở ra hướng thiết kế hybrid (mục 5.4).
- Rủi ro trùng lặp dữ liệu (data leakage) trên dữ liệu CULane (mục 4.7), giảm thiểu một phần bằng kiểm chứng độc lập trên dữ liệu real-life.
- So sánh mô hình LLM và judge giới hạn trong các lựa chọn miễn phí, chi phí thấp, chưa mở rộng sang các mô hình thương mại lớn (Gemini, GPT, Deepseek phiên bản mới nhất, hoặc Claude...).
- Module biển báo trên CULane bị giới hạn bởi mật độ dữ liệu thưa của bản thân dataset.

## 5.4. Hướng phát triển tiếp theo

**Mở rộng sang dữ liệu và bối cảnh giao thông Việt Nam**. Sau khi đã chứng minh pipeline hoạt động hiệu quả và đáng tin cậy trên các bộ dữ liệu chuẩn quốc tế (CULane, TT100K), hướng phát triển tự nhiên tiếp theo là áp dụng và đánh giá lại trên dữ liệu giao thông Việt Nam thực tế — đặc thù vạch kẻ đường, biển báo theo quy chuẩn QCVN, mật độ xe máy cao, hành vi giao thông khác biệt. Bước đầu đã được khảo sát sơ bộ thông qua bộ dữ liệu real-life tự thu thập (mục 4.2), cho thấy tín hiệu tích cực về khả năng tổng quát hóa của module hiểu làn đường.

**Kiến trúc hybrid pipeline thị giác máy tính kết hợp cơ chế fallback sang VLM**. Dựa trên phát hiện ở mục 4.8 — VLM tự nhận diện vượt pipeline khi thiếu vạch kẻ hoặc trên domain khác CULane — một hướng phát triển cụ thể là sử dụng pipeline UFLD-v2 làm nguồn chính, nhanh và chính xác cao khi đúng điều kiện, và tự động chuyển sang kết quả tự nhận diện của VLM khi pipeline trả về tín hiệu thấp (ví dụ `lane_count=0` hoặc độ tin cậy thấp) — tận dụng ưu điểm của cả hai nguồn thay vì chỉ dùng một.

**Thực nghiệm đối chứng làm rõ cơ chế đóng góp của JSON**. Mục 4.9 đưa ra cách diễn giải hợp lý nhất dựa trên bằng chứng gián tiếp hiện có, nhưng chưa được kiểm chứng bằng một thực nghiệm đối chứng trực tiếp. Một thiết kế khả thi là chạy chế độ `image_only` với một prompt được viết lại có cùng mức độ khung đỡ như `json_only` — ví dụ yêu cầu VLM tự trích xuất một JSON có cấu trúc từ ảnh trước, rồi mới viết khuyến nghị dựa trên chính JSON tự trích xuất đó, tức hai bước thay vì một bước như hiện tại — rồi so sánh điểm số với `json_only` gốc. Nếu khoảng cách thu hẹp đáng kể, giả thuyết "khung đỡ" được củng cố thêm; nếu không, kết quả gợi ý vẫn còn một khoảng cách thực sự về năng lực cảm nhận thị giác trong bối cảnh suy luận phức hợp.

**Cải thiện tầng suy luận bằng cấu trúc tư duy có kiểm chứng**. Hiện tại tầng LLM Reasoning (mục 3.5) sử dụng một lệnh gọi prompt trực tiếp (single-shot). Các kỹ thuật cấu trúc tư duy gần đây như RATT — Retrieval Augmented Thought Tree [18] — kết hợp lập kế hoạch, nhìn trước, và xác minh sự kiện qua truy hồi thông tin (RAG) ở từng bước suy luận, là một hướng khả thi để giảm thêm rủi ro "ảo giác" trong khuyến nghị lái xe, đặc biệt ở các tình huống phức tạp như giao lộ và nhập làn, đã được xác định là điểm yếu ở mục 5.3.

**Các hướng khác**: bổ sung khả năng phân biệt làn ngược chiều và đường một chiều/hai chiều; cải thiện module biển báo bằng dữ liệu có mật độ cao hơn; mở rộng kiểm chứng đồng thuận người–AI ở quy mô lớn hơn, có thể áp dụng khung lấy mẫu thích ứng của [15] thay vì N=20 chọn ngẫu nhiên như hiện tại; thử nghiệm thêm các mô hình LLM thương mại tiên tiến hơn.

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
