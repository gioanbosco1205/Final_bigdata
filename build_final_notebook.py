"""
Script to generate the Master All-in-One Jupyter Notebook: DoAn-BigData-GA4-SourceCode-Final.ipynb
"""

import json
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()

cells = []

# Title & Metadata
cells.append(new_markdown_cell("""# ĐỒ ÁN CUỐI KỲ: PHÂN TÍCH DỮ LIỆU LỚN (BIG DATA ANALYTICS)

### Đề tài: Phân tích hành vi Khách hàng trên Dữ liệu Thương mại Điện tử quy mô lớn bằng Google BigQuery SQL & Python
**Tập dữ liệu:** Google Analytics 4 (GA4) Obfuscated Sample E-commerce Dataset  
**Nền tảng thực thi:** Google Cloud BigQuery, Python Data/ML Pipeline, Diễn giải kết quả bằng Python

---
### MỤC LỤC BÁO CÁO SOURCE CODE:
- **BLOCK 0:** Khởi tạo Môi trường & Cài đặt Thư viện
- **BLOCK 1:** Kết nối Google Cloud & Quản lý Dữ liệu BigQuery
- **BLOCK 2:** Khám phá Dữ liệu Lớn & Tổng quan KPIs (BigQuery SQL EDA)
- **BLOCK 3:** Phân tích Phễu Mua Sắm & Điểm Rơi rụng (Funnel Diagnostics)
- **BLOCK 4:** Kỹ thuật Trích xuất Đặc trưng Khách hàng (RFM & Clickstream Features)
- **BLOCK 5:** Tiền xử lý Dữ liệu Chuẩn hóa (Cắt theo phân vị + Log1p + StandardScaler)
- **BLOCK 6:** Huấn luyện K-Means & Đánh giá So sánh các giá trị K (Elbow & Silhouette)
- **BLOCK 7:** PCA ba thành phần & Biểu đồ phân cụm 2D
- **BLOCK 8:** Định danh Chân dung Khách hàng Động (Customer Personas)
- **BLOCK 9:** Khai phá Luật Kết hợp Giỏ hàng (Market Basket Apriori)
- **BLOCK 10:** Diễn giải kết quả & Đề xuất kinh doanh từ dữ liệu thật
- **BLOCK 11:** Tổng kết & Xuất Dữ liệu Báo cáo

**Cách chạy:** chọn Python kernel rồi Restart & Run All từ BLOCK 0 đến BLOCK 11.
Notebook truy vấn dữ liệu trực tiếp; mọi lỗi xác thực hoặc truy vấn cần được xử lý trước khi diễn giải.
Không dùng output cũ để chứng minh một lần chạy mới đã thành công.

**Phạm vi phương pháp:** phân tích mô tả 01/11/2020–31/01/2021 trên GA4 đã làm mờ.
Recency dựa trên hoạt động gần nhất; Frequency đếm phiên, Monetary cộng giá trị purchase.
Phân cụm là khám phá hành vi; luật mua kèm có mẫu số là đơn đa sản phẩm hợp lệ.
"""))

# BLOCK 0
cells.append(new_markdown_cell("""---
### BLOCK 0: KHỞI TẠO MÔI TRƯỜNG & CÀI ĐẶT THƯ VIỆN
"""))

cells.append(new_code_cell("""# Cài thư viện còn thiếu vào đúng kernel; giữ nguyên môi trường nếu đã đủ.
import importlib.util
import subprocess
import sys
dependencies = {
    'google.cloud.bigquery': 'google-cloud-bigquery', 'db_dtypes': 'db-dtypes',
    'pyarrow': 'pyarrow', 'pandas': 'pandas', 'numpy': 'numpy',
    'matplotlib': 'matplotlib', 'seaborn': 'seaborn', 'plotly': 'plotly',
    'sklearn': 'scikit-learn', 'IPython': 'ipython',
}
missing_packages = []
for module, package in dependencies.items():
    try:
        available = importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:
        available = False
    if not available:
        missing_packages.append(package)
if missing_packages:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', *missing_packages])

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import display
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 110
print("✓ Đã khởi tạo thư viện phân tích và BigQuery.")
"""))

# BLOCK 1
cells.append(new_markdown_cell("""---
### BLOCK 1: KẾT NỐI GOOGLE CLOUD & TRUY VẤN DỮ LIỆU THẬT

Điền **Project ID của bạn** vào `PROJECT_ID` ở cell dưới (hoặc đặt biến môi trường
`GCP_PROJECT_ID`). Project này phải bật BigQuery API và có quyền tạo query job.
`bigquery-public-data` là project chứa dữ liệu nguồn, không phải project chạy job của bạn.
Trên Colab, đăng nhập tài khoản Google khi được yêu cầu. Trên máy cá nhân, cấu hình
Application Default Credentials trước khi chạy.

Notebook luôn truy vấn BigQuery. Nếu xác thực, truy vấn hoặc lưu kết quả thất bại,
cell báo lỗi; không đọc CSV/cache cũ và không sinh dữ liệu mô phỏng.
Kết quả thành công được lưu vào `data/bigquery_exports/` cùng SQL và metadata job.
Phạm vi nghiên cứu: 01/11/2020–31/01/2021.

**Đối chiếu dữ liệu cũ:** bốn CSV trực tiếp trong `data/` trùng khớp bộ sinh dữ liệu tổng hợp của `src/bq_client.py` (kiểm tra ngày 03/10/2026). Chúng không phải bằng chứng kết quả truy vấn BigQuery. Notebook này không nạp các CSV đó; chỉ dùng dữ liệu từ query job thành công.
"""))

