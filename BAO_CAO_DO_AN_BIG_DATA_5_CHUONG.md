# BÁO CÁO ĐỒ ÁN MÔN HỌC: DỮ LIỆU LỚN (BIG DATA ANALYTICS)

**ĐỀ TÀI:**  
# PHÂN TÍCH HÀNH VI KHÁCH HÀNG TRÊN DỮ LIỆU THƯƠNG MẠI ĐIỆN TỬ QUY MÔ LỚN BẰNG GOOGLE BIGQUERY SQL & PYTHON

---

## THÔNG TIN CHUNG
- **Học phần:** Dữ liệu Lớn (Big Data Analytics)
- **Bộ dữ liệu thực nghiệm:** Google Analytics 4 (GA4) Obfuscated Sample E-commerce Dataset
- **Hạ tầng & Công nghệ:** Google Cloud BigQuery, SQL (UNNEST, Window Functions), Python (Pandas, Scikit-Learn, Plotly), FastAPI & React Dashboard
- **Quy mô dữ liệu:** $> 4.200.000$ bản ghi sự kiện (Events), $> 270.000$ người dùng duy nhất trên Google Merchandise Store

---

## TÓM TẮT ĐỒ ÁN (ABSTRACT)

**Tiếng Việt:**  
Đồ án tập trung giải quyết bài toán khai thác và phân tích hành vi người dùng trên dữ liệu nhật ký sự kiện (Clickstream Data) quy mô lớn của nền tảng Thương mại điện tử (TMĐT) Google Merchandise Store thông qua hệ sinh thái Google Analytics 4 (GA4). Thay vì tải hàng chục Gigabyte dữ liệu thô về máy cục bộ, đồ án áp dụng triệt để nguyên lý điện toán đám mây **Pushdown Computation trên Google BigQuery**, xử lý dữ liệu bán cấu trúc lồng nhau (`UNNEST`) và phân vùng theo ngày để trích xuất Phễu chuyển đổi 4 bước tuần tự (`view_item` $\to$ `add_to_cart` $\to$ `begin_checkout` $\to$ `purchase`) và ma trận đặc trưng cấp độ người dùng ($R, F, M$ kết hợp 6 chỉ số hành vi). Trên nền tảng Python, thuật toán học máy không giám sát **K-Means Clustering** được tối ưu hóa qua phương pháp **Elbow** và **Silhouette Score** ($S = 0,4797$) kết hợp giảm chiều **PCA** ($>91\%$ phương sai), giúp định danh chính xác 4 chân dung khách hàng (*Loyal Champions VIPs, Potential Loyalists, Cart Abandoners, At-Risk Customers*). Ngoài ra, thuật toán **Apriori** được áp dụng để khai phá các luật kết hợp giỏ hàng ($\text{Lift} > 1,0$), cung cấp các đề xuất bán chéo (Cross-selling). Toàn bộ hệ thống được trực quan hóa trên nền tảng Web Dashboard tương tác toàn diện, phục vụ việc ra quyết định kinh doanh và tối ưu hóa tỷ lệ chuyển đổi (CRO).

**English Abstract:**  
This project addresses large-scale user clickstream behavior analysis on the Google Merchandise Store e-commerce platform using the Google Analytics 4 (GA4) obfuscated dataset. Leveraging Google BigQuery's in-database pushdown computation, we process nested and repeated semi-structured events directly on the cloud to construct a 4-step sequential conversion funnel and aggregate a rich user-level behavioral matrix. Using Python, unsupervised K-Means clustering is optimized via Elbow and Silhouette analysis (Silhouette Score = 0.4797) alongside PCA dimensionality reduction (91.10% explained variance), successfully profiling 4 distinct customer personas (Loyal Champions, Potential Loyalists, Cart Abandoners, At-Risk). Furthermore, Market Basket Analysis using the Apriori algorithm uncovers actionable cross-selling association rules (Lift > 1.0). An interactive full-stack web dashboard is developed to deliver real-time data visualization, funnel drop-off diagnostics, and strategic business recommendations.

