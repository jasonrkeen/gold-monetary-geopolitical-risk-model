import unittest

import numpy as np
import pandas as pd

from src.indices import rolling_percentile


class TestIndices(unittest.TestCase):
    def test_monotonic_last_value_is_high_percentile(self):
        series = pd.Series(np.arange(200, dtype=float))
        score = rolling_percentile(series, window=100, minimum=20)
        self.assertAlmostEqual(score.iloc[-1], 100.0)

    def test_scores_remain_bounded(self):
        rng = np.random.default_rng(3)
        score = rolling_percentile(pd.Series(rng.normal(size=300)), window=100, minimum=20)
        valid = score.dropna()
        self.assertTrue(((valid >= 0) & (valid <= 100)).all())


if __name__ == "__main__":
    unittest.main()

