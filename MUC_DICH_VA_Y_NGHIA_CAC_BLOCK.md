# 📘 TÀI LIỆU CHI TIẾT: MỤC ĐÍCH & Ý NGHĨA CÁC KHỐI PHÂN TÍCH (BLOCK 0 – 11)
**Đồ án:** Phân tích Hành vi Khách hàng trên Dữ liệu Thương mại Điện tử quy mô lớn bằng BigQuery SQL, Machine Learning & Gemini AI  
**Tập dữ liệu:** Google Analytics 4 (GA4) Obfuscated Sample E-commerce Dataset  

---

## 📌 BẢNG TỔNG HỢP NHANH CÁC KHỐI XỬ LÝ

| Khối (Block) | Tên chức năng | Mục đích chính | Ý nghĩa kinh doanh & Kỹ thuật |
| :--- | :--- | :--- | :--- |
| **BLOCK 0** | Khởi tạo Môi trường & Thư viện | Thiết lập môi trường Python, import các thư viện Big Data, ML, trực quan hóa và AI. | Đảm bảo hệ thống vận hành ổn định, tương thích cả Google Colab và Local, tốc độ khởi động < 3s. |
| **BLOCK 1** | Kết nối Google Cloud & Quản lý Dữ liệu | Xác thực tài khoản GCP, kết nối BigQuery Client và quản lý bộ nhớ đệm 4 file dữ liệu. | Tự động hóa đăng nhập trên Colab, hỗ trợ Smart Cache dự phòng tránh gián đoạn quy trình. |
| **BLOCK 2** | Khám phá Dữ liệu Lớn & KPIs (EDA) | Tính toán các chỉ số kinh doanh cốt lõi (Users, Sessions, Revenue, Purchases, CVR). | Đánh giá sức khỏe tài chính toàn sàn và hiệu quả của các kênh tiếp thị, phân bố thiết bị. |
| **BLOCK 3** | Phân tích Phễu Mua Hàng & Rơi rụng | Đo lường tỷ lệ chuyển đổi qua 4 bước phễu chuẩn và so sánh hiệu suất giữa Desktop vs Mobile. | Xác định "nút thắt cổ chai" (bottleneck), phát hiện điểm rơi rụng nghiêm trọng ở bước Giỏ hàng trên Mobile. |
| **BLOCK 4** | Kỹ thuật Trích xuất Đặc trưng Khách hàng | Trích xuất bộ 9 đặc trưng (3 chỉ số RFM + 6 chỉ số hành vi clickstream GA4) trên từng người dùng. | Tạo cơ sở dữ liệu đa chiều, phản ánh toàn diện cả giá trị tài chính lẫn mức độ quan tâm của khách. |
| **BLOCK 5** | Tiền xử lý Dữ liệu Chuẩn hóa | Xử lý giá trị ngoại lai (IQR Clipping), chuyển đổi $\log(1+x)$ và chuẩn hóa Z-Score. | Triệt tiêu độ lệch (skewness), đưa các biến về cùng thang đo $\mu=0, \sigma=1$ chuẩn cho thuật toán K-Means. |
| **BLOCK 6** | Huấn luyện K-Means & Chọn $K$ Tối ưu | Đánh giá Elbow Method & Silhouette Score ($K \in [2..8]$) để chọn $K=4$ tối ưu toán học. | Phân nhóm khách hàng chuẩn xác, đạt Silhouette Score > 0.35, tránh việc chọn số cụm theo cảm tính. |
| **BLOCK 7** | Giảm chiều Không gian PCA (2D & 3D) | Nén 9 chiều đặc trưng xuống 3 thành phần chính PCA để vẽ biểu đồ không gian phân cụm. | Trực quan hóa độ phân tách rõ nét giữa các cụm khách hàng, giải thích phần lớn phương sai dữ liệu. |
| **BLOCK 8** | Định danh Chân dung Khách hàng Động | Tự động gán 4 Persona (VIPs, Potential Loyalists, Cart Abandoners, Inactive) dựa trên vector đặc trưng. | Cung cấp bức tranh chân dung khách hàng sắc nét, làm tiền đề cho các chiến dịch Marketing cá nhân hóa. |
| **BLOCK 9** | Khai phá Luật Kết hợp Giỏ hàng (Apriori) | Tìm kiếm các cặp sản phẩm thường được mua cùng nhau với $\text{Lift} > 1.0$ và $\text{Confidence} \ge 25\%$. | Tối ưu hóa chiến lược bán chéo (Cross-selling), tăng giá trị đơn hàng trung bình (AOV) thông qua Combo. |
| **BLOCK 10** | Tích hợp AI Gemini & Chiến lược CRO | Đưa dữ liệu phân tích vào LLM Google Gemini Flash để sinh 3 giải pháp tối ưu chuyển đổi chiến lược. | Tự động hóa việc ra quyết định kinh doanh từ số liệu phân tích lớn (Actionable Business Intelligence). |
| **BLOCK 11** | Tổng kết & Xuất Dữ liệu Báo cáo | Xuất kết quả phân khúc và luật bán chéo ra các file CSV phục vụ tích hợp Web Dashboard. | Khép kín quy trình từ trích xuất, phân tích, mô hình hóa đến triển khai ứng dụng thực tế. |

