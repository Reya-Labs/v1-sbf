from backtest import LongShortMomentumStrategyBacktest as LSM
from data import DataHandler
from reporter import SimpleBacktestReporter
import os
import optuna
import numpy as np
import json

RUN_OPTUNA = False
def main(start_date_time="2021-04-01 00:00:00", end_date_time="2022-06-01 00:00:00", leverage=1.0, \
            initial_capital=1.0, trend_lookback=15, apy_lookback=1, buffer=1.0, trade_trend=False):

    momentum_backtest = LSM(start_date_time=start_date_time,
                 end_date_time=end_date_time,
                 leverage=leverage, initial_capital=initial_capital,
                 trend_lookback=trend_lookback, apy_lookback=apy_lookback, buffer=buffer,
                 trade_trend=trade_trend)

    # Run the backtest and get the output portfolio object
    output_portfolio = momentum_backtest.run_backtest()

    # Extract the equity curve for computing performance metics
    output_portfolio.create_equity_curve_dataframe()

    # Collect the summary statistics: Sharpe ratio and maximum drawdown
    stats = output_portfolio.output_summary_stats()


    # Use the Excel reporter to conveniently summarise all results of the backtest
    end = end_date_time.split(" ")[0]
    if not os.path.exists(f"./reports/{end}"):
        os.makedirs(f"./reports/{end}")
    name = output_portfolio.equity_curve.columns[3]
    reporter = SimpleBacktestReporter(backtest_results_df=output_portfolio.equity_curve, summary_stats=stats)
    if trade_trend:
        reporter.generate_report(report_title=f"LongShortMomentum_TREND_{name}_trend_lookback_{trend_lookback}_apy_lookback_{apy_lookback}_buffer_{buffer}_leverage_{leverage}")
        output_portfolio.equity_curve.to_csv(f"./reports/{end}/df_LongShortMomentum_TREND_{name}_lookback_{trend_lookback}days_apy_lookback_{apy_lookback}_buffer_{buffer}_leverage_{leverage}.csv")
    else:
        reporter.generate_report(report_title=f"LongShortMomentum_RATE_{name}_trend_lookback_{trend_lookback}_apy_lookback_{apy_lookback}_buffer_{buffer}_leverage_{leverage}")
        output_portfolio.equity_curve.to_csv(f"./reports/{end}/df_LongShortMomentum_RATE_{name}_lookback_{trend_lookback}days_apy_lookback_{apy_lookback}_buffer_{buffer}_leverage_{leverage}.csv")

    print("Backtest summary:")
    print(stats)
    for s in stats:
        print(s[0]+ ": "+s[1])

    if RUN_OPTUNA:
        #obj = float(stats[1][1]) - 10*int(float(stats[2][1][:-1]) > 10.0) # Penalise maximum drawdown > 10 %
        obj = float(stats[1][1]) - float(stats[2][1][:-1])
        return obj 

def objective(trial):
    
    trend_lookback = trial.suggest_categorical("trend_lookback", np.arange(3, 50, 1).tolist())
    apy_lookback = trial.suggest_categorical("apy_lookback", np.arange(3, 50, 1).tolist())
    buffer = trial.suggest_categorical("buffer", np.linspace(0.0, 2, 2000).tolist())

    obj = main(start_date_time="2021-04-01 00:00:00", end_date_time="2022-02-01 00:00:00", leverage=1.0, \
            initial_capital=1.0, trend_lookback=trend_lookback, apy_lookback=apy_lookback, buffer=buffer)

    return obj

def run_single(parser):
    
    parser.add_argument("-sd", "--start_date_time", type=str, help="Starting date for backtest", default="2021-04-01 00:00:00")
    parser.add_argument("-ed", "--end_date_time", type=str, help="Ending date for backtest", default="2022-06-01 00:00:00")
    parser.add_argument("-l", "--leverage", type=float, help="Leverage (notional / margin)", default=1.0)
    parser.add_argument("-i", "--initial_capital", type=float, help="Initial capital (notional before leverage)", default=1.0)
    parser.add_argument("-tl", "--trend_lookback", type=int, help="Lookback window for momentum following (e.g. days)", default=15)
    parser.add_argument("-al", "--apy_lookback", type=int, help="Lookback window for converting liquidity index to APY", default=1)
    parser.add_argument("-b", "--buffer", type=float, help="Buffer to apply to momentum spread in lookback window", default=1.0)
    parser.add_argument("-t", "--trade_trend", action="store_true", help="Run simple trend-following strategy", default=False)

    params = parser.parse_args()
    param_dict = dict((k, v) for k, v in vars(params).items() if v is not None)
    print(param_dict)
    
    main(**param_dict)

def run_optimisation(parser):

    parser.add_argument("-n_trials", "--n_trials", type=float, help="Number of optimization trials", default=2)
    n_trials = parser.parse_args().n_trials

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(), pruner=optuna.pruners.SuccessiveHalvingPruner())
    study.optimize(objective, n_trials=n_trials)
    
    # Relevant output plots
    out_dir = "./Momentum_optimisation/"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Output optimised results
    trial = study.best_trial
    print(f"Best optimised value: {trial.value}")

    print("Optimised parameters: ")
    for key, value in trial.params.items():
        print(f"{key}: {value}")
    
    fig = optuna.visualization.plot_optimization_history(study)
    fig.write_image(out_dir+f"optuna_history.png")

    fig = optuna.visualization.plot_param_importances(study)
    fig.write_image(out_dir+f"optuna_importances.png")
    
    with open(out_dir+f"optimised_parameters.json", "w") as fp:
        json.dump(trial.params, fp, indent=4)

if __name__=="__main__":
    # Adding an argument parser
    from argparse import ArgumentParser
    parser = ArgumentParser()

    if RUN_OPTUNA:
        run_optimisation(parser=parser)
    else:
        run_single(parser=parser)
    