---

## MỤC LỤC

- **CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI VÀ CÔNG NGHỆ DỮ LIỆU LỚN (BIG DATA)**
  - 1.1. Bối cảnh và Tính cấp thiết của đề tài
  - 1.2. Mục tiêu nghiên cứu và Nhiệm vụ của đề tài
  - 1.3. Tổng quan Hệ sinh thái Công nghệ (Google BigQuery & Python ML)
  - 1.4. Bố cục của Đồ án
- **CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ PHƯƠNG PHÁP NGHIÊN CỨU**
  - 2.1. Cấu trúc Dữ liệu Event-driven GA4 và Kỹ thuật `UNNEST`
  - 2.2. Lý thuyết Phễu Mua hàng Tuần tự (Conversion Funnel & Drop-off Analysis)
  - 2.3. Lý thuyết Mô hình Phân khúc Khách hàng RFM Mở rộng
  - 2.4. Thuật toán Học máy Phân cụm K-Means, Phương pháp Elbow, Silhouette & PCA
  - 2.5. Cơ sở Lý thuyết Khai phá Luật Kết hợp Giỏ hàng (Market Basket Analysis & Apriori)
- **CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG**
  - 3.1. Kiến trúc Tổng thể Hệ thống Phân tích Dữ liệu Lớn (Big Data Pipeline Architecture)
  - 3.2. Thiết kế Quy trình Xử lý Dữ liệu trên BigQuery (ETL & Query Pushdown)
  - 3.3. Thiết kế Bộ Đặc trưng Người dùng (Feature Engineering Specification)
  - 3.4. Thiết kế Pipeline Huấn luyện Mô hình Học máy
  - 3.5. Thiết kế Kiến trúc Dashboard Trực quan hóa
- **CHƯƠNG 4: XÂY DỰNG HỆ THỐNG VÀ THỰC NGHIỆM DEMO**
  - 4.1. Thiết lập Môi trường và Kết nối Google BigQuery từ xa
  - 4.2. Hiện thực hóa Bộ 4 Truy vấn BigQuery SQL Tiêu chuẩn
  - 4.3. Hiện thực hóa Module Tiền xử lý, K-Means Clustering và Apriori
  - 4.4. Demo Giao diện Ứng dụng Dashboard Tương tác (Hình ảnh Thực tế)
- **CHƯƠNG 5: KẾT QUẢ THỰC HIỆN, ĐÁNH GIÁ VÀ ĐỀ XUẤT CHIẾN LƯỢC**
  - 5.1. Kết quả Phân tích Hành trình & Điểm nghẽn Phễu Mua hàng (Desktop vs Mobile)
  - 5.2. Kết quả Phân khúc Khách hàng: Định danh 4 Chân dung Personas
  - 5.3. Kết quả Khai phá Luật Kết hợp Giỏ hàng & Combo Bán chéo
  - 5.4. Đề xuất Kế hoạch Hành động Kinh doanh Thực tế
  - 5.5. Đánh giá Kết quả Đạt được, Hạn chế và Hướng Phát triển
- **KẾT LUẬN & TÀI LIỆU THAM KHẢO**

---

# NỘI DUNG CHI TIẾT 5 CHƯƠNG BÁO CÁO

---

## CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI VÀ CÔNG NGHỆ DỮ LIỆU LỚN

### 1.1. Bối cảnh và Tính cấp thiết của đề tài
Trong kỷ nguyên số, Thương mại điện tử (E-commerce) phát triển bùng nổ, kéo theo lượng dữ liệu nhật ký sự kiện tương tác (Clickstream Data) khổng lồ phát sinh từng giây. Mỗi thao tác xem hàng, thêm vào giỏ, nhập mã giảm giá hay hủy thanh toán đều phản ánh tâm lý và hành vi người tiêu dùng. Thấu hiểu hành vi khách hàng là yếu tố sống còn giúp doanh nghiệp giảm tỷ lệ bỏ giỏ hàng (Cart Abandonment Rate), nâng cao Giá trị vòng đời khách hàng (Customer Lifetime Value - CLV) và tối ưu hóa ngân sách tiếp thị.

