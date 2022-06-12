import unittest
from reporter import SimpleBacktestReporter
from backtest import LongRateStrategyBacktest


class TestReporter(unittest.TestCase):

    def setUp(self):

        self.leveredLongRateStrategyBacktest = LongRateStrategyBacktest(
            start_date_time='2022-04-01 00:00:00',
            end_date_time='2022-06-01 00:00:00',
            leverage=10.0,
            initial_capital=1.0
        )

        portfolio = self.leveredLongRateStrategyBacktest.run_backtest()
        portfolio.create_equity_curve_dataframe()

        self.equity_curve = portfolio.equity_curve.dropna()
        self.summary_stats = portfolio.output_summary_stats()

        self.reporter = SimpleBacktestReporter(
            backtest_results_df=self.equity_curve,
            summary_stats=self.summary_stats
        )

    def test_produce_backtest_summary_report(self):

        self.reporter.generate_report()




if __name__ == '__main__':
    unittest.main()