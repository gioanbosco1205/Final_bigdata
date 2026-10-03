"""
Script to create extract_real_data_from_bigquery_colab.ipynb
"""

import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
cells = []

cells.append(new_markdown_cell("""# 🚀 TRÍCH XUẤT 100% DỮ LIỆU THẬT TỪ GOOGLE CLOUD BIGQUERY (GA4 E-COMMERCE)

Notebook này dùng để kết nối trực tiếp vào kho dữ liệu công khai của Google:
`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
và trích xuất 4 tập dữ liệu chuẩn của đồ án vào thư mục `data/`.

---
### 📋 HƯỚNG DẪN 1-CLICK:
1. Bấm **Runtime -> Run all** (hoặc chạy từng cell từ trên xuống).
2. Khi hiện thông báo đăng nhập, chọn tài khoản Google của bạn để cấp quyền truy vấn BigQuery (miễn phí).
3. Sau khi chạy xong, 4 file CSV thật sẽ được lưu vào thư mục `data/`.
"""))

cells.append(new_code_cell("""# 1. Cài đặt thư viện BigQuery
!pip install -q google-cloud-bigquery db-dtypes pyarrow

# 2. Xác thực tài khoản Google trên Colab
from google.colab import auth
import google.auth
from google.cloud import bigquery
import pandas as pd
import os
from pathlib import Path

print("👉 Mở cửa sổ xác thực tài khoản Google...")
auth.authenticate_user()

credentials, project = google.auth.default()
client = bigquery.Client(project=project, credentials=credentials)
print(f"✓ Kết nối BigQuery thành công! (GCP Project: {client.project})")
"""))

code_queries = '''# 3. Tạo thư mục lưu trữ
LOCAL_DATA_DIR = Path("data")
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = LOCAL_DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 4. Định nghĩa 4 câu truy vấn SQL chuẩn đồ án
QUERIES = {
    "eda_overview": """
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
    """,
    
    "funnel_analysis": """
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
        ROUND(SAFE_DIVIDE(COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL)), COUNT(DISTINCT IF(step_1_view_item = 1, user_pseudo_id, NULL))) * 100, 2) AS step1_to_step2_cr_pct,
        ROUND(SAFE_DIVIDE(COUNT(DISTINCT IF(step_3_begin_checkout = 1, user_pseudo_id, NULL)), COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL))) * 100, 2) AS step2_to_step3_cr_pct,
        ROUND(SAFE_DIVIDE(COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)), COUNT(DISTINCT IF(step_3_begin_checkout = 1, user_pseudo_id, NULL))) * 100, 2) AS step3_to_step4_cr_pct,
        ROUND(SAFE_DIVIDE(COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL)) - COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)), COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL))) * 100, 2) AS cart_abandonment_rate_pct
    FROM user_funnel
    GROUP BY device_category
    ORDER BY step_1_view_item_users DESC;
    """,
    
    "rfm_features": """
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
    WHERE total_sessions > 0
    LIMIT 5000;
    """,
    
    "market_basket": """
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
    """
}

# 5. Thực thi và lưu kết quả
for name, sql in QUERIES.items():
    print(f"🚀 Đang truy vấn [{name}] từ BigQuery Cloud...")
    df = client.query(sql).to_dataframe()
    csv_p = LOCAL_DATA_DIR / f"{name}.csv"
    parquet_p = CACHE_DIR / f"{name}.parquet"
    df.to_csv(csv_p, index=False)
    df.to_parquet(parquet_p, index=False)
    print(f"✓ Hoàn thành [{name}]: {len(df):,} dòng -> {csv_p}")

print("\n🎉 TOÀN BỘ 4 TẬP DỮ LIỆU THẬT ĐÃ ĐƯỢC LƯU VÀO THƯ MỤC data/")
'''

cells.append(new_code_cell(code_queries))

nb.cells = cells
with open("extract_real_data_from_bigquery_colab.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("✓ Created extract_real_data_from_bigquery_colab.ipynb successfully.")
