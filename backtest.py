from event_loop import EventLoop
import queue
from abc import ABCMeta, abstractmethod
from data import HistoricCSVDataHandler
from strategy import LongRateStrategy
from LongShortMomentum import LongShortMomentumStrategy
from StatisticalArbitragePairs import StatisticalArbitragePairs
from execution import SimulatedExecutionHandler
from portfolio import NaivePortfolio
import datetime

# todo: add docs

class Backtest(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def run_backtest(self):

        raise NotImplementedError("Should implement run_backtest()")

class LongRateStrategyBacktest(Backtest):

    def __init__(self, start_date_time='2022-04-01 00:00:00',
                 end_date_time='2022-06-01 00:00:00',
                 leverage=1.0, initial_capital=1.0):

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
            leverage=leverage,
            initial_capital=initial_capital
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

class LongShortMomentumStrategyBacktest(Backtest):

    def __init__(self, start_date_time="2022-04-01 00:00:00",
                 end_date_time="2022-06-01 00:00:00",
                 leverage=1.0, initial_capital=1.0,
                 trend_lookback=15, apy_lookback=5, buffer=1,
                 trade_trend=False):

        self.events_queue = queue.Queue()

        self.dataHandler = HistoricCSVDataHandler(
            events=self.events_queue,
            csv_dir="datasets",
            token_list=["rocket_rETH"], 
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            is_liquid_staking=False
        )

        self.strategy = LongShortMomentumStrategy(
            rates=self.dataHandler,
            events=self.events_queue,
            trend_lookback=trend_lookback,
            apy_lookback=apy_lookback,
            buffer=buffer,
            trade_trend=trade_trend
        )

        self.portfolio = NaivePortfolio(
            rates=self.dataHandler,
            events=self.events_queue,
            start_date_time=start_date_time,
            leverage=leverage,
            initial_capital=initial_capital
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

class StatisticalArbitragePairsBacktest(Backtest):

    def __init__(self, start_date_time="2022-04-01 00:00:00",
                 end_date_time="2022-06-01 00:00:00",
                 leverage=1.0, initial_capital=1.0,
                 lookback_window=30, apy_lookback=5, deviations=1,
                 pairs = [("eth_ceth", "rocket_rETH")],
                 monthly=False):

        self.events_queue = queue.Queue()

        # We need to play around with datetime, and make sure that the stat arb lookback
        # window is still being picked up 
        read_date = datetime.datetime.strptime(start_date_time, "%Y-%m-%d 00:00:00")
        get_lookback = read_date - datetime.timedelta(days=lookback_window)
        formatted_start_date = get_lookback.strftime("%Y-%m-%d 00:00:00")

        self.dataHandler = HistoricCSVDataHandler(
            events=self.events_queue,
            csv_dir="datasets",
            token_list=list(pairs[0]),  
            start_date_time=formatted_start_date,
            end_date_time=end_date_time
        )
        
        self.strategy = StatisticalArbitragePairs(
            rates=self.dataHandler,
            events=self.events_queue,
            lookback_window=lookback_window,
            apy_lookback=apy_lookback,
            deviations=deviations,
            pairs=pairs,
            strategy_start=start_date_time, # True start of the analysis, so we can collect lookback window data first
            monthly=monthly
        )

        self.portfolio = NaivePortfolio(
            rates=self.dataHandler,
            events=self.events_queue,
            start_date_time=start_date_time,
            leverage=leverage,
            initial_capital=initial_capital
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