cells.append(new_code_cell("""from google.cloud import bigquery
import google.auth

# Điền Project ID của bạn vào đây nếu chưa đặt GCP_PROJECT_ID.
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "bigdata-510510").strip()
SOURCE_TABLE = "bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*"
START_DATE = "20201101"
END_DATE = "20210131"
# Ngăn thay đổi cấu hình nhưng SQL vẫn truy vấn một khoảng ngày khác.
if (START_DATE, END_DATE, SOURCE_TABLE) != (
    '20201101', '20210131',
    'bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*',
):
    raise ValueError('Notebook này cố định phạm vi nghiên cứu; cập nhật đồng bộ cả bốn SQL khi đổi nguồn/ngày.')
MAXIMUM_BYTES_BILLED = 10 * 1024 ** 3  # Giới hạn mỗi query job: 10 GiB.
LOCAL_DATA_DIR = Path("data") / "bigquery_exports"
QUERY_MANIFEST = {}

# Xóa trạng thái từ lần chạy cũ để lỗi kết nối không giữ lại client/dữ liệu cũ.
bq_client = None
for variable in ("df_eda", "df_funnel", "df_rfm", "df_basket_raw", "df_clean",
                 "df_segmented", "df_rules", "summary_table", "X_scaled",
                 "PREPROCESSING_JOB_ID", "MODEL_JOB_ID", "PCA_JOB_ID",
                 "SEGMENTATION_JOB_ID", "RULES_JOB_ID"):
    globals().pop(variable, None)

if not PROJECT_ID or PROJECT_ID == "bigquery-public-data":
    raise ValueError(
        "Điền PROJECT_ID của Google Cloud project bạn sở hữu ở BLOCK 1, "
        "hoặc đặt GCP_PROJECT_ID. Không dùng bigquery-public-data để chạy job."
    )



def query_bigquery(query_sql: str, filename: str, allow_empty: bool = False) -> pd.DataFrame:
    \"\"\"Chỉ trả về kết quả BigQuery đã truy vấn và lưu thành công.\"\"\"
    QUERY_MANIFEST.pop(filename, None)
    dependent_state = {
        "rfm_features": ("df_clean", "X_scaled", "df_segmented", "summary_table",
                         "PREPROCESSING_JOB_ID", "MODEL_JOB_ID", "PCA_JOB_ID", "SEGMENTATION_JOB_ID"),
        "market_basket": ("df_rules", "RULES_JOB_ID"),
    }
    for name in dependent_state.get(filename, ()):
        globals().pop(name, None)
    if bq_client is None:
        raise RuntimeError("Chưa kết nối BigQuery. Chạy lại BLOCK 1.")
    print(f"Đang chạy SQL [{filename}] trên BigQuery, project={PROJECT_ID}...")
    try:
        job_config = bigquery.QueryJobConfig(
            use_legacy_sql=False,
            maximum_bytes_billed=globals().get('MAXIMUM_BYTES_BILLED', 10 * 1024 ** 3),
        )
        job = bq_client.query(query_sql, job_config=job_config, location="US")
        df = job.result().to_dataframe(create_bqstorage_client=False)
    except Exception as exc:
        raise RuntimeError(
            f"BigQuery thất bại ở [{filename}]. Kiểm tra quyền, quota và SQL; "
            "notebook không dùng dữ liệu dự phòng."
        ) from exc
    if df.empty and not allow_empty:
        raise ValueError(f"Truy vấn [{filename}] không trả về dữ liệu. Kiểm tra bộ lọc SQL.")

    metadata = {
        "source": SOURCE_TABLE,
        "date_range": [START_DATE, END_DATE],
        "execution_project": PROJECT_ID,
        "job_id": job.job_id,
        "location": job.location,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "query_sha256": hashlib.sha256(query_sql.encode("utf-8")).hexdigest(),
        "rows": len(df),
        "columns": list(df.columns),
        "total_bytes_processed": job.total_bytes_processed,
        "cache_hit": job.cache_hit,
    }
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Metadata được ghi cuối cùng, sau khi lưu xong dữ liệu và SQL.
    # File cũ không bao giờ được nạp lại bởi notebook.
    metadata_path = LOCAL_DATA_DIR / f"{filename}.metadata.json"
    metadata_path.unlink(missing_ok=True)
    try:
        df.to_csv(LOCAL_DATA_DIR / f"{filename}.csv", index=False)
        df.to_parquet(LOCAL_DATA_DIR / f"{filename}.parquet", index=False)
        (LOCAL_DATA_DIR / f"{filename}.sql").write_text(query_sql, encoding="utf-8")
        metadata['file_sha256'] = {
            suffix: hashlib.sha256((LOCAL_DATA_DIR / f'{filename}{suffix}').read_bytes()).hexdigest()
            for suffix in ('.csv', '.parquet', '.sql')
        }
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Đã truy vấn nhưng không lưu được [{filename}].") from exc
    df.attrs["bigquery_job_id"] = job.job_id
    QUERY_MANIFEST[filename] = metadata
    print(f"✓ BigQuery thành công: {len(df):,} dòng; job_id={job.job_id}")
    print(f"✓ Đã lưu CSV, Parquet, SQL và metadata vào {LOCAL_DATA_DIR.resolve()}")
    return df


def percentage(numerator, denominator):
    return 100.0 * float(numerator) / float(denominator) if denominator else float("nan")


try:
    from google.colab import auth
except ImportError:
    auth = None

try:
    if auth is not None:
        auth.authenticate_user()
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    bq_client = bigquery.Client(project=PROJECT_ID, credentials=credentials, location="US")
except Exception as exc:
    raise RuntimeError(
        "Không thể xác thực Google Cloud. Trên Colab hãy đăng nhập; "
        "trên máy cá nhân hãy cấu hình Application Default Credentials."
    ) from exc


print(f"✓ Client sẵn sàng: project={PROJECT_ID}; nguồn={SOURCE_TABLE}")
"""))

# BLOCK 2
cells.append(new_markdown_cell("""---
### BLOCK 2: KHÁM PHÁ DỮ LIỆU LỚN & TỔNG QUAN HIỆU SUẤT (BIGQUERY SQL EDA)

KPI toàn bộ lấy từ hàng `overall`. Purchase là số sự kiện, chưa phải đơn hàng đã khử trùng. `traffic_source.medium` là nguồn thu hút user, không phải attribution từng phiên. Users theo thiết bị có thể trùng; biểu đồ thiết bị dùng tổng user–thiết bị làm mẫu số.
"""))

cells.append(new_code_cell("""sql_eda = \"\"\"
WITH base_events AS (
    SELECT user_pseudo_id, event_name,
        COALESCE(traffic_source.medium, '(not set)') AS traffic_medium,
        COALESCE(device.category, '(not set)') AS device_category,
        COALESCE(geo.country, '(not set)') AS country,
        (SELECT value.int_value FROM UNNEST(event_params)
         WHERE key = 'ga_session_id' LIMIT 1) AS session_id,
        IF(event_name = 'purchase',
           COALESCE(ecommerce.purchase_revenue_in_usd, event_value_in_usd, 0), 0) AS revenue_usd
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
)
SELECT
    CASE WHEN GROUPING(traffic_medium) = 0 THEN 'channel'
         WHEN GROUPING(device_category) = 0 THEN 'device'
         WHEN GROUPING(country) = 0 THEN 'country'
         ELSE 'overall' END AS aggregation_level,
    traffic_medium, device_category, country,
    COUNT(DISTINCT user_pseudo_id) AS total_users,
    COUNT(DISTINCT CONCAT(user_pseudo_id, ':', CAST(session_id AS STRING))) AS total_sessions,
    COUNTIF(event_name = 'page_view') AS total_pageviews,
    COUNTIF(event_name = 'purchase') AS total_purchases,
    ROUND(SUM(revenue_usd), 2) AS total_revenue_usd
FROM base_events
GROUP BY GROUPING SETS ((), (traffic_medium), (device_category), (country))
ORDER BY aggregation_level, total_users DESC;
\"\"\"

globals().pop('df_eda', None)
df_eda = query_bigquery(sql_eda, "eda_overview")

# Lấy KPI từ phép tổng hợp toàn bộ dữ liệu, tránh đếm trùng người dùng giữa các nhóm.
overall_rows = df_eda.loc[df_eda['aggregation_level'] == 'overall']
if len(overall_rows) != 1:
    raise ValueError("EDA phải có đúng một hàng tổng hợp toàn sàn.")
overall = overall_rows.iloc[0]
total_users = int(overall['total_users'])
total_sessions = int(overall['total_sessions'])
total_revenue = float(overall['total_revenue_usd'])
total_orders = int(overall['total_purchases'])
overall_cvr = percentage(total_orders, total_sessions)
print(f"Người dùng: {total_users:,}; phiên: {total_sessions:,}")
print(f"Doanh thu mua hàng: ${total_revenue:,.2f} USD")
print(f"Sự kiện purchase: {total_orders:,}; purchase/phiên: {overall_cvr:.2f}%")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
df_channel = df_eda.loc[df_eda['aggregation_level'] == 'channel'].nlargest(5, 'total_users')
sns.barplot(data=df_channel, x='total_users', y='traffic_medium', ax=axes[0], color='#3B82F6')
axes[0].set_title("Top 5 Kênh Tiếp Thị Theo Người Dùng")
axes[0].set_xlabel("Người dùng riêng biệt trong từng kênh")
axes[0].set_ylabel("Kênh tiếp thị")
df_device = df_eda.loc[df_eda['aggregation_level'] == 'device']
if df_device['total_users'].sum() > 0:
    axes[1].pie(df_device['total_users'], labels=df_device['device_category'], autopct='%1.1f%%')
else:
    axes[1].text(0.5, 0.5, "Không có người dùng có mã định danh", ha='center')
axes[1].set_title("Tỷ trọng user–thiết bị (có thể trùng user)")
plt.tight_layout()
plt.show()
print("Lưu ý: một user có thể xuất hiện ở nhiều thiết bị/kênh; không cộng các nhóm để tính users toàn sàn.")
"""))

