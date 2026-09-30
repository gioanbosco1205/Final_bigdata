-- ======================================================================================
-- ĐỒ ÁN BIG DATA: PHÂN TÍCH HÀNH VI KHÁCH HÀNG TRÊN GA4 E-COMMERCE DATASET
-- File: sql/04_market_basket.sql
-- Mục đích: Trích xuất Dữ liệu Giỏ hàng Thực tế cho Khai phá Luật Kết hợp (Market Basket Analysis)
-- Dataset: `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- NGUYÊN TẮC THIẾT KẾ CHO MARKET BASKET ANALYSIS:
-- 1. CHỈ lọc các sự kiện mua hàng thành công (event_name = 'purchase') trước khi UNNEST(items).
-- 2. Bóc tách UNNEST(items) để lấy item_id, item_name, item_category, price.
-- 3. Trích xuất transaction_id từ event_params (hoặc fallback theo user + event_timestamp).
-- 4. Loại bỏ trùng lặp sản phẩm trong cùng 1 đơn hàng bằng DISTINCT transaction_id, item_name.
-- 5. CHỈ giữ lại các đơn hàng có từ 2 sản phẩm KHÁC NHAU trở lên (COUNT(DISTINCT item_name) >= 2)
--    để phục vụ thuật toán Khai phá Luật kết hợp (Association Rules / Apriori).
-- --------------------------------------------------------------------------------------

WITH purchase_events AS (
    -- Bước 1: CHỈ lấy các sự kiện mua hàng thành công và bóc tách transaction_id
    SELECT
        user_pseudo_id,
        event_timestamp,
        PARSE_DATE('%Y%m%d', event_date) AS purchase_date,
        COALESCE(
            (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'transaction_id'),
            CONCAT('TX_', user_pseudo_id, '_', CAST(event_timestamp AS STRING))
        ) AS transaction_id,
        items
    FROM
        `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE
        event_name = 'purchase'
        AND items IS NOT NULL
        AND ARRAY_LENGTH(items) > 0
),

flattened_purchased_items AS (
    -- Bước 2: Bóc tách mảng items lồng nhau cho từng đơn hàng mua thành công
    SELECT DISTINCT
        p.user_pseudo_id,
        p.purchase_date,
        p.transaction_id,
        COALESCE(item.item_id, '(not set)') AS item_id,
        TRIM(COALESCE(item.item_name, '(not set)')) AS item_name,
        COALESCE(item.item_category, 'General') AS item_category,
        COALESCE(item.price_in_usd, item.price, 0.0) AS price_usd
    FROM
        purchase_events p,
        UNNEST(p.items) AS item
    WHERE
        item.item_name IS NOT NULL
        AND TRIM(item.item_name) NOT IN ('(not set)', '')
),

multi_item_transactions AS (
    -- Bước 3: Lọc chỉ giữ lại các đơn hàng có từ 2 sản phẩm KHÁC NHAU trở lên
    SELECT
        transaction_id
    FROM
        flattened_purchased_items
    GROUP BY
        transaction_id
    HAVING COUNT(DISTINCT item_name) >= 2
)

-- Bước 4: Xuất bảng danh sách sản phẩm cùng giỏ hàng sạch, chuẩn bị nạp vào thuật toán Apriori
SELECT
    f.purchase_date,
    f.user_pseudo_id,
    f.transaction_id,
    f.item_id,
    f.item_name,
    f.item_category,
    f.price_usd
FROM
    flattened_purchased_items f
INNER JOIN
    multi_item_transactions m
ON
    f.transaction_id = m.transaction_id
ORDER BY
    f.transaction_id, f.item_name;
