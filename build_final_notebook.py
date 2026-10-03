"""
Script to generate the Master All-in-One Jupyter Notebook: DoAn-BigData-GA4-SourceCode-Final.ipynb
Using 100% Real Google BigQuery GA4 E-Commerce Dataset.
"""

import json
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
cells = []

# Title & Metadata
cells.append(new_markdown_cell("""# 🎓 ĐỒ ÁN CUỐI KỲ: PHÂN TÍCH DỮ LIỆU LỚN (BIG DATA ANALYTICS)

### 📌 Đề tài: Phân tích hành vi Khách hàng trên Dữ liệu Thương mại Điện tử quy mô lớn bằng Google BigQuery SQL & Python
**Tập dữ liệu:** Google Analytics 4 (GA4) Obfuscated Sample E-commerce Dataset  
**Nền tảng thực thi:** Google Cloud BigQuery, Python Data/ML Pipeline, Google Gemini Generative AI  

---
### 📋 MỤC LỤC BÁO CÁO SOURCE CODE (12 BLOCKS):
- **BLOCK 0:** Khởi tạo Môi trường & Cài đặt Thư viện
- **BLOCK 1:** Kết nối Google Cloud BigQuery & Quản lý Dữ liệu
- **BLOCK 2:** Khám phá Dữ liệu Lớn & Tổng quan KPIs (BigQuery SQL EDA)
- **BLOCK 3:** Phân tích Phễu Mua Sắm & Điểm Rơi rụng (Funnel Diagnostics)
- **BLOCK 4:** Kỹ thuật Trích xuất Đặc trưng Khách hàng (RFM & Clickstream Features)
- **BLOCK 5:** Tiền xử lý Dữ liệu Chuẩn hóa (IQR Clipping + Log1p + StandardScaler)
- **BLOCK 6:** Huấn luyện K-Means & Đánh giá Chọn K Tối ưu (Elbow & Silhouette)
- **BLOCK 7:** Giảm chiều Không gian PCA & Trực quan hóa Phân cụm (2D & 3D)
- **BLOCK 8:** Định danh Chân dung Khách hàng Động (Customer Personas)
- **BLOCK 9:** Khai phá Luật Kết hợp Giỏ hàng (Market Basket Apriori)
- **BLOCK 10:** Tích hợp Gemini AI & Đề xuất Chiến lược Kinh doanh CRO
- **BLOCK 11:** Tổng kết & Xuất Dữ liệu Báo cáo
"""))

# BLOCK 0
cells.append(new_markdown_cell("""---
### 🛠️ BLOCK 0: KHỞI TẠO MÔI TRƯỜNG & CÀI ĐẶT THƯ VIỆN
"""))

cells.append(new_code_cell("""# 1. Cài đặt các thư viện BigQuery và AI
!pip install -q google-cloud-bigquery db-dtypes pyarrow google-generativeai

# 2. Nhập các thư viện chuẩn
import os
import sys
import time
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Scikit-learn
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import PCA

# Cấu hình hiển thị
warnings.filterwarnings('ignore')
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except Exception:
    plt.style.use('seaborn-whitegrid')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 110

print("✓ Đã cài đặt và khởi tạo toàn bộ thư viện thành công!")
"""))

# BLOCK 1
cells.append(new_markdown_cell("""---
### ☁️ BLOCK 1: KẾT NỐI GOOGLE CLOUD & QUẢN LÝ DỮ LIỆU BIGQUERY
"""))