# BLOCK 3
cells.append(new_markdown_cell("""---
### BLOCK 3: PHỄU MUA HÀNG THEO THỨ TỰ THỜI GIAN

Đếm user riêng biệt trên cùng thiết bị có chuỗi `view_item → add_to_cart →
begin_checkout → purchase`, với timestamp bước sau lớn hơn bước trước.
Chuỗi có thể trải qua nhiều phiên trong phạm vi nghiên cứu, không khẳng định cùng
một giỏ hàng. Các sự kiện trùng timestamp không được coi là đã xác định thứ tự.
Hàng `all` đếm user riêng biệt trên các thiết bị, không cộng các hàng thiết bị.
"""))

cells.append(new_code_cell("""sql_funnel = \"\"\"
WITH funnel_events AS (
    SELECT user_pseudo_id, COALESCE(device.category, '(not set)') AS device_category,
        event_name, event_timestamp
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
      AND user_pseudo_id IS NOT NULL
      AND event_name IN ('view_item', 'add_to_cart', 'begin_checkout', 'purchase')
), views AS (
    SELECT user_pseudo_id, device_category, MIN(event_timestamp) AS view_ts
    FROM funnel_events WHERE event_name = 'view_item'
    GROUP BY user_pseudo_id, device_category
), carts AS (
    SELECT v.user_pseudo_id, v.device_category, v.view_ts, MIN(e.event_timestamp) AS cart_ts
    FROM views v LEFT JOIN funnel_events e
      ON e.user_pseudo_id = v.user_pseudo_id AND e.device_category = v.device_category
      AND e.event_name = 'add_to_cart' AND e.event_timestamp > v.view_ts
    GROUP BY v.user_pseudo_id, v.device_category, v.view_ts
), checkouts AS (
    SELECT c.user_pseudo_id, c.device_category, c.view_ts, c.cart_ts,
        MIN(e.event_timestamp) AS checkout_ts
    FROM carts c LEFT JOIN funnel_events e
      ON e.user_pseudo_id = c.user_pseudo_id AND e.device_category = c.device_category
      AND e.event_name = 'begin_checkout' AND e.event_timestamp > c.cart_ts
    GROUP BY c.user_pseudo_id, c.device_category, c.view_ts, c.cart_ts
), purchases AS (
    SELECT c.user_pseudo_id, c.device_category, c.view_ts, c.cart_ts, c.checkout_ts,
        MIN(e.event_timestamp) AS purchase_ts
    FROM checkouts c LEFT JOIN funnel_events e
      ON e.user_pseudo_id = c.user_pseudo_id AND e.device_category = c.device_category
      AND e.event_name = 'purchase' AND e.event_timestamp > c.checkout_ts
    GROUP BY c.user_pseudo_id, c.device_category, c.view_ts, c.cart_ts, c.checkout_ts
)
SELECT IF(GROUPING(p.device_category) = 1, 'all', p.device_category) AS device_category,
    COUNT(DISTINCT user_pseudo_id) AS step1_view_item,
    COUNT(DISTINCT IF(cart_ts IS NOT NULL, user_pseudo_id, NULL)) AS step2_add_to_cart,
    COUNT(DISTINCT IF(checkout_ts IS NOT NULL, user_pseudo_id, NULL)) AS step3_begin_checkout,
    COUNT(DISTINCT IF(purchase_ts IS NOT NULL, user_pseudo_id, NULL)) AS step4_purchase
FROM purchases AS p
GROUP BY GROUPING SETS ((), (p.device_category))
ORDER BY step1_view_item DESC;
\"\"\"

globals().pop('df_funnel', None)
df_funnel = query_bigquery(sql_funnel, "funnel_analysis")
stage_cols = ['step1_view_item', 'step2_add_to_cart', 'step3_begin_checkout', 'step4_purchase']
stage_values = df_funnel[stage_cols].astype('float64').to_numpy()
if not np.isfinite(stage_values).all() or (stage_values < 0).any():
    raise ValueError("Phễu chứa số user thiếu, âm hoặc vô cực.")
if not (np.diff(stage_values, axis=1) <= 0).all():
    raise ValueError("Số user ở bước sau lớn hơn bước trước. Kiểm tra SQL phễu.")
all_rows = df_funnel.loc[df_funnel['device_category'] == 'all']
if len(all_rows) != 1:
    raise ValueError("Phễu phải có đúng một hàng all.")
funnel_all = all_rows.iloc[0]
s1, s2, s3, s4 = [int(funnel_all[col]) for col in stage_cols]
for label, count in zip(['Xem sản phẩm', 'Thêm giỏ', 'Thanh toán', 'Mua hàng'], [s1, s2, s3, s4]):
    print(f"{label}: {count:,} user ({percentage(count, s1):.2f}% so với bước 1)")

df_funnel['cart_abandonment_rate_pct'] = [
    percentage(row.step2_add_to_cart - row.step4_purchase, row.step2_add_to_cart)
    if row.step2_add_to_cart else np.nan for row in df_funnel.itertuples()
]
for output, numerator, denominator in [
    ('overall_conversion_rate_pct', 'step4_purchase', 'step1_view_item'),
    ('step1_to_step2_cr_pct', 'step2_add_to_cart', 'step1_view_item'),
    ('step2_to_step3_cr_pct', 'step3_begin_checkout', 'step2_add_to_cart'),
    ('step3_to_step4_cr_pct', 'step4_purchase', 'step3_begin_checkout'),
]:
    df_funnel[output] = [percentage(n, d) if d else np.nan
                         for n, d in zip(df_funnel[numerator], df_funnel[denominator])]
display(df_funnel)
fig, ax = plt.subplots(figsize=(10, 5))
device_rows = df_funnel.loc[df_funnel['device_category'].isin(['desktop', 'mobile'])]
x = np.arange(4)
width = 0.8 / max(1, len(device_rows))
for offset, (_, row) in enumerate(device_rows.iterrows()):
    rates = [percentage(row[col], row['step1_view_item']) for col in stage_cols]
    ax.bar(x - 0.4 + width / 2 + offset * width, rates, width, label=row['device_category'])
ax.set_xticks(x, ['View Item', 'Add to Cart', 'Checkout', 'Purchase'])
ax.set_ylabel('Tỷ lệ tích lũy (%)')
ax.set_title('Phễu theo thiết bị từ kết quả BigQuery')
if not device_rows.empty:
    ax.legend()
plt.tight_layout()
plt.show()
for row in device_rows.itertuples():
    if pd.notna(row.cart_abandonment_rate_pct):
        print(f"Tỷ lệ user thêm giỏ chưa hoàn tất chuỗi trên {row.device_category}: {row.cart_abandonment_rate_pct:.2f}%")
    else:
        print(f"{row.device_category}: chưa có user thêm giỏ để tính tỷ lệ.")
"""))

# BLOCK 4
cells.append(new_markdown_cell("""---
### BLOCK 4: KỸ THUẬT TRÍCH XUẤT ĐẶC TRƯNG KHÁCH HÀNG (FEATURE ENGINEERING)

Đây là bộ đặc trưng hoạt động mở rộng: R = ngày từ sự kiện cuối đến 31/01/2021; F = số phiên có ga_session_id; M = tổng giá trị sự kiện purchase. Người không mua vẫn được giữ. Không diễn giải đây là RFM chỉ dành cho người mua hoặc doanh thu ròng sau hoàn tiền.
"""))

