-- ======================================================================================
-- ĐỒ ÁN BIG DATA: PHÂN TÍCH HÀNH VI KHÁCH HÀNG TRÊN GA4 E-COMMERCE DATASET
-- File: sql/02_funnel_analysis.sql
-- Mục đích: Phân tích Phễu Mua hàng 4 bước (Conversion Funnel Analysis) theo User và Thiết bị
-- Dataset: `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- NGUYÊN TẮC PHỄU (STRICT USER-LEVEL FUNNEL):
-- 1. Đếm DISTINCT USER (COUNT(DISTINCT user_pseudo_id)), không đếm số lượng event rời rạc.
-- 2. Đảm bảo đúng trình tự: view_item -> add_to_cart -> begin_checkout -> purchase.
-- 3. Một user chỉ được tính ở Bước N nếu đã hoàn thành tất cả các bước trước đó (1 -> N-1).
-- 4. Đảm bảo tính chất phễu chuẩn: Bước sau LUÔN LUÔN <= Bước trước.
-- --------------------------------------------------------------------------------------

WITH user_event_flags AS (
    -- Bước 1: Trích xuất các sự kiện thuộc phễu của từng User và Thiết bị chính
    SELECT
        user_pseudo_id,
        device.category AS device_category,
        MAX(IF(event_name = 'view_item', 1, 0)) AS has_view_item,
        MAX(IF(event_name = 'add_to_cart', 1, 0)) AS has_add_to_cart,
        MAX(IF(event_name = 'begin_checkout', 1, 0)) AS has_begin_checkout,
        MAX(IF(event_name = 'purchase', 1, 0)) AS has_purchase
    FROM
        `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE
        event_name IN ('view_item', 'add_to_cart', 'begin_checkout', 'purchase')
    GROUP BY
        user_pseudo_id,
        device_category
),

user_funnel_stages AS (
    -- Bước 2: Ràng buộc logic phễu tuần tự nghiêm ngặt (Strict Sequential Progression)
    SELECT
        user_pseudo_id,
        device_category,
        -- Bước 1: User có xem sản phẩm
        has_view_item AS step_1_view_item,
        
        -- Bước 2: User phải xem sản phẩm VÀ thêm vào giỏ hàng
        IF(has_view_item = 1 AND has_add_to_cart = 1, 1, 0) AS step_2_add_to_cart,
        
        -- Bước 3: User phải xem VÀ thêm giỏ VÀ bắt đầu thanh toán
        IF(has_view_item = 1 AND has_add_to_cart = 1 AND has_begin_checkout = 1, 1, 0) AS step_3_begin_checkout,
        
        -- Bước 4: User hoàn thành đầy đủ hành trình đến mua hàng thành công
        IF(has_view_item = 1 AND has_add_to_cart = 1 AND has_begin_checkout = 1 AND has_purchase = 1, 1, 0) AS step_4_purchase
    FROM
        user_event_flags
)

-- Bước 3: Tổng hợp phễu, tính toán Conversion Rate, Drop-off Rate và Cart Abandonment Rate
SELECT
    COALESCE(device_category, 'all') AS device_category,
    
    -- Số lượng Distinct Users ở từng bước của phễu (Đảm bảo Bước sau <= Bước trước)
    COUNT(DISTINCT IF(step_1_view_item = 1, user_pseudo_id, NULL)) AS step_1_view_item_users,
    COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL)) AS step_2_add_to_cart_users,
    COUNT(DISTINCT IF(step_3_begin_checkout = 1, user_pseudo_id, NULL)) AS step_3_begin_checkout_users,
    COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)) AS step_4_purchase_users,
    
    -- Tỷ lệ Chuyển đổi Tổng thể (Overall Conversion Rate: View -> Purchase)
    ROUND(
        SAFE_DIVIDE(
            COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)),
            COUNT(DISTINCT IF(step_1_view_item = 1, user_pseudo_id, NULL))
        ) * 100, 
        2
    ) AS overall_conversion_rate_pct,
    
    -- Tỷ lệ chuyển đổi từng bước (Step-by-Step Conversion Rates)
    ROUND(
        SAFE_DIVIDE(
            COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL)),
            COUNT(DISTINCT IF(step_1_view_item = 1, user_pseudo_id, NULL))
        ) * 100, 
        2
    ) AS step1_to_step2_cr_pct,
    
    ROUND(
        SAFE_DIVIDE(
            COUNT(DISTINCT IF(step_3_begin_checkout = 1, user_pseudo_id, NULL)),
            COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL))
        ) * 100, 
        2
    ) AS step2_to_step3_cr_pct,
    
    ROUND(
        SAFE_DIVIDE(
            COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)),
            COUNT(DISTINCT IF(step_3_begin_checkout = 1, user_pseudo_id, NULL))
        ) * 100, 
        2
    ) AS step3_to_step4_cr_pct,
    
    -- Tỷ lệ rơi rụng lớn nhất tại giỏ hàng (Cart Abandonment Rate - CAR)
    -- CAR = (Users thêm giỏ - Users hoàn tất mua) / Users thêm giỏ
    ROUND(
        SAFE_DIVIDE(
            COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL)) - COUNT(DISTINCT IF(step_4_purchase = 1, user_pseudo_id, NULL)),
            COUNT(DISTINCT IF(step_2_add_to_cart = 1, user_pseudo_id, NULL))
        ) * 100, 
        2
    ) AS cart_abandonment_rate_pct
FROM
    user_funnel_stages
GROUP BY
    device_category
ORDER BY
    step_1_view_item_users DESC;
