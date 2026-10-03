
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
