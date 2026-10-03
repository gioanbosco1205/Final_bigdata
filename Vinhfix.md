# Vinhfix — Kế hoạch chỉnh sửa và kiểm tra notebook GA4

**Ngày thực hiện:** 03/10/2026
**Notebook:** [DoAn-BigData-GA4-SourceCode-Final.ipynb](DoAn-BigData-GA4-SourceCode-Final.ipynb)
**Mục tiêu:** chạy toàn bộ các block, phân tích những phần chưa hợp lý, sửa lỗi và hoàn thiện cách trình bày, phương pháp phân tích cùng bằng chứng kiểm tra.

## 1. Trạng thái hiện tại

- **Đã sửa notebook và đồng bộ script tạo notebook.**
- **12/12 block chạy thành công trong kernel Jupyter mới với dữ liệu kiểm thử tổng hợp.**
- **25/25 bài kiểm tra đạt**, không có bài lỗi hoặc bị bỏ qua.
- **Đã thử chạy toàn bộ notebook ở chế độ BigQuery thật:** BLOCK 0 thành công; BLOCK 1 lỗi do thiếu Application Default Credentials; các block còn lại thiếu kết quả đầu vào.
- **Chưa hoàn tất kiểm chứng số liệu trên BigQuery thật.** Cần đăng nhập Google Cloud để tiếp tục phần này.

## 2. Kế hoạch đã thực hiện

### Giai đoạn 1 — Kiểm tra hiện trạng

- [x] Xác định notebook chính, các script, dữ liệu và bộ kiểm thử liên quan.
- [x] Đọc toàn bộ cell Python, SQL và phần giải thích của notebook.
- [x] Kiểm tra môi trường Python, thư viện và khả năng xác thực Google Cloud.
- [x] Chạy bộ kiểm thử ban đầu: 19/19 bài đạt.
- [x] Phân tích thêm các vấn đề phương pháp và nguồn gốc dữ liệu mà bộ kiểm thử cũ chưa bao phủ.

### Giai đoạn 2 — Chỉnh sửa từng block

| Block | Công việc đã thực hiện | Mục đích |
|---|---|---|
| **0 — Khởi tạo môi trường** | Kiểm tra thư viện trước khi cài; dùng đúng Python của kernel. Thay script thực thi cũ bằng trình chạy Jupyter thật. | Tránh cài lại không cần thiết và lỗi xử lý notebook magic `%pip`. |
| **1 — Kết nối BigQuery** | Định nghĩa helper trước khi xác thực; báo lỗi phụ thuộc rõ ràng; kiểm tra phạm vi nguồn/ngày; giới hạn mỗi query job 10 GiB billed. Lưu SQL, job ID, metadata và SHA-256 các file dữ liệu. | Bảo đảm truy vấn có nguồn gốc kiểm chứng được và không âm thầm thay bằng dữ liệu mẫu. |
| **2 — EDA và KPI** | Giữ KPI toàn bộ từ hàng `overall`, không cộng user giữa các nhóm. Xếp Top kênh theo số user trong Python; sửa nhãn biểu đồ thiết bị để thể hiện user có thể xuất hiện ở nhiều thiết bị. | Tránh đếm trùng và diễn giải sai mẫu số. |
| **3 — Phễu mua hàng** | Giữ kiểm tra chuỗi timestamp tăng nghiêm ngặt trên cùng thiết bị; kiểm tra số user giảm dần qua các bước. Mẫu số bằng 0 trả NaN. Làm rõ phễu có thể kéo dài nhiều phiên. | Tránh tỷ lệ không xác định bị trình bày như 0% và tránh suy luận đây là cùng một giỏ hàng. |
| **4 — Đặc trưng khách hàng** | Làm rõ Recency dựa trên hoạt động gần nhất, Frequency đếm phiên, Monetary tổng giá trị sự kiện purchase. Giữ kiểm tra user thiếu/trùng và phạm vi Recency. | Thống nhất ý nghĩa đặc trưng với SQL thực tế. |
| **5 — Tiền xử lý** | Chuyển đặc trưng sang float64; giữ dữ liệu nguồn; từ chối giá trị âm/vô cực; thống kê giá trị thiếu được điền 0. Xuất ngưỡng clipping, số hàng bị cắt, mean/std và tương quan. | Tránh lỗi clipping trên nullable Int64 và tránh thay đổi dữ liệu bất thường mà không có thông báo. |
| **6 — K-Means** | Huấn luyện trên toàn bộ user; so sánh K=2..8 bằng Inertia và Silhouette ước lượng. Hiển thị K có điểm cao nhất và quy mô các cụm; ghi rõ K=4 là lựa chọn nghiên cứu. | Cung cấp căn cứ đánh giá, không khẳng định K=4 tối ưu khi chưa đủ bằng chứng. |
| **7 — PCA** | Tính phương sai giải thích khi chạy; xuất ba thành phần và vẽ hai thành phần đầu. Giới hạn số điểm vẽ, vẫn giữ toàn bộ user trong kết quả. Kiểm tra hình, trục, chú thích và chữ tiếng Việt. | Biểu đồ dễ đọc và không làm sai quy mô dữ liệu huấn luyện. |
| **8 — Chân dung khách hàng** | Thay nhãn VIP/trung thành/rủi ro bằng các nhãn mô tả số liệu tương đối. Tổng hợp đặc trưng trên thang đo gốc. | Tránh suy luận lòng trung thành hoặc nguy cơ rời bỏ chỉ từ quy tắc gán tên cụm. |
| **9 — Luật mua kèm** | Ghép khóa user + transaction ID bằng JSON; lọc placeholder tên sản phẩm không phân biệt hoa/thường. Xét mỗi cặp một lần và tạo cả hai hướng; lọc bằng số chưa làm tròn. | Tránh gộp nhầm đơn của hai user, giảm tính toán lặp và giữ độ chính xác của ngưỡng luật. |
| **10 — Diễn giải kết quả** | Chặn kết quả phân cụm/luật cũ không khớp query hiện tại. Làm rõ nhận xét sinh bằng Python; các đề xuất kinh doanh là giả thuyết để kiểm thử. | Chỉ diễn giải kết quả thuộc đúng lần chạy và không trình bày nhận xét như phản hồi Gemini. |
| **11 — Xuất báo cáo** | Đối chiếu job ID, metadata và SHA-256 trước khi đóng ZIP. Bổ sung audit tiền xử lý, tương quan, phiên bản Python và thư viện. | Giúp kiểm tra tính toàn vẹn và tái lập kết quả. |

