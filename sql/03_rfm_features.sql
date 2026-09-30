-- ======================================================================================
-- ĐỒ ÁN BIG DATA: PHÂN TÍCH HÀNH VI KHÁCH HÀNG TRÊN GA4 E-COMMERCE DATASET
-- File: sql/03_rfm_features.sql
-- Mục đích: Trích xuất Đặc trưng Cấp độ User (RFM + 6 Chỉ số Hành vi tương tác)
-- Dataset: `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- NGUYÊN TẮC THIẾT KẾ ĐẶC TRƯNG (FEATURE ENGINEERING RULES):
-- 1. Tính toán chuẩn xác ở cấp độ `user_pseudo_id` (1 dòng duy nhất cho mỗi khách hàng).
-- 2. Recency (R): Số ngày tính từ lần tương tác gần nhất của user đến ngày kết thúc dữ liệu.
-- 3. Frequency (F): Tổng số phiên truy cập duy nhất (COUNT DISTINCT ga_session_id).
-- 4. Monetary (M): Tổng giá trị chi tiêu thực tế ($) từ sự kiện 'purchase' (không đếm số event).
-- 5. 6 Chỉ số Hành vi: Tính toán trực tiếp bằng Conditional Aggregation, không dùng JOIN thừa 
--    để tránh nguy cơ nhân bản dòng (Cartesian Fanout).
-- 6. Xử lý triệt để giá trị NULL bằng COALESCE, đảm bảo R >= 0, F >= 1, M >= 0.
-- --------------------------------------------------------------------------------------

WITH raw_events_parsed AS (
    -- Bước 1: Trích xuất các trường cơ bản và bóc tách tham số lồng nhau
    SELECT
        user_pseudo_id,
        PARSE_DATE('%Y%m%d', event_date) AS event_date,
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'engagement_time_msec') AS engagement_time_msec,
        event_name,
        COALESCE(event_value_in_usd, 0) AS event_value_in_usd,
        device.category AS device_category,
        traffic_source.medium AS traffic_medium
    FROM
        `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
),

dataset_boundary AS (
    -- Bước 2: Xác định ngày cận trên lớn nhất của toàn bộ Dataset để làm mốc tính Recency
    SELECT MAX(event_date) AS max_snapshot_date
    FROM raw_events_parsed
),

user_aggregated_metrics AS (
    -- Bước 3: Tổng hợp toàn bộ chỉ số cấp User (RFM + 6 Đặc trưng hành vi)
    SELECT
        e.user_pseudo_id,
        
        -- Mốc thời gian tương tác gần nhất và xa nhất
        MAX(e.event_date) AS latest_event_date,
        MIN(e.event_date) AS first_event_date,
        
        -- Frequency (F): Tổng số Session phân biệt của user
        COUNT(DISTINCT e.ga_session_id) AS total_sessions,
        
        -- Monetary (M): Tổng số tiền mua sắm thực tế ($ USD) từ các sự kiện purchase
        ROUND(SUM(IF(e.event_name = 'purchase', e.event_value_in_usd, 0)), 2) AS monetary_value,
        
        -- Purchase Count: Tổng số đơn hàng mua thành công
        COUNTIF(e.event_name = 'purchase') AS purchase_count,
        
        -- 6 CHỈ SỐ HÀNH VI TƯƠNG TÁC (BEHAVIORAL METRICS):
        -- Chỉ số 1: Tổng thời gian tương tác chủ động (tính bằng giây)
        ROUND(COALESCE(SUM(e.engagement_time_msec), 0) / 1000.0, 1) AS total_engagement_sec,
        
        -- Chỉ số 2: Tổng số lượt xem trang (pageviews)
        COUNTIF(e.event_name = 'page_view') AS total_pageviews,
        
        -- Chỉ số 3: Tổng số sản phẩm đã xem chi tiết (view_item)
        COUNTIF(e.event_name = 'view_item') AS items_viewed_count,
        
        -- Chỉ số 4: Tổng số sản phẩm đã thêm vào giỏ hàng (add_to_cart)
        COUNTIF(e.event_name = 'add_to_cart') AS items_added_to_cart_count,
        
        -- Chỉ số 5: Tổng số lượt tiến hành thanh toán (begin_checkout)
        COUNTIF(e.event_name = 'begin_checkout') AS checkout_attempts_count,
        
        -- Thiết bị và Kênh tiếp thị chính (Lấy giá trị xuất hiện phổ biến)
        APPROX_TOP_COUNT(e.device_category, 1)[OFFSET(0)].value AS primary_device,
        APPROX_TOP_COUNT(COALESCE(e.traffic_medium, 'unknown'), 1)[OFFSET(0)].value AS primary_channel
    FROM
        raw_events_parsed e
    WHERE
        e.user_pseudo_id IS NOT NULL
    GROUP BY
        e.user_pseudo_id
)

-- Bước 4: Hoàn thiện bảng RFM + Behavioral Features cuối cùng sẵn sàng nạp vào Machine Learning
SELECT
    u.user_pseudo_id,
    
    -- Recency (R): Số ngày kể từ lần truy cập cuối cùng đến ngày chốt dataset
    DATE_DIFF(b.max_snapshot_date, u.latest_event_date, DAY) AS recency_days,
    
    -- Frequency (F)
    COALESCE(u.total_sessions, 1) AS total_sessions,
    
    -- Monetary (M)
    COALESCE(u.monetary_value, 0.0) AS monetary_value,
    
    -- Các chỉ số hành vi đã chuẩn hóa & tỷ lệ giỏ hàng
    COALESCE(u.total_engagement_sec, 0.0) AS total_engagement_sec,
    COALESCE(u.total_pageviews, 0) AS total_pageviews,
    COALESCE(u.items_viewed_count, 0) AS items_viewed_count,
    COALESCE(u.items_added_to_cart_count, 0) AS items_added_to_cart_count,
    COALESCE(u.checkout_attempts_count, 0) AS checkout_attempts_count,
    COALESCE(u.purchase_count, 0) AS purchase_count,
    
    -- Chỉ số 6: Tỷ lệ thêm vào giỏ / xem sản phẩm (Cart-to-View Ratio)
    ROUND(
        COALESCE(
            SAFE_DIVIDE(u.items_added_to_cart_count, u.items_viewed_count), 
            0.0
        ), 
        3
    ) AS cart_to_view_ratio,
    
    u.primary_device,
    u.primary_channel
FROM
    user_aggregated_metrics u
CROSS JOIN
    dataset_boundary b
ORDER BY
    monetary_value DESC, total_sessions DESC;
