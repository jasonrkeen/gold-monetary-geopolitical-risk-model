import unittest

import numpy as np
import pandas as pd

from src.models import fit_ols
from src.scenarios import run_scenarios


class TestScenarios(unittest.TestCase):
    def _models(self):
        rng = np.random.default_rng(11)
        n = 350
        frame = pd.DataFrame(
            {
                "Real-yield change": rng.normal(0, 0.15, n),
                "Dollar return": rng.normal(0, 0.02, n),
                "VIX change": rng.normal(0, 0.15, n),
                "GPR change": rng.normal(0, 0.20, n),
                "Breakeven change": rng.normal(0, 0.08, n),
                "S&P 500 return": rng.normal(0.005, 0.04, n),
            }
        )
        frame["GLD return"] = (
            -0.04 * frame["Real-yield change"]
            - 0.35 * frame["Dollar return"]
            + rng.normal(0, 0.02, n)
        )
        models = {
            "GLD": fit_ols(
                frame,
                "GLD return",
                ["Real-yield change", "Dollar return", "VIX change", "GPR change", "Breakeven change", "S&P 500 return"],
            )
        }
        miner_predictors = ["GLD return", "S&P 500 return", "Dollar return", "Real-yield change", "GPR change"]
        for asset in ["GDX", "Newmont", "Barrick", "Agnico Eagle", "AngloGold Ashanti"]:
            frame[f"{asset} return"] = 1.2 * frame["GLD return"] + 0.3 * frame["S&P 500 return"] + rng.normal(0, 0.03, n)
            models[asset] = fit_ols(frame, f"{asset} return", miner_predictors)
        return models

    def test_expected_shape_and_quantile_order(self):
        summary, draws = run_scenarios(self._models(), runs=250, seed=4)
        self.assertEqual(len(summary), 8 * 6)
        self.assertEqual(len(draws), 8 * 2 * 250)
        self.assertTrue((summary["p05_return"] <= summary["median_return"]).all())
        self.assertTrue((summary["median_return"] <= summary["p95_return"]).all())


if __name__ == "__main__":
    unittest.main()