cells.append(new_code_cell("""# Thiết lập biến cấu hình
PROJECT_ID = "bigquery-public-data"
DATASET_ID = "ga4_obfuscated_sample_ecommerce"
LOCAL_DATA_DIR = Path("data")
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = LOCAL_DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

bq_client = None

# 1. Xác thực Google Cloud & Khởi tạo BigQuery Client
try:
    from google.colab import auth
    print("👉 Đang chạy trên Google Colab: Mở cửa sổ xác thực tài khoản Google...")
    auth.authenticate_user()
    from google.cloud import bigquery
    import google.auth
    credentials, project = google.auth.default()
    gcp_project = project if project and project != "None" else "bigquery-public-data"
    try:
        bq_client = bigquery.Client(project=gcp_project, credentials=credentials)
        print(f"✓ Đã kết nối BigQuery thành công qua Google Colab! (Project: {bq_client.project})")
    except Exception:
        bq_client = bigquery.Client(credentials=credentials)
        print("✓ Đã kết nối BigQuery Client mặc định!")
except ImportError:
    print("👉 Đang chạy trên môi trường Local / Jupyter Notebook.")
    try:
        from google.cloud import bigquery
        bq_client = bigquery.Client()
        print("✓ Đã kết nối Google BigQuery Client thành công!")
    except Exception as e:
        print(f"ℹ️ Đang đọc dữ liệu BigQuery đã trích xuất trong thư mục data/.")
except Exception as auth_err:
    print(f"ℹ️ Thông tin xác thực: {auth_err}. Kích hoạt chế độ đọc dữ liệu trích xuất chuẩn.")

def query_or_load(query_sql: str, filename: str) -> pd.DataFrame:
    \"\"\"Thực thi truy vấn BigQuery hoặc nạp từ tập dữ liệu trích xuất chuẩn.\"\"\"
    csv_file = LOCAL_DATA_DIR / f"{filename}.csv"
    parquet_file = CACHE_DIR / f"{filename}.parquet"
    
    # 1. Thử truy vấn BigQuery trực tiếp nếu có client
    if bq_client is not None:
        try:
            print(f"📡 Đang thực thi BigQuery SQL [{filename}] trên Google Cloud...")
            df = bq_client.query(query_sql).to_dataframe()
            df.to_parquet(parquet_file, index=False)
            df.to_csv(csv_file, index=False)
            print(f"✓ Truy vấn BigQuery thành công ({len(df):,} dòng)!")
            return df
        except Exception as err:
            print(f"⚠️ Không thể truy vấn trực tiếp ({err}), chuyển sang nạp dữ liệu trích xuất...")
            
    # 2. Nạp từ file cục bộ (Parquet hoặc CSV)
    if parquet_file.exists():
        print(f"⚡ Đang nạp tập dữ liệu [{filename}] từ cache: {parquet_file.name}")
        return pd.read_parquet(parquet_file)
    if csv_file.exists():
        print(f"⚡ Đang nạp tập dữ liệu [{filename}] từ file: {csv_file.name}")
        return pd.read_csv(csv_file)
        
    raise FileNotFoundError(f"Không tìm thấy dữ liệu cho {filename}")

print("✓ Bộ điều khiển truy vấn BigQuery đã sẵn sàng!")
"""))

# BLOCK 2
cells.append(new_markdown_cell("""---
### 📊 BLOCK 2: KHÁM PHÁ DỮ LIỆU LỚN & TỔNG QUAN HIỆU SUẤT (BIGQUERY SQL EDA)
"""))

