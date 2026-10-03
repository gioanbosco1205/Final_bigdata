# Kiểm tra notebook GA4 ngày 03/10/2026

Đã rà soát và sửa notebook `DoAn-BigData-GA4-SourceCode-Final.ipynb`, đồng bộ `build_final_notebook.py`, rồi thực thi tuần tự bằng một kernel Jupyter mới. Kết quả kiểm thử: **12/12 block thành công với dữ liệu tổng hợp được ghi nhãn; 25/25 bài kiểm tra đạt**. Lần chạy BigQuery thật đã thử toàn bộ 12 block: BLOCK 0 thành công; BLOCK 1 thiếu Application Default Credentials; các block sau không có dữ liệu đầu vào. Chưa có kết quả thực nghiệm mới từ BigQuery.

## Phát hiện ảnh hưởng trực tiếp đến kết luận

Bốn CSV cũ trong `data/` trùng khớp toàn bộ giá trị với bộ sinh dữ liệu `_generate_calibrated_sample` của `src/bq_client.py` (sai số so sánh 1e-10). Đối chiếu được thực hiện bằng cách chạy riêng hàm sinh dữ liệu; không tạo BigQuery client, không gọi cloud và không thay thế các CSV. Bảng RFM cũ có **1.069/4.500** Recency nằm ngoài 0–91 ngày. Không dùng các số liệu cũ để khẳng định hiệu quả trên dữ liệu GA4 thật. [Bằng chứng đối chiếu](report_assets/notebook_review_2026-10-03/legacy_data_provenance.json).

Nguồn công khai GA4 đã được làm mờ và có thể hạn chế tính nhất quán nội bộ. Các nhận xét kinh doanh phải được xem là giả thuyết mô tả trong cửa sổ nghiên cứu, cần kiểm chứng thêm trước khi đưa ra kết luận thực tế. [Tài liệu chính thức Google](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset).

## Phân tích và sửa từng block

| Block | Đánh giá và sửa đổi |
|---|---|
| 0 — Môi trường | Kiểm tra thư viện trước khi cài; dùng đúng Python của kernel. Script cũ không xử lý `%pip` và có thể dừng ngay từ cell đầu; đã thay bằng trình chạy Jupyter thật. |
| 1 — BigQuery | Giữ luồng chỉ truy vấn cloud, không nạp cache mẫu. Định nghĩa helper trước xác thực để lỗi phụ thuộc có thông báo rõ. Giới hạn mỗi query 10 GiB billed; kiểm tra phạm vi nguồn/ngày; xuất job ID, SQL và SHA-256 CSV/Parquet/SQL. |
| 2 — EDA | KPI toàn bộ lấy từ hàng `overall`; không cộng users của các nhóm. Top kênh được xếp theo số user ngay trong Python. Nhãn biểu đồ thiết bị ghi rõ user–thiết bị có thể trùng; purchase/phiên là tỷ số sự kiện, chưa phải conversion rate của phiên mua hàng. |
| 3 — Phễu | Giữ kiểm tra chuỗi timestamp tăng nghiêm ngặt trên cùng thiết bị, đếm user riêng biệt và kiểm tra số bước giảm dần. Mẫu số 0 trả NaN. Đây là phễu user nhiều phiên trong ba tháng, chưa xác minh cùng một giỏ hoặc cùng phiên. |
| 4 — Đặc trưng | Recency dựa trên hoạt động gần nhất; Frequency đếm phiên; Monetary tổng sự kiện purchase. Kiểm tra user thiếu/trùng và phạm vi Recency. Tỷ lệ thêm giỏ/xem không chứng minh bỏ giỏ. |
| 5 — Tiền xử lý | Chuyển đặc trưng về float64 để tránh lỗi clipping trên nullable Int64. Giữ nguyên nguồn `df_rfm`. Từ chối giá trị âm/vô cực; thống kê giá trị thiếu điền 0. Ghi ngưỡng clipping, số hàng bị cắt, mean/std và tương quan. Ngưỡng dùng Q01/Q99, không gọi là IQR Q25/Q75. Cột mua hàng hiếm không bị xóa khi Q99=0. |
| 6 — K-Means | Huấn luyện trên toàn bộ user; so sánh K=2..8 theo Inertia/Silhouette. Hiển thị K có điểm ước lượng cao nhất và quy mô cụm. K=4 là lựa chọn nghiên cứu để có bốn hồ sơ, chưa khẳng định tối ưu tổng quát. |
| 7 — PCA | Tính phương sai giải thích khi chạy; xuất ba thành phần, vẽ hai thành phần. Giới hạn tối đa 5.000 điểm/cụm khi vẽ, không bỏ user khỏi huấn luyện/xuất kết quả. Đã kiểm tra hình: chữ tiếng Việt, trục và chú thích đọc được. |
| 8 — Chân dung | Thay nhãn VIP/trung thành/rủi ro bằng mô tả số liệu: doanh thu trung bình cao, hoạt động gần nhất cách xa, tỷ lệ thêm giỏ/xem cao và nhóm còn lại. Tổng hợp trên thang đo gốc. Đây là nhãn tương đối được gán theo thứ tự quy tắc, chưa phải nhãn hành vi đã được xác thực. |
| 9 — Mua kèm | Ghép khóa user + transaction ID bằng JSON để không gộp nhầm đơn của hai user trùng mã. Lọc placeholder tên sản phẩm không phân biệt hoa/thường. Apriori giới hạn tập hai sản phẩm; xét cặp một lần, tạo cả hai hướng. Lọc bằng độ chính xác đầy đủ, chỉ làm tròn khi hiển thị. Support có điều kiện trên đơn đa sản phẩm. Không tạo luật nếu dữ liệu không đạt ngưỡng. |
| 10 — Diễn giải | Chặn kết quả phân cụm/luật cũ không khớp query hiện tại. Nhận xét sinh từ số liệu trong bộ nhớ; không giả lập phản hồi Gemini. Đề xuất kinh doanh được ghi là giả thuyết để kiểm thử. |
| 11 — Xuất kết quả | Kiểm tra job ID, metadata và SHA-256 file trước xuất ZIP. Bổ sung audit tiền xử lý, tương quan và thông tin Python/thư viện để tái lập. ZIP chỉ chứa các file được liệt kê, không gom cache cũ. |