cells.append(new_code_cell("""sql_rfm = \"\"\"
WITH raw_user_events AS (
    SELECT user_pseudo_id, event_name, PARSE_DATE('%Y%m%d', event_date) AS event_date,
        (SELECT value.int_value FROM UNNEST(event_params)
         WHERE key = 'ga_session_id' LIMIT 1) AS session_id,
        (SELECT value.int_value FROM UNNEST(event_params)
         WHERE key = 'engagement_time_msec' LIMIT 1) AS engagement_time_msec,
        IF(event_name = 'purchase',
           COALESCE(ecommerce.purchase_revenue_in_usd, event_value_in_usd, 0), 0) AS purchase_value
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
      AND user_pseudo_id IS NOT NULL
)
SELECT user_pseudo_id,
    DATE_DIFF(DATE('2021-01-31'), MAX(event_date), DAY) AS recency_days,
    COUNT(DISTINCT session_id) AS frequency_sessions,
    ROUND(SUM(purchase_value), 2) AS monetary_usd,
    COUNTIF(event_name = 'view_item') AS view_item_count,
    COUNTIF(event_name = 'add_to_cart') AS add_to_cart_count,
    COUNTIF(event_name = 'begin_checkout') AS checkout_count,
    COUNTIF(event_name = 'purchase') AS purchase_count,
    ROUND(COALESCE(SAFE_DIVIDE(COUNTIF(event_name = 'add_to_cart'),
                              COUNTIF(event_name = 'view_item')), 0), 3) AS cart_to_view_ratio,
    ROUND(COALESCE(SUM(engagement_time_msec), 0) / 1000.0, 1) AS total_engagement_time_sec,
    COUNTIF(event_name = 'page_view') AS total_pageviews
FROM raw_user_events
GROUP BY user_pseudo_id;
\"\"\"

globals().pop('df_rfm', None)
df_rfm = query_bigquery(sql_rfm, "rfm_features")
if df_rfm['user_pseudo_id'].isna().any():
    raise ValueError("RFM chứa user thiếu mã định danh.")
if df_rfm['user_pseudo_id'].duplicated().any():
    raise ValueError("RFM có user trùng lặp.")
if not df_rfm['recency_days'].between(0, 91).all():
    raise ValueError("Recency nằm ngoài khoảng ngày nghiên cứu.")
print(f"✓ BigQuery trả về {len(df_rfm):,} user, {len(df_rfm.columns)} cột.")
display(df_rfm.head(5))
print("Recency tính từ lần hoạt động cuối, không phải lần mua cuối. Frequency đếm phiên; purchase_count đếm sự kiện purchase; tỷ lệ thêm giỏ/xem có thể lớn hơn 1.")
"""))

# BLOCK 5
cells.append(new_markdown_cell("""---
### BLOCK 5: TIỀN XỬ LÝ DỮ LIỆU MACHINE LEARNING

Chỉ chuyển chín đặc trưng số sang `float64`; dữ liệu BigQuery gốc được giữ lại.
Ngưỡng cắt trên là Q99 + 1,5 × (Q99 − Q01), không phải IQR Q25/Q75.
Nếu ngưỡng bằng 0 trên cột hiếm có giá trị dương, giữ cột để không xóa hành vi hiếm.
Sau đó dùng log1p và StandardScaler. Cột hằng sau chuẩn hóa có độ lệch chuẩn 0.
"""))

cells.append(new_code_cell("""feature_cols = [
    'recency_days', 'frequency_sessions', 'monetary_usd',
    'view_item_count', 'add_to_cart_count', 'checkout_count',
    'cart_to_view_ratio', 'total_engagement_time_sec', 'total_pageviews'
]

if 'df_rfm' not in globals():
    raise RuntimeError('Chưa có kết quả BLOCK 4. Chạy block đó thành công trước khi tiếp tục.')
for name in ('X_scaled', 'MODEL_JOB_ID', 'PCA_JOB_ID', 'SEGMENTATION_JOB_ID',
             'df_segmented', 'summary_table'):
    globals().pop(name, None)
df_clean = df_rfm.copy()
if df_clean.empty:
    raise ValueError("RFM rỗng. Chạy lại BLOCK 4.")
PREPROCESSING_JOB_ID = df_rfm.attrs.get('bigquery_job_id')

# 1. Chuyển đặc trưng ML sang float64 để nhận ngưỡng clipping thập phân.
# BigQuery có thể trả cột đếm về Int64 (nullable integer).
df_clean[feature_cols] = (
    df_clean[feature_cols]
    .apply(pd.to_numeric, errors='raise')
    .astype('float64')
)

missing_feature_counts = df_clean[feature_cols].isna().sum()
if not np.isfinite(df_clean[feature_cols].fillna(0).to_numpy()).all():
    raise ValueError('Đặc trưng đầu vào chứa giá trị vô cực.')
negative_feature_counts = df_clean[feature_cols].lt(0).sum()
if negative_feature_counts.any():
    raise ValueError('Đặc trưng chứa giá trị âm: ' + str(negative_feature_counts[negative_feature_counts > 0].to_dict())
                     + '. Kiểm tra nguồn; không tự đổi dữ liệu âm thành 0.')
# Giá trị thiếu được điền 0 theo quy ước đặc trưng không ghi nhận; luôn báo số lượng.
df_clean[feature_cols] = df_clean[feature_cols].fillna(0)
if missing_feature_counts.any():
    print('Giá trị thiếu được điền 0:', missing_feature_counts[missing_feature_counts > 0].to_dict())
if not np.isfinite(df_clean[feature_cols].to_numpy()).all():
    raise ValueError("Đặc trưng đầu vào chứa giá trị vô cực.")
# df_rfm giữ dữ liệu nguồn; df_clean giữ thang đo gốc để diễn giải cụm.

# 2. Cắt trên theo phân vị, giữ các cột hành vi hiếm có Q99 = 0.
clipping_caps = {}
sparse_features_preserved = []
df_clipped = df_clean.copy()
for col in feature_cols:
    if col != 'cart_to_view_ratio':
        q1 = df_clipped[col].quantile(0.01)
        q3 = df_clipped[col].quantile(0.99)
        iqr = q3 - q1
        upper_limit = q3 + 1.5 * iqr
        if upper_limit > 0:
            clipping_caps[col] = float(upper_limit)
            df_clipped[col] = df_clipped[col].clip(upper=upper_limit)
        elif (df_clipped[col] > 0).any():
            sparse_features_preserved.append(col)

# 3. Biến đổi Logarit phi tuyến tính log(1 + x)
df_log = df_clipped.copy()
for col in feature_cols:
    if col != 'cart_to_view_ratio':
        df_log[col] = np.log1p(df_log[col])

# 4. Chuẩn hóa Z-Score StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_log[feature_cols])

# Kiểm tra chất lượng dữ liệu sau chuẩn hóa
means = np.mean(X_scaled, axis=0)
stds = np.std(X_scaled, axis=0)
has_nan = not np.isfinite(X_scaled).all()

print("="*60)
print("✓ KIỂM ĐỊNH CHẤT LƯỢNG DỮ LIỆU SAU TIỀN XỬ LÝ:")
print("="*60)
print(f"• Kích thước Ma trận X_scaled  : {X_scaled.shape}")
print(f"• Giá trị Trung bình (Mean)   : [{means.min():.4f}, {means.max():.4f}] (Tất cả ≈ 0.0)")
constant_features = [col for col, std in zip(feature_cols, stds) if std == 0]
print(f"• Độ lệch chuẩn (Std): [{stds.min():.4f}, {stds.max():.4f}]; cột hằng có std = 0")
print(f"• Cột hằng: {constant_features}; cột hiếm giữ nguyên: {sparse_features_preserved}")
print(f"• Chứa giá trị NaN / Inf      : {'CÓ LỖI' if has_nan else 'HOÀN HẢO (0 NaN)'}")
print("="*60)

if has_nan:
    raise ValueError("Ma trận đặc trưng chứa NaN hoặc Inf.")
preprocessing_audit = pd.DataFrame({
    'feature': feature_cols,
    'missing_filled_zero': missing_feature_counts.to_numpy(),
    'upper_cap': [clipping_caps.get(col, np.nan) for col in feature_cols],
    'clipped_rows': [(df_clean[col] != df_clipped[col]).sum() for col in feature_cols],
    'scaled_mean': means, 'scaled_std': stds,
})
feature_correlations = df_log[feature_cols].corr()
print('Đặc trưng gồm nhiều chỉ số hành vi tương quan; K-Means là phân tích khám phá, chưa phải mô hình dự đoán.')
print(preprocessing_audit.to_string(index=False))
"""))

