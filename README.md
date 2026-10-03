# 📊 Phân Tích Hành Vi Khách Hàng Trên Dữ Liệu Thương Mại Điện Tử Quy Mô Lớn (Big Data GA4 E-Commerce Analytics)

> **Kiểm tra notebook ngày 03/10/2026:** xem [phân tích từng block và bằng chứng chạy](NOTEBOOK_REVIEW_2026-10-03.md). Bốn CSV cũ trong `data/` khớp bộ sinh dữ liệu tổng hợp; các số liệu minh họa cũ chưa được xác minh bằng BigQuery. Notebook chính chỉ dùng query job thành công. Kiểm thử kỹ thuật đã chạy 12/12 block với fixture và 25/25 tests; chạy dữ liệu thật cần Google Cloud credentials.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Google BigQuery](https://img.shields.io/badge/Google%20Cloud-BigQuery-669DF6.svg)](https://cloud.google.com/bigquery)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.0%2B-orange.svg)](https://scikit-learn.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Tests-7%2F7%20Passed-brightgreen.svg)](tests/)

> **Đề tài:** Phân tích hành vi Khách hàng trên Dữ liệu Thương mại Điện tử quy mô lớn bằng dataset Google BigQuery SQL & Python (GA4 Dataset)  
> **Tập dữ liệu:** Google Analytics 4 (GA4) Obfuscated Sample E-commerce Public Dataset (`bigquery-public-data.ga4_obfuscated_sample_ecommerce`)

---

## 📌 Tổng Quan Dự Án

Dự án nghiên cứu và hiện thực hóa một quy trình phân tích dữ liệu lớn toàn diện (End-to-End Big Data Analytics & Machine Learning Pipeline) từ dữ liệu sự kiện clickstream thương mại điện tử thực tế của **Google Merchandise Store**:

1. **Big Data Pushdown Computing:** Tối ưu hóa truy vấn SQL trên Google Cloud BigQuery, xử lý hàng triệu sự kiện phân cấp (nested & repeated records: `event_params`, `items`).
2. **Funnel Diagnostics:** Phân tích phễu chuyển đổi 4 bước (`view_item` $\to$ `add_to_cart` $\to$ `begin_checkout` $\to$ `purchase`), phát hiện điểm rơi rụng giỏ hàng (Cart Abandonment) giữa các thiết bị (Mobile vs Desktop).
3. **RFM & Behavioral Feature Engineering:** Trích xuất bộ 9 đặc trưng hành vi và giá trị tài chính cấp độ từng người dùng (`user_pseudo_id`).
4. **Machine Learning Pipeline & Phân Cụm Khách Hàng:**
   - Xử lý Outlier (IQR Winsorization), $\log(1+x)$ và chuẩn hóa `StandardScaler`.
   - Đánh giá Elbow Method & Silhouette Score ($K \in [2..8] \to K=4$ tối ưu với Silhouette = `0.4797`).
   - Giảm chiều không gian PCA 2D/3D (giải thích `91.1%` phương sai).
   - Định danh 4 Chân dung Khách hàng: **Loyal Champions (VIPs)**, **Potential Loyalists**, **Cart Abandoners**, **At-Risk / Inactive**.
5. **Khai Phá Luật Kết Hợp Giỏ Hàng (Market Basket Analysis):** Sử dụng thuật toán Apriori tìm ra các quy luật mua kèm sản phẩm có $\text{Lift} > 1.0$ và $\text{Confidence} \ge 25\%$, phục vụ đề xuất Combo & Cross-selling.
6. **Ứng Dụng Web Dashboard:** Xây dựng Dashboard tương tác thời gian thực với FastAPI Backend và React Frontend.

---

## 🗂️ Cấu Trúc Thư Mục Dự Án

```bash
├── DoAn-BigData-GA4-SourceCode-Final.ipynb  # Master Jupyter Notebook hoàn chỉnh 12 Block (Colab/Local)
├── BAO_CAO_DO_AN_BIG_DATA_5_CHUONG.md       # Báo cáo học thuật chi tiết 5 Chương
├── MUC_DICH_VA_Y_NGHIA_CAC_BLOCK.md         # Hướng dẫn chi tiết mục đích & ý nghĩa các Block
├── TODO.md                                  # Bảng theo dõi tiến độ dự án
├── requirements.txt                         # Thư viện phụ thuộc Python
├── run_tests.py                             # Script chạy tự động bộ kiểm thử E2E (7/7 tests)
├── run_dashboard.py                         # Script khởi động nhanh Web Dashboard (Localhost:8000)
├── config/                                  # Cấu hình dự án & hằng số phân tích
├── sql/                                     # 4 bộ truy vấn Google BigQuery SQL
│   ├── 01_eda_overview.sql                  # Truy vấn khám phá EDA & KPIs
│   ├── 02_funnel_analysis.sql               # Truy vấn Phễu chuyển đổi & Thiết bị
│   ├── 03_rfm_features.sql                  # Trích xuất 9 đặc trưng RFM + Clickstream
│   └── 04_market_basket.sql                 # Bóc tách giỏ hàng cho thuật toán Apriori
├── src/                                     # Mã nguồn cốt lõi Pipeline Python
│   ├── bq_client.py                         # BigQuery Client & Smart Cache Fallback
│   ├── data_processor.py                    # Tiền xử lý dữ liệu chuẩn hóa
│   ├── clustering.py                        # K-Means, Elbow, Silhouette, PCA, Personas
│   └── market_basket.py                     # One-Hot Matrix, Apriori & Association Rules
├── data/                                    # Dữ liệu trích xuất (CSV / Parquet)
├── notebooks/                               # Bộ 2 Notebooks phân đoạn
├── backend/                                 # FastAPI Backend API Server
├── frontend/                                # React + TypeScript + Tailwind Web Dashboard
└── tests/                                   # Bộ kiểm thử tự động End-to-End
```

---

## 🚀 Hướng Dẫn Khởi Chạy

### 1. Cài đặt môi trường
```bash
# Clone repository
git clone https://github.com/gioanbosco1205/Final_bigdata.git
cd Final_bigdata

# Cài đặt thư viện Python
pip install -r requirements.txt
```

### 2. Chạy Kiểm Thử Toàn Diện (End-to-End Test Suite)
```bash
python run_tests.py
```

### 3. Chạy Khởi Động Web Dashboard
```bash
python run_dashboard.py
```
Truy cập giao diện tại: `http://localhost:8000`

### 4. Chạy Jupyter Notebook
Mở file `DoAn-BigData-GA4-SourceCode-Final.ipynb` trực tiếp trên VSCode, Jupyter Lab hoặc tải lên Google Colab để thực thi toàn bộ 12 khối phân tích.