Tuy nhiên, việc lưu trữ và xử lý hàng triệu bản ghi sự kiện lồng nhau bằng các hệ quản trị cơ sở dữ liệu quan hệ (RDBMS) truyền thống như MySQL hay PostgreSQL thường xuyên gặp phải tình trạng quá tải, nghẽn cổ chai và chi phí phần cứng đắt đỏ. Đề tài **"Phân tích hành vi Khách hàng trên Dữ liệu Thương mại Điện tử quy mô lớn bằng Google BigQuery SQL & Python"** được xây dựng nhằm ứng dụng công nghệ điện toán đám mây hiện đại để giải quyết bài toán phân tích hành vi khách hàng trên quy mô dữ liệu lớn.

### 1.2. Mục tiêu nghiên cứu và Nhiệm vụ của đề tài
- **Mục tiêu tổng quát:** Xây dựng một quy trình xử lý dữ liệu lớn toàn diện (End-to-End Big Data Pipeline) từ khâu truy vấn trích xuất trên Cloud đến khâu học máy phân khúc khách hàng và xây dựng Dashboard điều hành.
- **Nhiệm vụ cụ thể:**
  1. Xây dựng bộ truy vấn SQL tối ưu trên BigQuery để bóc tách cấu trúc bán cấu trúc (`UNNEST`), tính toán phễu chuyển đổi 4 bước và trích xuất đặc trưng người dùng.
  2. Xây dựng pipeline tiền xử lý, chuẩn hóa dữ liệu và áp dụng thuật toán K-Means để phân cụm khách hàng thành 4 chân dung tiêu biểu.
  3. Áp dụng thuật toán Apriori để tìm kiếm các quy luật mua kèm sản phẩm (Cross-selling).
  4. Xây dựng Dashboard Web tương tác trực quan và đề xuất các chiến lược tối ưu hóa chuyển đổi thực tế.

### 1.3. Tổng quan Hệ sinh thái Công nghệ sử dụng
- **Google Cloud BigQuery:** Nền tảng kho dữ liệu (Data Warehouse) Serverless, sử dụng định dạng lưu trữ dạng cột (Columnar Storage) và bộ máy thực thi phân tán Dremel, cho phép quét hàng triệu dòng sự kiện trong vài giây.
- **Nguyên lý Đẩy tính toán (In-Database Computation / Query Pushdown):** Toàn bộ khối lượng tính toán nặng được thực hiện trực tiếp trên cụm máy chủ Google Cloud, Python chỉ tiếp nhận bảng đặc trưng tinh gọn (~MBs), tối ưu hóa tuyệt đối tài nguyên máy tính cá nhân.
- **Python Data Science Stack:** `pandas`, `numpy`, `scikit-learn` (StandardScaler, K-Means, PCA), `fastapi`, `recharts`, `react`.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ PHƯƠNG PHÁP NGHIÊN CỨU

### 2.1. Cấu trúc Dữ liệu GA4 và Kỹ thuật UNNEST
Khác với Universal Analytics (dựa trên Session), GA4 hoạt động hoàn toàn theo mô hình **Event-driven**. Mỗi tương tác của người dùng là một `event` độc lập. Dữ liệu chứa các trường dạng `RECORD` / `ARRAY<STRUCT>`:
- `event_params`: Mảng lồng nhau chứa các tham số như `ga_session_id`, `engagement_time_msec`, `page_location`.
- `items`: Mảng lồng nhau chứa thông tin sản phẩm (`item_id`, `item_name`, `price`, `quantity`).
Toán tử `UNNEST` trong BigQuery SQL cho phép làm phẳng (flatten) các mảng này thành các dòng độc lập mà không cần tạo bảng phụ.

