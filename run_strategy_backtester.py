from backtest import LongShortMomentumStrategyBacktest as LSM
from reporter import SimpleBacktestReporter
import os

def main(start_date_time="2021-04-01 00:00:00", end_date_time="2022-06-01 00:00:00", leverage=1.0, \
            initial_capital=1.0, trend_lookback=15, apy_lookback=1, buffer=1.0):

    momentum_backtest = LSM(start_date_time=start_date_time,
                 end_date_time=end_date_time,
                 leverage=leverage, initial_capital=initial_capital,
                 trend_lookback=trend_lookback, apy_lookback=apy_lookback, buffer=buffer)

    # Run the backtest and get the output portfolio object
    output_portfolio = momentum_backtest.run_backtest()

    # Extract the equity curve for computing performance metics
    output_portfolio.create_equity_curve_dataframe()

    # Collect the summary statistics: Sharpe ratio and maximum drawdown
    stats = output_portfolio.output_summary_stats()

    # Use the Excel reporter to conveniently summarise all results of the backtest
    if not os.path.exists("./reports"):
        os.makedirs("./reports")
    reporter = SimpleBacktestReporter(backtest_results_df=output_portfolio.equity_curve, summary_stats=stats)
    reporter.generate_report(report_title=f"LongShortMomentum_lookback_{trend_lookback}_buffer_{buffer}_leverage_{leverage}")

    print("Backtest summary:")
    for s in stats:
        print(s[0]+ ": "+s[1])

if __name__=="__main__":
    # Adding an argument parser
    from argparse import ArgumentParser
    parser = ArgumentParser()
    
    parser.add_argument("-sd", "--start_date_time", type=str, help="Starting date for backtest", default="2021-04-01 00:00:00")
    parser.add_argument("-ed", "--end_date_time", type=str, help="Ending date for backtest", default="2022-06-01 00:00:00")
    parser.add_argument("-l", "--leverage", type=float, help="Leverage (notional / margin)", default=1.0)
    parser.add_argument("-i", "--initial_capital", type=float, help="Initial capital (notional before leverage)", default=1.0)
    parser.add_argument("-tl", "--trend_lookback", type=int, help="Lookback window for momentum following (e.g. days)", default=15)
    parser.add_argument("-al", "--apy_lookback", type=int, help="Lookback window for converting liquidity index to APY", default=1)
    parser.add_argument("-b", "--buffer", type=float, help="Buffer to apply to momentum spread in lookback window", default=1.0)

    params = parser.parse_args()
    param_dict = dict((k, v) for k, v in vars(params).items() if v is not None)
    print(param_dict)
    
    main(**param_dict)