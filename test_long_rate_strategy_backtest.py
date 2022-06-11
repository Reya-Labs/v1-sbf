import unittest
from backtest import LongRateStrategyBacktest


class TestLongRateStrategyBacktest(unittest.TestCase):

    def setUp(self):

        self.longRateStrategyBacktest = LongRateStrategyBacktest(
            start_date_time='2022-04-01 00:00:00',
            end_date_time='2022-06-01 00:00:00',
            leverage=1.0,
            initial_capital=1.0
        )

    def test_run_backtest(self):

        portfolio = self.longRateStrategyBacktest.run_backtest()
        portfolio.create_equity_curve_dataframe()
        equity_curve = portfolio.equity_curve.dropna()
        self.assertEqual(equity_curve.iloc[-1, -1], 0.9990527468734619)

    def test_run_levered_backtest(self):

        self.leveredLongRateStrategyBacktest = LongRateStrategyBacktest(
            start_date_time='2022-04-01 00:00:00',
            end_date_time='2022-06-01 00:00:00',
            leverage=10.0,
            initial_capital=1.0
        )

        portfolio = self.leveredLongRateStrategyBacktest.run_backtest()
        portfolio.create_equity_curve_dataframe()
        equity_curve = portfolio.equity_curve.dropna()
        self.assertEqual(equity_curve.iloc[-1, -1], 0.9905274687346195)


if __name__ == '__main__':
    unittest.main()