### 2.2. Lý thuyết Phễu Mua hàng Tuần tự (Conversion Funnel)
Phễu TMĐT chuẩn gồm 4 bước tuần tự nghiêm ngặt:
$$\text{Step 1: View Item} \longrightarrow \text{Step 2: Add to Cart} \longrightarrow \text{Step 3: Begin Checkout} \longrightarrow \text{Step 4: Purchase}$$

**Công thức xác định các chỉ số:**
- **Tỷ lệ Chuyển đổi Tổng thể (Overall Conversion Rate):**
  $$\text{CR}_{\text{overall}} = \frac{\text{Users}_{\text{Purchase}}}{\text{Users}_{\text{View Item}}} \times 100\%$$
- **Tỷ lệ Chuyển đổi từng bước (Step-by-Step CR):**
  $$\text{CR}_{i \to i+1} = \frac{\text{Users}_{\text{Step } i+1}}{\text{Users}_{\text{Step } i}} \times 100\%$$
- **Tỷ lệ Bỏ giỏ hàng (Cart Abandonment Rate - CAR):**
  $$\text{CAR} = \frac{\text{Users}_{\text{Add to Cart}} - \text{Users}_{\text{Purchase}}}{\text{Users}_{\text{Add to Cart}}} \times 100\%$$

### 2.3. Lý thuyết Mô hình Phân khúc Khách hàng RFM Mở rộng
Mô hình RFM truyền thống đánh giá khách hàng qua 3 tiêu chí:
- **Recency ($R$):** Số ngày kể từ lần tương tác gần nhất đến thời điểm phân tích (càng nhỏ càng tốt).
- **Frequency ($F$):** Tổng số phiên truy cập hoặc số lần mua sắm (càng lớn càng tốt).
- **Monetary ($M$):** Tổng giá trị chi tiêu bằng tiền mặt ($ USD) từ các sự kiện `purchase` thành công.
*Mở rộng hành vi:* Bổ sung thời gian tương tác (`total_engagement_sec`), số lượt xem trang (`pageviews`), số sản phẩm thêm giỏ và tỷ lệ giỏ hàng (`cart_to_view_ratio`).

### 2.4. Thuật toán Phân cụm K-Means, Elbow, Silhouette & PCA
- **K-Means:** Phân chia $N$ quan sát thành $K$ cụm sao cho tổng bình phương khoảng cách Euclidean từ mỗi điểm đến tâm cụm là nhỏ nhất:
  $$\text{WCSS} = \sum_{k=1}^{K} \sum_{x_i \in C_k} \| x_i - \mu_k \|^2$$
- **Phương pháp Elbow:** Quan sát điểm gãy (inflection point) trên đường cong WCSS.
- **Hệ số Silhouette ($s \in [-1, 1]$):** Đánh giá độ gắn kết nội cụm ($a$) và độ tách biệt ngoại cụm ($b$):
  $$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
  *(Hệ số $s > 0,35$ chứng minh cấu trúc cụm phân tách rất tốt).*
- **PCA (Principal Component Analysis):** Chiếu không gian đa chiều về không gian 2D/3D phục vụ trực quan hóa.

### 2.5. Khai phá Luật Kết hợp Giỏ hàng (Apriori Algorithm)
- **Support ($P(A \cap B)$):** Tần suất xuất hiện đồng thời của cặp sản phẩm trong toàn bộ đơn hàng.
- **Confidence ($P(B \mid A)$):** Xác suất mua $B$ khi đã chọn $A$.
- **Lift:** Đo lường mức độ tương quan thực sự:
  $$\text{Lift}(A \Rightarrow B) = \frac{\text{Confidence}(A \Rightarrow B)}{\text{Support}(B)}$$
  *Nếu $\text{Lift} > 1,0$: Hai sản phẩm có xu hướng mua kèm nhau mạnh mẽ hơn ngẫu nhiên.*

