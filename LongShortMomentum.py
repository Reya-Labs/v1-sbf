
from strategy import Strategy
from signal import signal
from event import SignalEvent
import numpy as np
from sklearn.linear_model import RANSACRegressor

SECONDS_IN_YEAR = 31536000
class LongShortMomentumStrategy(Strategy):
    """
    A basic time series momentum (i.e. trend-following) strategy using a 
    lookback window to compute the moving average of the rate. 
    
    Basic strategy as follows:

    1) Convert liquidity indices to APYs
    IF trade_trend set:
        2) Compute the individual (log) relative change in APY at each timestamp: log(dAPY) ~ log(APY(t)/APY(t-1))
        3) Computing moving average of this change over a lookback window, S = EWMA[log(dAPY)] from time t
        4) Current APY trend > S + buffer => LONG; current APY trend < S - buffer => LONG; else EXIT position with the execution handler  
    ELSE:
        2) We just form the same signals as above but with the APY value rather than its trend
    """

    def __init__(self, rates, events, trend_lookback=15, apy_lookback=5, buffer=1, trade_trend=False):
        
        self.rates = rates
        self.token_list = self.rates.token_list
        self.events = events
        self.trend_lookback = trend_lookback
        self.apy_lookback = apy_lookback
        self.buffer = buffer
        self.trade_trend = trade_trend
        self.prior_position = "NONE" # Need to track when positions change

    def calculate_signals(self, event):
        position = self.prior_position # Reset position so that something is always registered at the start of a new event
        if event.type == "MARKET":
            for t in self.token_list:
                liquidity_indexes = self.rates.get_latest_rates(t, N=self.trend_lookback) # List of (token, timestamp, liquidity index) tuples
                rates = self.liquidity_index_to_apy(liquidity_indexes) # Convert to APYs
                #trends = self.calculate_trend(rates) # Get trends
                if rates is not None and rates != []:
                    if self.trade_trend:
                        sig, buffer = self.update_beta(series=rates) # ---> Rolling trends
                    else:
                        sig, buffer = self.update_moving_average_and_buffer(series=rates, alpha=0.80) # ---> Rolling rates
                    
                    # Now trade trend or trade rate
                    if self.trade_trend: 
                        if sig > buffer:
                            position = "LONG"
                        elif sig < -buffer:
                            position = "SHORT"
                        else:
                            signal_exit = SignalEvent(liquidity_indexes[-1][0], "EXIT", liquidity_indexes[-1][1])
                            self.events.put(signal_exit)
                    else: 
                        if rates[-1] > sig + buffer:
                            position = "SHORT"
                        elif rates[-1] < sig - buffer:
                            position = "LONG"
                        else:
                            signal_exit = SignalEvent(liquidity_indexes[-1][0], "EXIT", liquidity_indexes[-1][1])
                            self.events.put(signal_exit)
                    
                    if position != self.prior_position:
                        # When changing from a net LONG/SHORT to a net SHORT/LONG we first have to net
                        # out the current position
                        if self.prior_position=="LONG": # --> Net out current VT
                            signal_net_out = SignalEvent(liquidity_indexes[-1][0], "SHORT", liquidity_indexes[-1][1])
                            self.events.put(signal_net_out)
                        if self.prior_position=="SHORT": # --> Net out curent FT
                            signal_net_out = SignalEvent(liquidity_indexes[-1][0], "LONG", liquidity_indexes[-1][1])
                            self.events.put(signal_net_out)
                        
                        signal = SignalEvent(liquidity_indexes[-1][0], position, liquidity_indexes[-1][1])
                        self.events.put(signal)
                        # Update new prior position to prevent N-counting of the same LONG, SHORT position
                        self.prior_position = position
                    
                    print(liquidity_indexes[-1][1], " ",  liquidity_indexes[-1][2], " ", rates[-1], " ", position)

    def liquidity_index_to_apy(self, rates):
        liq_idx = np.array([r[2] for r in rates])
        timestamps = np.array([r[1] for r in rates])
        apys = []
        for i in range(1, len(liq_idx)):
            window = i-self.apy_lookback if self.apy_lookback<i else 0
            variable_rate = (liq_idx[i]/liq_idx[window]) - 1.0 
            # Annualise the rate
            compounding_periods = SECONDS_IN_YEAR / (timestamps[i] - timestamps[window]).total_seconds()
            apys.append(((1 + variable_rate)**compounding_periods) - 1)
        return np.array(apys)

    @staticmethod
    def calculate_trend(apys):
        return np.array([np.log(apys[i]/apys[i-1]) for i in range(1, len(apys))])

    @staticmethod
    def update_beta(series):
        time_steps = np.arange(len(series)).reshape(-1,1)
        reg = RANSACRegressor(random_state=42).fit(time_steps, series.reshape(-1,1))
        beta = reg.estimator_.coef_.flatten()[0]
        return beta, 1e-5

    """
    Calculates the exponential moving average over a vector.
    Will fail for large inputs.
    :param data: Input data
    :param alpha: scalar float in range (0,1)
        The alpha parameter for the moving average.
    :param offset: optional
        The offset for the moving average, scalar. Defaults to data[0].
    :param dtype: optional
        Data type used for calculations. Defaults to float64 unless
        data.dtype is float32, then it will use float32.
    :param order: {'C', 'F', 'A'}, optional
        Order to use when flattening the data. Defaults to 'C'.
    :param out: ndarray, or None, optional
        A location into which the result is stored. If provided, it must have
        the same shape as the input. If not provided or `None`,
        a freshly-allocated array is returned.
    """
    @staticmethod
    def ewma_vectorized(data, alpha, offset=None, dtype=None, order='C', out=None):
        data = np.array(data, copy=False)

        if dtype is None:
            if data.dtype == np.float32:
                dtype = np.float32
            else:
                dtype = np.float64
        else:
            dtype = np.dtype(dtype)

        if data.ndim > 1:
            # flatten input
            data = data.reshape(-1, order)

        if out is None:
            out = np.empty_like(data, dtype=dtype)
        else:
            assert out.shape == data.shape
            assert out.dtype == dtype

        if data.size < 1:
            # empty input, return empty array
            return out

        if offset is None:
            offset = data[0]

        alpha = np.array(alpha, copy=False).astype(dtype, copy=False)

        # scaling_factors -> 0 as len(data) gets large
        # this leads to divide-by-zeros below
        scaling_factors = np.power(1. - alpha, np.arange(data.size + 1, dtype=dtype),
                                   dtype=dtype)
        # create cumulative sum array
        np.multiply(data, (alpha * scaling_factors[-2]) / scaling_factors[:-1],
                dtype=dtype, out=out)
        np.cumsum(out, dtype=dtype, out=out)

        # cumsums / scaling
        out /= scaling_factors[-2::-1]

        if offset != 0:
            offset = np.array(offset, copy=False).astype(dtype, copy=False)
            # add offsets
            out += offset * scaling_factors[1:]

        return out
    
    def update_moving_average_and_buffer(self, series, alpha=0.99):
        series = series[~np.isnan(series)] # Remove NaNs
        moving_average = self.ewma_vectorized(data=series[:-1], alpha=alpha).mean() # Trend up to, but excluding, latest bar
        moving_buffer = self.buffer * self.ewma_vectorized(data=series[:-1], alpha=alpha).std()/np.sqrt(len(series[:-1]))
        return moving_average, moving_buffer
    
