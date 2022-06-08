import unittest
from strategy import LongRateStrategy
from data import HistoricCSVDataHandler
import queue


class TestStrategy(unittest.TestCase):

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

    def test_strategy_object_initialization(self):

        self.assertEqual(self.strategy.rates, self.dataHandler)
        self.assertEqual(self.strategy.aped['aave_usdc'], False)
        self.assertEqual(self.strategy.token_list, ['aave_usdc'])


    def test_calculate_signals(self):

        pass













