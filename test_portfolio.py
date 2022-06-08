import unittest
from portfolio import NaivePortfolio
from data import HistoricCSVDataHandler
from event import SignalEvent
import queue



class TestPortfolio(unittest.TestCase):

    def setUp(self):

        events_queue = queue.Queue()

        self.dataHandler = HistoricCSVDataHandler(
            events=events_queue,
            csv_dir="datasets",
            token_list=["aave_usdc"]
        )

        self.portfolio = NaivePortfolio(
            rates=self.dataHandler,
            events=events_queue,
            start_date='2021-03-11 14:49',
            initial_capital=1000.00
        )


    def test_update_timeindex(self):

        # todo: Timestamp should be a datetime object
        # (Token, Direction = LONG, SHORT or EXIT, Timestamp)
        signal = SignalEvent('aave_usdc', 'LONG', '2021-03-11 14:49')
        self.dataHandler.update_rates()

        self.portfolio.update_timeindex(
            event=signal
        )

        print('here')




if __name__ == '__main__':
    unittest.main()