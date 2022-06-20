from event_loop import EventLoop
import queue
from abc import ABCMeta, abstractmethod
from data import HistoricCSVDataHandler
from strategy import LongRateStrategy, LongShortMomentumStrategy, StatisticalArbitragePairs
from execution import SimulatedExecutionHandler
from portfolio import NaivePortfolio

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

    def __init__(self, start_date_time='2022-04-01 00:00:00',
                 end_date_time='2022-06-01 00:00:00',
                 leverage=1.0, initial_capital=1.0,
                 trend_lookback=15, apy_lookback=1, buffer=1,
                 trade_trend=False):

        self.events_queue = queue.Queue()

        self.dataHandler = HistoricCSVDataHandler(
            events=self.events_queue,
            csv_dir="datasets",
            #token_list=["rocket_stETH"],
            #token_list=["lido_stETH"],
            #token_list=["aave_usdc"],
            #token_list=["aave_dai"],
            #token_list=["aave_usdt"],
            #token_list=["aave_tusd"],
            #token_list=["aave_wbtc"],
            #token_list=["compound_dai"],
            #token_list=["compound_usdc"],
            #token_list=["compound_wbtc2"],
            token_list=["eth_aweth"],
            #token_list=["eth_ceth"],
            start_date_time=start_date_time,
            end_date_time=end_date_time
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
                 lookback_window=30, apy_lookback=1, deviations=1,
                 pairs = [("aave_usdc", "aave_dai")]):

        self.events_queue = queue.Queue()

        self.dataHandler = HistoricCSVDataHandler(
            events=self.events_queue,
            csv_dir="datasets",
            token_list=["aave_usdc", "aave_dai"], # aUSDC - aDAI arbitrage 
            start_date_time=start_date_time,
            end_date_time=end_date_time
        )

        self.strategy = StatisticalArbitragePairs(
            rates=self.dataHandler,
            events=self.events_queue,
            lookback_window=lookback_window,
            apy_lookback=apy_lookback,
            deviations=deviations,
            pairs=pairs
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