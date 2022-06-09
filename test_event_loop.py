import unittest
from strategy import LongRateStrategy
from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from portfolio import NaivePortfolio
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
            initial_capital=1000.00
        )


    def test_run_outer_loop(self):

        pass



if __name__ == '__main__':
    unittest.main()