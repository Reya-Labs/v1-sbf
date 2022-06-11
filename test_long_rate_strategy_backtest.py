import unittest
from backtest import LongRateStrategyBacktest


class TestLongRateStrategyBacktest(unittest.TestCase):

    def setUp(self):

        self.longRateStrategyBacktest = LongRateStrategyBacktest()

    def test_run_backtest(self):

        pass


if __name__ == '__main__':
    unittest.main()