# BLOCK 6
cells.append(new_markdown_cell("""---
### BLOCK 6: HUẤN LUYỆN K-MEANS & SO SÁNH CÁC GIÁ TRỊ K

Huấn luyện trên toàn bộ user. So sánh K=2..8 bằng Inertia và Silhouette ước lượng tối đa 2.000 user, có đại diện từng cụm. K=4 là lựa chọn nghiên cứu để tạo bốn hồ sơ; bảng hiển thị K có điểm cao nhất để đánh giá sự đánh đổi. Chưa kiểm chứng độ ổn định cụm qua nhiều seed/thời kỳ.
"""))

cells.append(new_code_cell("""if 'X_scaled' not in globals():
    raise RuntimeError('Chưa có kết quả BLOCK 5. Chạy block đó thành công trước khi tiếp tục.')
for name in ('MODEL_JOB_ID', 'PCA_JOB_ID', 'SEGMENTATION_JOB_ID',
             'df_segmented', 'summary_table'):
    globals().pop(name, None)
if len(X_scaled) != len(df_clean) or not np.isfinite(X_scaled).all():
    raise ValueError("Ma trận huấn luyện không hợp lệ. Chạy lại BLOCK 5.")
n_distinct = len(np.unique(X_scaled, axis=0))
if len(X_scaled) < 5 or n_distinct < 4:
    raise ValueError("Cần ít nhất 5 user và 4 vector khác nhau để tạo bốn chân dung.")
k_range = range(2, min(8, n_distinct, len(X_scaled) - 1) + 1)
SILHOUETTE_SAMPLE_SIZE = min(2000, len(X_scaled))


def estimate_silhouette(matrix, labels, max_samples=2000, seed=42):
    \"\"\"Ước lượng trên user thật, bảo đảm mọi cụm có đại diện trong tập đánh giá.\"\"\"
    labels = np.asarray(labels)
    unique_labels = np.unique(labels)
    if not 2 <= len(unique_labels) < len(matrix):
        raise ValueError("Silhouette cần từ 2 đến n_users - 1 cụm.")
    reserved = []
    for label in unique_labels:
        indices = pd.Series(np.flatnonzero(labels == label))
        reserved.extend(indices.sample(n=min(2, len(indices)), random_state=seed).tolist())
    budget = min(len(matrix), max(max_samples, len(reserved)))
    remaining = pd.Series(np.setdiff1d(np.arange(len(matrix)), reserved))
    extra = remaining.sample(n=budget - len(reserved), random_state=seed).tolist()
    selected = np.asarray(reserved + extra, dtype=int)
    return silhouette_score(matrix[selected], labels[selected])


inertias, silhouette_scores = [], []
kmeans_final = None
N_CLUSTERS = 4
print(f"K-Means dùng toàn bộ {len(X_scaled):,} user; Silhouette dùng tối đa {SILHOUETTE_SAMPLE_SIZE:,} user thật.")
print("Silhouette là ước lượng có đại diện từng cụm, không phải điểm trên toàn bộ dataset.")
for k in k_range:
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(X_scaled)
    if len(np.unique(labels)) != k:
        raise ValueError(f"K-Means chỉ tạo được {len(np.unique(labels))} cụm khi yêu cầu K={k}.")
    score = estimate_silhouette(X_scaled, labels, SILHOUETTE_SAMPLE_SIZE)
    inertias.append(float(model.inertia_))
    silhouette_scores.append(float(score))
    if k == N_CLUSTERS:
        kmeans_final = model
        final_labels = labels.copy()
        final_silhouette_score = float(score)
    print(f"K={k}: inertia={model.inertia_:,.2f}; silhouette ước lượng={score:.4f}")

cluster_evaluation = pd.DataFrame({'k': list(k_range), 'inertia': inertias,
                                   'silhouette_estimate': silhouette_scores})
best_k_by_silhouette = int(cluster_evaluation.loc[cluster_evaluation['silhouette_estimate'].idxmax(), 'k'])
print(f'K có Silhouette ước lượng cao nhất trong các giá trị đã thử: {best_k_by_silhouette}.')
display(cluster_evaluation)
cluster_sizes = pd.Series(final_labels).value_counts().sort_index()
print('Quy mô từng cụm K=4:', cluster_sizes.to_dict())
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.plot(list(k_range), inertias, 'o-')
ax1.set(title='Inertia theo K', xlabel='K', ylabel='Inertia')
ax2.plot(list(k_range), silhouette_scores, 's-')
ax2.set(title='Silhouette ước lượng theo K', xlabel='K', ylabel='Silhouette')
for ax in (ax1, ax2):
    ax.axvline(N_CLUSTERS, color='#DC2626', linestyle='--', label='K=4: lựa chọn nghiên cứu')
    ax.legend()
plt.tight_layout()
plt.show()
# Dùng lại mô hình K=4 đã fit; không huấn luyện lần nữa.
df_clean['cluster'] = final_labels
MODEL_JOB_ID = PREPROCESSING_JOB_ID
print(f"✓ K=4; Silhouette ước lượng={final_silhouette_score:.4f}. Không khẳng định K=4 tối ưu.")
"""))

# BLOCK 7
cells.append(new_markdown_cell("""---
### BLOCK 7: PCA BA THÀNH PHẦN & BIỂU ĐỒ PHÂN CỤM 2D

PCA học từ cùng ma trận chuẩn hóa; dùng ba thành phần để xuất dữ liệu, hai thành phần đầu để vẽ. Phương sai giải thích được tính khi chạy. Mỗi cụm vẽ tối đa 5.000 user; mức tách biệt trên hình 2D không thay thế đánh giá trong không gian chín đặc trưng.
"""))

cells.append(new_code_cell("""if 'MODEL_JOB_ID' not in globals():
    raise RuntimeError('Chưa có kết quả BLOCK 6. Chạy block đó thành công trước khi tiếp tục.')
globals().pop('PCA_JOB_ID', None)
if 'cluster' not in df_clean.columns:
    raise ValueError("Chạy BLOCK 6 trước khi vẽ PCA.")
# Giảm chiều trên toàn bộ user dùng để huấn luyện K-Means.
pca = PCA(n_components=3, random_state=42)
pca_transformed = pca.fit_transform(X_scaled)

df_clean['pca_1'] = pca_transformed[:, 0]
df_clean['pca_2'] = pca_transformed[:, 1]
df_clean['pca_3'] = pca_transformed[:, 2]

var_ratio = pca.explained_variance_ratio_
print(f"✓ Tỷ lệ phương sai giải thích: PCA1 = {var_ratio[0]*100:.2f}%, PCA2 = {var_ratio[1]*100:.2f}%, PCA3 = {var_ratio[2]*100:.2f}% (Tổng = {var_ratio.sum()*100:.2f}%)")

pca_loadings = pd.DataFrame(pca.components_.T, index=feature_cols,
                            columns=['PC1', 'PC2', 'PC3'])
pca_loadings.index.name = 'feature'
PCA_JOB_ID = MODEL_JOB_ID

# Chỉ giới hạn số điểm vẽ; toàn bộ user vẫn có tọa độ PCA và được xuất báo cáo.
plot_data = pd.concat([group.sample(n=min(5000, len(group)), random_state=42)
                       for _, group in df_clean.groupby('cluster')])
print(f"Biểu đồ hiển thị {len(plot_data):,}/{len(df_clean):,} user thật, tối đa 5.000 mỗi cụm.")
# Vẽ biểu đồ Scatter Plot 2D
plt.figure(figsize=(10, 6))
palette_colors = ['#DC2626', '#3B82F6', '#10B981', '#F59E0B']
sns.scatterplot(
    data=plot_data,
    x='pca_1',
    y='pca_2',
    hue='cluster',
    palette=palette_colors,
    alpha=0.7,
    s=45
)
plt.title(f"Không Gian Phân Cụm Khách Hàng PCA 2D (Tổng phương sai giải thích: {(var_ratio[0]+var_ratio[1])*100:.1f}%)", fontsize=13, fontweight='bold')
plt.xlabel(f"PC1 ({var_ratio[0]*100:.1f}% phương sai)")
plt.ylabel(f"PC2 ({var_ratio[1]*100:.1f}% phương sai)")
plt.legend(title="Cluster ID", loc="best")
plt.tight_layout()
plt.show()
"""))

