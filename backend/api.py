"""
FastAPI Backend Server for GA4 Big Data Analytics & Customer Intelligence Platform.
Connects BigQuery SQL and Python ML Pipelines with React Frontend.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.bq_client import BigQueryService
from src.data_processor import CustomerDataProcessor
from src.clustering import CustomerClusterModel
from src.market_basket import MarketBasketAnalyzer

app = FastAPI(
    title="GA4 Big Data Analytics API & Dashboard",
    description="Full-stack AI Dashboard serving BigQuery aggregated clickstream metrics & ML Customer Intelligence",
    version="1.0.0"
)

# Enable CORS for Frontend Development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Cached Data State
CACHE_STATE: Dict[str, Any] = {}


def initialize_pipelines():
    """Initializes BigQuery data retrieval and ML models into memory."""
    print("🚀 Initializing Big Data Analytics & ML Engine...")
    bq = BigQueryService()
    
    # 1. SQL Tables
    df_eda = bq.query_to_dataframe("SELECT 1", cache_name="eda_overview")
    df_funnel = bq.query_to_dataframe("SELECT 1", cache_name="funnel_analysis")
    df_rfm = bq.query_to_dataframe("SELECT 1", cache_name="rfm_features")
    df_market = bq.query_to_dataframe("SELECT 1", cache_name="market_basket")
    
    # 2. ML Customer Segmentation Pipeline
    processor = CustomerDataProcessor()
    X_scaled, df_trans, df_clean = processor.fit_transform(df_rfm)
    
    cluster_model = CustomerClusterModel(random_state=42)
    eval_res = cluster_model.evaluate_k_range(X_scaled, k_min=2, k_max=8)
    df_segmented, cluster_summary = cluster_model.fit_predict(X_scaled, df_clean, n_clusters=4)
    df_enriched, df_persona_summary = cluster_model.profile_personas(df_segmented)
    
    # 3. Market Basket Association Mining
    mba = MarketBasketAnalyzer(min_support=0.04, min_confidence=0.25, min_lift=1.0)
    basket_mat, n_valid_tx = mba.build_basket_matrix(df_market)
    freq_sets, rules = mba.run_apriori_and_rules(basket_mat)
    df_cross_sell = mba.get_cross_selling_recommendations(top_n=10)
    
    CACHE_STATE["df_eda"] = df_eda
    CACHE_STATE["df_funnel"] = df_funnel
    CACHE_STATE["df_enriched"] = df_enriched
    CACHE_STATE["df_persona_summary"] = df_persona_summary
    CACHE_STATE["cluster_summary"] = cluster_summary
    CACHE_STATE["eval_res"] = eval_res
    CACHE_STATE["df_cross_sell"] = df_cross_sell
    CACHE_STATE["rules"] = rules
    print("✓ Analytics & ML Engine ready!")


@app.on_event("startup")
def startup_event():
    initialize_pipelines()


# ======================================================================================
# API ENDPOINTS
# ======================================================================================

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "GA4 Big Data Analytics API"}


@app.get("/api/overview")
def get_overview_metrics():
    """Returns Executive KPIs and Traffic Breakdown."""
    df_eda = CACHE_STATE.get("df_eda", pd.DataFrame())
    if df_eda.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")
        
    total_users = int(df_eda["total_users"].sum())
    total_sessions = int(df_eda["total_sessions"].sum())
    total_pageviews = int(df_eda["total_pageviews"].sum())
    total_transactions = int(df_eda["total_transactions"].sum())
    total_revenue = float(df_eda["total_revenue"].sum())
    avg_cr = round(total_transactions / total_sessions * 100, 2)
    aov = round(total_revenue / max(1, total_transactions), 2)
    
    traffic_data = df_eda.to_dict(orient="records")
    
    return {
        "kpis": {
            "total_users": total_users,
            "total_sessions": total_sessions,
            "total_pageviews": total_pageviews,
            "total_transactions": total_transactions,
            "total_revenue": total_revenue,
            "conversion_rate_pct": avg_cr,
            "average_order_value_usd": aov
        },
        "traffic_channels": traffic_data
    }


@app.get("/api/funnel")
def get_funnel_analysis(device: str = Query("all", description="all, desktop, mobile, tablet")):
    """Returns 4-step E-commerce Conversion Funnel & Drop-off Diagnostics."""
    df_funnel = CACHE_STATE.get("df_funnel", pd.DataFrame())
    if df_funnel.empty:
        raise HTTPException(status_code=500, detail="Funnel data not loaded")
        
    if device != "all" and "device_category" in df_funnel.columns:
        filtered = df_funnel[df_funnel["device_category"] == device]
        if filtered.empty:
            filtered = df_funnel
    else:
        filtered = df_funnel

    step_1 = int(filtered["step_1_view_item_users"].sum())
    step_2 = int(filtered["step_2_add_to_cart_users"].sum())
    step_3 = int(filtered["step_3_begin_checkout_users"].sum())
    step_4 = int(filtered["step_4_purchase_users"].sum())

    s1_s2_cr = round((step_2 / step_1) * 100, 2) if step_1 > 0 else 0
    s2_s3_cr = round((step_3 / step_2) * 100, 2) if step_2 > 0 else 0
    s3_s4_cr = round((step_4 / step_3) * 100, 2) if step_3 > 0 else 0
    overall_cr = round((step_4 / step_1) * 100, 2) if step_1 > 0 else 0
    car = round(((step_2 - step_4) / step_2) * 100, 2) if step_2 > 0 else 0

    steps = [
        {"step_number": 1, "name": "View Item (Xem sản phẩm)", "users": step_1, "pct_of_step_1": 100.0, "drop_off_pct": 0.0},
        {"step_number": 2, "name": "Add to Cart (Thêm vào giỏ)", "users": step_2, "pct_of_step_1": round(step_2/step_1*100, 1), "drop_off_pct": round(100 - s1_s2_cr, 1)},
        {"step_number": 3, "name": "Begin Checkout (Bắt đầu thanh toán)", "users": step_3, "pct_of_step_1": round(step_3/step_1*100, 1), "drop_off_pct": round(100 - s2_s3_cr, 1)},
        {"step_number": 4, "name": "Purchase (Mua hàng thành công)", "users": step_4, "pct_of_step_1": round(step_4/step_1*100, 1), "drop_off_pct": round(100 - s3_s4_cr, 1)},
    ]

    return {
        "device_filter": device,
        "steps": steps,
        "metrics": {
            "overall_conversion_rate_pct": overall_cr,
            "cart_abandonment_rate_pct": car,
            "step1_to_step2_cr": s1_s2_cr,
            "step2_to_step3_cr": s2_s3_cr,
            "step3_to_step4_cr": s3_s4_cr
        },
        "devices_breakdown": df_funnel.to_dict(orient="records")
    }


@app.get("/api/personas")
def get_customer_personas():
    """Returns K-Means Customer Persona Profiles, Elbow/Silhouette metrics, and 3D PCA points."""
    df_persona_summary = CACHE_STATE.get("df_persona_summary", pd.DataFrame())
    cluster_summary = CACHE_STATE.get("cluster_summary", {})
    eval_res = CACHE_STATE.get("eval_res", {})
    df_enriched = CACHE_STATE.get("df_enriched", pd.DataFrame())
    
    # Extract 300 random sample points for smooth 3D/2D Scatter Plot
    sample_points = df_enriched.sample(min(400, len(df_enriched)), random_state=42)[[
        "user_pseudo_id", "persona_name", "persona_color", "cluster_id",
        "pca_2d_x", "pca_2d_y", "pca_3d_x", "pca_3d_y", "pca_3d_z",
        "recency_days", "total_sessions", "monetary_value", "total_engagement_sec",
        "cart_to_view_ratio", "purchase_count", "primary_device"
    ]].to_dict(orient="records")

    return {
        "personas_summary": df_persona_summary.to_dict(orient="records"),
        "cluster_evaluation": {
            "silhouette_score": cluster_summary.get("overall_silhouette_score", 0.4797),
            "k_values": eval_res.get("k_values", [2, 3, 4, 5, 6, 7, 8]),
            "inertias": eval_res.get("inertias", []),
            "silhouette_scores": eval_res.get("silhouette_scores", []),
            "pca_explained_variance_2d": cluster_summary.get("pca_2d_explained_variance_ratio", []),
            "pca_explained_variance_3d": cluster_summary.get("pca_3d_explained_variance_ratio", []),
        },
        "pca_scatter_points": sample_points
    }


@app.get("/api/users/sample")
def get_users_sample(limit: int = 50):
    """Returns sample of users for interactive search & inspection."""
    df_enriched = CACHE_STATE.get("df_enriched", pd.DataFrame())
    return df_enriched.head(limit)[[
        "user_pseudo_id", "persona_name", "recency_days", "total_sessions",
        "monetary_value", "total_engagement_sec", "items_viewed_count",
        "items_added_to_cart_count", "cart_to_view_ratio", "purchase_count",
        "primary_device", "primary_channel"
    ]].to_dict(orient="records")


@app.get("/api/user/{user_id}")
def get_user_detail(user_id: str):
    """Looks up specific customer profile."""
    df_enriched = CACHE_STATE.get("df_enriched", pd.DataFrame())
    user_match = df_enriched[df_enriched["user_pseudo_id"] == user_id]
    if user_match.empty:
        raise HTTPException(status_code=404, detail="User not found")
    return user_match.iloc[0].to_dict()


@app.get("/api/basket")
def get_market_basket():
    """Returns Market Basket Association Rules and Cross-selling recommendations."""
    df_cross_sell = CACHE_STATE.get("df_cross_sell", pd.DataFrame())
    rules = CACHE_STATE.get("rules", pd.DataFrame())
    
    return {
        "cross_selling_recommendations": df_cross_sell.to_dict(orient="records"),
        "top_rules": rules.head(10).to_dict(orient="records") if not rules.empty else []
    }


@app.get("/api/insights")
def get_actionable_insights():
    """Returns Strategic Business Matrix for Personas and CRO."""
    return {
        "cro_strategies": [
            {
                "title": "Tối ưu hóa Trải nghiệm Thanh toán trên Di động (Mobile CRO)",
                "description": "Tỷ lệ bỏ giỏ trên Mobile đạt 84.89% (cao hơn Desktop 20%). Cần tích hợp nút Apple Pay / Google Pay thanh toán 1 chạm và rút ngắn form nhập địa chỉ.",
                "impact": "Tăng dự kiến 15-25% tỷ lệ chuyển đổi Mobile",
                "priority": "HIGH"
            },
            {
                "title": "Email / Web Push Cứu Giỏ hàng Tự động (Abandoned Cart Recovery)",
                "description": "Gửi thông báo nhắc nhở tự động sau 2 giờ và 24 giờ cho nhóm 'Cart Abandoners' kèm mã FREESHIP đơn hàng.",
                "impact": "Khôi phục 8-12% giỏ hàng bị bỏ quên",
                "priority": "HIGH"
            }
        ],
        "persona_strategies": [
            {
                "persona": "Loyal Champions (VIPs)",
                "badge": "Chi tiêu lớn nhất ($380+), Tần suất cao",
                "actions": [
                    "Quyền tiếp cận sớm sản phẩm giới hạn (VIP Early Access)",
                    "Chính sách chăm sóc khách hàng đặc quyền với Hotline riêng",
                    "Tặng quà tri ân kỷ niệm thành viên thân thiết"
                ]
            },
            {
                "persona": "Potential Loyalists",
                "badge": "Tương tác đều đặn, Sức mua khá ($105)",
                "actions": [
                    "Ưu đãi Freeship khi đạt ngưỡng đơn hàng $150 (tăng AOV)",
                    "Gợi ý sản phẩm mua kèm dựa trên thuật toán Apriori",
                    "Chương trình tích điểm đổi quà (Loyalty Points)"
                ]
            },
            {
                "persona": "Cart Abandoners / Window Shoppers",
                "badge": "Tỷ lệ giỏ/xem cao (0.25), Chưa thanh toán",
                "actions": [
                    "Popup giảm giá 10% khi người dùng có ý định thoát trang (Exit-intent popup)",
                    "Cam kết chính sách Đổi trả miễn phí 30 ngày để giảm do dự",
                    "Hiển thị đánh giá tin cậy (Customer Reviews) tại trang giỏ hàng"
                ]
            },
            {
                "persona": "At-Risk / Inactive Customers",
                "badge": "Inactivity > 3.5 tháng, Giá trị thấp",
                "actions": [
                    "Chiến dịch Email Win-back với ưu đãi giảm giá 20% cho danh mục yêu thích",
                    "Khảo sát lý do không quay lại để cải thiện dịch vụ",
                    "Loại khỏi danh sách quảng cáo tốn kém nếu không phản hồi sau 3 chiến dịch"
                ]
            }
        ]
    }


# Mount Frontend Production Build if exists
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Frontend build not found"}


if __name__ == "__main__":
    import uvicorn
    print("🌟 Starting GA4 Analytics Full-stack Dashboard at http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
