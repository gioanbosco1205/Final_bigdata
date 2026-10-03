"""
Script to extract 100% real data from Google Cloud BigQuery public dataset
`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
using the 4 SQL query files in the `sql/` directory.

Usage:
  python extract_real_bigquery_data.py [--project-id YOUR_GCP_PROJECT]
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd

# Base directories
BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"

DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SQL_FILES = {
    "eda_overview": "01_eda_overview.sql",
    "funnel_analysis": "02_funnel_analysis.sql",
    "rfm_features": "03_rfm_features.sql",
    "market_basket": "04_market_basket.sql"
}


def run_extraction(project_id: str = None):
    print("=" * 70)
    print("🚀 GOOGLE CLOUD BIGQUERY REAL DATA EXTRACTION")
    print("Dataset: bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*")
    print("=" * 70)

    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id) if project_id else bigquery.Client()
        print(f"✓ Đã kết nối BigQuery Client thành công (GCP Project: {client.project})")
    except Exception as e:
        print(f"❌ Lỗi kết nối BigQuery: {e}")
        print("\nHướng dẫn khắc phục:")
        print("1. Nếu chạy trên máy cá nhân: Chạy lệnh `gcloud auth application-default login`")
        print("2. Hoặc thiết lập biến môi trường `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`")
        print("3. Hoặc mở file `extract_real_data_from_bigquery_colab.ipynb` trên Google Colab để chạy trực tiếp 1-click.")
        return False

    for name, sql_filename in SQL_FILES.items():
        sql_path = SQL_DIR / sql_filename
        if not sql_path.exists():
            print(f"⚠️ Không tìm thấy file: {sql_path}")
            continue

        print(f"\n📡 Đang thực thi truy vấn [{sql_filename}] trên BigQuery Cloud...")
        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()

        try:
            job = client.query(query)
            df = job.to_dataframe()
            
            csv_path = DATA_DIR / f"{name}.csv"
            parquet_path = CACHE_DIR / f"{name}.parquet"
            
            df.to_csv(csv_path, index=False)
            df.to_parquet(parquet_path, index=False)
            
            print(f"✓ Hoàn tất trích xuất [{name}]: {len(df):,} dòng, {len(df.columns)} cột.")
            print(f"  -> Đã lưu: {csv_path} & {parquet_path}")
        except Exception as query_err:
            print(f"❌ Lỗi truy vấn {name}: {query_err}")

    print("\n" + "=" * 70)
    print("🎉 TOÀN BỘ DỮ LIỆU THẬT ĐÃ ĐƯỢC CẬP NHẬT VÀO THƯ MỤC data/")
    print("=" * 70)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract real GA4 data from BigQuery.")
    parser.add_argument("--project-id", type=str, default=None, help="GCP Project ID to bill queries to")
    args = parser.parse_args()

    run_extraction(args.project_id)
