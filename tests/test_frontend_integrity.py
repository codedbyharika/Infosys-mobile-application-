"""
Frontend Static Integrity & Contract Tests:
1. Validates that every DOM ID queried by JS exists in static/index.html
2. Validates that all REST endpoints invoked in static/js/api.js exist in api/main.py
3. Validates design tokens and CSS variables in static/css/style.css
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.main import app


class TestFrontendIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.static_dir = os.path.join(cls.base_dir, "static")

        with open(os.path.join(cls.static_dir, "index.html"), "r", encoding="utf-8") as f:
            cls.html_content = f.read()

        with open(os.path.join(cls.static_dir, "js", "app.js"), "r", encoding="utf-8") as f:
            cls.app_js = f.read()

        with open(os.path.join(cls.static_dir, "js", "api.js"), "r", encoding="utf-8") as f:
            cls.api_js = f.read()

        with open(os.path.join(cls.static_dir, "css", "style.css"), "r", encoding="utf-8") as f:
            cls.css_content = f.read()

    # ── 1. DOM Element Contract Verification ─────────────────────────────────
    def test_all_queried_dom_ids_exist(self):
        """Every getElementById in app.js must exist in index.html or be guarded by null-check."""
        id_pattern = re.compile(r"document\.getElementById\(['\"]([^'\"]+)['\"]\)")
        queried_ids = set(id_pattern.findall(self.app_js))

        # Extract all id="..." attributes in index.html
        html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', self.html_content))

        # Known dynamic or guarded container IDs
        allowed_missing = {"toast-container", "city-map", "overview-station-grid", "header-health-pill-text"}

        missing_ids = []
        for dom_id in queried_ids:
            if dom_id not in html_ids and dom_id not in allowed_missing:
                missing_ids.append(dom_id)

        self.assertEqual(
            missing_ids, [],
            f"JavaScript queries DOM elements that do not exist in index.html: {missing_ids}"
        )

    # ── 2. REST API Contract Verification ────────────────────────────────────
    def test_api_client_endpoints_match_fastapi_routes(self):
        """All REST endpoints defined in static/js/api.js must have corresponding routes in FastAPI."""
        app_routes = {route.path for route in app.routes}

        # Extract API endpoint paths from api.js
        fetch_pattern = re.compile(r"fetch\(`?\$\{API_BASE\}(/api/[a-zA-Z0-9_\-\/]+)")
        queried_endpoints = set(fetch_pattern.findall(self.api_js))

        for endpoint in queried_endpoints:
            # Handle parameterized routes like /api/stations/...
            if "/api/stations/" in endpoint:
                matched = any("/api/stations/" in r or "/api/stations/{station_name}" in r for r in app_routes)
                self.assertTrue(matched, f"Station detail route {endpoint} not registered in FastAPI")
            else:
                self.assertIn(
                    endpoint, app_routes,
                    f"Frontend invokes endpoint {endpoint} which is not registered on FastAPI ASGI router"
                )

    # ── 3. CSS Design Token Verification ─────────────────────────────────────
    def test_css_design_system_tokens(self):
        """Verifies core modern design system variables exist in static/css/style.css."""
        required_vars = [
            "--bg-main",
            "--bg-card",
            "--border-subtle",
            "--text-primary",
            "--text-muted",
            "--primary",
            "--aqi-good",
            "--aqi-moderate",
            "--aqi-poor"
        ]
        for var_name in required_vars:
            self.assertIn(var_name, self.css_content, f"CSS variable {var_name} missing from design system")


if __name__ == "__main__":
    unittest.main()
