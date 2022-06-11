# portfolio.py

import pandas as pd

from abc import ABCMeta, abstractmethod
from performance import PerformanceMetricsCalculator
from event import OrderEvent


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

    def __init__(self, rates, events, start_date_time, leverage, initial_capital=1.0):
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
        self.start_date_time = start_date_time
        self.initial_capital = initial_capital
        self.leverage = leverage

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
        d['datetime'] = self.start_date_time
        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        # d = dict((k,v) for k, v in [(s, 0.0) for s in self.token_list])
        d = {}
        d['datetime'] = self.start_date_time
        d['cash'] = self.initial_capital
        d['fee'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all tokens.
        """
        # d = dict((k,v) for k, v in [(s, 0.0) for s in self.token_list])
        d = {}
        d['cash'] = self.initial_capital
        d['fee'] = 0.0
        d['total'] = self.initial_capital
        return d

    def years_since_swap_start(self, positionStartTimestamp, currentTimestamp):

        time_delta_in_years = (currentTimestamp - positionStartTimestamp).total_seconds() / 31536000 # 31536000 is the number of seconds in a year

        return time_delta_in_years

    def compute_total_value_of_positions(self, positions, currentRateTuple):

        # todo: inline docs

        total_cashflow = 0
        for position in positions:

            # cover the cashflow from IRS initiation to now

            yearsSinceSwapStart = self.years_since_swap_start(
                positionStartTimestamp=position['timestamp'],
                currentTimestamp=currentRateTuple[1]
            )

            fixedFactorFromStartToNow = position['fixedRate'] * yearsSinceSwapStart
            variableFactorFromStartToNow = (currentRateTuple[2] / position['startingRateValue'] - 1)

            cashflow = position['notional'] * (variableFactorFromStartToNow - fixedFactorFromStartToNow)

            if position['direction'] == "SHORT":
                cashflow = -cashflow

            total_cashflow += (cashflow + position['margin'])

        return total_cashflow

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
        # dh = dict((k,v) for k, v in [(s, 0) for s in self.token_list])
        dh = {}
        dh['datetime'] = rates[self.token_list[0]][0][1]
        dh['cash'] = self.current_holdings['cash']
        dh['fee'] = self.current_holdings['fee']
        dh['total'] = self.current_holdings['cash']

        for t in self.token_list:
            # current way of computing current value (note, the sum below is across all the positions in token t):
            # market_value = sum(position margin + irs cashflow of the position until current timestamp)
            market_value = self.compute_total_value_of_positions(self.current_positions[t], rates[t][0])
            dh[t] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)

    def annualize_variable_rate(self, variableRate, timeDelta):

        # todo: move to utils
        # have two ways to annualise: with and without compounding

        # with compounding
        numberOfCompoundingPeriodsInYear = 31536000 /  timeDelta.total_seconds() # 31536000 is number of seconds in a year
        annualizedVariableRate = (1 + variableRate)**(numberOfCompoundingPeriodsInYear) - 1

        return annualizedVariableRate

    def get_current_fixed_rate(self, token):

        # todo: we might want to set N to a higher period
        two_latest_rates = self.rates.get_latest_rates(token=token, N=2)

        fr = None

        if len(two_latest_rates) == 2:
            liquidityIndex1 = two_latest_rates[0][2]
            liquidityIndex2 = two_latest_rates[1][2]

            variableRate = (liquidityIndex2 / liquidityIndex1) - 1.0

            # assume the fixed rate is equal to the annualizedVariableRate calculated from the variableFactor based on the last two bars
            fr = self.annualize_variable_rate(variableRate=variableRate, timeDelta=two_latest_rates[1][1] - two_latest_rates[0][1])

        return fr

    def get_current_rate_value(self, token):

        latest_rates = self.rates.get_latest_rates(token=token, N=1)

        latest_rate_value = latest_rates[0][2]

        return latest_rate_value

    def update_positions_from_fill(self, fill):
        """
        Takes a FilltEvent object and updates the position matrix
        to reflect the new IRS position.

        Parameters:
        fill - The FillEvent object to update the positions with.
        """

        # the fixed rate can be set here, because we already have access to the rates data!

        # Update the list of current positions with the newly traded IRS contract

        new_position = {}
        new_position['timestamp'] = fill.timestamp
        new_position['direction'] = fill.direction
        new_position['notional'] = fill.notional
        new_position['margin'] = fill.margin
        new_position['fixedRate'] = self.get_current_fixed_rate(token=fill.token)
        new_position['startingRateValue'] = self.get_current_rate_value(token=fill.token)
        new_position['fee'] = fill.fee

        self.current_positions[fill.token].append(new_position)

    def update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix
        to reflect the holdings value.

        Parameters:
        fill - The FillEvent object to update the holdings with.
        """

        # Update holdings list with new quantities
        self.current_holdings['fee'] += fill.fee
        self.current_holdings['cash'] -= (fill.fee + fill.margin)
        self.current_holdings['total'] -= (fill.fee + fill.margin)

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_notional(self):

        return self.initial_capital * self.leverage

    def generate_naive_margin(self):

        # in the naive case where we have a strategy running on top of a single pool we push all
        # capital into the margin account for a position in the given pool

        return self.initial_capital

    def generate_naive_order(self, signal):
        """
        Simply trades an OrderEvent object as a constant notional
        amount for the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The SignalEvent signal information.
        """

        order = OrderEvent(
            token=signal.token,
            timestamp=signal.timestamp,
            direction=signal.direction,
            notional=self.generate_naive_notional(),
            margin=self.generate_naive_margin()
        )

        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()

        self.equity_curve = curve

    # todo: unit test
    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio such
        as Sharpe Ratio and drawdown information.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = PerformanceMetricsCalculator.create_sharpe_ratio(returns)
        max_dd, dd_duration = PerformanceMetricsCalculator.create_drawdowns(pnl)

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        return stats