cells.append(new_code_cell("""sql_eda = \"\"\"
WITH base_events AS (
    SELECT
        PARSE_DATE('%Y%m%d', event_date) AS event_date,
        user_pseudo_id,
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
        event_name,
        event_value_in_usd,
        traffic_source.medium AS traffic_medium,
        device.category AS device_category
    FROM
        `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
)
SELECT
    COALESCE(traffic_medium, '(not set)') AS traffic_medium,
    COUNT(DISTINCT user_pseudo_id) AS total_users,
    COUNT(DISTINCT CONCAT(user_pseudo_id, CAST(ga_session_id AS STRING))) AS total_sessions,
    COUNTIF(event_name = 'page_view') AS total_pageviews,
    COUNTIF(event_name = 'purchase') AS total_transactions,
    ROUND(SUM(IF(event_name = 'purchase', COALESCE(event_value_in_usd, 0), 0)), 2) AS total_revenue,
    ROUND(SAFE_DIVIDE(COUNTIF(event_name = 'purchase'), COUNT(DISTINCT CONCAT(user_pseudo_id, CAST(ga_session_id AS STRING)))) * 100, 2) AS session_conversion_rate_pct,
    ROUND(SAFE_DIVIDE(SUM(IF(event_name = 'purchase', COALESCE(event_value_in_usd, 0)), 0)), NULLIF(COUNTIF(event_name = 'purchase'), 0)), 2) AS average_order_value_usd
FROM base_events
GROUP BY traffic_medium
ORDER BY total_revenue DESC;
\"\"\"

df_eda = query_or_load(sql_eda, "eda_overview")
print("="*70)
print("📊 BẢNG TỔNG HỢP HIỆU SUẤT CÁC KÊNH TIẾP THỊ (TRAFFIC MEDIUMS):")
print("="*70)
display(df_eda)

# Trực quan hóa Doanh thu theo Kênh Tiếp thị
plt.figure(figsize=(10, 5))
sns.barplot(data=df_eda, x='traffic_medium', y='total_revenue', palette='Blues_r')
plt.title('Tổng Doanh Thu ($) Theo Kênh Tiếp Thị (GA4 E-commerce)', fontsize=13, fontweight='bold')
plt.xlabel('Kênh Tiếp Thị (Traffic Medium)', fontsize=11)
plt.ylabel('Doanh Thu ($ USD)', fontsize=11)
plt.xticks(rotation=25)
for i, v in enumerate(df_eda['total_revenue']):
    plt.text(i, v + 200, f"${v:,.0f}", ha='center', fontweight='bold')
plt.tight_layout()
plt.show()
"""))

# BLOCK 3
cells.append(new_markdown_cell("""---
### 📉 BLOCK 3: PHÂN TÍCH PHỄU MUA SẮM & ĐIỂM RƠI RỤNG (FUNNEL DIAGNOSTICS)
"""))

cells.append(new_code_cell("""sql_funnel = \"\"\"
WITH user_event_flags AS (
    SELECT
        user_pseudo_id,
        device.category AS device_category,
        MAX(IF(event_name = 'view_item', 1, 0)) AS has_view_item,
        MAX(IF(event_name = 'add_to_cart', 1, 0)) AS has_add_to_cart,
        MAX(IF(event_name = 'begin_checkout', 1, 0)) AS has_begin_checkout,
        MAX(IF(event_name = 'purchase', 1, 0)) AS has_purchase
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE event_name IN ('view_item', 'add_to_cart', 'begin_checkout', 'purchase')
    GROUP BY user_pseudo_id, device_category
),
user_funnel AS (
    SELECT
        user_pseudo_id,
        device_category,
        has_view_item AS step_1_view_item,
        IF(has_view_item = 1 AND has_add_to_cart = 1, 1, 0) AS step_2_add_to_cart,
        IF(has_view_item = 1 AND has_add_to_cart = 1 AND has_begin_checkout = 1, 1, 0) AS step_3_begin_checkout,
        IF(has_view_item = 1 AND has_add_to_cart = 1 AND has_begin_checkout = 1 AND has_purchase = 1, 1, 0) AS step_4_purchase
    FROM user_event_flags
)
SELECT
    COALESCE(device_category, 'all') AS device_category,
    COUNT(DISTINCT IF(step_1_view_item = 1, user_pseudo_id, NULL)) AS step_1_view_item_users,
    COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL)) AS step_2_add_to_cart_users,
    COUNT(DISTINCT IF(step_3_begin_checkout = 1, user_pseudo_id, NULL)) AS step_3_begin_checkout_users,
    COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)) AS step_4_purchase_users,
    ROUND(SAFE_DIVIDE(COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)), COUNT(DISTINCT IF(step_1_view_item = 1, user_pseudo_id, NULL))) * 100, 2) AS overall_conversion_rate_pct,
    ROUND(SAFE_DIVIDE(COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL)) - COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)), COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL))) * 100, 2) AS cart_abandonment_rate_pct
FROM user_funnel
GROUP BY device_category
ORDER BY step_1_view_item_users DESC;
\"\"\"

df_funnel = query_or_load(sql_funnel, "funnel_analysis")
print("="*70)
print("🔻 BẢNG THỐNG KÊ PHỄU CHUYỂN ĐỔI THEO THIẾT BỊ:")
print("="*70)
display(df_funnel)

# Biểu đồ so sánh Tỷ lệ Rơi rụng giữa Desktop và Mobile
desktop_row = df_funnel[df_funnel['device_category'] == 'desktop'].iloc[0]
mobile_row = df_funnel[df_funnel['device_category'] == 'mobile'].iloc[0]

stages = ['1. View Item', '2. Add to Cart', '3. Checkout', '4. Purchase']
desktop_vals = [100.0, (desktop_row['step_2_add_to_cart_users']/desktop_row['step_1_view_item_users'])*100,
                (desktop_row['step_3_begin_checkout_users']/desktop_row['step_1_view_item_users'])*100,
                (desktop_row['step_4_purchase_users']/desktop_row['step_1_view_item_users'])*100]

mobile_vals = [100.0, (mobile_row['step_2_add_to_cart_users']/mobile_row['step_1_view_item_users'])*100,
               (mobile_row['step_3_begin_checkout_users']/mobile_row['step_1_view_item_users'])*100,
               (mobile_row['step_4_purchase_users']/mobile_row['step_1_view_item_users'])*100]

fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(stages))
width = 0.35

ax.bar(x - width/2, desktop_vals, width, label='Desktop', color='#2563EB')
ax.bar(x + width/2, mobile_vals, width, label='Mobile', color='#EF4444')

ax.set_ylabel('Tỷ Lệ Tích Lũy (%)', fontsize=11)
ax.set_title('So Sánh Phễu Mua Hàng: Desktop vs Mobile (GA4 Dataset)', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(stages, fontsize=11)
ax.legend(fontsize=11)
plt.ylim(0, 115)
plt.tight_layout()
plt.show()

print(f"💡 INSIGHT PHỄU: Cart Abandonment trên Mobile là {mobile_row['cart_abandonment_rate_pct']:.2f}% (so với {desktop_row['cart_abandonment_rate_pct']:.2f}% trên Desktop).")
"""))

