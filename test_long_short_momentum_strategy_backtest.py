import unittest
from backtest import LongShortMomentumStrategyBacktest as LSM


class TestLongShortMomentumStrategyBacktest(unittest.TestCase):

    def setUp(self):

        self.momentumBacktest = LSM(
            start_date_time="2022-04-01 00:00:00",
            end_date_time="2022-06-01 00:00:00",
            leverage=1.0,
            initial_capital=1.0,
            trend_lookback=15, 
            apy_lookback=5, 
            buffer=1,
            trade_trend=False)

        self.momentumBacktest.dataHandler.token_list = ["rocket_rETH"]
        

    def test_run_backtest(self):

        portfolio = self.momentumBacktest.run_backtest()
        portfolio.create_equity_curve_dataframe()
        equity_curve = portfolio.equity_curve.dropna()
        self.assertEqual(equity_curve.iloc[-1, -1], 1.0007282844849714)


if __name__ == '__main__':
    unittest.main()