Các giới hạn phương pháp đã được ghi rõ trong notebook:

- Clipping dùng Q01/Q99, không gọi là IQR Q25/Q75.
- Silhouette được ước lượng trên tối đa 2.000 user có đại diện từng cụm.
- Tỷ lệ thêm giỏ/xem không chứng minh khách hàng bỏ giỏ.
- Khai phá mua kèm giới hạn tập hai sản phẩm; support có điều kiện trên đơn đa sản phẩm hợp lệ.
- Số sự kiện purchase chưa tương đương số đơn hàng đã khử trùng.

### Giai đoạn 3 — Kiểm chứng nguồn dữ liệu

- [x] Đối chiếu bốn CSV cũ trong `CODE/data/` với hàm `_generate_calibrated_sample` của `CODE/src/bq_client.py`.
- [x] Xác nhận toàn bộ giá trị trùng khớp bộ sinh dữ liệu tổng hợp với sai số số học 1e-10.
- [x] Phát hiện 1.069/4.500 user trong RFM cũ có Recency ngoài khoảng 0–91 ngày của nghiên cứu.
- [x] Bổ sung thông tin nguồn gốc dữ liệu vào notebook, README và tài liệu dataset.
- [x] Giữ nguyên các CSV; không dùng chúng để thay kết quả truy vấn BigQuery của notebook chính.

**Kết luận:** bốn CSV cũ là dữ liệu tổng hợp phục vụ chạy thử. Không dùng các số liệu này để khẳng định kết quả thực nghiệm trên GA4 thật.

### Giai đoạn 4 — Chạy và kiểm tra sau sửa

- [x] Bổ sung kiểm thử lỗi gộp transaction ID giữa các user.
- [x] Bổ sung kiểm thử dữ liệu âm, mẫu số bằng 0, độ chính xác luật và kết quả cũ.
- [x] Bổ sung kiểm thử phát hiện dữ liệu xuất bị thay đổi qua SHA-256.
- [x] Chạy bộ kiểm thử cuối: **25/25 bài đạt**.
- [x] Chạy **12/12 block** bằng kernel Jupyter mới với **6.000 user và 600 đơn tổng hợp**.
- [x] Ghi nhãn dữ liệu tổng hợp trong notebook và các hình kiểm thử.
- [x] Lưu notebook đã chạy, HTML, biểu đồ, log và trạng thái từng block.
- [x] Thử toàn bộ 12 block ở chế độ BigQuery thật và lưu lỗi xác thực/phụ thuộc.
- [x] Đồng bộ nội dung notebook với `build_final_notebook.py`.
- [x] Kiểm tra định dạng thay đổi bằng `git diff --check`.

