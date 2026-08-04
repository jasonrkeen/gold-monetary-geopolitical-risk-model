import unittest

import numpy as np
import pandas as pd

from src.transform import clean_daily_data


class TestTransform(unittest.TestCase):
    def test_uses_gld_trading_calendar(self):
        index = pd.date_range("2026-01-01", periods=5, freq="D")
        frame = pd.DataFrame(
            {
                "GLD": [100.0, 101.0, np.nan, np.nan, 102.0],
                "GPR": [90.0, 95.0, 130.0, 125.0, 100.0],
                "Real Yield": [1.5, np.nan, 1.6, np.nan, 1.7],
            },
            index=index,
        )
        cleaned = clean_daily_data(frame)
        self.assertEqual(len(cleaned), 3)
        self.assertTrue(cleaned["GLD"].notna().all())
        self.assertEqual(cleaned.index[-1], index[-1])


if __name__ == "__main__":
    unittest.main()

