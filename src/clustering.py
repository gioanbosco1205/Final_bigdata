"""
Customer Clustering Module: K-Means, Elbow Method, Silhouette Score Analysis,
and PCA 2D/3D Dimensionality Reduction for Visualization.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import PCA

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import RFM_FEATURES, PERSONA_LABELS, PERSONA_COLORS


class CustomerClusterModel:
    """
    Implements Unsupervised Customer Segmentation Pipeline:
    1. Elbow Method (Inertia) & Silhouette Score Optimization (K=2..8).
    2. K-Means Clustering on Full Multi-dimensional Feature Space.
    3. PCA 2D & 3D Projections for Interactive Visualizations.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.optimal_k = 4
        self.kmeans_model: KMeans = None
        self.pca_2d: PCA = None
        self.pca_3d: PCA = None
        self.evaluation_results: Dict[str, Any] = {}

    def evaluate_k_range(
        self, 
        X_scaled: np.ndarray, 
        k_min: int = 2, 
        k_max: int = 8
    ) -> Dict[str, Any]:
        """
        Runs Elbow Method (Inertia/WCSS) and Silhouette Score analysis for K in [k_min, k_max].
        Returns dictionary containing evaluation metrics to justify optimal K mathematically.
        """
        k_values = list(range(k_min, k_max + 1))
        inertias = []
        silhouette_scores_list = []

        print(f"📊 Evaluating K-Means across range K={k_min}..{k_max}...")
        for k in k_values:
            km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=self.random_state)
            cluster_labels = km.fit_predict(X_scaled)
            
            inertia = km.inertia_
            sil_score = silhouette_score(X_scaled, cluster_labels)
            
            inertias.append(float(inertia))
            silhouette_scores_list.append(float(sil_score))
            print(f"  • K={k}: Inertia = {inertia:10.2f} | Silhouette Score = {sil_score:.4f}")

        self.evaluation_results = {
            "k_values": k_values,
            "inertias": inertias,
            "silhouette_scores": silhouette_scores_list,
            "best_k_by_silhouette": k_values[int(np.argmax(silhouette_scores_list))]
        }
        return self.evaluation_results

    def fit_predict(
        self, 
        X_scaled: np.ndarray, 
        df_clean: pd.DataFrame, 
        n_clusters: int = 4
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fits final K-Means model on full feature space (9 features),
        computes PCA 2D & 3D projections strictly for visualization,
        and attaches cluster labels to dataframe.
        """
        self.optimal_k = n_clusters
        
        # 1. Fit K-Means on full scaled features
        self.kmeans_model = KMeans(
            n_clusters=n_clusters, 
            init="k-means++", 
            n_init=15, 
            random_state=self.random_state
        )
        cluster_labels = self.kmeans_model.fit_predict(X_scaled)
        overall_sil = silhouette_score(X_scaled, cluster_labels)

        # 2. Compute PCA Projections (2D and 3D) strictly for visualization
        self.pca_2d = PCA(n_components=2, random_state=self.random_state)
        pca_2d_coords = self.pca_2d.fit_transform(X_scaled)
        
        self.pca_3d = PCA(n_components=3, random_state=self.random_state)
        pca_3d_coords = self.pca_3d.fit_transform(X_scaled)

        # 3. Create enriched dataframe
        df_result = df_clean.copy()
        df_result["cluster_id"] = cluster_labels
        df_result["pca_2d_x"] = pca_2d_coords[:, 0].round(4)
        df_result["pca_2d_y"] = pca_2d_coords[:, 1].round(4)
        df_result["pca_3d_x"] = pca_3d_coords[:, 0].round(4)
        df_result["pca_3d_y"] = pca_3d_coords[:, 1].round(4)
        df_result["pca_3d_z"] = pca_3d_coords[:, 2].round(4)

        # 4. Check Cluster Size Distribution
        cluster_counts = df_result["cluster_id"].value_counts().to_dict()
        cluster_percents = {k: round(v / len(df_result) * 100, 2) for k, v in cluster_counts.items()}

        summary = {
            "n_clusters": n_clusters,
            "overall_silhouette_score": round(overall_sil, 4),
            "pca_2d_explained_variance_ratio": self.pca_2d.explained_variance_ratio_.tolist(),
            "pca_3d_explained_variance_ratio": self.pca_3d.explained_variance_ratio_.tolist(),
            "cluster_sizes": cluster_counts,
            "cluster_percentages": cluster_percents
        }

        self._validate_clusters(summary, len(df_clean))
        return df_result, summary

    def profile_personas(self, df_segmented: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Dynamically profiles and maps Customer Personas to Clusters based on 
        multi-dimensional feature statistics (RFM + 6 Behavioral Metrics), 
        rather than relying on arbitrary cluster_id index numbers.
        
        Returns:
            - df_enriched (pd.DataFrame): Dataframe with assigned 'persona_name' and color codes.
            - df_persona_summary (pd.DataFrame): Comprehensive academic profile comparison table.
        """
        # 1. Compute Mean and Median across all features per cluster
        agg_funcs = ["mean", "median"]
        feature_list = RFM_FEATURES
        
        cluster_stats = df_segmented.groupby("cluster_id")[feature_list].agg(["mean", "median"])
        cluster_means = df_segmented.groupby("cluster_id")[feature_list].mean()
        
        # 2. Dynamic Rule-based Persona Matching:
        # We score each cluster based on multi-dimensional traits:
        # - VIPs: Highest Monetary, High Frequency, Low Recency, High Engagement
        # - At-Risk: Highest Recency, Lowest Frequency, Lowest Engagement
        # - Cart Abandoners: High Cart Ratio / Items Added, but Low/Zero Purchases
        # - Potential Loyalists: Balanced High Sessions, Moderate Monetary, Low Recency
        
        clusters = list(cluster_means.index)
        assigned_personas = {}
        unassigned_clusters = set(clusters)
        
        # Step A: Identify Loyal Champions (VIPs) -> Cluster with highest monetary value & purchases
        vip_cluster = cluster_means["monetary_value"].idxmax()
        assigned_personas[vip_cluster] = "Loyal Champions (VIPs)"
        unassigned_clusters.remove(vip_cluster)
        
        # Step B: Identify At-Risk / Inactive -> Remaining cluster with highest recency_days (longest inactivity)
        rem_means = cluster_means.loc[list(unassigned_clusters)]
        at_risk_cluster = rem_means["recency_days"].idxmax()
        assigned_personas[at_risk_cluster] = "At-Risk / Inactive Customers"
        unassigned_clusters.remove(at_risk_cluster)
        
        # Step C: Distinguish between Cart Abandoners and Potential Loyalists
        rem_clusters = list(unassigned_clusters)
        if len(rem_clusters) == 2:
            c1, c2 = rem_clusters[0], rem_clusters[1]
            # Compare cart_to_view_ratio and monetary/purchases
            if cluster_means.loc[c1, "cart_to_view_ratio"] > cluster_means.loc[c2, "cart_to_view_ratio"] and cluster_means.loc[c1, "monetary_value"] <= cluster_means.loc[c2, "monetary_value"]:
                assigned_personas[c1] = "Cart Abandoners / Window Shoppers"
                assigned_personas[c2] = "Potential Loyalists"
            else:
                assigned_personas[c2] = "Cart Abandoners / Window Shoppers"
                assigned_personas[c1] = "Potential Loyalists"
        else:
            for c in rem_clusters:
                assigned_personas[c] = f"Segment {c}"

        # 3. Attach Persona Names & Colors to Dataframe
        df_enriched = df_segmented.copy()
        df_enriched["persona_name"] = df_enriched["cluster_id"].map(assigned_personas)
        df_enriched["persona_color"] = df_enriched["persona_name"].map(PERSONA_COLORS)

        # 4. Generate Final Professional Persona Summary Table
        summary_rows = []
        total_users = len(df_enriched)
        
        behavioral_highlights = {
            "Loyal Champions (VIPs)": "Chi tiêu lớn nhất, tương tác lâu, mua sắm định kỳ thường xuyên",
            "Potential Loyalists": "Tương tác đều đặn, xem nhiều sản phẩm, chi tiêu ở mức khá",
            "Cart Abandoners / Window Shoppers": "Tỷ lệ thêm vào giỏ cao nhưng tỷ lệ hoàn tất đơn hàng rất thấp",
            "At-Risk / Inactive Customers": "Đã lâu không quay lại website, tần suất và giá trị rất thấp"
        }
        
        for cid in sorted(clusters):
            p_name = assigned_personas[cid]
            c_df = df_enriched[df_enriched["cluster_id"] == cid]
            cnt = len(c_df)
            pct = round(cnt / total_users * 100, 2)
            
            summary_rows.append({
                "Cluster ID": cid,
                "Chân dung Khách hàng (Persona)": p_name,
                "Số lượng Users": f"{cnt:,} ({pct}%)",
                "Recency TB (ngày)": round(c_df["recency_days"].mean(), 1),
                "Sessions TB": round(c_df["total_sessions"].mean(), 1),
                "Doanh thu TB ($)": round(c_df["monetary_value"].mean(), 2),
                "Thời gian Tương tác TB (s)": round(c_df["total_engagement_sec"].mean(), 1),
                "Số SP Xem TB": round(c_df["items_viewed_count"].mean(), 1),
                "Số SP Thêm Giỏ TB": round(c_df["items_added_to_cart_count"].mean(), 1),
                "Tỷ lệ Giỏ/Xem": round(c_df["cart_to_view_ratio"].mean(), 3),
                "Đơn hàng TB": round(c_df["purchase_count"].mean(), 2),
                "Hành vi Nổi bật": behavioral_highlights.get(p_name, "Hành vi đặc thù theo cụm")
            })
            
        df_persona_summary = pd.DataFrame(summary_rows)
        return df_enriched, df_persona_summary

    def _validate_clusters(self, summary: Dict[str, Any], total_rows: int):
        """Validates that clusters are balanced and non-trivial."""
        for cid, count in summary["cluster_sizes"].items():
            pct = summary["cluster_percentages"][cid]
            assert count > 0, f"Cluster {cid} is empty!"
            assert pct >= 2.0, f"Cluster {cid} is too small (<2% of dataset)!"
        
        print("\n✓ K-Means Clustering Validation Passed:")
        print(f"  • Overall Silhouette Score: {summary['overall_silhouette_score']}")
        print(f"  • PCA 2D Explained Variance: {sum(summary['pca_2d_explained_variance_ratio'])*100:.2f}%")
        print(f"  • PCA 3D Explained Variance: {sum(summary['pca_3d_explained_variance_ratio'])*100:.2f}%")
        print("  • Cluster Distribution:")
        for cid in sorted(summary["cluster_sizes"].keys()):
            cnt = summary["cluster_sizes"][cid]
            pct = summary["cluster_percentages"][cid]
            print(f"    - Cluster {cid}: {cnt:,} users ({pct}%)")


if __name__ == "__main__":
    from src.bq_client import BigQueryService
    from src.data_processor import CustomerDataProcessor
    
    print("Testing CustomerClusterModel pipeline with Dynamic Persona Profiling...")
    bq = BigQueryService()
    df_rfm = bq.query_to_dataframe("SELECT 1", cache_name="rfm_features")
    
    processor = CustomerDataProcessor()
    X_scaled, df_trans, df_clean = processor.fit_transform(df_rfm)
    
    model = CustomerClusterModel(random_state=42)
    model.evaluate_k_range(X_scaled, k_min=2, k_max=8)
    
    df_segmented, summary = model.fit_predict(X_scaled, df_clean, n_clusters=4)
    df_enriched, df_persona_table = model.profile_personas(df_segmented)
    
    print("\n" + "="*80)
    print("=== BẢNG TỔNG HỢP CHÂN DUNG KHÁCH HÀNG (PERSONA PROFILING TABLE) ===")
    print("="*80)
    print(df_persona_table.to_string(index=False))