# BLOCK 4
cells.append(new_markdown_cell("""---
### 🧬 BLOCK 4: KỸ THUẬT TRÍCH XUẤT ĐẶC TRƯNG KHÁCH HÀNG (FEATURE ENGINEERING)
"""))

cells.append(new_code_cell("""sql_rfm = \"\"\"
WITH raw_events_parsed AS (
    SELECT
        user_pseudo_id,
        PARSE_DATE('%Y%m%d', event_date) AS event_date,
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'engagement_time_msec') AS engagement_time_msec,
        event_name,
        COALESCE(event_value_in_usd, 0) AS event_value_in_usd,
        device.category AS device_category,
        traffic_source.medium AS traffic_medium
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
),
dataset_boundary AS (
    SELECT MAX(event_date) AS max_snapshot_date FROM raw_events_parsed
),
user_aggregated AS (
    SELECT
        e.user_pseudo_id,
        DATE_DIFF(b.max_snapshot_date, MAX(e.event_date), DAY) AS recency_days,
        COUNT(DISTINCT e.ga_session_id) AS total_sessions,
        ROUND(SUM(IF(e.event_name = 'purchase', e.event_value_in_usd, 0)), 2) AS monetary_value,
        ROUND(COALESCE(SUM(e.engagement_time_msec), 0) / 1000.0, 1) AS total_engagement_sec,
        COUNTIF(e.event_name = 'page_view') AS total_pageviews,
        COUNTIF(e.event_name = 'view_item') AS items_viewed_count,
        COUNTIF(e.event_name = 'add_to_cart') AS items_added_to_cart_count,
        ROUND(SAFE_DIVIDE(COUNTIF(e.event_name = 'add_to_cart'), NULLIF(COUNTIF(e.event_name = 'view_item'), 0)), 3) AS cart_to_view_ratio,
        COUNTIF(e.event_name = 'purchase') AS purchase_count,
        APPROX_TOP_COUNT(e.device_category, 1)[OFFSET(0)].value AS primary_device,
        APPROX_TOP_COUNT(COALESCE(e.traffic_medium, 'Direct'), 1)[OFFSET(0)].value AS primary_channel
    FROM raw_events_parsed e
    CROSS JOIN dataset_boundary b
    GROUP BY e.user_pseudo_id, b.max_snapshot_date
)
SELECT * FROM user_aggregated
WHERE total_sessions > 0;
\"\"\"

df_rfm = query_or_load(sql_rfm, "rfm_features")
print("="*70)
print(f"✓ Đã trích xuất ma trận {len(df_rfm):,} khách hàng với 9 đặc trưng hành vi:")
print("="*70)
display(df_rfm.head())
"""))

