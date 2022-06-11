from event_loop import EventLoop
import queue
from abc import ABCMeta, abstractmethod
from data import HistoricCSVDataHandler
from strategy import LongRateStrategy
from execution import SimulatedExecutionHandler
from portfolio import NaivePortfolio

# todo: add docs

class Backtest(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def run_backtest(self):

        raise NotImplementedError("Should implement run_backtest()")


class LongRateStrategyBacktest(Backtest):

    def __init__(self, start_date_time='2022-04-01 00:00:00', end_date_time='2022-06-01 00:00:00'):

        self.events_queue = queue.Queue()

        self.dataHandler = HistoricCSVDataHandler(
            events=self.events_queue,
            csv_dir="datasets",
            token_list=["aave_usdc"],
            start_date_time=start_date_time,
            end_date_time=end_date_time
        )

        self.strategy = LongRateStrategy(
            rates=self.dataHandler,
            events=self.events_queue
        )

        self.portfolio = NaivePortfolio(
            rates=self.dataHandler,
            events=self.events_queue,
            start_date_time=start_date_time,
            leverage=1,
            initial_capital=1.0
        )

        self.executionHandler = SimulatedExecutionHandler(
            events=self.events_queue
        )

        # one day needs to pass to enable fixed rate calculations which needs at least two historical rate values
        self.dataHandler.update_rates()

        self.eventLoop = EventLoop(
            events=self.events_queue,
            rates=self.dataHandler,
            strategy=self.strategy,
            portfolio=self.portfolio,
            executionHandler=self.executionHandler
        )

    def run_backtest(self):

        self.eventLoop.run_outer_loop()

        return self.eventLoop.portfolio