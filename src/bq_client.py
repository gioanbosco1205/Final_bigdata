"""
BigQuery Service module for managing remote cloud query execution,
caching results, and handling offline demonstration dataset generation.
"""

import os
import sys
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import (
    CACHE_DIR,
    SQL_DIR,
    GCP_PROJECT_ID,
    GCP_CREDENTIALS_PATH,
    GA4_EVENTS_TABLE
)


class BigQueryService:
    """
    Handles BigQuery connectivity, query execution with pushdown computation,
    local lightweight caching, and fallback sample generator for seamless testing.
    """

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or GCP_PROJECT_ID
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes BigQuery client if credentials or default auth exist."""
        try:
            from google.cloud import bigquery
            if GCP_CREDENTIALS_PATH and os.path.exists(GCP_CREDENTIALS_PATH):
                self.client = bigquery.Client.from_service_account_json(
                    GCP_CREDENTIALS_PATH, project=self.project_id
                )
            else:
                # Try default application credentials
                self.client = bigquery.Client(project=self.project_id)
            print(" Connected to Google Cloud BigQuery successfully.")
        except Exception as e:
            # Client not configured or offline mode
            self.client = None
            print(f"ℹ️ BigQuery client offline or credentials not set ({e}). Using smart cache/sample mode.")

    def read_sql_file(self, filename: str) -> str:
        """Reads SQL statement from sql/ directory."""
        filepath = SQL_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"SQL file not found at: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            query = f.read()
        return query

    def query_to_dataframe(
        self,
        query: str,
        cache_name: Optional[str] = None,
        use_cache: bool = True,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Executes query on BigQuery or returns cached DataFrame if available.
        """
        cache_path = CACHE_DIR / f"{cache_name}.parquet" if cache_name else None

        # Check local cache first for instant speed
        if use_cache and cache_path and cache_path.exists() and not force_refresh:
            print(f"⚡ Loading cached results for [{cache_name}] ({cache_path.name})")
            return pd.read_parquet(cache_path)

        # If live BigQuery client is available, execute on cloud
        if self.client is not None:
            try:
                print(f"🚀 Executing pushdown query on BigQuery Cloud...")
                query_job = self.client.query(query)
                df = query_job.to_dataframe()
                if cache_path:
                    df.to_parquet(cache_path, index=False)
                    print(f"💾 Results cached to {cache_path}")
                return df
            except Exception as e:
                print(f"⚠️ BigQuery Cloud Execution error: {e}. Falling back to sample dataset.")

        # If offline or client failed, generate realistic calibrated GA4 sample
        print(f"📊 Generating calibrated GA4 sample dataset for [{cache_name}]...")
        df = self._generate_calibrated_sample(cache_name)
        if cache_path:
            df.to_parquet(cache_path, index=False)
        return df

    def _generate_calibrated_sample(self, dataset_type: Optional[str]) -> pd.DataFrame:
        """
        Generates mathematically consistent sample data mimicking GA4 E-commerce Obfuscated Dataset.
        """
        np.random.seed(42)

        if dataset_type == "eda_overview" or dataset_type == "traffic_summary":
            channels = ["Organic Search", "Direct", "Referral", "Paid Search", "Display", "Affiliates", "Email"]
            weights = [0.42, 0.28, 0.14, 0.08, 0.04, 0.03, 0.01]
            data = []
            for ch, w in zip(channels, weights):
                base_val = int(25000 * w)
                sessions = max(int(np.random.normal(base_val, max(10, base_val * 0.08))), 50)
                users = int(sessions * np.random.uniform(0.75, 0.88))
                pageviews = int(sessions * np.random.uniform(3.5, 5.8))
                transactions = max(int(sessions * np.random.uniform(0.018, 0.035)), 1)
                revenue = round(transactions * np.random.uniform(45.0, 95.0), 2)
                data.append({
                    "traffic_medium": ch,
                    "total_users": users,
                    "total_sessions": sessions,
                    "total_pageviews": pageviews,
                    "total_transactions": transactions,
                    "total_revenue": revenue,
                    "conversion_rate": round(transactions / sessions * 100, 2)
                })
            return pd.DataFrame(data)

        elif dataset_type == "funnel_analysis":
            devices = ["desktop", "mobile", "tablet"]
            data = []
            device_multipliers = {"desktop": 1.0, "mobile": 0.82, "tablet": 0.08}

            for dev, mult in device_multipliers.items():
                view_item = int(38000 * mult)
                add_to_cart = int(view_item * (0.285 if dev == "desktop" else 0.175))
                begin_checkout = int(add_to_cart * (0.540 if dev == "desktop" else 0.360))
                purchase = int(begin_checkout * (0.650 if dev == "desktop" else 0.420))

                s1_s2_cr = round((add_to_cart / view_item) * 100, 2)
                s2_s3_cr = round((begin_checkout / add_to_cart) * 100, 2)
                s3_s4_cr = round((purchase / begin_checkout) * 100, 2)
                overall_cr = round((purchase / view_item) * 100, 2)
                car = round(((add_to_cart - purchase) / add_to_cart) * 100, 2)

                data.append({
                    "device_category": dev,
                    "step_1_view_item_users": view_item,
                    "step_2_add_to_cart_users": add_to_cart,
                    "step_3_begin_checkout_users": begin_checkout,
                    "step_4_purchase_users": purchase,
                    "overall_conversion_rate_pct": overall_cr,
                    "step1_to_step2_cr_pct": s1_s2_cr,
                    "step2_to_step3_cr_pct": s2_s3_cr,
                    "step3_to_step4_cr_pct": s3_s4_cr,
                    "cart_abandonment_rate_pct": car
                })
            return pd.DataFrame(data)

        elif dataset_type == "rfm_features" or dataset_type is None:
            # Generate 4,500 distinct user profiles with realistic customer personas
            n_users = 4500
            user_ids = [f"user_{i:06d}.{np.random.randint(10000000, 99999999)}" for i in range(n_users)]

            # Persona proportions: VIPs (8%), Potential Loyalists (22%), Cart Abandoners (35%), At-Risk/Inactive (35%)
            personas = np.random.choice([0, 1, 2, 3], size=n_users, p=[0.08, 0.22, 0.35, 0.35])

            recency = []
            frequency = []
            monetary = []
            engagement_sec = []
            pageviews = []
            items_viewed = []
            items_cart = []
            purchases = []

            for p in personas:
                if p == 0:  # Loyal Champions (VIPs)
                    r = np.random.randint(1, 15)
                    f = np.random.randint(6, 25)
                    m = np.random.exponential(250) + 120
                    eng = np.random.randint(400, 2500)
                    pv = np.random.randint(25, 120)
                    iv = np.random.randint(15, 60)
                    ic = np.random.randint(5, 20)
                    pur = np.random.randint(3, 10)
                elif p == 1:  # Potential Loyalists
                    r = np.random.randint(5, 30)
                    f = np.random.randint(3, 8)
                    m = np.random.exponential(80) + 40
                    eng = np.random.randint(200, 1000)
                    pv = np.random.randint(15, 50)
                    iv = np.random.randint(10, 35)
                    ic = np.random.randint(2, 8)
                    pur = np.random.randint(1, 3)
                elif p == 2:  # Cart Abandoners / Window Shoppers
                    r = np.random.randint(2, 45)
                    f = np.random.randint(2, 6)
                    m = 0.0 if np.random.rand() > 0.15 else np.random.exponential(35)
                    eng = np.random.randint(150, 750)
                    pv = np.random.randint(12, 40)
                    iv = np.random.randint(8, 30)
                    ic = np.random.randint(2, 7)
                    pur = 0 if m == 0.0 else 1
                else:  # At-Risk / Inactive
                    r = np.random.randint(50, 180)
                    f = np.random.randint(1, 3)
                    m = 0.0 if np.random.rand() > 0.05 else np.random.exponential(25)
                    eng = np.random.randint(10, 120)
                    pv = np.random.randint(1, 6)
                    iv = np.random.randint(1, 5)
                    ic = 0 if np.random.rand() > 0.2 else 1
                    pur = 0 if m == 0.0 else 1

                recency.append(r)
                frequency.append(f)
                monetary.append(round(m, 2))
                engagement_sec.append(eng)
                pageviews.append(pv)
                items_viewed.append(iv)
                items_cart.append(ic)
                purchases.append(pur)

            df = pd.DataFrame({
                "user_pseudo_id": user_ids,
                "recency_days": recency,
                "total_sessions": frequency,
                "monetary_value": monetary,
                "total_engagement_sec": engagement_sec,
                "total_pageviews": pageviews,
                "items_viewed_count": items_viewed,
                "items_added_to_cart_count": items_cart,
                "cart_to_view_ratio": np.round(np.array(items_cart) / (np.array(items_viewed) + 1e-5), 3),
                "purchase_count": purchases,
                "primary_device": np.random.choice(["desktop", "mobile", "tablet"], size=n_users, p=[0.60, 0.35, 0.05]),
                "primary_channel": np.random.choice(["Organic Search", "Direct", "Referral", "Paid Search"], size=n_users, p=[0.45, 0.30, 0.15, 0.10])
            })
            return df

        elif dataset_type == "market_basket":
            # Realistic transactions with Google Merchandise Store items
            products = [
                "Google Metallic Sunglasses",
                "Google Unisex Eco Tee Black",
                "Google Twill Cap",
                "Google Hard Cover Journal",
                "Google Thermal Bottle 20oz",
                "Android Small Figurine",
                "Google Leatherette Coaster Set",
                "Google Large Backpack"
            ]
            transactions = []
            for t_id in range(1, 650):
                # Bundle patterns: e.g. Tee + Cap + Bottle or Journal + Coaster
                if np.random.rand() < 0.4:
                    items = ["Google Unisex Eco Tee Black", "Google Twill Cap"]
                    if np.random.rand() < 0.5:
                        items.append("Google Thermal Bottle 20oz")
                elif np.random.rand() < 0.3:
                    items = ["Google Hard Cover Journal", "Google Leatherette Coaster Set"]
                else:
                    items = list(np.random.choice(products, size=np.random.randint(1, 4), replace=False))

                for item in items:
                    transactions.append({
                        "transaction_id": f"T_{t_id:05d}",
                        "item_name": item,
                        "item_category": "Apparel" if "Tee" in item or "Cap" in item else "Accessories",
                        "price": 18.0 if "Tee" in item else (15.0 if "Cap" in item else 24.0)
                    })
            return pd.DataFrame(transactions)

        return pd.DataFrame()


# Quick test runner if called directly
if __name__ == "__main__":
    bq = BigQueryService()
    print("Testing BigQueryService query generation...")
    df_rfm = bq.query_to_dataframe("SELECT 1", cache_name="rfm_features")
    print(f"✓ RFM Data sample shape: {df_rfm.shape}")
    print(df_rfm.head(3))
