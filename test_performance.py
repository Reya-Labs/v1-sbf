import unittest
from performance import PerformanceMetricsCalculator
import pandas as pd

class TestPerformanceMetricsCalculator(unittest.TestCase):

    def setUp(self):
        self.performanceMetricsCalculator = PerformanceMetricsCalculator()
        self.dummy_daily_returns = pd.Series([0.0001, -0.0003, -0.0002, -0.0004, 0.0007, 0.0003])
        self.dumy_equity_curve = pd.Series([1.0001, 0.9999, 0.9989, 0.9994, 1.0004, 1.0006])

    def test_create_sharpe_ratio(self):

        sharpe_ratio = self.performanceMetricsCalculator.create_sharpe_ratio(returns=self.dummy_daily_returns)
        self.assertEqual(sharpe_ratio, 1.6692092564998355)

    def test_create_drawdowns(self):

        drawdown, duration = self.performanceMetricsCalculator.create_drawdowns(equity_curve=self.dumy_equity_curve)
        self.assertEqual(drawdown, 0.0010000000000000009)
        self.assertEqual(duration, 2.0)







if __name__ == '__main__':
    unittest.main()