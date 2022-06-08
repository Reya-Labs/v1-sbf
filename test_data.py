import unittest
from datetime import datetime
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

    def test_open_and_convert_csv_files(self):

        self.assertEqual(self.dataHandler.csv_dir, "datasets")
        self.assertEqual(self.dataHandler.token_list, ["aave_usdc"])

        self.assertEqual(next(self.dataHandler.token_data['aave_usdc'])[1].loc["liquidityIndex"], 1e27)
        self.assertEqual(str(next(self.dataHandler.token_data['aave_usdc'])[0]), '2021-03-16 11:49:16+00:00')

        self.assertEqual(self.dataHandler.latest_token_data['aave_usdc'], [])

    def test_get_new_rate(self):

        new_rate = next(self.dataHandler._get_new_rate('aave_usdc'))
        self.assertEqual(new_rate[0], 'aave_usdc')
        self.assertEqual(str(new_rate[1]), '2021-03-11 14:49:24+00:00')
        self.assertEqual(new_rate[2], 1e27)

    def test_get_latest_rates(self):

        rates = self.dataHandler.get_latest_rates("aave_usdc")

        self.assertEqual(rates, [])

    def test_update_rates(self):

        self.dataHandler.update_rates()

        self.assertEqual(self.dataHandler.events.get().type, 'MARKET')

        self.assertEqual(self.dataHandler.latest_token_data['aave_usdc'][0][0], 'aave_usdc')
        self.assertEqual(str(self.dataHandler.latest_token_data['aave_usdc'][0][1]), '2021-03-11 14:49:24+00:00')
        self.assertEqual(self.dataHandler.latest_token_data['aave_usdc'][0][2], 1e27)


    def test_latest_token_data(self):

        pass

    def test_token_data(self):

        pass

    def test_csv_dir(self):

        pass

    def test_events(self):

        pass

    def test_latest_bars(self):

        pass














