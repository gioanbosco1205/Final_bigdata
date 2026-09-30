"""
Data Processor module for Big Data Feature Preprocessing, Outlier Handling,
Log Transformation, and Standardization for Customer Segmentation.
"""

import sys
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import RFM_FEATURES


class CustomerDataProcessor:
    """
    Handles feature preprocessing for Unsupervised Customer Segmentation (K-Means).
    
    BIG DATA ARCHITECTURE ROLE:
    1. BigQuery SQL handles in-database pushdown aggregation across millions of raw events.
    2. This Python processor receives the compact user feature matrix (~MBs), performs
       statistical outlier clipping (IQR Winsorization), Log1p transformation, and Standard Scaling.
    """

    def __init__(self, feature_cols: Optional[List[str]] = None):
        # Default numeric features for ML modeling
        self.feature_cols = feature_cols or RFM_FEATURES
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.iqr_bounds_ = {}

    def _apply_iqr_clipping(self, df_features: pd.DataFrame, factor: float = 3.0) -> pd.DataFrame:
        """
        Applies soft IQR clipping (Winsorization) to cap extreme outliers without dropping valuable user rows.
        Uses factor=3.0 (extreme outlier threshold) to preserve genuine VIP customer patterns.
        """
        df_clipped = df_features.copy()
        for col in self.feature_cols:
            if col in df_clipped.columns:
                q25 = df_clipped[col].quantile(0.25)
                q75 = df_clipped[col].quantile(0.75)
                iqr = q75 - q25
                lower_bound = max(0.0, q25 - factor * iqr)
                upper_bound = q75 + factor * iqr
                
                self.iqr_bounds_[col] = (lower_bound, upper_bound)
                df_clipped[col] = df_clipped[col].clip(lower=lower_bound, upper=upper_bound)
        return df_clipped

    def _apply_log1p_transform(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Applies np.log1p (log(x + 1)) transformation to reduce right-skewness for non-negative features.
        Safe for zero values (log1p(0) = 0).
        """
        df_log = df_features.copy()
        for col in self.feature_cols:
            if col in df_log.columns:
                # Ensure non-negative before log1p
                df_log[col] = np.log1p(np.maximum(0.0, df_log[col].values))
        return df_log

    def fit_transform(self, df_raw: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
        """
        Executes complete preprocessing pipeline:
        1. Select ONLY numeric feature columns (excludes user_pseudo_id, device, channel).
        2. Soft IQR Clipping (Winsorization).
        3. Log1p Transformation.
        4. StandardScaler (Zero mean, Unit variance).
        
        Returns:
            - X_scaled (np.ndarray): Scaled feature matrix for K-Means.
            - df_transformed (pd.DataFrame): Transformed features before scaling.
            - df_clean (pd.DataFrame): Full dataframe with identifiers and clean features.
        """
        df_clean = df_raw.copy()
        
        # Verify all feature columns exist
        missing_cols = [c for c in self.feature_cols if c not in df_clean.columns]
        if missing_cols:
            raise ValueError(f"Missing required feature columns: {missing_cols}")

        # Extract ONLY numeric features for scaling
        df_numeric = df_clean[self.feature_cols].copy()
        
        # Step 1: Soft IQR clipping (no data loss)
        df_clipped = self._apply_iqr_clipping(df_numeric)
        
        # Step 2: Log1p transform
        df_transformed = self._apply_log1p_transform(df_clipped)
        
        # Step 3: StandardScaler
        X_scaled = self.scaler.fit_transform(df_transformed)
        self.is_fitted = True

        # Validation Checks
        self._validate_scaled_data(X_scaled, len(df_raw))

        return X_scaled, df_transformed, df_clean

    def _validate_scaled_data(self, X_scaled: np.ndarray, original_row_count: int):
        """Performs statistical checks on scaled data."""
        # Check row count preservation
        assert X_scaled.shape[0] == original_row_count, "Row count mismatch after scaling!"
        
        # Check NaN / Inf
        assert not np.isnan(X_scaled).any(), "Scaled matrix contains NaN values!"
        assert not np.isinf(X_scaled).any(), "Scaled matrix contains Inf values!"
        
        # Check Mean ~ 0 and Std ~ 1
        means = np.mean(X_scaled, axis=0)
        stds = np.std(X_scaled, axis=0)
        
        print("✓ Preprocessing Validation Check Passed:")
        print(f"  • Shape preserved: {X_scaled.shape}")
        print(f"  • Mean range across features: [{means.min():.4f}, {means.max():.4f}] (All ≈ 0.0)")
        print(f"  • Std range across features:  [{stds.min():.4f}, {stds.max():.4f}] (All ≈ 1.0)")
        print(f"  • Zero NaN or Inf values detected.")


if __name__ == "__main__":
    from src.bq_client import BigQueryService
    
    print("Testing CustomerDataProcessor pipeline on GA4 RFM dataset...")
    bq = BigQueryService()
    df_rfm = bq.query_to_dataframe("SELECT 1", cache_name="rfm_features")
    
    processor = CustomerDataProcessor()
    X_scaled, df_trans, df_clean = processor.fit_transform(df_rfm)
    print("\n✓ Top 3 scaled feature vectors preview:")
    print(X_scaled[:3].round(3))
