import unittest
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
        self.assertEqual(str(next(self.dataHandler.token_data['aave_usdc'])[0]), '2021-03-13 00:00:00')

        self.assertEqual(self.dataHandler.latest_token_data['aave_usdc'], [])

    def test_open_and_convert_csv_files_custom_start_end_dates(self):

        new_events_queue = queue.Queue()

        # 2022-04-15T17:01:56+00:00,1056882202617775997733954411 start here
        # 2022-06-05T12:42:24+00:00,1058972855433991520134610549 stop here

        dataHandlerWithCustomStartEndDates = HistoricCSVDataHandler(
            events=new_events_queue,
            csv_dir="datasets",
            token_list=["aave_usdc"],
            start_date_time='2022-04-15 17:01:55',
            end_date_time='2022-06-05 12:42:24'
        )

        dataHandlerWithCustomStartEndDates.update_rates()

        latest_dat_str = str(dataHandlerWithCustomStartEndDates.get_latest_rates(token='aave_usdc')[0][1])
        self.assertEqual(latest_dat_str, '2022-04-16 00:00:00')

    def test_get_new_rate(self):

        new_rate = next(self.dataHandler._get_new_rate('aave_usdc'))
        self.assertEqual(new_rate[0], 'aave_usdc')
        self.assertEqual(str(new_rate[1]), '2021-03-12 00:00:00')
        self.assertEqual(new_rate[2], 1e27)

    def test_get_latest_rates(self):

        rates = self.dataHandler.get_latest_rates("aave_usdc")

        self.assertEqual(rates, [])

    def test_update_rates(self):

        self.dataHandler.update_rates()

        self.assertEqual(self.dataHandler.events.get().type, 'MARKET')

        self.assertEqual(self.dataHandler.latest_token_data['aave_usdc'][0][0], 'aave_usdc')
        self.assertEqual(str(self.dataHandler.latest_token_data['aave_usdc'][0][1]), '2021-03-12 00:00:00')
        self.assertEqual(self.dataHandler.latest_token_data['aave_usdc'][0][2], 1e27)


if __name__ == '__main__':
    unittest.main()