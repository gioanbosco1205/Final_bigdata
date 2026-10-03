"""Run labeled synthetic fixtures in a real Jupyter kernel.

Outputs under report_assets/notebook_review_2026-10-03/fixture are test evidence,
not an offline reproduction of real GA4/BigQuery results.
"""
import sys
from verify_master_notebook import main

if __name__ == '__main__':
    sys.argv = [sys.argv[0], '--mode', 'fixture', *sys.argv[1:]]
    raise SystemExit(main())
