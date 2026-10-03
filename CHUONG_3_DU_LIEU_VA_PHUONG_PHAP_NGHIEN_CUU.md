# CHƯƠNG 3. DỮ LIỆU VÀ PHƯƠNG PHÁP NGHIÊN CỨU

## 3.1. Nguồn dữ liệu sử dụng trong đồ án

### 3.1.1. Giới thiệu bộ dữ liệu GA4

Trong đồ án này, dữ liệu được lựa chọn là **Google Analytics 4 (GA4) Obfuscated Sample E-commerce** của Google Merchandise Store. Đây là bộ dữ liệu công khai được lưu trên Google BigQuery với tên **bigquery-public-data.ga4_obfuscated_sample_ecommerce**. Bộ dữ liệu ghi lại những hành động của người dùng khi truy cập website thương mại điện tử, ví dụ như xem trang, xem sản phẩm, thêm sản phẩm vào giỏ hàng, bắt đầu thanh toán và mua hàng.

Việc chọn dữ liệu GA4 phù hợp với mục tiêu của đồ án vì có thể quan sát hành vi khách hàng ở nhiều giai đoạn, từ lúc tìm hiểu sản phẩm cho đến khi hoàn tất đơn hàng. Ngoài việc tính các chỉ số kinh doanh cơ bản, dữ liệu sự kiện còn cho phép xây dựng phễu mua hàng, mô tả đặc điểm từng người dùng và tìm các sản phẩm thường được mua cùng nhau.

Trong notebook tổng hợp, phạm vi thời gian được đặt từ **ngày 01/11/2020 đến ngày 31/01/2021**. Điều kiện thời gian này được thể hiện qua bộ lọc _TABLE_SUFFIX trong câu lệnh SQL. Tuy nhiên, bốn file SQL riêng trong thư mục sql hiện chưa có cùng bộ lọc ngày. Khi sử dụng các file đó để truy vấn lại BigQuery, cần bổ sung điều kiện thời gian để các kết quả có cùng phạm vi nghiên cứu.

### 3.1.2. Cấu trúc dữ liệu GA4

GA4 lưu dữ liệu theo mô hình **sự kiện**. Mỗi dòng dữ liệu tương ứng với một hành động được ghi nhận, thay vì một dòng đại diện cho toàn bộ quá trình mua sắm của một khách hàng. Những trường được sử dụng trong đồ án gồm tên sự kiện (event_name), ngày phát sinh (event_date), mã người dùng ẩn danh (user_pseudo_id), loại thiết bị và nguồn truy cập.

Một đặc điểm cần chú ý là dữ liệu GA4 có các trường lồng nhau. Trường event_params chứa những tham số như mã phiên truy cập (ga_session_id) và thời gian tương tác (engagement_time_msec). Trường items chứa danh sách sản phẩm liên quan đến một sự kiện mua hàng. Để lấy dữ liệu từ các trường này, các câu lệnh SQL trong đồ án sử dụng toán tử UNNEST của BigQuery.

Tùy theo câu hỏi nghiên cứu, dữ liệu được tổng hợp ở các mức khác nhau. Phần đánh giá kênh tiếp thị được tổng hợp theo traffic_medium; phễu mua hàng được tổng hợp theo người dùng và thiết bị; đặc trưng RFM được tính cho từng user_pseudo_id; còn phân tích giỏ hàng dựa trên transaction_id và item_name. Mã user_pseudo_id đã được ẩn danh nên trong báo cáo, khái niệm “người dùng” được hiểu là mã người dùng trong GA4, không khẳng định chắc chắn là một cá nhân duy nhất ngoài thực tế.

### 3.1.3. Các bảng dữ liệu phục vụ phân tích

Sau bước truy vấn hoặc chuẩn bị dữ liệu ngoại tuyến, đồ án sử dụng bốn bảng chính. Các file CSV hiện nằm trong thư mục data và có cấu trúc như sau:

| Tập dữ liệu | Quy mô file hiện có | Vai trò trong đồ án |
| --- | ---: | --- |
| eda_overview.csv | 7 dòng, 7 cột | Tổng hợp người dùng, phiên, lượt xem trang, đơn hàng và doanh thu theo kênh tiếp thị. |
| funnel_analysis.csv | 3 dòng, 10 cột | Thống kê bốn bước mua hàng theo desktop, mobile và tablet. |
| rfm_features.csv | 4.500 dòng, 12 cột | Lưu đặc trưng RFM, chỉ số hành vi, thiết bị và kênh truy cập của từng mã người dùng. |
| market_basket.csv | 1.443 dòng, 4 cột | Lưu các sản phẩm theo mã giao dịch để phân tích mua kèm. |

