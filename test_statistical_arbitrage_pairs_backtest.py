import unittest
from backtest import StatisticalArbitragePairsBacktest as SAP


class TestStatisticalArbitragePairsBacktest(unittest.TestCase):

    def setUp(self):

        self.statArbBacktest = SAP(
            start_date_time="2022-04-01 00:00:00",
            end_date_time="2022-06-01 00:00:00",
            leverage=1.0,
            initial_capital=1.0,
            lookback_window=30, 
            apy_lookback=5, 
            deviations=1,
            pairs = [("eth_ceth", "rocket_rETH")],
            monthly=False)  

    def test_run_backtest(self):

        portfolio = self.statArbBacktest.run_backtest()
        portfolio.create_equity_curve_dataframe()
        equity_curve = portfolio.equity_curve.dropna()
        self.assertEqual(equity_curve.iloc[-1, -1], 0.9963324674078823)
    
    def test_run_backtest_monthly(self):
        
        self.statArbBacktestMonthly = SAP(
            start_date_time="2022-04-01 00:00:00",
            end_date_time="2022-06-01 00:00:00",
            leverage=1.0,
            initial_capital=1.0,
            lookback_window=30, 
            apy_lookback=5, 
            deviations=1,
            pairs = [("eth_ceth", "rocket_rETH")],
            monthly=True)  

        portfolio = self.statArbBacktestMonthly.run_backtest()
        portfolio.create_equity_curve_dataframe()
        equity_curve = portfolio.equity_curve.dropna()
        self.assertEqual(equity_curve.iloc[-1, -1], 1.0019509472971466)

if __name__=="__main__":
    unittest.main()