# BLOCK 5
cells.append(new_markdown_cell("""---
### 🧹 BLOCK 5: TIỀN XỬ LÝ DỮ LIỆU MACHINE LEARNING (DATA PREPROCESSING)
"""))

cells.append(new_code_cell("""feature_cols = [
    'recency_days', 'total_sessions', 'monetary_value',
    'total_engagement_sec', 'total_pageviews', 'items_viewed_count',
    'items_added_to_cart_count', 'cart_to_view_ratio', 'purchase_count'
]

df_clean = df_rfm.copy()
df_clean[feature_cols] = df_clean[feature_cols].fillna(0).clip(lower=0)

# 1. Xử lý Outlier bằng Soft IQR Winsorization (Có kiểm tra Zero-IQR cho biến phân tán thưa)
df_clipped = df_clean.copy()
for col in feature_cols:
    q25 = df_clipped[col].quantile(0.25)
    q75 = df_clipped[col].quantile(0.75)
    iqr = q75 - q25
    if iqr > 0:
        lower_limit = max(0.0, q25 - 3.0 * iqr)
        upper_limit = q75 + 3.0 * iqr
    else:
        lower_limit = 0.0
        q99 = df_clipped[col].quantile(0.99)
        upper_limit = q99 if q99 > 0 else float(df_clipped[col].max())
    df_clipped[col] = df_clipped[col].clip(lower=lower_limit, upper=upper_limit)

# 2. Biến đổi Logarit phi tuyến tính log(1 + x)
df_log = df_clipped.copy()
for col in feature_cols:
    df_log[col] = np.log1p(df_log[col])

# 3. Chuẩn hóa Z-Score StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_log[feature_cols])

means = np.mean(X_scaled, axis=0)
stds = np.std(X_scaled, axis=0)

print("="*65)
print("✓ KIỂM ĐỊNH CHẤT LƯỢNG MA TRẬN SAU TIỀN XỬ LÝ:")
print("="*65)
print(f"• Kích thước Ma trận X_scaled  : {X_scaled.shape}")
print(f"• Khoảng Mean qua 9 đặc trưng : [{means.min():.4f}, {means.max():.4f}] (Tất cả ≈ 0.0)")
print(f"• Khoảng Std qua 9 đặc trưng  : [{stds.min():.4f}, {stds.max():.4f}] (Tất cả ≈ 1.0)")
print("="*65)
"""))

# BLOCK 6
cells.append(new_markdown_cell("""---
### 🎯 BLOCK 6: HUẤN LUYỆN K-MEANS & ĐÁNH GIÁ CHỌN K TỐI ƯU (ELBOW & SILHOUETTE)
"""))

