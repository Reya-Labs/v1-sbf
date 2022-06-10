import unittest
from strategy import LongRateStrategy
from data import HistoricCSVDataHandler
from event import MarketEvent
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

        marketEvent = MarketEvent()
        self.dataHandler.update_rates()
        self.strategy.events = queue.Queue() # empty the queue
        self.strategy.calculate_signals(event=marketEvent)
        signalEvent = self.strategy.events.get()
        self.assertEqual(signalEvent.type, "SIGNAL")
        self.assertEqual(str(signalEvent.timestamp), '2021-03-11 14:49:24')
        self.assertEqual(signalEvent.token, "aave_usdc")
        self.assertEqual(signalEvent.direction, "LONG")

        # if recalculate the signal event nothing should happen since already holding
        self.strategy.calculate_signals(event=marketEvent)
        queue_size = self.strategy.events.qsize()
        self.assertEqual(queue_size, 0)


if __name__ == '__main__':
    unittest.main()










