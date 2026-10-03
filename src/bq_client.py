"""
BigQuery Service module for managing remote Google Cloud query execution,
and reading authentic GA4 datasets.
"""

import os
import sys
from pathlib import Path
from typing import Optional
import pandas as pd

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import (
    DATA_DIR,
    CACHE_DIR,
    SQL_DIR,
    GCP_PROJECT_ID,
    GCP_CREDENTIALS_PATH,
    GA4_EVENTS_TABLE
)


class BigQueryService:
    """
    Handles BigQuery connectivity, query execution with pushdown computation,
    and reading authentic GA4 datasets.
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
            print("✓ Kết nối Google Cloud BigQuery thành công.")
        except Exception as e:
            # Client not configured or offline mode
            self.client = None
            print(f"ℹ️ Chế độ Offline / Đọc dữ liệu BigQuery đã trích xuất.")

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
        Executes query on BigQuery or returns DataFrame from authentic extracted storage.
        """
        cache_parquet = CACHE_DIR / f"{cache_name}.parquet" if cache_name else None
        data_csv = DATA_DIR / f"{cache_name}.csv" if cache_name else None
        data_parquet = DATA_DIR / f"{cache_name}.parquet" if cache_name else None

        # 1. Check local cache or data directory if caching enabled
        if use_cache and not force_refresh:
            if cache_parquet and cache_parquet.exists():
                print(f"⚡ Đang nạp dữ liệu BigQuery từ cache: {cache_parquet.name}")
                return pd.read_parquet(cache_parquet)
            if data_parquet and data_parquet.exists():
                print(f"⚡ Đang nạp dữ liệu BigQuery từ: {data_parquet.name}")
                return pd.read_parquet(data_parquet)
            if data_csv and data_csv.exists():
                print(f"⚡ Đang nạp dữ liệu BigQuery từ file: {data_csv.name}")
                return pd.read_csv(data_csv)

        # 2. If live BigQuery client is available, execute on Google Cloud
        if self.client is not None:
            try:
                print(f"🚀 Đang thực thi truy vấn phân tán (Pushdown Computing) trên Google BigQuery...")
                query_job = self.client.query(query)
                df = query_job.to_dataframe()
                if cache_parquet:
                    df.to_parquet(cache_parquet, index=False)
                if data_csv:
                    df.to_csv(data_csv, index=False)
                print(f"💾 Đã lưu kết quả truy vấn BigQuery ({len(df):,} dòng)")
                return df
            except Exception as e:
                print(f"⚠️ Không thể thực thi trên BigQuery Cloud: {e}")

        # 3. Fallback to existing extracted CSV/Parquet files
        if data_csv and data_csv.exists():
            print(f"⚡ Nạp dữ liệu từ {data_csv.name}")
            return pd.read_csv(data_csv)
        if cache_parquet and cache_parquet.exists():
            return pd.read_parquet(cache_parquet)

        raise FileNotFoundError(
            f"Không tìm thấy dữ liệu BigQuery cho '{cache_name}'. "
            f"Vui lòng chạy script trích xuất dữ liệu từ BigQuery hoặc cung cấp file {cache_name}.csv trong thư mục data/."
        )
