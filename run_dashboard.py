"""
Dashboard Launcher Script.
Starts FastAPI backend server serving both REST API and React Frontend on http://localhost:8000
"""

import sys
import os
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.api import app

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 ĐỒ ÁN BIG DATA: GA4 CUSTOMER ANALYTICS & INTELLIGENCE PLATFORM")
    print("="*70)
    print("✨ Frontend UI: React + TypeScript + TailwindCSS + Recharts")
    print("⚡ Backend API: FastAPI + Google BigQuery SQL + Python ML")
    print("\n👉 Mở trình duyệt và truy cập: http://localhost:8000")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