Các file CSV và Parquet trong thư mục dự án giúp việc chạy thử thuận tiện khi không kết nối BigQuery. Mã nguồn cũng có chức năng tạo **dữ liệu mẫu mô phỏng GA4** để dùng ở chế độ ngoại tuyến. Vì vậy, khi trình bày kết quả từ các file có sẵn, đồ án cần ghi rõ đây là kết quả trên dữ liệu đang lưu trong dự án. Chỉ những kết quả được truy vấn lại thành công từ BigQuery mới có thể xem là kết quả trực tiếp từ bộ dữ liệu công khai.

## 3.2. Quy trình thu thập và xử lý dữ liệu

### 3.2.1. Trích xuất dữ liệu bằng BigQuery SQL

Quy trình xử lý bắt đầu từ bốn file SQL trong thư mục sql. Truy vấn thứ nhất tính các chỉ số tổng quan theo kênh tiếp thị. Truy vấn thứ hai thống kê số người dùng có các sự kiện ở từng bước của phễu mua hàng. Truy vấn thứ ba gom dữ liệu sự kiện thành một dòng đặc trưng cho mỗi người dùng. Truy vấn thứ tư tách danh sách sản phẩm trong các sự kiện mua hàng để chuẩn bị dữ liệu giỏ hàng.

Các phép lọc, đếm và tổng hợp được thực hiện trên BigQuery trước khi chuyển kết quả về Python. Cách làm này giảm lượng dữ liệu cần xử lý trên máy cá nhân. Trong mã nguồn Python, BigQueryService có thể đọc kết quả từ bộ nhớ đệm Parquet, truy vấn BigQuery khi có kết nối hoặc tạo dữ liệu mẫu khi chạy ngoại tuyến. Đây là cơ sở để notebook và dashboard vẫn có dữ liệu minh họa trong trường hợp không có tài khoản Google Cloud.

Ở phiên bản hiện tại, backend của dashboard nạp các bảng theo tên cache và sử dụng câu lệnh thử SELECT 1 khi gọi BigQueryService. Do đó, việc mở dashboard không đồng nghĩa với việc cả bốn truy vấn SQL phân tích được chạy lại trên BigQuery. Nếu cần báo cáo số liệu trực tiếp từ dữ liệu gốc, cần chạy truy vấn tương ứng và lưu kết quả mới trước khi sử dụng dashboard.

### 3.2.2. Kiểm tra và làm sạch dữ liệu

Trước khi phân tích, dữ liệu cần được kiểm tra về tên cột, số dòng và tính hợp lệ của các giá trị. Đối với phễu mua hàng, số người dùng ở bước sau phải nhỏ hơn hoặc bằng bước trước. Đối với bảng đặc trưng khách hàng, những cột số dùng cho học máy không được chứa giá trị thiếu hoặc vô cực. Đối với dữ liệu giỏ hàng, mỗi sản phẩm phải có tên và mã giao dịch để xác định đúng những sản phẩm thuộc cùng một đơn hàng.

Các truy vấn SQL dùng COALESCE để thay một số giá trị rỗng và SAFE_DIVIDE để tránh lỗi khi mẫu số bằng 0. Trong notebook tổng hợp, các giá trị thiếu ở những đặc trưng đầu vào được thay bằng 0. Riêng module tiền xử lý độc lập chỉ kiểm tra NaN và vô cực sau biến đổi, chưa tự thay thế mọi giá trị thiếu. Vì vậy, nếu đưa dữ liệu mới vào module này, bước làm sạch đầu vào cần được kiểm tra lại.

Đối với phân tích giỏ hàng, dữ liệu được loại các cặp giao dịch – sản phẩm trùng lặp. Sau đó, hệ thống chỉ giữ những giao dịch có ít nhất hai sản phẩm khác nhau để tìm các cặp mua kèm có ý nghĩa.

### 3.2.3. Xử lý giá trị ngoại lai và chuẩn hóa đặc trưng

Các đặc trưng như doanh thu, số lần truy cập và thời gian tương tác có thể chênh lệch khá lớn giữa những người dùng. Nếu đưa trực tiếp vào K-Means, những biến có giá trị lớn dễ ảnh hưởng mạnh đến khoảng cách giữa các điểm dữ liệu. Vì vậy, module src/data_processor.py áp dụng lần lượt ba bước tiền xử lý.

Đầu tiên, giá trị quá lớn hoặc quá nhỏ được chặn theo khoảng tứ phân vị. Module dùng hệ số **3 × IQR** để hạn chế ảnh hưởng của ngoại lai mà vẫn giữ lại các trường hợp khách hàng có mức chi tiêu cao. Tiếp theo, phép biến đổi **log(1 + x)** được dùng để giảm độ lệch của các phân phối không âm. Cuối cùng, **StandardScaler** đưa các đặc trưng về cùng thang đo, với trung bình gần 0 và độ lệch chuẩn gần 1. Sau bước này, dữ liệu mới được đưa vào mô hình phân cụm.