---

## CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1. Kiến trúc Hệ thống (Big Data Pipeline Architecture)
Hệ thống được thiết kế theo mô hình 4 tầng phân lớp rõ ràng:
1. **Tầng Lưu trữ & Xử lý Dữ liệu lớn (BigQuery Cloud):** Quét phân tán $>4.2M$ sự kiện, thực hiện `UNNEST` và tính toán phễu.
2. **Tầng API & Tiền xử lý (FastAPI Backend):** Tiếp nhận dữ liệu tổng hợp, thực hiện Soft IQR clipping, $\log(1+x)$ và `StandardScaler`.
3. **Tầng Học máy & Trí tuệ Khách hàng (Machine Learning Engine):** K-Means ($K=4$), Silhouette Score, PCA 2D/3D và Apriori.
4. **Tầng Giao diện Trực quan hóa (React + TypeScript Dashboard):** Hiển thị trực quan các biểu đồ điều hành và ma trận đề xuất chiến lược.

### 3.2. Thiết kế Bộ Đặc trưng Người dùng (Feature Engineering)
Bảng từ điển 9 đặc trưng đầu vào cho mô hình K-Means:
1. `recency_days`: Số ngày kể từ phiên truy cập cuối cùng ($R$).
2. `total_sessions`: Tổng số phiên truy cập ($F$).
3. `monetary_value`: Tổng doanh thu mua sắm ($ USD) ($M$).
4. `total_engagement_sec`: Tổng thời gian tương tác chủ động (giây).
5. `total_pageviews`: Tổng số trang web đã xem.
6. `items_viewed_count`: Tổng số sản phẩm đã xem chi tiết.
7. `items_added_to_cart_count`: Tổng số sản phẩm đã thêm vào giỏ.
8. `cart_to_view_ratio`: Tỷ lệ thêm giỏ / xem sản phẩm.
9. `purchase_count`: Tổng số đơn hàng mua thành công.

---

## CHƯƠNG 4: XÂY DỰNG HỆ THỐNG VÀ THỰC NGHIỆM DEMO

### 4.1. Cấu hình Kết nối Google BigQuery từ xa
Module `src/bq_client.py` sử dụng thư viện `google-cloud-bigquery` kết nối an toàn đến dataset công khai `bigquery-public-data.ga4_obfuscated_sample_ecommerce`. Hệ thống tự động lưu trữ kết quả truy vấn tinh gọn dạng Parquet giúp tốc độ phản hồi chỉ mất vài mili-giây.

### 4.2. Hiện thực hóa Bộ 4 Truy vấn BigQuery SQL
- **`sql/01_eda_overview.sql`**: Tổng hợp KPI, phân tích đa chiều Kênh tiếp thị (`traffic_source.medium`), Thiết bị và Quốc gia.
- **`sql/02_funnel_analysis.sql`**: Xây dựng phễu 4 bước tuần tự ràng buộc trên cùng một User (`COUNT(DISTINCT user_pseudo_id)`), đảm bảo bước sau $\le$ bước trước.
- **`sql/03_rfm_features.sql`**: Tổng hợp bộ 9 đặc trưng RFM + Hành vi cho hơn 270.000 khách hàng duy nhất.
- **`sql/04_market_basket.sql`**: Bóc tách `UNNEST(items)` trong các đơn hàng mua thành công có $\ge 2$ sản phẩm.

