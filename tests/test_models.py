import unittest

import numpy as np
import pandas as pd

from src.models import fit_ols


class TestOLS(unittest.TestCase):
    def test_recovers_known_coefficients(self):
        rng = np.random.default_rng(7)
        x1 = rng.normal(size=500)
        x2 = rng.normal(size=500)
        y = 0.25 + 1.5 * x1 - 0.7 * x2 + rng.normal(0, 0.01, size=500)
        frame = pd.DataFrame({"y": y, "x1": x1, "x2": x2})
        result = fit_ols(frame, "y", ["x1", "x2"])
        self.assertAlmostEqual(result.coefficients["Intercept"], 0.25, places=2)
        self.assertAlmostEqual(result.coefficients["x1"], 1.5, places=2)
        self.assertAlmostEqual(result.coefficients["x2"], -0.7, places=2)
        self.assertGreater(result.r_squared, 0.99)


if __name__ == "__main__":
    unittest.main()

