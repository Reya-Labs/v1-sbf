import unittest
from datetime import datetime
from data import HistoricCSVDataHandler
import queue

class TestDataHandler(unittest.TestCase):


    def setUp(self):

        events_queue = queue.Queue()

        self.dataHandler = HistoricCSVDataHandler(
            events=events_queue,
            csv_dir="",
            token_list=["test"]
        )

    def test_open_and_convert_csv_files(self):

        pass

    def test_get_latest_rates(self):

        pass


    def test_get_new_rate(self):

        pass

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

    def test_update_bars(self):

        pass