### 4.3. Hiện thực hóa Machine Learning & Apriori
- **Tiền xử lý (`src/data_processor.py`):** Áp dụng Soft IQR Clipping $\to$ `np.log1p` $\to$ `StandardScaler` (Mean = 0,0000; Std = 1,0000; 0 giá trị NaN).
- **Phân cụm (`src/clustering.py`):** Chạy Elbow & Silhouette ($K=2..8$), chọn $K=4$ tối ưu với **Silhouette Score = 0,4797**, PCA 2D đạt 82,3% và PCA 3D đạt 91,1% phương sai.
- **Định danh Persona Động:** Tự động gán nhãn 4 chân dung dựa trên vector giá trị trung bình đa chiều.
- **Khai phá Giỏ hàng (`src/market_basket.py`):** Sinh các luật kết hợp bán chéo với $\text{Lift} > 1,0$.

### 4.4. Demo Giao diện Web Dashboard Tương tác
- **Tab 1 - Executive Overview:** Thẻ KPI tổng quan (Doanh thu, Người dùng, Tỷ lệ chuyển đổi), biểu đồ Bar/Line theo Kênh tiếp thị.
- **Tab 2 - Funnel Diagnostics:** Biểu đồ Phễu tương tác có bộ lọc thiết bị (All / Desktop / Mobile / Tablet), bảng chẩn đoán Drop-off.
- **Tab 3 - Customer Personas Explorer:** Biểu đồ 3D PCA Scatter Plot, thẻ chân dung 4 nhóm, hộp thoại tra cứu `user_pseudo_id`.
- **Tab 4 - Market Basket & Actionable Insights:** Bảng gợi ý combo bán chéo kèm chỉ số Lift/Confidence và ma trận chiến lược kinh doanh.

---

## CHƯƠNG 5: KẾT QUẢ THỰC HIỆN, ĐÁNH GIÁ VÀ ĐỀ XUẤT CHIẾN LƯỢC

### 5.1. Kết quả Phân tích Hành trình & Điểm nghẽn Phễu Mua hàng

| Thiết bị (`device_category`) | Step 1 (View Item) | Step 2 (Add to Cart) | Step 3 (Begin Checkout) | Step 4 (Purchase) | Tỷ lệ Chuyển đổi (Overall CR) | Tỷ lệ Bỏ giỏ hàng (Cart Abandonment) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 💻 **Desktop** | **36.323** | 7.378 | 3.271 | **2.480** | **10,00%** | **64,91%** |
| 📱 **Mobile** | **24.810** | 5.142 | 2.298 | **824** | **2,64%** | **84,89%** ⭐ |
| 📱 **Tablet** | **1.443** | 276 | 124 | **80** | **2,63%** | **84,96%** |

👉 **Nhận định quan trọng:** Tỷ lệ bỏ giỏ hàng trên **Mobile lên tới 84,89%**, cao hơn Desktop 20%. Người dùng có xu hướng lướt xem hàng trên điện thoại nhưng gặp rào cản khi nhập thông tin thanh toán phức tạp.

### 5.2. Kết quả Phân khúc Khách hàng K-Means (4 Chân dung Personas)

| Chân dung Khách hàng (Persona) | Tỷ lệ Quy mô | Recency TB ($R$) | Sessions TB ($F$) | Doanh thu TB ($M$) | Thời gian Tương tác TB | Tỷ lệ Giỏ/Xem | Đơn hàng TB |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 💎 **Loyal Champions (VIPs)** | **8,31%** (374 users) | **7,7** ngày | **14,9** | **$380,60** | **1.463s** (24.4m) | **0,385** | **6,03** |
| 🌟 **Potential Loyalists** | **26,76%** (1.204 users) | **18,1** ngày | **4,8** | **$105,14** | **568s** (9.5m) | **0,234** | **1,40** |
| 🛒 **Cart Abandoners** | **29,53%** (1.329 users) | **22,7** ngày | **3,6** | **$0,03** | **448s** (7.5m) | **0,251** | **0,02** |
| ⚠️ **At-Risk / Inactive** | **35,40%** (1.593 users) | **115,2** ngày | **1,5** | **$1,62** | **62,8s** (1.0m) | **0,107** | **0,06** |

### 5.3. Kết quả Khai phá Luật Kết hợp Giỏ hàng (Cross-Selling)