# BLOCK 8
cells.append(new_markdown_cell("""---
### BLOCK 8: ĐỊNH DANH CHÂN DUNG KHÁCH HÀNG ĐỘNG (CUSTOMER PERSONAS)

Nhãn dựa trên trung bình tương đối giữa bốn cụm và được gán theo thứ tự doanh thu → recency → tỷ lệ thêm giỏ/xem → cụm còn lại. Không suy ra trung thành, VIP hoặc nguy cơ rời bỏ từ các quy tắc này. Tổng hợp trên thang đo gốc, không dùng số đã log/chuẩn hóa.
"""))

cells.append(new_code_cell("""if 'PCA_JOB_ID' not in globals():
    raise RuntimeError('Chưa có kết quả BLOCK 7. Chạy block đó thành công trước khi tiếp tục.')
globals().pop('SEGMENTATION_JOB_ID', None)
# 1. Tính toán số user và trung bình của từng cụm.
cluster_stats = df_clean.groupby('cluster')[feature_cols].agg(['mean', 'count']).reset_index()

# 2. Thuật toán phân bổ Persona động
def assign_persona_dynamically(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    grouped = df_out.groupby('cluster').agg({
        'monetary_usd': 'mean',
        'recency_days': 'mean',
        'frequency_sessions': 'mean',
        'cart_to_view_ratio': 'mean'
    })
    
    if len(grouped) != 4:
        raise ValueError("Định danh bốn chân dung cần đúng 4 cụm. Chạy lại BLOCK 6.")
    if grouped['monetary_usd'].max() <= 0:
        df_out['persona'] = df_out['cluster'].map(lambda label: f"Cluster {label} (chưa có doanh thu)")
        return df_out
    # Nhãn mô tả theo số liệu; không suy ra lòng trung thành hoặc rủi ro rời bỏ.
    vip_cluster = grouped['monetary_usd'].idxmax()
    # Inactive: Recency lớn nhất (hoặc tần suất thấp nhất trong số các cluster còn lại)
    rem1 = grouped.drop(index=vip_cluster)
    inactive_cluster = rem1['recency_days'].idxmax()
    # Nhóm thiên về thêm giỏ: tỷ lệ thêm giỏ/xem cao nhất trong các cụm còn lại
    rem2 = rem1.drop(index=inactive_cluster)
    cart_cluster = rem2['cart_to_view_ratio'].idxmax()
    # Potential Loyalist: Cluster còn lại
    potential_cluster = [c for c in grouped.index if c not in [vip_cluster, inactive_cluster, cart_cluster]][0]
    
    persona_map = {
        vip_cluster: "Doanh thu trung bình cao",
        potential_cluster: "Nhóm hành vi còn lại",
        cart_cluster: "Tỷ lệ thêm giỏ/xem cao",
        inactive_cluster: "Hoạt động gần nhất cách xa"
    }
    
    df_out['persona'] = df_out['cluster'].map(persona_map)
    return df_out

df_segmented = assign_persona_dynamically(df_clean)

# Bảng tổng hợp đặc trưng theo từng Persona
summary_table = df_segmented.groupby('persona').agg({
    'user_pseudo_id': 'count',
    'recency_days': 'mean',
    'frequency_sessions': 'mean',
    'monetary_usd': 'mean',
    'cart_to_view_ratio': 'mean',
    'view_item_count': 'mean',
    'total_engagement_time_sec': 'mean'
}).reset_index()

summary_table.columns = ['Persona Chân Dung', 'Số Khách Hàng', 'R (Ngày)', 'F (Phiên)', 'M ($ USD)', 'Tỷ Lệ Thêm Giỏ/Xem', 'Lượt Xem SP', 'Thời Gian (s)']
summary_table['Tỷ Trọng (%)'] = (summary_table['Số Khách Hàng'] / len(df_segmented) * 100).round(2)

print("="*90)
print("📊 BẢNG TỔNG HỢP 4 NHÓM CHÂN DUNG KHÁCH HÀNG (CUSTOMER PERSONAS)")
print("="*90)
display(summary_table[['Persona Chân Dung', 'Số Khách Hàng', 'Tỷ Trọng (%)', 'R (Ngày)', 'F (Phiên)', 'M ($ USD)', 'Tỷ Lệ Thêm Giỏ/Xem']])

SEGMENTATION_JOB_ID = MODEL_JOB_ID
print("Tên chân dung là diễn giải dựa trên trung bình cụm; tỷ lệ thêm giỏ/xem không chứng minh bỏ giỏ.")
"""))

# BLOCK 9
cells.append(new_markdown_cell("""---
### BLOCK 9: KHAI PHÁ LUẬT KẾT HỢP GIỎ HÀNG (MARKET BASKET APRIORI)

Apriori giới hạn ở tập hai sản phẩm: lọc sản phẩm đơn đạt support, xét mỗi cặp một lần, rồi tạo cả hai hướng A→B và B→A. Không khai phá tập từ ba sản phẩm trở lên. Support có điều kiện trên đơn có ≥2 tên sản phẩm hợp lệ; kết quả không đại diện toàn bộ đơn. Khóa đơn gồm user và transaction ID; fallback theo event khi ID bị thiếu. Gộp theo tên sản phẩm nên các biến thể trùng tên được xem là một sản phẩm. Lọc ngưỡng bằng số chưa làm tròn.
"""))