Notebook tổng hợp có cách xử lý ngoại lai khác với module Python: notebook dựa trên phân vị 1% và 99%, dùng hệ số 1,5 cho cận trên, đồng thời không biến đổi log đối với tỷ lệ bỏ giỏ. Hai luồng thực hiện này đều có trong dự án nhưng không hoàn toàn giống nhau. Khi viết phần kết quả thực nghiệm, cần nêu rõ kết quả đang lấy từ luồng nào.

## 3.3. Các phương pháp phân tích được áp dụng

### 3.3.1. Phân tích tổng quan và phễu mua hàng

Phân tích tổng quan giúp mô tả tình hình hoạt động của website qua số người dùng, số phiên, lượt xem trang, số đơn hàng, doanh thu và tỷ lệ chuyển đổi. Các chỉ số được chia theo kênh tiếp thị để xem kênh nào mang lại lưu lượng truy cập và doanh thu. Đây là phần tạo bối cảnh trước khi đi sâu vào hành vi mua sắm.

Phễu mua hàng trong đồ án gồm bốn bước: **xem sản phẩm → thêm vào giỏ → bắt đầu thanh toán → mua hàng**. Tỷ lệ chuyển đổi giữa hai bước được tính bằng số người dùng ở bước sau chia cho số người dùng ở bước trước. Tỷ lệ bỏ giỏ được tính bằng số người đã thêm sản phẩm vào giỏ nhưng chưa mua, chia cho tổng số người đã thêm giỏ. Kết quả được so sánh theo desktop, mobile và tablet để nhận ra giai đoạn có mức rơi rụng cao.

Truy vấn SQL hiện đánh dấu người dùng theo việc họ **có phát sinh** từng loại sự kiện và chỉ tính bước sau khi đã có đủ sự kiện của các bước trước. Cách tính này giữ được số lượng giảm dần qua các bước, nhưng chưa kiểm tra thời điểm của từng sự kiện. Do đó, kết quả phản ánh mức độ hoàn thành các nhóm hành động, chưa chứng minh chắc chắn mọi hành động đã diễn ra đúng thứ tự thời gian.

### 3.3.2. Xây dựng đặc trưng RFM và hành vi người dùng

Để phân nhóm khách hàng, đồ án kết hợp ba đặc trưng RFM với sáu đặc trưng hành vi. **Recency** là số ngày tính từ lần tương tác cuối cùng đến ngày chốt dữ liệu. **Frequency** được biểu diễn bằng tổng số phiên truy cập. **Monetary** là tổng giá trị mua hàng của người dùng. Những chỉ số này cho biết mức độ gần đây, tần suất quay lại và giá trị chi tiêu.

Sáu đặc trưng còn lại gồm thời gian tương tác, số lượt xem trang, số lần xem sản phẩm, số lần thêm sản phẩm vào giỏ, tỷ lệ thêm giỏ trên lượt xem sản phẩm và số lần mua hàng. Việc bổ sung hành vi tương tác giúp phân biệt, chẳng hạn, một người chưa mua gì nhưng thường xuyên xem và thêm sản phẩm vào giỏ với một người gần như không còn hoạt động. Thiết bị và kênh truy cập chính được giữ lại để mô tả các nhóm sau phân cụm, nhưng không nằm trong chín đặc trưng số đưa vào mô hình của pipeline module.

### 3.3.3. Phân cụm khách hàng bằng K-Means

Sau khi chuẩn hóa dữ liệu, mô hình K-Means được thử với số cụm K từ 2 đến 8. Với mỗi K, hệ thống tính **inertia** để xem các điểm trong cùng cụm có gần nhau hay không, đồng thời tính **silhouette score** để đánh giá mức tách biệt giữa các cụm. Trong luồng phân tích hiện có, mô hình cuối cùng được đặt **K = 4** để xây dựng bốn chân dung khách hàng phục vụ phần diễn giải và dashboard.

Tên của các nhóm không được K-Means tạo ra sẵn. Sau khi mô hình gán mã cụm, chương trình so sánh doanh thu, thời gian từ lần tương tác cuối, số phiên và hành vi giỏ hàng trung bình của từng cụm để đặt tên. Bốn nhóm được sử dụng là **Loyal Champions (VIPs)**, **Potential Loyalists**, **Cart Abandoners / Window Shoppers** và **At-Risk / Inactive Customers**. Việc gán tên dựa trên đặc điểm trung bình giúp kết quả dễ hiểu hơn khi chuyển thành đề xuất kinh doanh.

Đồ án dùng **PCA** để chuyển dữ liệu từ chín chiều xuống hai hoặc ba chiều cho biểu đồ phân tán. PCA ở đây phục vụ trực quan hóa; K-Means vẫn được huấn luyện trên toàn bộ chín đặc trưng đã chuẩn hóa. Vì biểu đồ chỉ thể hiện hai hoặc ba chiều, khoảng cách nhìn thấy trên hình không thể thay thế hoàn toàn việc đánh giá trong không gian đặc trưng ban đầu.