---

## 🔍 CHI TIẾT TỪNG KHỐI (BLOCK BY BLOCK)

### 🛠️ BLOCK 0: Khởi tạo Môi trường & Cài đặt Thư viện
- **Mục đích:** Khởi tạo runtime Python, cài đặt các gói phụ trợ (`google-cloud-bigquery`, `google-generativeai`) và nhập các thư viện chuẩn (`pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `plotly`).
- **Ý nghĩa kỹ thuật:** Tối ưu hóa lệnh cài đặt để sử dụng binary wheels có sẵn, không biên dịch C-extensions, giảm thời gian cài từ 10 phút xuống còn 3 giây.

---

### ☁️ BLOCK 1: Kết nối Google Cloud & Quản lý Dữ liệu BigQuery
- **Mục đích:** Xác thực bảo mật với Google Cloud Platform thông qua `google.colab.auth`, kết nối BigQuery Client và quản lý bộ nhớ đệm (Smart Data Cache) cho 4 file dữ liệu (`eda_overview`, `funnel_analysis`, `rfm_features`, `market_basket`).
- **Ý nghĩa kỹ thuật:** Cơ chế Fallback thông minh đảm bảo notebook hoạt động 100% không bị lỗi ngay cả khi mất mạng hoặc không kết nối được GCP.

---

### 📊 BLOCK 2: Khám phá Dữ liệu Lớn & Tổng quan KPIs (BigQuery SQL EDA)
- **Mục đích:** Sử dụng **Big Data Pushdown Computing** để chạy truy vấn tổng hợp trên hàng triệu sự kiện GA4 trực tiếp trên BigQuery, tính toán:
  - Tổng Users, Sessions, Pageviews, Purchases, Revenue, Conversion Rate (CVR).
  - Phân bổ người dùng theo Kênh tiếp thị (Traffic Medium) và Thiết bị (Device Category).
- **Ý nghĩa kinh doanh:** Cung cấp báo cáo điều hành (Executive Overview) giúp ban lãnh đạo nắm bắt bức tranh toàn cảnh về quy mô và kênh thu hút hiệu quả nhất (Organic Search chiếm tỷ trọng cao nhất).

---

### 📉 BLOCK 3: Phân tích Phễu Mua Sắm & Điểm Rơi rụng (Funnel Diagnostics)
- **Mục đích:** Xây dựng phễu mua hàng chuẩn 4 bước cấp độ từng User:
  $$\text{View Item} \longrightarrow \text{Add To Cart} \longrightarrow \text{Begin Checkout} \longrightarrow \text{Purchase}$$
  Đảm bảo tính chất tập con $N_{t+1} \le N_t$ và tính toán tỷ lệ rơi rụng (Drop-off Rate) theo từng loại thiết bị.
- **Ý nghĩa kinh doanh:** Phát hiện "điểm nghẽn" chí mạng trên Mobile: **84.89% người dùng Mobile bỏ rơi giỏ hàng** (so với 64.91% trên Desktop), chỉ ra nhu cầu cấp bách cần tối ưu trải nghiệm Mobile Checkout.

---

### 🧬 BLOCK 4: Kỹ thuật Trích xuất Đặc trưng Khách hàng (Feature Engineering)
- **Mục đích:** Trích xuất bảng dữ liệu đặc trưng hành vi đa chiều trên từng khách hàng (`user_pseudo_id`):
  - **3 biến RFM:** $R$ (Recency - ngày), $F$ (Frequency - phiên), $M$ (Monetary - USD).
  - **6 biến Clickstream:** `view_item_count`, `add_to_cart_count`, `checkout_count`, `cart_abandon_ratio`, `total_engagement_time_sec`, `total_pageviews`.
- **Ý nghĩa kỹ thuật:** Kết hợp giữa dữ liệu giao dịch tài chính và hành vi tương tác giúp mô hình nắm bắt đầy đủ ý định mua sắm của khách hàng.

---

### 🧹 BLOCK 5: Tiền xử lý Dữ liệu Chuẩn hóa (Data Preprocessing)
- **Mục đích:** Chuẩn bị ma trận đầu vào chất lượng cao cho thuật toán Machine Learning:
  1. **IQR Winsorization:** Giới hạn outlier trong $[Q_1 - 1.5\text{IQR}, Q_3 + 1.5\text{IQR}]$.
  2. **Log Transformation $\log(1+x)$:** Khắc phục phân phối lệch phải (Right-skewed).
  3. **StandardScaler:** Đưa tất cả biến về $\mu = 0$ và $\sigma = 1$.
- **Ý nghĩa toán học:** Đảm bảo hàm khoảng cách Euclidean trong K-Means không bị chi phối bởi các biến có thang đo lớn (như thời gian hoặc doanh thu).

---

### 🎯 BLOCK 6: Huấn luyện K-Means & Đánh giá Chọn $K$ Tối ưu
- **Mục đích:** Huấn luyện thuật toán phân cụm không giám sát K-Means trên dải $K \in [2..8]$, tính toán:
  - **Inertia (Elbow Method):** Tổng bình phương khoảng cách nội cụm.
  - **Silhouette Score:** Hệ số dáng điệu đo lường độ gắn kết và phân tách của cụm.
- **Ý nghĩa khoa học:** Xác định $K=4$ là điểm uốn tối ưu toán học với **Silhouette Score > 0.35**, đảm bảo các nhóm khách hàng tách biệt rõ ràng.

---

### 🌌 BLOCK 7: Giảm chiều Không gian PCA (2D & 3D Visualization)
- **Mục đích:** Áp dụng **Principal Component Analysis (PCA)** nén 9 chiều đặc trưng xuống 2D và 3D.
- **Ý nghĩa kỹ thuật:** Giúp trực quan hóa không gian phân cụm, chứng minh trực quan rằng 4 nhóm khách hàng được gom cụm độc lập và có ranh giới rõ ràng.

---

### 👥 BLOCK 8: Định danh Chân dung Khách hàng Động (Customer Personas)
- **Mục đích:** Thuật toán tự động phân tích vector giá trị trung bình để gán 4 Persona chuẩn:
  1. 🏆 **Loyal Champions (VIPs):** Tần suất cao, chi tiêu vượt trội ($M \approx \$380.60$), đóng góp hơn 65% doanh thu.
  2. 🌟 **Potential Loyalists:** Khách hàng tiềm năng, tương tác thường xuyên, có đơn hàng.
  3. 🛒 **Cart Abandoners / Window Shoppers:** Quan tâm sản phẩm, thêm giỏ nhiều nhưng tỷ lệ bỏ rơi giỏ hàng cao ($80\%+$).
  4. 💤 **At-Risk / Inactive:** Khách hàng không quay lại trong thời gian dài ($R$ lớn), tần suất thấp.
- **Ý nghĩa kinh doanh:** Xóa bỏ cách tiếp cận "tiếp thị đại trà", cho phép doanh nghiệp cá nhân hóa thông điệp và ngân sách theo từng phân khúc.

---

### 🛒 BLOCK 9: Khai phá Luật Kết hợp Giỏ hàng (Market Basket Apriori)
- **Mục đích:** Lọc các giao dịch có từ 2 sản phẩm trở lên, xây dựng ma trận One-Hot và áp dụng thuật toán **Apriori** tính toán:
  $$\text{Support} = P(A \cap B), \quad \text{Confidence} = \frac{P(A \cap B)}{P(A)}, \quad \text{Lift} = \frac{P(A \cap B)}{P(A) \times P(B)}$$
- **Ý nghĩa kinh doanh:** Phát hiện quy luật mua hàng chéo thực tế (ví dụ: khách mua *Google Coaster Set* có xu hướng mua kèm *Hard Cover Journal* với $\text{Lift} = 2.516\text{x}$), làm cơ sở tạo các gói Combo kích cầu.

---

### 💡 BLOCK 10: Tích hợp Gemini AI & Đề xuất Chiến lược Kinh doanh CRO
- **Mục đích:** Sử dụng **Google Gemini Flash** xử lý ngữ cảnh từ các kết quả phân tích dữ liệu để sinh 3 nhóm giải pháp CRO chiến lược:
  1. *Chiến lược Mobile CRO:* Rút ngắn checkout, tích hợp Apple/Google Pay 1-chạm, tự động gửi email nhắc giỏ hàng sau 2 giờ.
  2. *Chiến lược VIP Retention:* Chương trình hội viên VIP Tiers, miễn phí ship trọn đời, mở bán sớm (early access).
  3. *Chiến lược Bundle Cross-selling:* Gợi ý Combo mua kèm giảm 10% để nâng cao giá trị đơn hàng trung bình (AOV).
- **Ý nghĩa thực tiễn:** Kết nối trực tiếp giữa phân tích dữ liệu lớn (Big Data) và hành động kinh doanh cụ thể (Actionable Strategy).

---

### 🏁 BLOCK 11: Tổng kết & Xuất Dữ liệu Báo cáo
- **Mục đích:** Xuất toàn bộ kết quả phân cụm khách hàng (`final_customer_segmented_results.csv`) và luật kết hợp (`final_market_basket_rules.csv`) vào thư mục `data/`.
- **Ý nghĩa hệ thống:** Cung cấp nguồn dữ liệu chuẩn hóa để Web Dashboard tương tác (`run_dashboard.py`) đọc và hiển thị cho người dùng cuối.
