import unittest
from strategy import LongRateStrategy
from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from portfolio import NaivePortfolio
from event_loop import EventLoop
import queue


class TestEventLoop(unittest.TestCase):

    def setUp(self):

        events_queue = queue.Queue()

        self.dataHandler = HistoricCSVDataHandler(
            events=events_queue,
            csv_dir="datasets",
            token_list=["aave_usdc"]
        )

        self.strategy = LongRateStrategy(
            rates=self.dataHandler,
            events=events_queue
        )

        self.executionHandler = SimulatedExecutionHandler(
            events=events_queue
        )

        self.portfolio = NaivePortfolio(
            rates=self.dataHandler,
            events=events_queue,
            start_date='2021-03-11 14:49', # todo: should be a timestamp
            initial_capital=1000.00,
            leverage=10
        )

        self.eventLoop = EventLoop(
            events=events_queue,
            rates=self.dataHandler,
            strategy=self.strategy,
            portfolio=self.portfolio,
            executionHandler=self.executionHandler
        )


    def test_run_outer_loop(self):

        self.eventLoop.run_outer_loop()

        self.portfolio.create_equity_curve_dataframe()

        equity_curve = self.portfolio.equity_curve

        self.assertEqual(equity_curve.iloc[-1, -1], 1)


if __name__ == '__main__':
    unittest.main()