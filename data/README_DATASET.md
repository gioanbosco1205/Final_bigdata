# 📦 THÔNG TIN BỘ DỮ LIỆU ĐỒ ÁN (DATASET INFORMATION)

**Đề tài:** Phân tích hành vi Khách hàng trên Dữ liệu Thương mại Điện tử quy mô lớn bằng Google BigQuery SQL & Python  
**Loại dữ liệu nguồn nghiên cứu:** Clickstream E-commerce Event Data (Google Analytics 4 - GA4)

**Kết quả kiểm tra ngày 03/10/2026:** cả bốn CSV trực tiếp trong thư mục này trùng khớp bộ sinh dữ liệu tổng hợp `_generate_calibrated_sample` trong `src/bq_client.py`, sau khi đối chiếu toàn bộ giá trị với sai số số học 1e-10. Đây là dữ liệu mẫu để kiểm thử, không phải kết quả BigQuery đã xác minh. Có 1.069/4.500 user có Recency vượt khoảng 0–91 ngày của nghiên cứu.

Notebook chính chỉ dùng dữ liệu từ truy vấn BigQuery thành công và lưu vào `data/bigquery_exports/` kèm SQL, job ID và SHA-256. Xem [báo cáo kiểm tra notebook](../NOTEBOOK_REVIEW_2026-10-03.md) và [bằng chứng đối chiếu](../report_assets/notebook_review_2026-10-03/legacy_data_provenance.json).

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
Các file cũ dưới đây dùng để chạy thử Offline/Local. Không dùng chúng để báo cáo số liệu thực nghiệm GA4. Các file này có schema khác kết quả truy vấn của notebook hiện tại:

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
