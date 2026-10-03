"""
Comprehensive End-to-End Pipeline & Integration Test Suite for Big Data GA4 Analytics Platform.
Validates SQL integrity, BigQuery Data Caching, Preprocessing, ML Clustering, Market Basket,
Backend FastAPI Endpoints, and Jupyter Notebooks code syntax.
"""

import os
import sys
import json
import ast
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

# Setup project root path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import (
    BASE_DIR,
    SQL_DIR,
    DATA_DIR,
    CACHE_DIR,
    NOTEBOOKS_DIR,
    RFM_FEATURES,
    PERSONA_LABELS,
    PERSONA_COLORS
)
from src.bq_client import BigQueryService
from src.data_processor import CustomerDataProcessor
from src.clustering import CustomerClusterModel
from src.market_basket import MarketBasketAnalyzer
from backend.api import app, initialize_pipelines, CACHE_STATE
from fastapi.testclient import TestClient


class TestGA4BigDataPipeline(unittest.TestCase):
    """Full End-to-End Automated Test Case for all components."""

    @classmethod
    def setUpClass(cls):
        """Initializes services and backend state once before running tests."""
        print("\n" + "="*80)
        print("🧪 RUNNING END-TO-END AUTOMATED PIPELINE TEST SUITE (TASK 6.1)")
        print("="*80)
        cls.bq_service = BigQueryService()
        cls.processor = CustomerDataProcessor()
        cls.cluster_model = CustomerClusterModel(random_state=42)
        cls.mba_analyzer = MarketBasketAnalyzer(min_support=0.04, min_confidence=0.20, min_lift=1.0)
        
        # Initialize Backend Pipelines
        initialize_pipelines()
        cls.client = TestClient(app)

    # ----------------------------------------------------------------------------------
    # 1. SQL FILES INTEGRITY TESTS
    # ----------------------------------------------------------------------------------
    def test_01_sql_files_exist_and_valid_syntax(self):
        """Test that all 4 required BigQuery SQL files exist and contain valid query structures."""
        expected_sql_files = [
            "01_eda_overview.sql",
            "02_funnel_analysis.sql",
            "03_rfm_features.sql",
            "04_market_basket.sql"
        ]
        for filename in expected_sql_files:
            file_path = SQL_DIR / filename
            self.assertTrue(file_path.exists(), f"SQL file not found: {filename}")
            
            content = file_path.read_text(encoding="utf-8")
            self.assertGreater(len(content), 100, f"SQL file is too short: {filename}")
            
            # Check standard BigQuery SQL keywords
            content_upper = content.upper()
            self.assertIn("SELECT", content_upper, f"Missing SELECT in {filename}")
            self.assertIn("FROM", content_upper, f"Missing FROM in {filename}")
            
            # Specific assertions for each query logic
            if filename == "01_eda_overview.sql":
                self.assertIn("TRAFFIC_MEDIUM", content_upper)
                self.assertIn("COUNT(DISTINCT", content_upper)
            elif filename == "02_funnel_analysis.sql":
                self.assertIn("VIEW_ITEM", content_upper)
                self.assertIn("ADD_TO_CART", content_upper)
                self.assertIn("BEGIN_CHECKOUT", content_upper)
                self.assertIn("PURCHASE", content_upper)
            elif filename == "03_rfm_features.sql":
                self.assertIn("USER_PSEUDO_ID", content_upper)
                self.assertIn("TOTAL_SESSIONS", content_upper)
                self.assertIn("MONETARY_VALUE", content_upper)
                self.assertIn("RECENCY_DAYS", content_upper)
            elif filename == "04_market_basket.sql":
                self.assertIn("UNNEST(P.ITEMS)", content_upper)
                self.assertIn("TRANSACTION_ID", content_upper)
                self.assertIn("HAVING COUNT(DISTINCT ITEM_NAME) >= 2", content_upper)
        print("  ✓ [PASS] SQL Files Integrity & BigQuery syntax verified.")

    # ----------------------------------------------------------------------------------
    # 2. BIGQUERY SERVICE & CACHING TESTS
    # ----------------------------------------------------------------------------------
    def test_02_bigquery_service_caching(self):
        """Test BigQuery data caching mechanism and dataframe outputs."""
        datasets = ["eda_overview", "funnel_analysis", "rfm_features", "market_basket"]
        for dataset_name in datasets:
            df = self.bq_service.query_to_dataframe("SELECT 1", cache_name=dataset_name, use_cache=True)
            self.assertIsInstance(df, pd.DataFrame, f"Expected DataFrame for {dataset_name}")
            self.assertFalse(df.empty, f"DataFrame is empty for {dataset_name}")
            self.assertGreater(len(df), 0, f"No rows returned for {dataset_name}")
            
            # Check cache file creation
            cache_file = CACHE_DIR / f"{dataset_name}.parquet"
            self.assertTrue(cache_file.exists(), f"Parquet cache file missing: {cache_file}")
            
        # Verify RFM Data columns
        df_rfm = self.bq_service.query_to_dataframe("SELECT 1", cache_name="rfm_features")
        for col in RFM_FEATURES:
            self.assertIn(col, df_rfm.columns, f"Missing feature column {col} in RFM data")
        self.assertIn("user_pseudo_id", df_rfm.columns)
        print(f"  ✓ [PASS] BigQuery Service & Parquet Caching ({len(df_rfm):,} RFM rows) verified.")

    # ----------------------------------------------------------------------------------
    # 3. PREPROCESSING PIPELINE TESTS
    # ----------------------------------------------------------------------------------
    def test_03_data_processor_pipeline(self):
        """Test IQR clipping, Log1p transform, and StandardScaler."""
        df_rfm = self.bq_service.query_to_dataframe("SELECT 1", cache_name="rfm_features")
        X_scaled, df_transformed, df_clean = self.processor.fit_transform(df_rfm)
        
        # 1. Check shapes
        self.assertEqual(X_scaled.shape[0], len(df_rfm))
        self.assertEqual(X_scaled.shape[1], len(RFM_FEATURES))
        self.assertEqual(len(df_transformed), len(df_rfm))
        self.assertEqual(len(df_clean), len(df_rfm))
        
        # 2. Check no NaN or Infinite values
        self.assertFalse(np.isnan(X_scaled).any(), "Scaled matrix contains NaN values")
        self.assertFalse(np.isinf(X_scaled).any(), "Scaled matrix contains Inf values")
        
        # 3. Check statistical normalization: Mean ≈ 0, Std ≈ 1
        means = np.mean(X_scaled, axis=0)
        stds = np.std(X_scaled, axis=0)
        np.testing.assert_allclose(means, np.zeros_like(means), atol=1e-2, err_msg="Feature means not zero")
        np.testing.assert_allclose(stds, np.ones_like(stds), atol=1e-2, err_msg="Feature stds not one")
        print(f"  ✓ [PASS] Data Processor (Winsorization + Log1p + StandardScaler) verified.")

    # ----------------------------------------------------------------------------------
    # 4. MACHINE LEARNING CLUSTERING & PERSONAS TESTS
    # ----------------------------------------------------------------------------------
    def test_04_clustering_and_persona_profiling(self):
        """Test K-Means evaluation, fitting, PCA 2D/3D projections, and dynamic persona profiling."""
        df_rfm = self.bq_service.query_to_dataframe("SELECT 1", cache_name="rfm_features")
        X_scaled, df_trans, df_clean = self.processor.fit_transform(df_rfm)
        
        # 1. K evaluation (Elbow & Silhouette)
        eval_res = self.cluster_model.evaluate_k_range(X_scaled, k_min=2, k_max=8)
        self.assertEqual(len(eval_res["k_values"]), 7)
        self.assertEqual(len(eval_res["inertias"]), 7)
        self.assertEqual(len(eval_res["silhouette_scores"]), 7)
        
        # 2. Fit K-Means K=4
        df_segmented, summary = self.cluster_model.fit_predict(X_scaled, df_clean, n_clusters=4)
        self.assertEqual(summary["n_clusters"], 4)
        self.assertGreater(summary["overall_silhouette_score"], 0.30)
        
        # 3. PCA Projections
        self.assertIn("pca_2d_x", df_segmented.columns)
        self.assertIn("pca_2d_y", df_segmented.columns)
        self.assertIn("pca_3d_z", df_segmented.columns)
        explained_2d = sum(summary["pca_2d_explained_variance_ratio"])
        explained_3d = sum(summary["pca_3d_explained_variance_ratio"])
        self.assertGreater(explained_2d, 0.70, "PCA 2D explained variance < 70%")
        self.assertGreater(explained_3d, 0.85, "PCA 3D explained variance < 85%")
        
        # 4. Persona Profiling
        df_enriched, df_persona_summary = self.cluster_model.profile_personas(df_segmented)
        self.assertIn("persona_name", df_enriched.columns)
        self.assertIn("persona_color", df_enriched.columns)
        
        unique_personas = df_enriched["persona_name"].unique()
        self.assertEqual(len(unique_personas), 4, "Expected exactly 4 distinct personas")
        self.assertEqual(len(df_persona_summary), 4, "Summary table must have 4 rows")
        
        # Verify VIP cluster has highest average monetary value
        vip_df = df_enriched[df_enriched["persona_name"] == "Loyal Champions (VIPs)"]
        at_risk_df = df_enriched[df_enriched["persona_name"] == "At-Risk / Inactive Customers"]
        self.assertGreater(vip_df["monetary_value"].mean(), at_risk_df["monetary_value"].mean())
        print(f"  ✓ [PASS] ML Clustering (Silhouette = {summary['overall_silhouette_score']:.4f}, PCA 3D = {explained_3d*100:.1f}%) & Persona Profiling verified.")

    # ----------------------------------------------------------------------------------
    # 5. MARKET BASKET & ASSOCIATION RULES TESTS
    # ----------------------------------------------------------------------------------
    def test_05_market_basket_analysis(self):
        """Test One-Hot Matrix building, Apriori algorithm, and Association Rules (Support, Confidence, Lift)."""
        df_tx = self.bq_service.query_to_dataframe("SELECT 1", cache_name="market_basket")
        basket_matrix, total_orders = self.mba_analyzer.build_basket_matrix(df_tx, min_item_frequency=2)
        
        self.assertGreater(total_orders, 0)
        self.assertIsInstance(basket_matrix, pd.DataFrame)
        
        # Values in One-Hot must be binary 0 or 1
        unique_vals = np.unique(basket_matrix.values)
        for val in unique_vals:
            self.assertIn(val, [0, 1])
            
        freq_itemsets, rules = self.mba_analyzer.run_apriori_and_rules(basket_matrix)
        self.assertFalse(freq_itemsets.empty, "No frequent itemsets found")
        self.assertFalse(rules.empty, "No association rules generated")
        
        # Verify rule metrics
        self.assertTrue((rules["support"] >= self.mba_analyzer.min_support).all())
        self.assertTrue((rules["confidence"] >= self.mba_analyzer.min_confidence).all())
        self.assertTrue((rules["lift"] >= self.mba_analyzer.min_lift).all())
        
        df_recs = self.mba_analyzer.get_cross_selling_recommendations(top_n=5)
        self.assertGreaterEqual(len(df_recs), 1)
        self.assertIn("Sản phẩm Đã mua (A)", df_recs.columns)
        self.assertIn("Sản phẩm Gợi ý Mua kèm (B)", df_recs.columns)
        self.assertIn("Hệ số Tương quan (Lift)", df_recs.columns)
        print(f"  ✓ [PASS] Market Basket Analysis ({len(freq_itemsets)} itemsets, {len(rules)} rules, Lift > 1.0) verified.")

    # ----------------------------------------------------------------------------------
    # 6. FASTAPI BACKEND REST API ENDPOINTS TESTS
    # ----------------------------------------------------------------------------------
    def test_06_fastapi_rest_endpoints(self):
        """Test that all FastAPI backend endpoints return HTTP 200 and valid JSON data."""
        # Endpoint 1: Health
        res_health = self.client.get("/api/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["status"], "ok")
        
        # Endpoint 2: Overview
        res_overview = self.client.get("/api/overview")
        self.assertEqual(res_overview.status_code, 200)
        data_overview = res_overview.json()
        self.assertIn("kpis", data_overview)
        self.assertIn("total_users", data_overview["kpis"])
        self.assertIn("traffic_channels", data_overview)
        
        # Endpoint 3: Funnel
        res_funnel = self.client.get("/api/funnel?device=all")
        self.assertEqual(res_funnel.status_code, 200)
        data_funnel = res_funnel.json()
        self.assertEqual(len(data_funnel["steps"]), 4)
        self.assertIn("overall_conversion_rate_pct", data_funnel["metrics"])
        self.assertIn("cart_abandonment_rate_pct", data_funnel["metrics"])
        
        # Endpoint 4: Personas
        res_personas = self.client.get("/api/personas")
        self.assertEqual(res_personas.status_code, 200)
        data_personas = res_personas.json()
        self.assertEqual(len(data_personas["personas_summary"]), 4)
        self.assertIn("pca_scatter_points", data_personas)
        self.assertGreater(len(data_personas["pca_scatter_points"]), 0)
        
        # Endpoint 5: Sample Users & Single User Lookup
        res_users = self.client.get("/api/users/sample?limit=10")
        self.assertEqual(res_users.status_code, 200)
        users = res_users.json()
        self.assertEqual(len(users), 10)
        sample_user_id = users[0]["user_pseudo_id"]
        
        res_single_user = self.client.get(f"/api/user/{sample_user_id}")
        self.assertEqual(res_single_user.status_code, 200)
        self.assertEqual(res_single_user.json()["user_pseudo_id"], sample_user_id)
        
        # Endpoint 6: Market Basket
        res_basket = self.client.get("/api/basket")
        self.assertEqual(res_basket.status_code, 200)
        data_basket = res_basket.json()
        self.assertIn("cross_selling_recommendations", data_basket)
        self.assertIn("top_rules", data_basket)
        
        # Endpoint 7: Insights
        res_insights = self.client.get("/api/insights")
        self.assertEqual(res_insights.status_code, 200)
        data_insights = res_insights.json()
        self.assertIn("cro_strategies", data_insights)
        self.assertIn("persona_strategies", data_insights)
        print("  ✓ [PASS] FastAPI Backend REST API Endpoints (100% 200 OK) verified.")

    # ----------------------------------------------------------------------------------
    # 7. JUPYTER NOTEBOOKS SYNTAX & CODE CELLS INTEGRITY
    # ----------------------------------------------------------------------------------
    def test_07_jupyter_notebooks_code_integrity(self):
        """Test that all Jupyter Notebook files are valid JSON and all Python code cells parse without syntax error."""
        notebook_files = [
            BASE_DIR / "DoAn-BigData-GA4-SourceCode-Final.ipynb",
            NOTEBOOKS_DIR / "01_eda_and_funnel.ipynb",
            NOTEBOOKS_DIR / "02_rfm_kmeans_clustering.ipynb"
        ]
        
        for nb_path in notebook_files:
            self.assertTrue(nb_path.exists(), f"Notebook not found: {nb_path.name}")
            with open(nb_path, "r", encoding="utf-8") as f:
                nb_json = json.load(f)
                
            self.assertIn("cells", nb_json, f"Invalid notebook format in {nb_path.name}")
            code_cell_count = 0
            
            for idx, cell in enumerate(nb_json["cells"]):
                if cell.get("cell_type") == "code":
                    code_cell_count += 1
                    source_code = "".join(cell.get("source", []))
                    
                    # Filter out IPython magic commands (! or %) for AST validation
                    clean_lines = []
                    for line in source_code.splitlines():
                        if not line.strip().startswith("!") and not line.strip().startswith("%"):
                            clean_lines.append(line)
                    code_to_parse = "\n".join(clean_lines)
                    
                    try:
                        ast.parse(code_to_parse)
                    except SyntaxError as e:
                        self.fail(f"Syntax error in {nb_path.name} cell {idx}: {e}")
                        
            self.assertGreater(code_cell_count, 0, f"No code cells found in {nb_path.name}")
        print("  ✓ [PASS] Jupyter Notebooks Code Integrity & AST Syntax verified.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
