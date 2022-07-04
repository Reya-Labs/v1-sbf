from strategy import Strategy
from event import SignalEvent
import pandas as pd
import numpy as np
import os
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import coint
import seaborn as sns
import matplotlib.pyplot as plt

SECONDS_IN_YEAR = 31536000
class StatisticalArbitragePairs(Strategy):

    def __init__(self, rates, events, pairs, lookback_window=30, apy_lookback=5, deviations=1.0, strategy_start="2022-04-01 00:00:00", monthly=False):
        
        self.rates = rates
        self.token_list = self.rates.token_list
        self.events = events
        self.lookback_window = lookback_window # Statistical arbitrage lookback window
        self.apy_lookback = apy_lookback
        self.deviations = deviations # How much to scale the standard deviation of the pairs ratio by
        self.pairs = pairs # The token pairs to arbitrage --> [(token1, token2), (token2, token4), (token1, token4), ...]
        self.prior_position = "EXIT" # Tracker for the first stat arb position
        self.strategy_start = pd.to_datetime(strategy_start)
        self.monthly = monthly

        if self.monthly:
            self.lookback_window = 90 # Make sure we look far back enough in the past

    """
        Compute z-score for downstream stat. arb. signal
        construction.
    """
    @staticmethod
    def z_score(series):
        return (series - series.mean())/series.std()

    """
        Generate an APY DataFame from the initial liquidity
        indices
    """
    def liquidity_index_to_apy_df(self, rates, token):
        liq_idx = np.array([r[2] for r in rates])
        timestamps = np.array([r[1] for r in rates])
        apys = []
        for i in range(1, len(liq_idx)):
            window = i-self.apy_lookback if self.apy_lookback<=i else 0
            variable_rate = liq_idx[i]/liq_idx[window] - 1.0 
            # Annualise the rate
            compounding_periods = SECONDS_IN_YEAR / (timestamps[i] - timestamps[window]).total_seconds()
            apys.append(((1 + variable_rate)**compounding_periods) - 1)
        df = pd.DataFrame(data={"Date": timestamps[1:], f"{token} APY": np.array(apys)})
        df.set_index("Date", inplace=True)
        return df

    
    """
        Summarise the signal update logic here
    """
    def signal_update_logic(self, signals, token1, token2, time1, time2):
        # Create signal - short if Z-score is greater than upper limit else long
        signals["Signals 1"] = 0
        signals["Signals 1"] = np.select([signals["Z"] > \
                        signals["Z upper limit"], signals["Z"] < signals["Z lower limit"]], [-1, 1], default=0)
        
        # We take the first order difference to obtain the execution signal
        # at the given timestamp
        signals["Positions 1"] = signals["Signals 1"].diff()
        
        # Repeat for the second token signal, going bear/bull if initial token is bull/bear          
        signals["Signals 2"] = -signals["Signals 1"]
        signals["Positions 2"] = signals["Signals 2"].diff()

        # Send the different positions to the execution handler
        # Just need to use replace to get LONG, SHORT, EXIT
        # Then send to the execution handler    
        signals["Positions 1"] = signals["Positions 1"].map({1: "LONG", -1: "SHORT", 0: "EXIT"})
        signals["Positions 2"] = signals["Positions 2"].map({1: "LONG", -1: "SHORT", 0: "EXIT"})
                        
        position_tracker = signals["Positions 1"].iloc[-1]
        if position_tracker != self.prior_position: # To ensure we only go LONG/SHORT once, until the signal changes 
            # Now we need to set up the positions 
            signal1 = SignalEvent(token1, signals["Positions 1"].iloc[-1], time1)
            signal2 = SignalEvent(token2, signals["Positions 2"].iloc[-1], time2)
            self.events.put(signal1)
            self.events.put(signal2)
            self.prior_position = position_tracker # Reset the prior position to LONG/SHORT
    
    """
        Take in the z-score and compute the bounds necessary to exit and
        enter positions, which we save as individual signals and run 
        over in the trading engine.
    """
    def calculate_signals(self, event):
        position_tracker = self.prior_position # Keep track of the first position to prevent double counting 
        if event.type == "MARKET":
            for pair in self.pairs:
                liq_idx_1 = self.rates.get_latest_rates(pair[0], N=self.lookback_window+1) 
                liq_idx_2 = self.rates.get_latest_rates(pair[1], N=self.lookback_window+1) 
                if liq_idx_1[-1][1] >= self.strategy_start: # Enter strategy
                    
                    df_1, df_2 = self.liquidity_index_to_apy_df(rates=liq_idx_1, token=pair[0]), \
                        self.liquidity_index_to_apy_df(rates=liq_idx_2, token=pair[1])
                    
                    # Make sure the pairs share common timestamps, by concatenating
                    signals = pd.concat([df_1, df_2], join="inner", axis=1)
                    signals.dropna(inplace=True)
                    
                    # Signal construction and analysis
                    signals["Ratios"] = signals[f"{pair[0]} APY"]/signals[f"{pair[1]} APY"]

                    if self.monthly:
                        # Currently using previous month's information, but this might be updated to a more "rolling"
                        # arbitrage strategy
                        signals["Year"] = np.array([int("-".join(i.strftime("%Y-%m-%d").split(" ")[0].split("-")[:1])) for i in signals.index])
                        signals["Month"] = np.array([int("-".join(i.strftime("%Y-%m-%d").split(" ")[0].split("-")[1:2])) for i in signals.index])

                        # Calculate z-score and define upper and lower thresholds (e.g. 1 standard deviation)
                        # Using previous month's means and spreads 
                        signals_collected = []
                        for y in signals["Year"].unique(): 
                            for m in signals["Month"].unique():
                                # Monthly change to signal values
                                (y_prev, m_prev) = (y-1, 12) if m==1 else (y, m-1)
                                signals_prev = signals.loc[lambda signals: (signals["Year"]== y_prev) & (signals["Month"]==m_prev)]
                                signals_temp = signals.loc[lambda signals: (signals["Year"]== y) & (signals["Month"]==m)]
                                z_prev = self.z_score(signals_prev["Ratios"])
                                signals_temp["Z"] = self.z_score(signals_temp["Ratios"])
                                signals_temp["Z upper limit"] = z_prev.mean() + z_prev.std()*self.deviations
                                signals_temp["Z lower limit"] = z_prev.mean() - z_prev.std()*self.deviations
                                signals_collected.append(signals_temp)
                        
                        signals = pd.concat(signals_collected) # Re-define signals DataFrame
                        self.signal_update_logic(signals=signals, token1=liq_idx_1[-1][0], token2=liq_idx_2[-1][0], time1=liq_idx_1[-1][1], time2=liq_idx_2[-1][1])                       
                    else:
                        # Use lookback_window
                        # We need to confirm the signals are still cointegrating over the lookback window
                        coint_check = coint(signals[f"{pair[0]} APY"], signals[f"{pair[1]} APY"])
                        if coint_check[1] >= 0.05: # Need to think more about this approac. Might be too conservative.
                            # Pairs are not cointegrated, and we need to exit existing trades and reset with EXIT
                            if position_tracker=="LONG":
                                signal1_exit = SignalEvent(liq_idx_1[-1][0], "SHORT", liq_idx_1[-1][1])
                                signal2_exit = SignalEvent(liq_idx_2[-1][0], "LONG", liq_idx_2[-1][1])
                                self.events.put(signal1_exit)
                                self.events.put(signal2_exit)
                            if position_tracker=="SHORT":
                                signal1_exit = SignalEvent(liq_idx_1[-1][0], "LONG", liq_idx_1[-1][1])
                                signal2_exit = SignalEvent(liq_idx_2[-1][0], "SHORT", liq_idx_2[-1][1])
                                self.events.put(signal1_exit)
                                self.events.put(signal2_exit)                      
                        
                            signal1 = SignalEvent(liq_idx_1[-1][0], "EXIT", liq_idx_1[-1][1])
                            signal2 = SignalEvent(liq_idx_2[-1][0], "EXIT", liq_idx_2[-1][1])
                    
                            # Exit first pair trade
                            self.events.put(signal1)

                            # Exit second pair trade
                            self.events.put(signal2)

                            # Reset 
                            self.prior_position = "EXIT"
                        else: # The pairs are actually cointegrated
                            print("COINTEGRATED")     
                            signals["Z"] = self.z_score(signals["Ratios"])
                            signals["Z upper limit"] = signals["Z"].mean() + signals["Z"].std()*self.deviations
                            signals["Z lower limit"] = signals["Z"].mean() - signals["Z"].std()*self.deviations
                            self.signal_update_logic(signals=signals, token1=liq_idx_1[-1][0], token2=liq_idx_2[-1][0], time1=liq_idx_1[-1][1], time2=liq_idx_2[-1][1])

    """
        Compute the fortnights for bi-monthly rebalancing
    """
    @staticmethod
    def get_fortnight(df):
        fnight = []
        num = 1
        counter = 0
        for i in range(len(df)):
            counter += 1
            if counter > 14:
                counter = 0
            num += 1
            fnight.append(num)
        df["Fnight"] = fnight  

    """
    Some additional methods to investigate if different pairs are coinintegated,
    and the associated statistical significances. These are not part of the signal-forming
    strategy managed by the execution handler downstream, but they can be called
    from the Stat Arb class for initial investigations between the pairs. Need to provide
    a DataFrame of the APYs to investigate this, together with stating and ending
    timestamps. The DataFrame can contain multiple APY series, and all pairwise 
    combinations are investigated.
    """

    def plot_coint_p_values(self, df, term_start="2020-02-29", term_end="2020-03-29"):

        df = df.loc[lambda df: (df["Date"] > term_start) & (df["Date"] < term_end)]
        pvalues, pairs = self.find_cointegrated_pairs(df=df)

        fig, ax = plt.subplots(figsize=(10, 7))
        sns.heatmap(pvalues, xticklabels=df.columns, yticklabels=df.columns, \
            cmap='RdYlGn_r', annot=True, fmt=".2f", mask=(pvalues >= 0.99))

        ax.set_title('Rates Cointregration Matrix p-values Between Pairs')
        plt.tight_layout()
        if not os.path.exists("./stat_arb_tests"):
            os.makedirs("./stat_arb_tests")
        plt.savefig(f'stat_arb_tests/cointegrated_pairs_{term_start}_{term_end}.png', dpi=300)
        plt.close()

    """
    Pairwise conintegration tests on an APY DataFrame. This can also be called to continuously check
    that the pairs remain cointegrated before making the stat arb trade 
    """
    @staticmethod
    def find_cointegrated_pairs(df):
        
        n = df.shape[1]
        p_value_matrix = np.ones((n, n))
        keys = df.columns.tolist()
        pairs = []

        for i in range(n):
            for j in range(i+1, n):

                series_1 = df.loc[:, keys[i]]
                series_2 = df.loc[:, keys[j]]

                result = coint(series_1, series_2)
                p_value_matrix[i, j] = result[1]
                if result[1] < 0.05:
                    pairs.append((keys[i], keys[j]))

        return p_value_matrix, pairs
    
    """
    Pairwise (Pearson) correlation matrix
    """
    @staticmethod
    def plot_correlation_matrix(df, term_start="2020-02-29", term_end="2020-03-29"):

        df = df.loc[lambda df: (df["Date"] > term_start) & (df["Date"] < term_end)]
        fig, ax = plt.subplots(figsize=(10, 7))
        sns.heatmap(df.corr(method="pearson"), ax=ax, cmap="coolwarm", annot=True, fmt=".2f")  

        ax.set_title('Rates Correlation Matrix')
        plt.tight_layout()
        if not os.path.exists("./stat_arb_tests"):
            os.makedirs("./stat_arb_tests")
        plt.savefig(f"stat_arb_tests/correlation_{term_start}_{term_end}.png", dpi=300)
        plt.close()


    def perform_stationarity_test(self, df, term_start="2020-02-29", term_end="2020-03-29", label=" APY"):
        
        df = df.loc[lambda df: (df["Date"] > term_start) & (df["Date"] < term_end)]
        for pair in self.pairs:
            train = pd.DataFrame()
            train['token_1'] = df.loc[:, pair[0]+label]
            train['token_2'] = df.loc[:, pair[1]+label]

            # Visualize rates
            ax = train[["token_1", "token_2"]].plot(figsize=(12, 6), title = f"Rates for {pair[0]} and {pair[1]}")
            ax.set_ylabel("Rate")
            ax.grid(True)
            if not os.path.exists("./stat_arb_tests"):
                os.makedirs("./stat_arb_tests")
            plt.savefig(f"stat_arb_tests/rates_{term_start}_{term_end}_{pair[0]}_{pair[1]}.png", dpi=300)
            plt.close()

            # Run OLS
            model = sm.OLS(train["token_1"], train["token_2"]).fit()

            # Regression summary results
            plt.rc('figure', figsize=(12, 7))
            plt.text(0.01, 0.05, str(model.summary()), {'fontsize': 16}, fontproperties='monospace')
            plt.axis('off')
            plt.tight_layout()
            plt.subplots_adjust(left=0.2, right=0.8, top=0.7, bottom=0.1)
            plt.savefig(f"stat_arb_tests/OLS_results_{term_start}_{term_end}_{pair[0]}_{pair[1]}.png", dpi=300)
            plt.close()

            print("Hedge Ratio = ", model.params[0])

            # Calculate spread
            spread = train['coin_1'] - model.params[0] * train['coin_2']

            # Plot spread
            ax = spread.plot(figsize=(12, 6), title="Rates Spread")
            ax.set_ylabel("Spread")
            ax.grid(True)
            plt.savefig(f'stat_arb_tests/spread_{term_start}_{term_end}_{pair[0]}_{pair[1]}', dpi=300)
            plt.close()

            # Conduct Augmented Dickey-Fuller test
            adf = adfuller(spread, maxlag=1)
            print("Critical Value = ", adf[0])

            # Critical values
            print("ADF critical values: ", adf[4])