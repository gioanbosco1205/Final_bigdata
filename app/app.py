"""
Streamlit Web Application: Big Data Analytics & Customer Intelligence Platform
Powered by Google BigQuery SQL, Scikit-Learn K-Means, and Plotly.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# Set page config as very first Streamlit call
st.set_page_config(
    page_title="GA4 Big Data Customer Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root and app directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from src.bq_client import BigQueryService
from src.data_processor import CustomerDataProcessor
from src.clustering import CustomerClusterModel
from src.market_basket import MarketBasketAnalyzer

try:
    from app.utils_ui import (
        CUSTOM_CSS,
        render_header,
        render_kpi_card,
        create_funnel_chart,
        create_traffic_breakdown_chart,
        create_pca_3d_scatter,
        create_persona_radar_chart
    )
except (ImportError, ModuleNotFoundError):
    from utils_ui import (
        CUSTOM_CSS,
        render_header,
        render_kpi_card,
        create_funnel_chart,
        create_traffic_breakdown_chart,
        create_pca_3d_scatter,
        create_persona_radar_chart
    )

# Inject Modern CSS Theme
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ======================================================================================
# DATA PIPELINE CACHING (Streamlit Performance Optimization)
# ======================================================================================

@st.cache_data(show_spinner=False)
def load_all_analytics_data():
    """Loads and computes all SQL queries and Machine Learning pipelines dynamically."""
    bq = BigQueryService()
    
    # 1. Load SQL Tables
    df_eda = bq.query_to_dataframe("SELECT 1", cache_name="eda_overview")
    df_funnel = bq.query_to_dataframe("SELECT 1", cache_name="funnel_analysis")
    df_rfm = bq.query_to_dataframe("SELECT 1", cache_name="rfm_features")
    df_market = bq.query_to_dataframe("SELECT 1", cache_name="market_basket")
    
    # 2. Run Machine Learning Pipeline (DataProcessor + K-Means + PCA)
    processor = CustomerDataProcessor()
    X_scaled, df_trans, df_clean = processor.fit_transform(df_rfm)
    
    model = CustomerClusterModel(random_state=42)
    df_segmented, cluster_summary = model.fit_predict(X_scaled, df_clean, n_clusters=4)
    df_enriched, df_persona_summary = model.profile_personas(df_segmented)
    
    # 3. Run Market Basket Apriori Mining
    mba = MarketBasketAnalyzer(min_support=0.04, min_confidence=0.25, min_lift=1.0)
    basket_mat, n_valid_tx = mba.build_basket_matrix(df_market)
    freq_sets, rules = mba.run_apriori_and_rules(basket_mat)
    df_cross_sell = mba.get_cross_selling_recommendations(top_n=6)
    
    return {
        "df_eda": df_eda,
        "df_funnel": df_funnel,
        "df_enriched": df_enriched,
        "df_persona_summary": df_persona_summary,
        "cluster_summary": cluster_summary,
        "df_cross_sell": df_cross_sell
    }


# ======================================================================================
# MAIN APPLICATION ORCHESTRATION
# ======================================================================================

def main():
    # Render Top Header
    st.markdown(
        render_header(
            title="Hệ thống Phân tích Hành vi Khách hàng Thương mại Điện tử",
            subtitle="Đồ án môn Big Data • Google BigQuery SQL (GA4 Public Dataset) & Python Machine Learning",
            dataset_badge="GA4 Obfuscated Dataset (Active)"
        ),
        unsafe_allow_html=True
    )
    
    with st.spinner("Đang tải dữ liệu BigQuery & Huấn luyện mô hình K-Means..."):
        data = load_all_analytics_data()
        
    df_eda = data["df_eda"]
    df_funnel = data["df_funnel"]
    df_enriched = data["df_enriched"]
    df_persona_summary = data["df_persona_summary"]
    df_cross_sell = data["df_cross_sell"]

    # Sidebar Filter & Info
    with st.sidebar:
        st.markdown("### ⚙️ Điều khiển & Bộ lọc")
        st.info("💡 Dữ liệu được tổng hợp trực tiếp từ Google BigQuery và xử lý qua K-Means & Apriori.")
        
        selected_device = st.selectbox(
            "Chọn phân khúc Thiết bị cho Phễu:",
            options=["all", "desktop", "mobile", "tablet"],
            format_func=lambda x: "Tất cả thiết bị (All)" if x == "all" else f"Thiết bị {x.capitalize()}"
        )
        
        st.markdown("---")
        st.markdown("### 🎓 Thông tin Đồ án")
        st.markdown("""
        - **Đề tài:** Phân tích hành vi Khách hàng TMĐT quy mô lớn.
        - **Công nghệ:** BigQuery SQL, Python, K-Means, PCA, Apriori, Streamlit.
        - **Dataset:** GA4 E-commerce (Google Store).
        """)

    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 1. Tổng quan & KPI Điều hành",
        "🛒 2. Phễu Mua hàng & Điểm nghẽn",
        "👥 3. Phân khúc Khách hàng (K-Means)",
        "💡 4. Gợi ý Combo & Chiến lược"
    ])

    # ----------------------------------------------------------------------------------
    # TAB 1: EXECUTIVE KPI & OVERVIEW
    # ----------------------------------------------------------------------------------
    with tab1:
        total_users = int(df_eda["total_users"].sum())
        total_sessions = int(df_eda["total_sessions"].sum())
        total_revenue = float(df_eda["total_revenue"].sum())
        total_transactions = int(df_eda["total_transactions"].sum())
        avg_cr = round(total_transactions / total_sessions * 100, 2)
        
        # Render KPI Cards Row
        st.markdown(f"""
        <div class="kpi-container">
            {render_kpi_card("TỔNG NGƯỜI DÙNG (USERS)", f"{total_users:,}", "Từ 92 bảng phân vùng GA4", "#3b82f6")}
            {render_kpi_card("TỔNG PHIÊN TRUY CẬP (SESSIONS)", f"{total_sessions:,}", "Tương tác thực tế", "#0ea5e9")}
            {render_kpi_card("TỔNG DOANH THU ($ USD)", f"${total_revenue:,.2f}", "Google Merchandise Store", "#10b981")}
            {render_kpi_card("TỶ LỆ CHUYỂN ĐỔI (CR)", f"{avg_cr}%", f"{total_transactions:,} đơn hàng thành công", "#f59e0b")}
        </div>
        """, unsafe_allow_html=True)
        
        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.plotly_chart(create_traffic_breakdown_chart(df_eda), use_container_width=True)
        with col_right:
            st.markdown("#### 📋 Hiệu suất theo Kênh Tiếp thị")
            st.dataframe(
                df_eda[[
                    "traffic_medium", "total_users", "total_transactions", 
                    "total_revenue", "conversion_rate"
                ]].rename(columns={
                    "traffic_medium": "Kênh Tiếp thị",
                    "total_users": "Users",
                    "total_transactions": "Đơn hàng",
                    "total_revenue": "Doanh thu ($)",
                    "conversion_rate": "CR (%)"
                }),
                use_container_width=True,
                hide_index=True
            )

    # ----------------------------------------------------------------------------------
    # TAB 2: FUNNEL & DROP-OFF DIAGNOSTICS
    # ----------------------------------------------------------------------------------
    with tab2:
        st.markdown("### 🛒 Hành trình Khách hàng & Chẩn đoán Rơi rụng tại Phễu")
        
        col_f1, col_f2 = st.columns([3, 2])
        with col_f1:
            st.plotly_chart(create_funnel_chart(df_funnel, selected_device), use_container_width=True)
        with col_f2:
            st.markdown("#### 🔍 Thống kê Phễu theo Thiết bị")
            st.dataframe(
                df_funnel[[
                    "device_category", "step_1_view_item_users", "step_2_add_to_cart_users", 
                    "step_4_purchase_users", "overall_conversion_rate_pct", "cart_abandonment_rate_pct"
                ]].rename(columns={
                    "device_category": "Thiết bị",
                    "step_1_view_item_users": "1. Xem SP",
                    "step_2_add_to_cart_users": "2. Thêm Giỏ",
                    "step_4_purchase_users": "4. Mua Hàng",
                    "overall_conversion_rate_pct": "Overall CR (%)",
                    "cart_abandonment_rate_pct": "Bỏ Giỏ (%)"
                }),
                use_container_width=True,
                hide_index=True
            )
            
            st.warning("""
            **⚠️ Điểm nghẽn lớn nhất (Bottleneck):**
            - Tỷ lệ bỏ giỏ hàng trên **Mobile lên tới >84%**, cao hơn đáng kể so với Desktop (64.9%).
            - Cần tối ưu luồng thanh toán trên thiết bị di động để cứu vãn doanh thu bị thất thoát.
            """)

    # ----------------------------------------------------------------------------------
    # TAB 3: CUSTOMER SEGMENTATION (K-MEANS)
    # ----------------------------------------------------------------------------------
    with tab3:
        st.markdown("### 👥 Phân khúc Khách hàng Tự động bằng Học máy (K-Means Clustering)")
        
        col_s1, col_s2 = st.columns([3, 2])
        with col_s1:
            st.plotly_chart(create_pca_3d_scatter(df_enriched), use_container_width=True)
        with col_s2:
            st.plotly_chart(create_persona_radar_chart(df_persona_summary), use_container_width=True)
            
        st.markdown("#### 📑 Bảng Chân dung 4 Nhóm Khách hàng (Personas Profiling Table)")
        st.dataframe(df_persona_summary, use_container_width=True, hide_index=True)
        
        # User Lookup Search
        st.markdown("---")
        st.markdown("#### 🔎 Tra cứu Chi tiết Hành vi Từng Khách hàng (`user_pseudo_id`)")
        search_user = st.selectbox(
            "Chọn User ID để tra cứu:",
            options=df_enriched["user_pseudo_id"].head(50).tolist()
        )
        if search_user:
            user_row = df_enriched[df_enriched["user_pseudo_id"] == search_user].iloc[0]
            col_u1, col_u2, col_u3, col_u4 = st.columns(4)
            col_u1.metric("Nhóm Phân khúc", user_row["persona_name"])
            col_u2.metric("Số ngày từ lần cuối (R)", f"{user_row['recency_days']} ngày")
            col_u3.metric("Tổng chi tiêu (M)", f"${user_row['monetary_value']:,.2f}")
            col_u4.metric("Thời gian tương tác", f"{user_row['total_engagement_sec']:.0f} s")

    # ----------------------------------------------------------------------------------
    # TAB 4: MARKET BASKET & STRATEGIC RECOMMENDATIONS
    # ----------------------------------------------------------------------------------
    with tab4:
        st.markdown("### 💡 Khai phá Luật Kết hợp Giỏ hàng & Kế hoạch Hành động Kinh doanh")
        
        col_m1, col_m2 = st.columns([3, 2])
        with col_m1:
            st.markdown("#### 🛍️ Gợi ý Combo Bán Chéo (Cross-Selling Rules - Apriori)")
            st.dataframe(df_cross_sell, use_container_width=True, hide_index=True)
        with col_m2:
            st.markdown("#### 🎯 Ma trận Chiến lược Tiếp thị cho 4 Phân khúc")
            st.markdown("""
            - 💎 **VIPs (Loyal Champions):**
              *Chính sách:* Tặng quyền truy cập sớm sản phẩm giới hạn (Early Access), miễn phí vận chuyển trọn đời, hotline VIP riêng.
            - 🌟 **Potential Loyalists:**
              *Chính sách:* Tặng voucher giảm giá 15% khi đạt đơn hàng tối thiểu $150 để nâng cao Giá trị Đơn hàng Trung bình (AOV).
            - 🛒 **Cart Abandoners (Bỏ giỏ hàng):**
              *Chính sách:* Tự động kích hoạt Web Push Notification / Email cứu giỏ hàng sau 2 giờ kèm mã FREESHIP.
            - ⚠️ **At-Risk Customers:**
              *Chính sách:* Gửi chiến dịch Email Win-back với thông điệp "We miss you" kèm ưu đãi 20% danh mục họ từng xem.
            """)


if __name__ == "__main__":
    main()
