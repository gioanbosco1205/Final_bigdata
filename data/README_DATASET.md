# 📦 THÔNG TIN BỘ DỮ LIỆU ĐỒ ÁN (DATASET INFORMATION)

**Đề tài:** Phân tích hành vi Khách hàng trên Dữ liệu Thương mại Điện tử quy mô lớn bằng Google BigQuery SQL & Python  
**Loại dữ liệu:** Clickstream E-commerce Event Data (Google Analytics 4 - GA4)

---

### 🌐 1. NGUỒN GỐC DỮ LIỆU GỐC TRÊN GOOGLE CLOUD (CLOUD REPOSITORY)
- **Tên kho dữ liệu công khai:** Google Analytics 4 Obfuscated Sample E-commerce Dataset
- **Địa chỉ BigQuery Public Dataset:** `bigquery-public-data.ga4_obfuscated_sample_ecommerce`
- **Bảng dữ liệu sự kiện:** `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
- **Khoảng thời gian:** 01/11/2020 đến 31/01/2021 (3 tháng giao dịch thực tế trên Google Merchandise Store)
- **Quy mô dữ liệu thô:** Hàng triệu sự kiện clickstream với cấu trúc lồng nhau (Nested & Repeated Records).
- **Phương pháp xử lý:** Big Data Pushdown Computing (xử lý trực tiếp trên cụm máy chủ phân tán của Google Cloud BigQuery bằng SQL, không tải toàn bộ dữ liệu thô nhiều Gigabytes về máy cá nhân).

---

### 📂 2. CÁC TẬP DỮ LIỆU NỘP BÀI (DATASET FILES NỘP KÈM)
Để thuận tiện cho Giảng viên kiểm tra, chấm bài và chạy thử nghiệm Offline/Local, toàn bộ dữ liệu đã được trích xuất bằng BigQuery SQL và lưu trữ dưới dạng chuẩn **CSV** và **Parquet** trong thư mục `data/`:

| Tên File | Định dạng | Số dòng | Số cột | Mô tả nội dung dữ liệu |
| :--- | :---: | :---: | :---: | :--- |
| **`rfm_features.csv`** / `.parquet` | CSV / Parquet | 4,500+ | 12 | **Bảng dữ liệu khách hàng cấp độ `user_pseudo_id`**:<br>• 3 chỉ số RFM: $R$ (Recency), $F$ (Frequency), $M$ (Monetary - USD).<br>• 6 chỉ số hành vi: `view_item_count`, `add_to_cart_count`, `checkout_count`, `cart_abandon_ratio`, `engagement_time_sec`, `pageviews`. |
| **`funnel_analysis.csv`** / `.parquet` | CSV / Parquet | 3 | 10 | **Dữ liệu Phễu Mua Sắm 4 bước** (`view_item` $\to$ `add_to_cart` $\to$ `begin_checkout` $\to$ `purchase`), tỷ lệ chuyển đổi và Drop-off rate theo thiết bị (*Desktop, Mobile, Tablet*). |
| **`eda_overview.csv`** / `.parquet` | CSV / Parquet | 7 | 7 | **Dữ liệu tổng quan KPI & Kênh Tiếp thị** (Organic Search, Direct, Referral, Paid Search...), Users, Sessions, Doanh thu và Đơn hàng. |
| **`market_basket.csv`** / `.parquet` | CSV / Parquet | 1,443+ | 4 | **Dữ liệu Giỏ hàng** gồm các đơn hàng có $\ge 2$ sản phẩm cùng giao dịch (`transaction_id`, `item_id`, `item_name`, `price_in_usd`) dùng cho thuật toán Apriori. |

---

### 💻 3. HƯỚNG DẪN ĐỌC DỮ LIỆU BẰNG PYTHON / PANDAS
```python
import pandas as pd

# Đọc bảng đặc trưng khách hàng RFM
df_rfm = pd.read_csv('data/rfm_features.csv')
print(f"RFM Dataset shape: {df_rfm.shape}")
display(df_rfm.head())

# Đọc bảng giỏ hàng
df_basket = pd.read_csv('data/market_basket.csv')
print(f"Market Basket shape: {df_basket.shape}")
display(df_basket.head())
```