**Phạm vi xác nhận:** fixture kiểm chứng luồng Python, mô hình, biểu đồ và xuất file. SQL được kiểm tra cú pháp BigQuery; phễu và khóa giao dịch được kiểm thử thực thi bằng DuckDB. Những kiểm tra này chưa thay thế việc chạy SQL trên BigQuery thật.

## 3. Các file liên quan đã sửa hoặc bổ sung

| File | Nội dung |
|---|---|
| [Notebook chính](DoAn-BigData-GA4-SourceCode-Final.ipynb) | Mã nguồn và phần giải thích đã chỉnh sửa. |
| [build_final_notebook.py](build_final_notebook.py) | Đồng bộ script tạo notebook. |
| [verify_master_notebook.py](verify_master_notebook.py) | Chạy kernel mới với chế độ `live` hoặc `fixture`, lưu bằng chứng từng block. |
| [run_master_notebook_offline.py](run_master_notebook_offline.py) | Chuyển sang luồng kiểm thử bằng Jupyter với dữ liệu tổng hợp được ghi nhãn. |
| [test_master_notebook.py](tests/test_master_notebook.py) | Bộ 25 bài kiểm tra notebook. |
| [notebook_fixtures.py](tests/notebook_fixtures.py) | Dữ liệu kiểm thử tổng hợp được định nghĩa riêng. |
| [requirements-notebook-review.txt](requirements-notebook-review.txt) | Thư viện bổ sung cho thực thi và kiểm thử notebook. |
| [README dự án](README.md) | Bổ sung trạng thái kiểm tra và nguồn gốc dữ liệu cũ. |
| [README dataset](data/README_DATASET.md) | Ghi rõ CSV cũ là dữ liệu tổng hợp. |
| [Báo cáo phân tích](NOTEBOOK_REVIEW_2026-10-03.md) | Phát hiện, sửa đổi, bằng chứng và giới hạn kiểm chứng. |

## 4. Bằng chứng kết quả

- [Notebook kiểm thử đã chạy](report_assets/notebook_review_2026-10-03/fixture/DoAn-BigData-GA4-SourceCode-Final_fixture_executed.ipynb).
- [Bản HTML kiểm thử](report_assets/notebook_review_2026-10-03/fixture/notebook.html).
- [Trạng thái 12 block kiểm thử](report_assets/notebook_review_2026-10-03/fixture/summary.json).
- [Notebook lần chạy BigQuery thật](report_assets/notebook_review_2026-10-03/live/DoAn-BigData-GA4-SourceCode-Final_live_executed.ipynb).
- [Lỗi từng block khi chạy BigQuery thật](report_assets/notebook_review_2026-10-03/live/summary.json).
- [Kết quả 25 bài kiểm tra](report_assets/notebook_review_2026-10-03/unit_tests.json) và [log chi tiết](report_assets/notebook_review_2026-10-03/unit_tests.log).
- [Bằng chứng đối chiếu CSV cũ](report_assets/notebook_review_2026-10-03/legacy_data_provenance.json).

## 5. Kế hoạch tiếp tục với BigQuery thật

- [ ] Cấu hình Application Default Credentials hoặc đăng nhập khi chạy trên Colab.
- [ ] Kiểm tra quyền của project chạy job; notebook hiện mặc định `bigdata-510510`.
- [ ] Restart & Run All toàn bộ notebook trên dữ liệu thật.
- [ ] Xác nhận cả bốn query job thành công và metadata khớp kết quả xuất.
- [ ] Kiểm tra số user, phiên, purchase, doanh thu và dữ liệu thiếu/bất thường từ kết quả thật.
- [ ] Phân tích lại bảng chọn K, quy mô cụm, PCA, nhãn chân dung và các luật mua kèm.
- [ ] Đánh giá độ nhạy với seed, đặc trưng tương quan, quy ước điền thiếu và cửa sổ thời gian.
- [ ] Hoàn thiện kết luận nghiên cứu bằng số liệu thật, chỉ sử dụng hình và bảng từ lần chạy đã xác minh.

### Lệnh thực hiện từ thư mục CODE

```powershell
gcloud auth application-default login
$env:GCP_PROJECT_ID = 'bigdata-510510'
python -m pip install -r requirements.txt -r requirements-notebook-review.txt
python verify_master_notebook.py --mode live
```

Để chạy lại kiểm thử kỹ thuật:

```powershell
python -m unittest tests.test_master_notebook -v
python verify_master_notebook.py --mode fixture
```

**Điều kiện hoàn tất phần thực nghiệm:** toàn bộ 12 block chạy thành công với dữ liệu BigQuery thật; kết quả và file xuất có nguồn gốc khớp query job; nhận xét trong báo cáo được cập nhật theo các kết quả đó.
