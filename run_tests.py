"""
Automated Test Runner for Big Data GA4 Analytics & Customer Intelligence Platform.
Executes complete test suite with high-verbosity logging and summary reports.
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(BASE_DIR / "tests"), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n" + "="*80)
        print("🎉 ALL END-TO-END PIPELINE TESTS PASSED SUCCESSFULLY! (EXIT CODE 0)")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ SOME TESTS FAILED! PLEASE CHECK THE LOGS ABOVE.")
        print("="*80)
        sys.exit(1)