### 3.3.4. Phân tích sản phẩm mua kèm

Đối với mỗi đơn hàng, các sản phẩm được chuyển thành một hàng của ma trận giỏ hàng. Mỗi cột biểu diễn một sản phẩm; giá trị 1 nghĩa là sản phẩm xuất hiện trong đơn và giá trị 0 nghĩa là không xuất hiện. Từ ma trận này, chương trình tính tần suất của từng sản phẩm và từng cặp sản phẩm, sau đó tạo các luật gợi ý theo dạng **nếu mua A thì có xu hướng mua B**.

Ba chỉ số được dùng để xem xét một luật gồm **support**, **confidence** và **lift**. Support cho biết tỷ lệ đơn hàng chứa cả A và B. Confidence cho biết trong các đơn có A, tỷ lệ đơn cũng có B. Lift so sánh tỷ lệ mua kèm đó với mức xuất hiện thông thường của B; lift lớn hơn 1 cho thấy A và B xuất hiện cùng nhau nhiều hơn mức kỳ vọng nếu hai sản phẩm độc lập.

Trong backend, ngưỡng đang dùng là support từ 0,04, confidence từ 0,25 và lift lớn hơn 1. Module hiện xét các tập gồm một hoặc hai sản phẩm, phù hợp với mục tiêu tìm **cặp sản phẩm** để gợi ý bán chéo. Chương trình chưa khai phá các tổ hợp gồm ba sản phẩm trở lên.

## 3.4. Kiến trúc và cách vận hành hệ thống

### 3.4.1. Luồng xử lý dữ liệu

Luồng xử lý chính của đồ án có thể tóm tắt như sau: **sự kiện GA4 trên BigQuery → truy vấn SQL tổng hợp → dữ liệu CSV/Parquet → tiền xử lý và phân tích bằng Python → API FastAPI → giao diện React**. Trong đó, BigQuery thực hiện phần tổng hợp dữ liệu sự kiện; Python đảm nhiệm phân cụm khách hàng và phân tích giỏ hàng; dashboard trình bày các chỉ số và kết quả theo cách dễ theo dõi hơn.

Hệ thống cũng có chế độ chạy ngoại tuyến bằng dữ liệu đã lưu hoặc dữ liệu mẫu. Cách này phù hợp để trình bày quy trình xử lý và kiểm tra giao diện khi không thể truy vấn BigQuery. Mã nguồn hiện chưa có bộ thu thập sự kiện liên tục hoặc cơ chế cập nhật mô hình khi có sự kiện mới. Vì vậy, phạm vi thực hiện của đồ án là **phân tích theo lô**, chưa phải xử lý dữ liệu thời gian thực.

### 3.4.2. API và giao diện trực quan hóa

Backend FastAPI nạp dữ liệu và kết quả mô hình khi khởi động, sau đó cung cấp các endpoint cho phần tổng quan, phễu mua hàng, chân dung khách hàng, tra cứu người dùng, luật kết hợp giỏ hàng và đề xuất kinh doanh. Frontend React/TypeScript hiển thị những nội dung này thành năm màn hình tương ứng. Ngoài giao diện React, dự án còn có một giao diện Streamlit trong thư mục app để minh họa các biểu đồ và bảng phân tích theo cách khác.

### 3.4.3. Phần đề xuất kinh doanh và AI tạo sinh

Notebook tổng hợp có một block cấu hình thư viện Gemini và chuẩn bị đoạn ngữ cảnh từ kết quả phân tích. Tuy nhiên, mã hiện tại in ra ba khuyến nghị được viết sẵn, chưa gửi yêu cầu tới Gemini để nhận phản hồi tự động. Vì vậy, trong báo cáo, phần này nên được trình bày là **các đề xuất kinh doanh minh họa dựa trên kết quả phân tích**. Tích hợp API AI tạo sinh để tạo và kiểm tra khuyến nghị theo dữ liệu mới là hướng có thể phát triển sau đồ án.

## 3.5. Kết luận chương

Chương 3 đã trình bày nguồn dữ liệu GA4, các bảng dữ liệu sử dụng, cách thu thập và tiền xử lý, cùng những phương pháp phân tích chính của đồ án. Các bước này tạo nền tảng cho phần trình bày kết quả ở chương tiếp theo. Khi đánh giá kết quả, cần phân biệt dữ liệu truy vấn trực tiếp từ BigQuery với dữ liệu mẫu ngoại tuyến và lưu ý những giới hạn của cách xây dựng phễu, mô hình phân cụm cũng như phần đề xuất bằng AI.
