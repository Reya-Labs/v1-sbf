import unittest
from portfolio import NaivePortfolio
from data import HistoricCSVDataHandler
from event import SignalEvent, FillEvent
import queue
from datetime import datetime

# todo: need to test the portfolio with multiple tokens

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

        all_holdings = self.portfolio.all_holdings

        # todo: fix since the market value calculation is not done yet
        self.assertEqual(all_holdings[1]['aave_usdc'], 10000)
        self.assertEqual(str(all_holdings[1]['datetime']), '2021-03-11 14:49:24+00:00')
        self.assertEqual(all_holdings[1]['cash'], 1000)
        self.assertEqual(all_holdings[1]['fee'], 0.0)
        self.assertEqual(all_holdings[1]['total'], 11000.0)


    def test_update_positions_from_fill(self):

        fill = FillEvent(
            token='aave_usdc',
            fixedRate=0.01,
            fee=0,
            timestamp=datetime(2021, 11, 28, 23, 55, 59, 342380),
            notional=1000,
            direction='LONG'
        )

        self.portfolio.update_positions_from_fill(
            fill=fill
        )

        latest_position = self.portfolio.current_positions['aave_usdc'][0]

        self.assertEqual(latest_position['timestamp'], datetime(2021, 11, 28, 23, 55, 59, 342380))
        self.assertEqual(latest_position['direction'], "LONG")
        self.assertEqual(latest_position['notional'], 1000)
        self.assertEqual(latest_position['fixedRate'], 0.01)
        self.assertEqual(latest_position['fee'], 0.0)


    def test_update_holdings_from_fill(self):

        fill = FillEvent(
            token='aave_usdc',
            fixedRate=0.01,
            fee=10,
            timestamp=datetime(2021, 11, 28, 23, 55, 59, 342380),
            notional=1000,
            direction='LONG'
        )

        self.portfolio.update_holdings_from_fill(
            fill=fill
        )

        self.assertEqual(self.portfolio.current_holdings['cash'], 990)
        self.assertEqual(self.portfolio.current_holdings['total'], 990)

    def test_update_fill(self):

        fill = FillEvent(
            token='aave_usdc',
            fixedRate=0.01,
            fee=10,
            timestamp=datetime(2021, 11, 28, 23, 55, 59, 342380),
            notional=1000,
            direction='LONG'
        )

        self.portfolio.update_fill(
            event=fill
        )

        self.assertEqual(self.portfolio.current_holdings['cash'], 990)
        self.assertEqual(self.portfolio.current_holdings['total'], 990)

        latest_position = self.portfolio.current_positions['aave_usdc'][0]

        self.assertEqual(latest_position['timestamp'], datetime(2021, 11, 28, 23, 55, 59, 342380))
        self.assertEqual(latest_position['direction'], "LONG")
        self.assertEqual(latest_position['notional'], 1000)
        self.assertEqual(latest_position['fixedRate'], 0.01)
        self.assertEqual(latest_position['fee'], 10.0)

        print("here")




if __name__ == '__main__':
    unittest.main()