cells.append(new_code_cell("""sql_basket = \"\"\"
WITH raw_purchases AS (
    SELECT event_timestamp, user_pseudo_id,
        COALESCE(
            NULLIF(NULLIF(NULLIF(ecommerce.transaction_id, ''), '(not set)'), '<Other>'),
            (SELECT NULLIF(NULLIF(NULLIF(value.string_value, ''), '(not set)'), '<Other>')
             FROM UNNEST(event_params) WHERE key = 'transaction_id' LIMIT 1),
            CONCAT('event:', COALESCE(user_pseudo_id, '(unknown)'), ':', CAST(event_timestamp AS STRING))
        ) AS transaction_id,
        items
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE event_name = 'purchase'
      AND _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
), purchases AS (
    -- Transaction ID chỉ có ý nghĩa trong phạm vi một user. JSON tránh va chạm dấu phân cách.
    SELECT event_timestamp, user_pseudo_id,
        TO_JSON_STRING(STRUCT(user_pseudo_id AS user_id, transaction_id AS order_id)) AS transaction_id,
        items
    FROM raw_purchases
), purchased_items AS (
    SELECT p.transaction_id, MIN(p.event_timestamp) AS event_timestamp,
        MIN(p.user_pseudo_id) AS user_pseudo_id, MIN(item.item_id) AS item_id,
        TRIM(item.item_name) AS item_name, MAX(item.price_in_usd) AS price_in_usd
    FROM purchases p, UNNEST(p.items) AS item
    WHERE item.item_name IS NOT NULL
      AND LOWER(TRIM(item.item_name)) NOT IN ('', '(not set)', '<other>', '(data deleted)')
    GROUP BY p.transaction_id, TRIM(item.item_name)
), valid_transactions AS (
    SELECT transaction_id FROM purchased_items
    GROUP BY transaction_id HAVING COUNT(DISTINCT item_name) >= 2
)
SELECT i.* FROM purchased_items i JOIN valid_transactions v USING (transaction_id)
ORDER BY transaction_id, item_name;
\"\"\"

globals().pop('df_basket_raw', None)
globals().pop('df_rules', None)
df_basket_raw = query_bigquery(sql_basket, "market_basket", allow_empty=True)
df_basket_clean = df_basket_raw.copy()
if df_basket_clean[['transaction_id', 'item_name']].isna().any().any():
    raise ValueError('Giỏ hàng thiếu mã giao dịch hoặc tên sản phẩm.')
if df_basket_clean[['transaction_id', 'item_name']].astype(str).apply(lambda col: col.str.strip().eq('')).any().any():
    raise ValueError('Giỏ hàng có mã giao dịch hoặc tên sản phẩm rỗng.')
df_basket_clean = df_basket_clean.drop_duplicates(['transaction_id', 'item_name']).copy()
df_basket_clean['tx_id'] = df_basket_clean['transaction_id']
if df_basket_clean['tx_id'].isna().any():
    raise ValueError("Có giao dịch thiếu mã định danh.")
tx_counts = df_basket_clean.groupby('tx_id')['item_name'].nunique()
if (tx_counts < 2).any():
    raise ValueError("SQL trả về đơn có ít hơn hai sản phẩm khác nhau.")

# Chỉ tạo ma trận cho sản phẩm đạt min support; vẫn giữ toàn bộ đơn làm mẫu số.
# Không cần tạo ma trận đặc cho hàng nghìn sản phẩm hiếm.
MIN_SUPPORT, MIN_CONFIDENCE, MIN_LIFT = 0.04, 0.25, 1.0
num_tx = len(tx_counts)
item_supports = (df_basket_clean.groupby('item_name')['tx_id'].nunique() / num_tx
                 if num_tx else pd.Series(dtype='float64'))
top_items = item_supports[item_supports >= MIN_SUPPORT].index.tolist()
frequent_rows = df_basket_clean.loc[df_basket_clean['item_name'].isin(top_items)]
basket_matrix = pd.crosstab(frequent_rows['tx_id'], frequent_rows['item_name'])
basket_matrix = basket_matrix.reindex(index=tx_counts.index, columns=top_items, fill_value=0).gt(0)
print(f"✓ {num_tx:,} đơn đa sản phẩm; {len(top_items)} sản phẩm đạt support >= {MIN_SUPPORT:.0%}.")

rule_columns = ['Sản Phẩm A (Đã Mua)', 'Sản Phẩm B (Gợi Ý Mua Kèm)',
                'Support (%)', 'Confidence (%)', 'Lift (Độ Nâng)']
rules_list = []
from itertools import combinations
for antecedent, consequent in combinations(top_items, 2):
    sup_a, sup_b = item_supports[antecedent], item_supports[consequent]
    sup_ab = float((basket_matrix[antecedent] & basket_matrix[consequent]).mean())
    if sup_ab < MIN_SUPPORT:
        continue
    lift = sup_ab / (sup_a * sup_b)
    if lift <= MIN_LIFT:
        continue
    for left, right, left_support in ((antecedent, consequent, sup_a),
                                      (consequent, antecedent, sup_b)):
        confidence = sup_ab / left_support
        if confidence >= MIN_CONFIDENCE:
            rules_list.append(dict(zip(rule_columns, [left, right,
                sup_ab * 100, confidence * 100, float(lift)])))
df_rules = pd.DataFrame(rules_list, columns=rule_columns).sort_values(
    by=['Lift (Độ Nâng)', 'Confidence (%)', rule_columns[0], rule_columns[1]],
    ascending=[False, False, True, True]).reset_index(drop=True)
if df_rules.empty:
    print("Không có luật đáp ứng các ngưỡng trên dữ liệu thật. Không tạo luật minh họa.")
else:
    display(df_rules.head(10).style.format({'Support (%)': '{:.2f}', 'Confidence (%)': '{:.2f}', 'Lift (Độ Nâng)': '{:.3f}'}))
RULES_JOB_ID = df_basket_raw.attrs.get('bigquery_job_id')
print("Luật thể hiện mua cùng đơn, không xác định thứ tự mua. Support tính trên các đơn đa sản phẩm.")
"""))

# BLOCK 10
cells.append(new_markdown_cell("""---
### BLOCK 10: DIỄN GIẢI KẾT QUẢ & ĐỀ XUẤT KINH DOANH

Các nhận xét dưới đây được tạo bằng quy tắc Python từ số liệu vừa truy vấn,
không phải phản hồi từ API Gemini. Có thể dùng `prompt_context` làm đầu vào
cho một hệ thống AI sau này; notebook không cần API key Gemini để chạy.
"""))

cells.append(new_code_cell("""# Ngữ cảnh và nhận xét chỉ dùng các kết quả đang có trong bộ nhớ.
required_context_queries = {'eda_overview', 'funnel_analysis', 'rfm_features', 'market_basket'}
if required_context_queries - QUERY_MANIFEST.keys():
    raise RuntimeError('Thiếu kết quả truy vấn hiện tại để diễn giải. Chạy lại BLOCK 2–9.')
if (globals().get('SEGMENTATION_JOB_ID') != QUERY_MANIFEST['rfm_features']['job_id']
        or globals().get('RULES_JOB_ID') != QUERY_MANIFEST['market_basket']['job_id']):
    raise RuntimeError('Kết quả phân cụm/luật không khớp truy vấn hiện tại. Chạy lại BLOCK 5–9.')
prompt_context = (
    "Nguồn: " + SOURCE_TABLE + "; thời gian: 2020-11-01 đến 2021-01-31.\\n"
    + "Phễu user theo thiết bị:\\n" + df_funnel.to_string(index=False)
    + "\\nĐặc điểm các nhóm khách hàng:\\n" + summary_table.to_string(index=False)
    + "\\nLuật mua kèm đạt ngưỡng:\\n" + df_rules.head(10).to_string(index=False)
)
eligible_devices = df_funnel.loc[
    (df_funnel['device_category'] != 'all') & df_funnel['cart_abandonment_rate_pct'].notna()
]
if not eligible_devices.empty:
    max_abandonment = eligible_devices['cart_abandonment_rate_pct'].max()
    worst_rows = eligible_devices.loc[
        eligible_devices['cart_abandonment_rate_pct'] == max_abandonment]
    worst = worst_rows.sort_values('device_category').iloc[0]
    if len(worst_rows) > 1:
        print("Các thiết bị đồng hạng về tỷ lệ chưa hoàn tất chuỗi:", ', '.join(worst_rows['device_category']))
    print(f"1. {worst['device_category']} có tỷ lệ user thêm giỏ chưa hoàn tất chuỗi cao nhất "
          f"({worst['cart_abandonment_rate_pct']:.2f}%). Ưu tiên kiểm tra luồng thanh toán trên thiết bị này.")
else:
    print("1. Chưa đủ user thêm giỏ để so sánh thiết bị.")
persona_revenue = df_segmented.groupby('persona')['monetary_usd'].sum()
if persona_revenue.sum() > 0:
    leading = persona_revenue.idxmax()
    share = percentage(persona_revenue[leading], persona_revenue.sum())
    print(f"2. Nhóm {leading} đóng góp {share:.2f}% doanh thu của user có mã định danh. "
          "Xem xét chương trình giữ chân phù hợp với hành vi nhóm.")
else:
    print("2. Không có doanh thu để xếp hạng đóng góp của các nhóm.")
if not df_rules.empty:
    top = df_rules.iloc[0]
    print(f"3. Cặp {top[rule_columns[0]]} → {top[rule_columns[1]]}: "
          f"lift={top['Lift (Độ Nâng)']:.3f}, confidence={top['Confidence (%)']:.2f}%. "
          "Có thể thử gợi ý mua kèm và đo tác động bằng thử nghiệm.")
else:
    print("3. Không có cặp sản phẩm đạt ngưỡng để đề xuất combo.")
print('Các đề xuất là giả thuyết để kiểm thử. Dataset đã làm mờ, cửa sổ 3 tháng và phễu nhiều phiên hạn chế suy luận kinh doanh.')
"""))