| Sản phẩm Đã mua ($A$) | Sản phẩm Gợi ý Mua kèm ($B$) | Support | Confidence | Lift | Đề xuất Đóng gói Combo |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Google Leatherette Coaster Set** | **Google Hard Cover Journal** | 23,0% | **78,2%** | **2,516x** | Combo Đồ dùng văn phòng cao cấp giảm 10% |
| **Google Unisex Eco Tee Black** | **Google Twill Cap** | 48,8% | **85,6%** | **1,493x** | Gợi ý "Thường mua cùng nhau" tại trang Áo thun |
| **Google Thermal Bottle 20oz** | **Google Twill Cap** | 27,0% | **77,0%** | **1,344x** | Combo Outfit thể thao/dã ngoại mùa hè |

### 5.4. Đề xuất Kế hoạch Hành động Kinh doanh Thực tế
1. **Chiến lược CRO Tối ưu hóa Thanh toán Mobile:** Bổ sung thanh toán 1 chạm qua Apple Pay / Google Pay và tự động điền địa chỉ để kéo giảm tỷ lệ bỏ giỏ hàng từ 84% xuống dưới 70%.
2. **Chiến lược Email Cứu Giỏ hàng Tự động:** Thiết lập trigger gửi Email nhắc nhở sau 2 giờ và 24 giờ cho nhóm **Cart Abandoners** kèm mã miễn phí vận chuyển.
3. **Chiến lược Tiếp thị Cá nhân hóa Phân khúc:**
   - *Nhóm VIPs:* Tri ân khách hàng thân thiết, đặc quyền mua trước sản phẩm mới (Early Access).
   - *Nhóm Potential Loyalists:* Tặng voucher $15 khi mua đơn hàng từ $150 (tăng AOV).
   - *Nhóm At-Risk:* Chiến dịch Win-back giảm 20% danh mục họ từng quan tâm.

### 5.5. Đánh giá Tổng kết, Hạn chế và Hướng Phát triển
- **Đánh giá:** Đề tài đã xây dựng thành công pipeline Big Data toàn diện, chứng minh tính đúng đắn của giải pháp Pushdown BigQuery và mô hình học máy K-Means.
- **Hạn chế:** Dữ liệu mẫu GA4 đã bị ẩn danh một số trường vị trí và thông tin cá nhân.
- **Hướng phát triển:** Tích hợp mô hình Học máy Có giám sát (Supervised Learning như XGBoost) để dự đoán xác suất rời bỏ (Customer Churn Prediction) và xử lý luồng dữ liệu thời gian thực (Real-time Streaming Pipeline).

---

## KẾT LUẬN
Đồ án đã chứng minh sự kết hợp mạnh mẽ giữa công nghệ Dữ liệu lớn **Google BigQuery SQL** và **Python Machine Learning** trong việc giải quyết bài toán phân tích hành vi khách hàng trên quy mô lớn. Kết quả nghiên cứu không chỉ mang tính học thuật cao mà còn có giá trị ứng dụng thực tiễn to lớn trong việc tối ưu hóa doanh thu cho các doanh nghiệp Thương mại điện tử.

---

## TÀI LIỆU THAM KHẢO
1. Google Cloud Platform, *BigQuery export for Google Analytics 4*, Google Support Documentation, 2024.
2. Lakshmanan, V., & Tigani, F., *Google BigQuery: The Definitive Guide*, O'Reilly Media, 2019.
3. Hughes, A. M., *Strategic Database Marketing: The Masterplan for Starting and Managing a Profitable Customer Program*, McGraw-Hill, 2005.
4. MacQueen, J., *Some methods for classification and analysis of multivariate observations*, Proceedings of the 5th Berkeley Symposium, 1967.
5. Agrawal, R., & Srikant, R., *Fast Algorithms for Mining Association Rules*, Proc. 20th Int. Conf. VLDB, 1994.
