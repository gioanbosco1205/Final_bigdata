
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
