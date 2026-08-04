import unittest
from pathlib import Path
from unittest.mock import patch

from reportlab.pdfbase import pdfmetrics

import src.report as report


class TestReportFonts(unittest.TestCase):
    def test_registered_fonts_are_available(self):
        registered = set(pdfmetrics.getRegisteredFontNames())
        core = {"Helvetica", "Helvetica-Bold"}
        self.assertTrue(report.REGULAR_FONT in registered | core)
        self.assertTrue(report.BOLD_FONT in registered | core)

    def test_missing_system_fonts_use_safe_fallback(self):
        missing = [(Path("missing-regular.ttf"), Path("missing-bold.ttf"))]
        with patch.object(report, "_font_candidates", return_value=missing):
            self.assertEqual(report._register_report_fonts(), ("Helvetica", "Helvetica-Bold"))


if __name__ == "__main__":
    unittest.main()