Silhouette trong notebook được ước lượng trên tối đa 2.000 user, bảo đảm đại diện từng cụm. Nó giúp so sánh các K đã thử, không đủ để khẳng định một lựa chọn tối ưu trên mọi dữ liệu. [Tài liệu scikit-learn](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html).

## Bằng chứng thực thi

- [Notebook đã chạy với dữ liệu kiểm thử](report_assets/notebook_review_2026-10-03/fixture/DoAn-BigData-GA4-SourceCode-Final_fixture_executed.ipynb), [bản HTML](report_assets/notebook_review_2026-10-03/fixture/notebook.html), [trạng thái 12 block](report_assets/notebook_review_2026-10-03/fixture/summary.json).
- [Notebook lần chạy BigQuery thật](report_assets/notebook_review_2026-10-03/live/DoAn-BigData-GA4-SourceCode-Final_live_executed.ipynb), [bản HTML](report_assets/notebook_review_2026-10-03/live/notebook.html), [trạng thái và lỗi từng block](report_assets/notebook_review_2026-10-03/live/summary.json).
- [Kết quả 25 bài kiểm tra](report_assets/notebook_review_2026-10-03/unit_tests.json), [log chi tiết](report_assets/notebook_review_2026-10-03/unit_tests.log), [mã kiểm thử](tests/test_master_notebook.py).

Fixture dùng 6.000 user và 600 đơn tổng hợp, có ID bắt đầu `fixture-`; job ID ghi `SYNTHETIC-FIXTURE-NOT-BIGQUERY`. Notebook và các hình đều ghi nhãn dữ liệu tổng hợp. Fixture kiểm chứng thực thi Python, mô hình, biểu đồ và xuất file; không kiểm chứng kết quả SQL trên cloud. SQL được kiểm tra cú pháp theo dialect BigQuery; phễu và khóa giao dịch có kiểm thử thực thi SQL bằng DuckDB. Các chỉ số Silhouette/PCA/doanh thu trong fixture không phải kết quả nghiên cứu GA4.

## Chạy lại trên dữ liệu thật

Trên Colab, mở notebook và chọn **Restart & Run All**, đăng nhập Google khi BLOCK 1 yêu cầu. Project mặc định là `bigdata-510510`; cần đúng quyền tạo query job và truy cập dataset công khai. Trên máy cá nhân, cấu hình ADC bằng tài khoản của bạn; không đưa token hoặc khóa vào notebook.

```powershell
gcloud auth application-default login
$env:GCP_PROJECT_ID = 'bigdata-510510'
python -m pip install -r requirements.txt -r requirements-notebook-review.txt
python verify_master_notebook.py --mode live
```

Lệnh ADC chỉ là hướng dẫn để chủ tài khoản thực hiện; phiên kiểm tra này chưa có credentials và chưa đăng nhập thay người dùng. [Hướng dẫn ADC của Google Cloud](https://cloud.google.com/docs/authentication/provide-credentials-adc).

Để tái chạy kiểm tra kỹ thuật:

```powershell
python -m unittest tests.test_master_notebook -v
python verify_master_notebook.py --mode fixture
```

Các vấn đề phương pháp còn cần đánh giá bằng dữ liệu thật: số purchase bị trùng, ảnh hưởng placeholder trong dữ liệu làm mờ, độ nhạy cụm với seed và các đặc trưng tương quan, ổn định theo thời kỳ, tác động của quy ước điền thiếu 0, và độ tin cậy luật trên tập kiểm chứng ngoài mẫu.
