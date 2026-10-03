
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
