import unittest
from backtest import LongRateStrategyBacktest


class TestLongRateStrategyBacktest(unittest.TestCase):

    def setUp(self):

        self.longRateStrategyBacktest = LongRateStrategyBacktest(
            start_date_time="2022-04-01 00:00:00",
            end_date_time="2022-06-01 00:00:00",
            leverage=1.0,
            initial_capital=1.0
        )

        self.longRateStrategyBacktest.dataHandler.token_list = ["aave_usdc"]

    def test_run_backtest(self):

        portfolio = self.longRateStrategyBacktest.run_backtest()
        portfolio.create_equity_curve_dataframe()
        equity_curve = portfolio.equity_curve.dropna()
        self.assertEqual(equity_curve.iloc[-1, -1], 0.9989570573528851)

    def test_run_levered_backtest(self):

        self.leveredLongRateStrategyBacktest = LongRateStrategyBacktest(
            start_date_time="2022-04-01 00:00:00",
            end_date_time="2022-06-01 00:00:00",
            leverage=10.0,
            initial_capital=1.0
        )
        
        self.leveredLongRateStrategyBacktest.dataHandler.token_list = ["aave_usdc"]

        portfolio = self.leveredLongRateStrategyBacktest.run_backtest()
        portfolio.create_equity_curve_dataframe()
        equity_curve = portfolio.equity_curve.dropna()
        self.assertEqual(equity_curve.iloc[-1, -1], 0.9895705735288505)

if __name__=="__main__":
    unittest.main()