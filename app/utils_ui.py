"""
UI Utilities Module: Custom Modern Theme Styling, Metric KPI Cards,
and Interactive Plotly Chart Generators for Streamlit Dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

from config.settings import PERSONA_COLORS


# Custom CSS Injection for Modern Dark Glassmorphism Styling
CUSTOM_CSS = """
<style>
    /* Global Styles & Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Header Container */
    .header-box {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* KPI Metric Cards */
    .kpi-container {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .kpi-card {
        flex: 1 1 calc(25% - 16px);
        min-width: 200px;
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    
    .kpi-subtitle {
        font-size: 0.8rem;
        color: #10b981;
        font-weight: 500;
    }
    
    /* Section Box Wrapper */
    .section-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 600;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: #ffffff !important;
    }
</style>
"""


def render_header(title: str, subtitle: str, dataset_badge: str = "GA4 BigQuery Dataset"):
    """Renders modern glassmorphism top header banner."""
    html = f"""
    <div class="header-box">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #f8fafc;">{title}</h1>
                <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 0.95rem;">{subtitle}</p>
            </div>
            <span style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                🟢 {dataset_badge}
            </span>
        </div>
    </div>
    """
    return html


def render_kpi_card(title: str, value: str, subtitle: str = "", trend_color: str = "#10b981") -> str:
    """Generates HTML snippet for a single KPI card."""
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle" style="color: {trend_color};">{subtitle}</div>
    </div>
    """


# ======================================================================================
# INTERACTIVE PLOTLY CHART GENERATORS
# ======================================================================================

def create_funnel_chart(df_funnel: pd.DataFrame, device_filter: str = "all") -> go.Figure:
    """
    Creates an interactive sequential Funnel chart for View -> Cart -> Checkout -> Purchase.
    """
    if device_filter != "all" and "device_category" in df_funnel.columns:
        filtered_df = df_funnel[df_funnel["device_category"] == device_filter]
        if filtered_df.empty:
            filtered_df = df_funnel
    else:
        filtered_df = df_funnel

    step_1 = int(filtered_df["step_1_view_item_users"].sum())
    step_2 = int(filtered_df["step_2_add_to_cart_users"].sum())
    step_3 = int(filtered_df["step_3_begin_checkout_users"].sum())
    step_4 = int(filtered_df["step_4_purchase_users"].sum())

    stages = [
        "1. View Item (Xem SP)",
        "2. Add to Cart (Thêm Giỏ)",
        "3. Begin Checkout (Thanh Toán)",
        "4. Purchase (Mua Thành Công)"
    ]
    values = [step_1, step_2, step_3, step_4]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial+percent previous",
        marker=dict(color=["#3b82f6", "#0ea5e9", "#f59e0b", "#10b981"]),
        connector={"line": {"color": "rgba(255,255,255,0.2)", "dash": "solid", "width": 1.5}},
        hovertemplate="<b>%{y}</b><br>Khách hàng: <b>%{x:,} users</b><br>Tỷ lệ so với Bước 1: <b>%{percentInitial:.1%}</b><extra></extra>"
    ))

    fig.update_layout(
        title=dict(text=f"Phễu Chuyển đổi Mua hàng (Thiết bị: {device_filter.upper()})", font=dict(size=16, color="#f8fafc")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=380
    )
    return fig


def create_traffic_breakdown_chart(df_eda: pd.DataFrame) -> go.Figure:
    """Creates a modern dual-axis chart for Traffic Channels (Revenue & Users)."""
    df_sorted = df_eda.sort_values(by="total_revenue", ascending=False)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted["traffic_medium"],
        y=df_sorted["total_revenue"],
        name="Doanh thu ($ USD)",
        marker_color="#3b82f6",
        hovertemplate="Kênh: <b>%{x}</b><br>Doanh thu: <b>$%{y:,.2f}</b><extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=df_sorted["traffic_medium"],
        y=df_sorted["total_users"],
        name="Số lượng Users",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#10b981", width=3),
        marker=dict(size=8, color="#10b981"),
        hovertemplate="Kênh: <b>%{x}</b><br>Users: <b>%{y:,}</b><extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text="Doanh thu & Lưu lượng Người dùng theo Kênh Tiếp thị", font=dict(size=16, color="#f8fafc")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Doanh thu ($ USD)", gridcolor="rgba(255,255,255,0.05)"),
        yaxis2=dict(title="Số lượng Users", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=20, r=20, t=60, b=20),
        height=360
    )
    return fig


def create_pca_3d_scatter(df_segmented: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive 3D PCA scatter visualization of the 4 Customer Clusters.
    """
    fig = px.scatter_3d(
        df_segmented,
        x="pca_3d_x",
        y="pca_3d_y",
        z="pca_3d_z",
        color="persona_name",
        color_discrete_map=PERSONA_COLORS,
        hover_name="user_pseudo_id",
        hover_data={
            "pca_3d_x": False,
            "pca_3d_y": False,
            "pca_3d_z": False,
            "recency_days": True,
            "total_sessions": True,
            "monetary_value": ":$.2f",
            "total_engagement_sec": ":.0f s",
            "cart_to_view_ratio": ":.2f"
        },
        title="Không gian Phân cụm Khách hàng 3D (PCA Dimensionality Reduction)"
    )

    fig.update_traces(marker=dict(size=4, opacity=0.85))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        legend=dict(
            title=dict(text="Chân dung Khách hàng"),
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        scene=dict(
            xaxis=dict(title="PCA Axis 1", backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(title="PCA Axis 2", backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
            zaxis=dict(title="PCA Axis 3", backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
        ),
        margin=dict(l=10, r=10, t=40, b=20),
        height=520
    )
    return fig


def create_persona_radar_chart(df_persona_summary: pd.DataFrame) -> go.Figure:
    """
    Creates a Radar / Spider chart comparing normalized behavioral metrics across Personas.
    """
    metrics = ["Recency TB (ngày)", "Sessions TB", "Doanh thu TB ($)", "Số SP Thêm Giỏ TB", "Tỷ lệ Giỏ/Xem"]
    
    fig = go.Figure()
    
    for _, row in df_persona_summary.iterrows():
        p_name = row["Chân dung Khách hàng (Persona)"]
        color = PERSONA_COLORS.get(p_name, "#3b82f6")
        
        # Normalize roughly for radar visual
        vals = [
            min(1.0, row["Recency TB (ngày)"] / 120.0),
            min(1.0, row["Sessions TB"] / 15.0),
            min(1.0, row["Doanh thu TB ($)"] / 400.0),
            min(1.0, row["Số SP Thêm Giỏ TB"] / 12.0),
            min(1.0, row["Tỷ lệ Giỏ/Xem"] / 0.40)
        ]
        # Close radar loop
        vals.append(vals[0])
        categories = ["Recency (Inverted)", "Frequency (Sessions)", "Monetary ($)", "Cart Items", "Cart Ratio", "Recency (Inverted)"]
        
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories,
            fill="toself",
            name=p_name,
            line=dict(color=color, width=2),
            opacity=0.6
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        title=dict(text="So sánh Đa chiều Đặc tính giữa các Nhóm Khách hàng", font=dict(size=15, color="#f8fafc")),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=30, r=30, t=50, b=30),
        height=420
    )
    return fig