# BLOCK 11
cells.append(new_markdown_cell("""---
### BLOCK 11: TỔNG KẾT & XUẤT DỮ LIỆU BÁO CÁO

Chỉ xuất khi tất cả query, phân cụm, PCA và luật thuộc đúng lần chạy. Đối chiếu SHA-256 dữ liệu/SQL và metadata trước khi đóng ZIP. Gói gồm dữ liệu nguồn, kết quả, kiểm tra tiền xử lý, tương quan, đánh giá K và cấu hình tái lập.
"""))

cells.append(new_code_cell("""required_queries = {'eda_overview', 'funnel_analysis', 'rfm_features', 'market_basket'}
missing = required_queries - QUERY_MANIFEST.keys()
if missing:
    raise RuntimeError(f"Chưa có kết quả BigQuery cho: {sorted(missing)}. Chạy lại các block tương ứng.")
current_rfm_job = QUERY_MANIFEST['rfm_features']['job_id']
if (globals().get('SEGMENTATION_JOB_ID') != current_rfm_job
        or globals().get('PCA_JOB_ID') != current_rfm_job):
    raise RuntimeError("Phân cụm/PCA chưa khớp truy vấn RFM hiện tại. Chạy lại BLOCK 5–8.")
if globals().get('RULES_JOB_ID') != QUERY_MANIFEST['market_basket']['job_id']:
    raise RuntimeError("Luật mua kèm chưa khớp truy vấn hiện tại. Chạy lại BLOCK 9.")

# Xác minh tất cả file truy vấn hiện tại trước khi xuất báo cáo.
query_files = []
for name in sorted(required_queries):
    for suffix in ('.csv', '.parquet', '.sql', '.metadata.json'):
        path = LOCAL_DATA_DIR / (name + suffix)
        if not path.exists():
            raise RuntimeError(f"Thiếu file {path}. Chạy lại truy vấn tương ứng.")
        if suffix != '.metadata.json':
            expected_hash = QUERY_MANIFEST[name].get('file_sha256', {}).get(suffix)
            if not expected_hash or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                raise RuntimeError(f'File {path.name} đã thay đổi so với kết quả truy vấn. Chạy lại truy vấn.')
        query_files.append(path)
    saved_sql = (LOCAL_DATA_DIR / f'{name}.sql').read_text(encoding='utf-8')
    if hashlib.sha256(saved_sql.encode('utf-8')).hexdigest() != QUERY_MANIFEST[name]['query_sha256']:
        raise RuntimeError(f"SQL đã lưu của {name} không khớp truy vấn hiện tại.")
    saved_metadata = json.loads((LOCAL_DATA_DIR / f'{name}.metadata.json').read_text(encoding='utf-8'))
    if saved_metadata != QUERY_MANIFEST[name]:
        raise RuntimeError(f"Metadata đã lưu của {name} không khớp phiên chạy hiện tại.")

output_segmented_path = LOCAL_DATA_DIR / 'final_customer_segmented_results.csv'
output_rules_path = LOCAL_DATA_DIR / 'final_market_basket_rules.csv'
df_segmented.to_csv(output_segmented_path, index=False)
df_rules.to_csv(output_rules_path, index=False)
df_funnel.to_csv(LOCAL_DATA_DIR / 'funnel_metrics.csv', index=False)
summary_table.to_csv(LOCAL_DATA_DIR / 'persona_summary.csv', index=False)
cluster_evaluation.to_csv(LOCAL_DATA_DIR / 'kmeans_evaluation.csv', index=False)
pca_loadings.to_csv(LOCAL_DATA_DIR / 'pca_loadings.csv')
preprocessing_audit.to_csv(LOCAL_DATA_DIR / 'preprocessing_audit.csv', index=False)
feature_correlations.to_csv(LOCAL_DATA_DIR / 'feature_correlations.csv')
manifest_path = LOCAL_DATA_DIR / 'query_manifest.json'
manifest_path.write_text(json.dumps(QUERY_MANIFEST, ensure_ascii=False, indent=2), encoding='utf-8')
analysis_metadata = {
    'rfm_job_id': current_rfm_job,
    'market_basket_job_id': RULES_JOB_ID,
    'feature_columns': feature_cols,
    'n_training_users': len(df_segmented),
    'n_clusters': N_CLUSTERS,
    'k_selection': 'K=4 chosen for four descriptive profiles; not asserted optimal',
    'best_k_by_estimated_silhouette': best_k_by_silhouette,
    'recency_definition': 'days since last observed event at 2021-01-31',
    'missing_feature_values_filled_zero': missing_feature_counts.astype(int).to_dict(),
    'persona_interpretation': 'relative descriptive labels, not validated loyalty/churn classes',
    'association_algorithm': 'Apriori restricted to two-item sets; both rule directions',
    'association_population': 'orders with at least two distinct valid product names',
    'transaction_identity': 'JSON of user_pseudo_id and transaction_id; event fallback when absent',
    'python_version': sys.version,
    'library_versions': {'numpy': np.__version__, 'pandas': pd.__version__,
                         'scikit_learn': __import__('sklearn').__version__},
    'random_state': 42,
    'silhouette_estimate': final_silhouette_score,
    'silhouette_max_users': SILHOUETTE_SAMPLE_SIZE,
    'clipping_caps': clipping_caps,
    'sparse_features_preserved': sparse_features_preserved,
    'pca_explained_variance_ratio': var_ratio.tolist(),
    'basket_orders': num_tx,
    'association_thresholds': {'support': MIN_SUPPORT, 'confidence': MIN_CONFIDENCE, 'lift': MIN_LIFT},
}
(LOCAL_DATA_DIR / 'analysis_metadata.json').write_text(
    json.dumps(analysis_metadata, ensure_ascii=False, indent=2), encoding='utf-8')

from zipfile import ZipFile, ZIP_DEFLATED
report_names = ['final_customer_segmented_results.csv', 'final_market_basket_rules.csv',
                'funnel_metrics.csv', 'persona_summary.csv', 'kmeans_evaluation.csv',
                'pca_loadings.csv', 'query_manifest.json', 'analysis_metadata.json',
                'preprocessing_audit.csv', 'feature_correlations.csv']
archive_path = LOCAL_DATA_DIR.parent / 'ga4_bigquery_exports.zip'
with ZipFile(archive_path, 'w', compression=ZIP_DEFLATED) as archive:
    for path in query_files + [LOCAL_DATA_DIR / name for name in report_names]:
        archive.write(path, arcname=path.name)
print(f"✓ Đã xuất kết quả của {len(df_segmented):,} user; job IDs và tham số nằm trong metadata.")
print(f"File tải về: {archive_path.resolve()}")
print("Trên Colab, chạy: from google.colab import files; files.download(str(archive_path))")
"""))

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.12'},
    'colab': {'provenance': []},
}
output_notebook_path = "DoAn-BigData-GA4-SourceCode-Final.ipynb"
with open(output_notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"✓ Master Notebook generated successfully: {output_notebook_path}")