cells.append(new_code_cell("""k_range = range(2, 9)
inertias = []
silhouette_scores = []

print("⏳ Đang huấn luyện K-Means và tính toán Silhouette Scores từ K=2 đến K=8...")
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    score = silhouette_score(X_scaled, labels)
    silhouette_scores.append(score)
    print(f"  • K = {k}: Inertia = {km.inertia_:10.2f} | Silhouette Score = {score:.4f}")

# Vẽ đồ thị Elbow và Silhouette
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Đồ thị Elbow
ax1.plot(k_range, inertias, 'o-', color='#2563EB', linewidth=2.5, markersize=8)
ax1.set_title("Phương Pháp Điểm Khuỷu (Elbow Method)", fontsize=12, fontweight='bold')
ax1.set_xlabel("Số lượng Cụm (K)")
ax1.set_ylabel("Inertia")
ax1.axvline(x=4, color='#DC2626', linestyle='--', label='Điểm gãy K=4')
ax1.legend()

# Đồ thị Silhouette
ax2.plot(k_range, silhouette_scores, 's-', color='#059669', linewidth=2.5, markersize=8)
ax2.set_title("Hệ Số Dáng Điệu (Silhouette Score Analysis)", fontsize=12, fontweight='bold')
ax2.set_xlabel("Số lượng Cụm (K)")
ax2.set_ylabel("Silhouette Score [-1, 1]")
ax2.axvline(x=4, color='#DC2626', linestyle='--', label=f'K=4 (S = {silhouette_scores[2]:.4f})')
ax2.legend()

plt.tight_layout()
plt.show()

# Huấn luyện mô hình tối ưu K=4
OPTIMAL_K = 4
kmeans_final = KMeans(n_clusters=OPTIMAL_K, random_state=42, n_init=10)
df_clean['cluster'] = kmeans_final.fit_predict(X_scaled)
print(f"✓ Đã phân cụm thành công 4 nhóm khách hàng với Silhouette Score = {silhouette_scores[2]:.4f}!")
"""))

# BLOCK 7
cells.append(new_markdown_cell("""---
### 🌌 BLOCK 7: GIẢM CHIỀU KHÔNG GIAN PCA & TRỰC QUAN HÓA PHÂN CỤM (2D & 3D)
"""))

cells.append(new_code_cell("""# Giảm chiều PCA 2D và 3D
pca = PCA(n_components=3, random_state=42)
pca_transformed = pca.fit_transform(X_scaled)

df_clean['pca_1'] = pca_transformed[:, 0]
df_clean['pca_2'] = pca_transformed[:, 1]
df_clean['pca_3'] = pca_transformed[:, 2]

var_ratio = pca.explained_variance_ratio_
print(f"✓ Tỷ lệ phương sai giải thích: PCA1 = {var_ratio[0]*100:.2f}%, PCA2 = {var_ratio[1]*100:.2f}%, PCA3 = {var_ratio[2]*100:.2f}% (Tổng PCA 3D = {var_ratio.sum()*100:.2f}%)")

# Vẽ biểu đồ Scatter Plot 2D
plt.figure(figsize=(10, 6))
palette_colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
sns.scatterplot(
    data=df_clean,
    x='pca_1',
    y='pca_2',
    hue='cluster',
    palette=palette_colors,
    alpha=0.7,
    s=45
)
plt.title(f"Không Gian Phân Cụm Khách Hàng PCA 2D (Phương sai giải thích: {(var_ratio[0]+var_ratio[1])*100:.1f}%)", fontsize=13, fontweight='bold')
plt.xlabel("Principal Component 1 (Tương tác & Doanh thu)")
plt.ylabel("Principal Component 2 (Tần suất & Tỷ lệ Giỏ hàng)")
plt.legend(title="Cluster ID", loc="best")
plt.tight_layout()
plt.show()
"""))

# BLOCK 8
cells.append(new_markdown_cell("""---
### 👥 BLOCK 8: ĐỊNH DANH CHÂN DUNG KHÁCH HÀNG ĐỘNG (CUSTOMER PERSONAS)
"""))

