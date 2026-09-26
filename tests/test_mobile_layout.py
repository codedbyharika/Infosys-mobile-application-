"""
AirSense AI — Mobile Layout & Responsive Chart Verification Test Suite
Verifies:
1. All responsive chart containers and canvas elements exist.
2. Chart.js options correctly adapt to mobile (maxTicksLimit, mobile paddings).
3. All mobile grid classes exist in style.css and index.html.
4. Mobile bottom navigation includes all primary views (Dashboard, Forecast, Routes, Map, My AQI, More).
5. PWA manifest.json and Service Worker sw.js are valid and registered.
"""

import unittest
import os
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestMobileLayoutIntegrity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        html_path = os.path.join(WORKSPACE_ROOT, "static", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            cls.html = f.read()

        css_path = os.path.join(WORKSPACE_ROOT, "static", "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            cls.css = f.read()

        charts_path = os.path.join(WORKSPACE_ROOT, "static", "js", "charts.js")
        with open(charts_path, "r", encoding="utf-8") as f:
            cls.charts_js = f.read()

        app_path = os.path.join(WORKSPACE_ROOT, "static", "js", "app.js")
        with open(app_path, "r", encoding="utf-8") as f:
            cls.app_js = f.read()

    def test_mobile_grid_classes_exist(self):
        """All responsive mobile grid classes must be defined in style.css and used in index.html."""
        required_classes = [
            "overview-comparison-grid",
            "m1-sensor-telemetry-grid",
            "m1-route-controls-grid",
            "route-cards-3col-grid",
            "retrain-action-grid",
            "chart-container-trend",
            "chart-container-comparison",
            "chart-container-forecast",
            "chart-container-pollutants",
            "topbar-preview-toggle-btn",
        ]
        for c in required_classes:
            self.assertIn(c, self.css, f"Class {c} missing in style.css")
            self.assertIn(c, self.html, f"Class {c} missing in index.html")

    def test_mobile_chart_heights_defined(self):
        """Chart containers must have dedicated mobile height rules to prevent vertical viewport stretching."""
        self.assertIn(".chart-container-trend", self.css)
        self.assertIn("250px", self.css)
        self.assertIn(".chart-container-forecast", self.css)
        self.assertIn(".chart-container-comparison", self.css)

    def test_charts_have_mobile_detection_and_tick_limits(self):
        """ChartEngine must implement isMobile() and autoSkip/maxTicksLimit to prevent tick overlapping on mobile."""
        self.assertIn("isMobile()", self.charts_js)
        self.assertIn("resizeAll()", self.charts_js)
        self.assertIn("maxTicksLimit", self.charts_js)
        self.assertIn("autoSkip: true", self.charts_js)

    def test_mobile_bottom_nav_has_core_modules(self):
        """Mobile bottom bar must include Dashboard, Forecast, Routes, Map, and History."""
        self.assertIn('id="mob-nav-overview"', self.html)
        self.assertIn('id="mob-nav-forecast"', self.html)
        self.assertIn('id="mob-nav-route"', self.html)
        self.assertIn('id="mob-nav-module1"', self.html)
        self.assertIn('id="mob-nav-history"', self.html)
        self.assertIn('id="mob-nav-more"', self.html)

    def test_mobile_preview_toggle_integrated(self):
        """The UI must have the interactive Mobile View toggle button."""
        self.assertIn('id="btn-mobile-preview-toggle"', self.html)
        self.assertIn("toggleMobilePreview", self.app_js)
        self.assertIn("mobile-preview-active", self.css)

    def test_pwa_manifest_validity(self):
        """PWA manifest.json must be valid JSON with name, icons, and display standalone."""
        manifest_path = os.path.join(WORKSPACE_ROOT, "static", "manifest.json")
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertIn("name", manifest)
        self.assertIn("icons", manifest)
        self.assertEqual(manifest.get("display"), "standalone")

    def test_service_worker_file_exists(self):
        """Service worker script sw.js must exist for offline PWA operation."""
        sw_path = os.path.join(WORKSPACE_ROOT, "static", "sw.js")
        self.assertTrue(os.path.exists(sw_path))
        with open(sw_path, "r", encoding="utf-8") as f:
            sw_code = f.read()
        self.assertIn("install", sw_code)
        self.assertIn("fetch", sw_code)

    def test_navigation_bar_behavior_and_accessibility(self):
        """Navigation bars must implement ARIA tablist/tab roles, href routing, and drawer close controls."""
        self.assertIn('role="tablist"', self.html)
        self.assertIn('role="tab"', self.html)
        self.assertIn('id="sidebar-close-btn"', self.html)
        self.assertIn('id="more-sub-indicator"', self.html)
        self.assertIn('href="#overview"', self.html)
        self.assertIn('href="#module2_route"', self.html)
        self.assertIn(".sidebar-close-btn", self.css)
        self.assertIn(".more-sub-indicator", self.css)

    def test_fallback_stations_and_hash_routing(self):
        """App.js must provide fallback Pune dataset telemetry and hash routing synchronization."""
        self.assertIn("FALLBACK_PUNE_STATIONS", self.app_js)
        self.assertIn("BopadiSquare_65", self.app_js)
        self.assertIn("popstate", self.app_js)
        self.assertIn("hashchange", self.app_js)
        self.assertIn("switchTab", self.app_js)


if __name__ == "__main__":
    unittest.main()
