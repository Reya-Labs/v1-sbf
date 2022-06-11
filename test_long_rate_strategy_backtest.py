import unittest
from backtest import LongRateStrategyBacktest


class TestLongRateStrategyBacktest(unittest.TestCase):

    def setUp(self):

        self.longRateStrategyBacktest = LongRateStrategyBacktest()

    def test_run_backtest(self):

        portfolio = self.longRateStrategyBacktest.run_backtest()
        portfolio.create_equity_curve_dataframe()
        equity_curve = portfolio.equity_curve.dropna()
        self.assertEqual(equity_curve.iloc[-1, -1], 0.9990527468734619)


if __name__ == '__main__':
    unittest.main()