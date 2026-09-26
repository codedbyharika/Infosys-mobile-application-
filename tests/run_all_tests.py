"""
EcoAir Intelligence — Comprehensive Executive Test Runner
Executes the entire verification suite:
  1. ML & Geostatistical Engines (PyTorch/NumPy Recurrent Models, Kriging, IDW, Route Exposure)
  2. REST API Integration & Contracts (All FastAPI endpoints, schemas, static delivery)
  3. Frontend Static Integrity & Design Tokens (DOM contracts, API alignment, CSS tokens)
"""

import os
import sys
import time
import unittest

# Ensure repo root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from tests.test_ml_engine import TestMLEngine
from tests.test_api_endpoints import TestAPIEndpoints
from tests.test_frontend_integrity import TestFrontendIntegrity
from tests.test_mobile_layout import TestMobileLayoutIntegrity


def run_full_suite():
    print("\n" + "=" * 78)
    print("      ECOAIR INTELLIGENCE (AIRSENSE) — EXECUTIVE QA VERIFICATION SUITE")
    print("=" * 78)
    print(f"  Target Environment: {sys.platform} | Python {sys.version.split()[0]}")
    print(f"  Project Root:       {BASE_DIR}")
    print("=" * 78 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suites = [
        ("1. ML & Geostatistical Engines Suite", loader.loadTestsFromTestCase(TestMLEngine)),
        ("2. REST API Microservice Suite", loader.loadTestsFromTestCase(TestAPIEndpoints)),
        ("3. Frontend Integrity & Design System Suite", loader.loadTestsFromTestCase(TestFrontendIntegrity)),
        ("4. Mobile Layout & Responsive PWA Suite", loader.loadTestsFromTestCase(TestMobileLayoutIntegrity)),
    ]

    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    start_time = time.time()

    for name, s in suites:
        count = s.countTestCases()
        total_tests += count
        print(f"==> Running: {name} ({count} test cases)...")
        runner = unittest.TextTestRunner(verbosity=1)
        res = runner.run(s)

        passed = count - len(res.failures) - len(res.errors)
        total_passed += passed
        total_failed += len(res.failures)
        total_errors += len(res.errors)

        status_tag = "[PASS]" if res.wasSuccessful() else "[FAIL]"
        print(f"    {status_tag} Completed {passed}/{count} tests passed in this suite.\n")

    elapsed = round(time.time() - start_time, 2)

    print("=" * 78)
    print("                          FINAL QA SUMMARY REPORT")
    print("=" * 78)
    print(f"  Total Test Cases Executed: {total_tests}")
    print(f"  Passed:                    {total_passed}")
    print(f"  Failures:                  {total_failed}")
    print(f"  Errors:                    {total_errors}")
    print(f"  Total Execution Duration:  {elapsed}s")
    print(f"  Success Rate:              {(total_passed / max(1, total_tests)) * 100:.1f}%")
    print("=" * 78)

    if total_failed == 0 and total_errors == 0:
        print("  [SUCCESS] All system suites passed! Application is 100% operational.")
        print("=" * 78 + "\n")
        return 0
    else:
        print(f"  [ERROR] {total_failed + total_errors} test(s) encountered issues.")
        print("=" * 78 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_full_suite())
