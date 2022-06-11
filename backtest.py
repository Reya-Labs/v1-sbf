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

    def __init__(self):

        events_queue = queue.Queue()

        dataHandler = HistoricCSVDataHandler(
            events=events_queue,
            csv_dir="datasets",
            token_list=["aave_usdc"]
        )

        strategy = LongRateStrategy(
            rates=dataHandler,
            events=events_queue
        )

        portfolio = NaivePortfolio(
            rates=dataHandler,
            events=events_queue,
            start_date='2022-04-15 17:01:55',
            leverage=1,
            initial_capital=1.0
        )

        executionHandler = SimulatedExecutionHandler(
            events=events_queue
        )

        self.eventLoop = EventLoop(
            events=queue.Queue(),
            rates=dataHandler,
            strategy=strategy,
            portfolio=portfolio,
            executionHandler=executionHandler
        )

    def run_backtest(self):

        self.eventLoop.run_inner_loop()

        return self.eventLoop.portfolio