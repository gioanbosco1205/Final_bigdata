"""
Project configuration and settings for Big Data Analytics on GA4 E-commerce dataset.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
APP_DIR = BASE_DIR / "app"

# Ensure runtime directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Google Cloud BigQuery Settings
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "bigquery-public-data")
GCP_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# Public GA4 Dataset Constants
GA4_PROJECT = "bigquery-public-data"
GA4_DATASET = "ga4_obfuscated_sample_ecommerce"
GA4_EVENTS_TABLE = f"{GA4_PROJECT}.{GA4_DATASET}.events_*"

# Feature Engineering Constants
RFM_FEATURES = [
    "recency_days",
    "total_sessions",
    "monetary_value",
    "total_engagement_sec",
    "total_pageviews",
    "items_viewed_count",
    "items_added_to_cart_count",
    "cart_to_view_ratio",
    "purchase_count",
]

# Customer Persona Labels
PERSONA_LABELS = {
    0: "Loyal Champions (VIPs)",
    1: "Potential Loyalists",
    2: "Cart Abandoners / Window Shoppers",
    3: "At-Risk / Inactive Customers"
}

# Persona Color Palette for UI Visuals
PERSONA_COLORS = {
    "Loyal Champions (VIPs)": "#10B981",              # Emerald Green
    "Potential Loyalists": "#3B82F6",                 # Royal Blue
    "Cart Abandoners / Window Shoppers": "#F59E0B",   # Amber / Orange
    "At-Risk / Inactive Customers": "#EF4444"         # Crimson Red
}
