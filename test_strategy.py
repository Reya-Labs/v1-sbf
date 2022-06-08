import unittest
from strategy import LongRateStrategy
from data import HistoricCSVDataHandler
import queue


class TestDataHandler(unittest.TestCase):

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










