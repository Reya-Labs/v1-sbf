# portfolio.py

import datetime
import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod
from math import floor

from event import FillEvent, OrderEvent


class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value of all interest rate swap contracts at a resolution of a "bar",
    i.e. one block or one day
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolio logic.
        """
        raise NotImplementedError("Should implement update_signal()")

    @abstractmethod
    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        raise NotImplementedError("Should implement update_fill()")


class NaivePortfolio(Portfolio):
    """
    The NaivePortfolio object is designed to send IRS trades to
    a voltzTrading object with a constant notional amount blindly,
    i.e. without any risk management or position sizing. It is
    used to test simpler strategies such as LongRateStrategy.
    """

    def __init__(self, rates, events, start_date, initial_capital=100000.0):
        """
        Initialises the portfolio with rates and an event queue.
        Also includes a starting datetime index and initial capital
        (USD unless otherwise stated).

        Parameters:
        rates - The DataHandler object with current market rates data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """

        self.rates = rates
        self.events = events
        self.token_list = self.rates.token_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((k, v) for k, v in [(s, []) for s in self.token_list])

        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

    def construct_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """

        d = dict((k,v) for k, v in [(s, []) for s in self.token_list])
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k,v) for k, v in [(s, 0.0) for s in self.token_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['fee'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all tokens.
        """
        d = dict((k,v) for k, v in [(s, 0.0) for s in self.token_list])
        d['cash'] = self.initial_capital
        d['fee'] = 0.0
        d['total'] = self.initial_capital
        return d

    def compute_market_value(self, positions, rates):

        # todo: docs & implementation

        return 10000.00

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current
        market data rate. This reflects the PREVIOUS bar, i.e. all
        current market rate data at this stage is known.

        Makes use of a MarketEvent from the events queue.
        """
        rates = {}
        for token in self.token_list:
            rates[token] = self.rates.get_latest_rates(token, N=1)

        # Update positions
        dp = dict((k,v) for k, v in [(s, []) for s in self.token_list])
        dp['datetime'] = rates[self.token_list[0]][0][1]

        for t in self.token_list:
            dp[t] = self.current_positions[t]

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        dh = dict((k,v) for k, v in [(s, 0) for s in self.token_list])
        dh['datetime'] = rates[self.token_list[0]][0][1]
        dh['cash'] = self.current_holdings['cash']
        dh['fee'] = self.current_holdings['fee']
        dh['total'] = self.current_holdings['cash']

        for t in self.token_list:
            # Approximation to the real value of all interest rate swap contracts held by the trader
            # OLD: market_value = self.current_positions[s] * bars[s][0][5]
            market_value = self.compute_market_value(self.current_positions[t], rates[t])
            dh[t] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):
        """
        Takes a FilltEvent object and updates the position matrix
        to reflect the new IRS position.

        Parameters:
        fill - The FillEvent object to update the positions with.
        """

        # Update the list of current positions with the newly traded IRS contract

        new_position = {}
        new_position['timestamp'] = fill.timestamp
        new_position['direction'] = fill.direction
        new_position['notional'] = fill.notional
        new_position['fixedRate'] = fill.fixedRate
        new_position['fee'] = fill.fee

        self.current_positions[fill.token].append(new_position)


    def update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix
        to reflect the holdings value.

        Parameters:
        fill - The FillEvent object to update the holdings with.
        """

        # todo: take into account margin deposited

        # Update holdings list with new quantities
        self.current_holdings['fee'] += fill.fee
        self.current_holdings['cash'] -= (fill.fee)
        self.current_holdings['total'] -= (fill.fee)


    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)