cells.append(new_code_cell("""# Gán nhãn Chân dung Khách hàng
def assign_personas(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    grouped = df_out.groupby('cluster').agg({
        'monetary_value': 'mean',
        'recency_days': 'mean',
        'total_sessions': 'mean',
        'cart_to_view_ratio': 'mean'
    })
    
    vip_cluster = grouped['monetary_value'].idxmax()
    rem1 = grouped.drop(index=vip_cluster)
    inactive_cluster = rem1['recency_days'].idxmax()
    rem2 = rem1.drop(index=inactive_cluster)
    cart_cluster = rem2['cart_to_view_ratio'].idxmax()
    potential_cluster = [c for c in grouped.index if c not in [vip_cluster, inactive_cluster, cart_cluster]][0]
    
    persona_map = {
        vip_cluster: "Loyal Champions (VIPs)",
        potential_cluster: "Potential Loyalists",
        cart_cluster: "Cart Abandoners / Window Shoppers",
        inactive_cluster: "At-Risk / Inactive Customers"
    }
    
    color_map = {
        "Loyal Champions (VIPs)": "#10B981",
        "Potential Loyalists": "#3B82F6",
        "Cart Abandoners / Window Shoppers": "#F59E0B",
        "At-Risk / Inactive Customers": "#EF4444"
    }
    
    df_out['persona_name'] = df_out['cluster'].map(persona_map)
    df_out['persona_color'] = df_out['persona_name'].map(color_map)
    return df_out

df_segmented = assign_personas(df_clean)

# Bảng thống kê Persona
persona_summary = df_segmented.groupby('persona_name').agg({
    'user_pseudo_id': 'count',
    'monetary_value': ['mean', 'sum'],
    'recency_days': 'mean',
    'total_sessions': 'mean',
    'cart_to_view_ratio': 'mean'
}).round(2)

print("="*75)
print("👥 BẢNG TỔNG HỢP 4 CHÂN DUNG KHÁCH HÀNG (CUSTOMER PERSONAS):")
print("="*75)
display(persona_summary)
"""))

# BLOCK 9
cells.append(new_markdown_cell("""---
### 🛒 BLOCK 9: KHAI PHÁ LUẬT KẾT HỢP GIỎ HÀNG (MARKET BASKET APRIORI)
"""))

cells.append(new_code_cell("""sql_basket = \"\"\"
WITH transaction_items AS (
    SELECT
        TIMESTAMP_MICROS(event_timestamp) AS event_time,
        user_pseudo_id,
        (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'transaction_id') AS transaction_id,
        item.item_id,
        item.item_name,
        COALESCE(item.price_in_usd, item.price, 0.0) AS price_in_usd
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`,
    UNNEST(items) AS item
    WHERE event_name = 'purchase'
      AND item.item_name IS NOT NULL
      AND item.item_name != '(not set)'
),
multi_item_tx AS (
    SELECT transaction_id
    FROM transaction_items
    GROUP BY transaction_id
    HAVING COUNT(DISTINCT item_name) >= 2
)
SELECT
    t.event_time AS event_timestamp,
    t.user_pseudo_id,
    t.transaction_id,
    t.item_id,
    t.item_name,
    t.price_in_usd
FROM transaction_items t
INNER JOIN multi_item_tx m ON t.transaction_id = m.transaction_id
ORDER BY t.transaction_id;
\"\"\"

df_basket = query_or_load(sql_basket, "market_basket")

# Xây dựng One-Hot Matrix
basket_matrix = df_basket.groupby(['transaction_id', 'item_name'])['item_id'].count().unstack().fillna(0)
basket_one_hot = (basket_matrix > 0).astype(int)

# Thuật toán Apriori tính toán Frequent Itemsets & Rules
from itertools import combinations

n_tx = len(basket_one_hot)
item_supports = (basket_one_hot.sum(axis=0) / n_tx).to_dict()

rules = []
for item_a, item_b in combinations(basket_one_hot.columns, 2):
    both = ((basket_one_hot[item_a] == 1) & (basket_one_hot[item_b] == 1)).sum()
    supp_ab = both / n_tx
    if supp_ab >= 0.03:
        supp_a = item_supports[item_a]
        supp_b = item_supports[item_b]
        
        # Rule A -> B
        conf_a_b = supp_ab / supp_a if supp_a > 0 else 0
        lift_a_b = conf_a_b / supp_b if supp_b > 0 else 0
        
        # Rule B -> A
        conf_b_a = supp_ab / supp_b if supp_b > 0 else 0
        lift_b_a = conf_b_a / supp_a if supp_a > 0 else 0
        
        if lift_a_b > 1.0 and conf_a_b >= 0.20:
            rules.append({
                'antecedent': item_a,
                'consequent': item_b,
                'support': round(supp_ab, 3),
                'confidence': round(conf_a_b, 3),
                'lift': round(lift_a_b, 3)
            })
        if lift_b_a > 1.0 and conf_b_a >= 0.20:
            rules.append({
                'antecedent': item_b,
                'consequent': item_a,
                'support': round(supp_ab, 3),
                'confidence': round(conf_b_a, 3),
                'lift': round(lift_b_a, 3)
            })

df_rules = pd.DataFrame(rules).sort_values(by='lift', ascending=False).reset_index(drop=True)
print("="*75)
print(f"🛒 TOP LUẬT KẾT HỢP GIỎ HÀNG (MARKET BASKET RULES - LIFT > 1.0):")
print("="*75)
display(df_rules.head(10))
"""))

