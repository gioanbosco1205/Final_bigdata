
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
