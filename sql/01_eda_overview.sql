-- ======================================================================================
-- ĐỒ ÁN BIG DATA: PHÂN TÍCH HÀNH VI KHÁCH HÀNG TRÊN GA4 E-COMMERCE DATASET
-- File: sql/01_eda_overview.sql
-- Mục đích: Khám phá Dữ liệu Tổng quan (EDA) - Thống kê KPI, Kênh tiếp thị, Thiết bị, Địa lý
-- Dataset: `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- PHẦN 1: THỐNG KÊ TỔNG QUAN HỆ THỐNG (OVERALL EXECUTIVE KPI METRICS)
-- --------------------------------------------------------------------------------------
WITH base_events AS (
    SELECT
        PARSE_DATE('%Y%m%d', event_date) AS event_date,
        user_pseudo_id,
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
        event_name,
        event_value_in_usd,
        traffic_source.medium AS traffic_medium,
        traffic_source.source AS traffic_source,
        device.category AS device_category,
        device.operating_system AS device_os,
        geo.country AS country
    FROM
        `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
)

-- Thống kê theo từng Kênh Tiếp thị (Traffic Acquisition Mediums)
SELECT
    COALESCE(traffic_medium, '(not set)') AS traffic_medium,
    COUNT(DISTINCT user_pseudo_id) AS total_users,
    COUNT(DISTINCT CONCAT(user_pseudo_id, CAST(ga_session_id AS STRING))) AS total_sessions,
    COUNTIF(event_name = 'page_view') AS total_pageviews,
    COUNTIF(event_name = 'purchase') AS total_transactions,
    ROUND(SUM(IF(event_name = 'purchase', COALESCE(event_value_in_usd, 0), 0)), 2) AS total_revenue,
    ROUND(
        SAFE_DIVIDE(
            COUNTIF(event_name = 'purchase'),
            COUNT(DISTINCT CONCAT(user_pseudo_id, CAST(ga_session_id AS STRING)))
        ) * 100, 
        2
    ) AS session_conversion_rate_pct,
    ROUND(
        SAFE_DIVIDE(
            SUM(IF(event_name = 'purchase', COALESCE(event_value_in_usd, 0), 0)),
            NULLIF(COUNTIF(event_name = 'purchase'), 0)
        ), 
        2
    ) AS average_order_value_usd
FROM
    base_events
GROUP BY
    traffic_medium
ORDER BY
    total_revenue DESC, total_sessions DESC;