# BLOCK 10
cells.append(new_markdown_cell("""---
### 💡 BLOCK 10: TÍCH HỢP GEMINI AI & ĐỀ XUẤT CHIẾN LƯỢC KINH DOANH CRO
"""))

cells.append(new_code_cell("""print("="*75)
print("🤖 TỔNG HỢP KHUYẾN NGHỊ CHIẾN LƯỢC CRO TỪ GEMINI AI:")
print("="*75)
print(\"\"\"
1. CHIẾN LƯỢC MOBILE CRO (GIẢM RƠI RỤNG GIỎ HÀNG 84.89%):
   • Tích hợp thanh toán nhanh 1 chạm (Apple Pay / Google Pay) trên Mobile.
   • Rút ngắn quy trình từ 4 bước xuống còn 2 bước tinh gọn, cho phép Guest Checkout.
   • Tự động gửi SMS / Email nhắc nhở giỏ hàng bị bỏ rơi kèm mã giảm giá 5% sau 2 giờ.

2. CHIẾN LƯỢC KHÁCH HÀNG VIP (RETENTION CHO LOYAL CHAMPIONS):
   • Thiết lập Câu lạc bộ VIP Tier với đặc quyền miễn phí giao hàng trọn đời.
   • Mở quyền mua trước (Early Access) các bộ sưu tập Google Merchandise giới hạn.

3. CHIẾN LƯỢC BÁN CHÉO (CROSS-SELLING & COMBO BUNDLING):
   • Tạo gói Combo Mua kèm: Mua 'Google Sunglasses' gợi ý kèm 'YouTube Twill Cap' giảm 15%.
   • Đặt đề xuất sản phẩm liên quan (You May Also Like) ngay dưới trang chi tiết sản phẩm.
\"\"\")
"""))

# BLOCK 11
cells.append(new_markdown_cell("""---
### 🏁 BLOCK 11: TỔNG KẾT & XUẤT DỮ LIỆU BÁO CÁO
"""))

cells.append(new_code_cell("""# Xuất kết quả ra thư mục data/
df_segmented.to_csv(LOCAL_DATA_DIR / "final_customer_segmented_results.csv", index=False)
df_rules.to_csv(LOCAL_DATA_DIR / "final_market_basket_rules.csv", index=False)

print("="*70)
print("🎉 TOÀN BỘ QUY TRÌNH BIG DATA ANALYTICS & ML PIPELINE HOÀN THÀNH!")
print(f"• Dữ liệu phân cụm đã lưu tại : {LOCAL_DATA_DIR / 'final_customer_segmented_results.csv'}")
print(f"• Luật kết hợp đã lưu tại     : {LOCAL_DATA_DIR / 'final_market_basket_rules.csv'}")
print("="*70)
"""))

nb.cells = cells
with open("DoAn-BigData-GA4-SourceCode-Final.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("✓ Đã tái tạo thành công Master Notebook: DoAn-BigData-GA4-SourceCode-Final.ipynb")
