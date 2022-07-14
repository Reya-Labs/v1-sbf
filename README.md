# Voltz Strategy Backtesting Framework (SBF)

## Overview

The Voltz SBF is an event-driven backtesting system, designed to work with generic trading strategies and evaluate 
their historic performance. Strategies are provided as independent classes which must inheritit from the ```Strategy```
abstract base class. The strageies are evaluated on an event-by-event basis, with the ```Event``` abstract base class handling
the different types of trading events. The corresponding strategy portfolios are evaluated using the ```Portfolio``` class. 

We define four different events, each inheriting from ```Event```:

1) ```MarketEvent```: Handles the event of receiving new market data e.g. a fresh update from a rates database and/or rate oracle.
2) ```SignalEvent```: Handles the event of sending a Signal from a ```Strategy``` object. This is received by a ```Portfolio``` object and acted upon.
3) ```OrderEvent```:  Handles the event of sending an Order to an execution system. The order contains a token (e.g. "Aave USDC"), IRS Swap notional and a direction.
   Our in-build ```ExecutionHandler``` is resposible for the backtesting execution, mimicing a live trading system. 
4) ```FillEvent```: Instantiated events of this type encapsulate the notion of a Filled IRS swap order, as returned by the Voltz protocol after executing the trade.
   Stores the IRS notional actually traded and at what fixed rate. In addition, stores the fees of the trade collected by liquidity providers.

Both historical and live trading data are handled by a centralised and dedicated ```DataHandler``` object.  The ```DataHandler``` is an abstract base class providing 
an interface for all subsequent (inherited) data handlers (both live and historic). The goal of a (derived) DataHandler object is to output a generated
set of rates for each token requested. This replicates how a live strategy would function as current market data would be sent "down the pipe". Thus a historic and live
system will be treated identically by the rest of the backtesting suite.

## Individual components

The SBF is modular in that a generic strategy can be added as an independent class, as long as it inherits the baseline functionality from the 
```Strategy``` interface. This strategy can then be called and incorporated into the ```backtests.py``` script -- a clear illustration on how
each of these moving parts connect together can be arrived at my following the simplistsic ```LongRateStrategy``` class in the code, paying
attention to how it is called in ```backtest.py``` and the master script, ```run_strategy_backetster.py```, which asutomates the full
event loop of the SBF and outputs performance metrics for a given strategy and data-set. The core scripts are as follows:

1) ```backtest.py```: defines the ```Backtest``` abstract base class, from which all strategies to be backtests inherit as separate derived
   strategy backtest classes e.g. ```LongRateStrategyBacktest```.
2) ```data.py```: defines the ```DataHandler``` abstract base class, with its derived ```HistoricCSVDataHandler``` class for formatting and 
   processing historical rates like an event-level live trading system. 
3) ```dune.py```: ```Dune``` class for reading the latest on-chain results via Dune Analytics.
4) ```event_loop.py```: the guts of the event-level analysis, defining the actual heartbeat of the framework. Per heartbeat it runs inner and outer loops 
    over events and market rates respectively. 
5) ```event.py```: defines the ```Event``` base class and all subsequent derived events to be handled.
6) ```execution.py```: defines the ```ExecutionHandler``` base class and its derived class for handling historical data.
7) ```performance.py```: defined the ```PerformanceMetricsCalculator``` class, which calculate the Sharpe ratio and maximum drawdown for a given
   trading strategy. For a general introduction to Sharpe ratios, and their associated frequentist statistics, I highly recommend Andrew Lo's
   excellent paper: https://alo.mit.edu/wp-content/uploads/2017/06/The-Statistics-of-Sharpe-Ratios.pdf .
8) ```portfolio.py```: defines the ```Portfolio``` class, which handles the strartegy equity curve asnd PnL calculations, and calls the
   calculations in the ```PerformanceMetricsCalculaor```. 
9) ```reporter.py```: a class for genersting a simple Excel-style results report for the strategy. Called in ```run_strategy_backtester.py```.
10) ```run_strategy_backtester.py```: master script which calls generic srategy backtests and runs the full event-level analysis. 
11) ```strategy.py```: defines the ```Strategy``` abstracct base class, from which all trading strategies inherit the functionality for
    computing individual signals and assigning long/short/exit positions per market heartbeat.
12) ```test_*.py```: unit testing scripts for the key SBF components and strategies. Every time a new strategy is created, a corresponding unit
    test class should also be implemented for good testing and continuous integration practice. 

# Terms & Conditions
The Voltz Protocol, and any products or services associated therewith, is offered only to persons (aged 18 years or older) or entities who are not residents of, citizens of, are incorporated in, owned or controlled by a person or entity in, located in, or have a registered office or principal place of business in any “Restricted Territory.”

The term Restricted Territory includes the United States of America (including its territories), Algeria, Bangladesh, Bolivia, Belarus, Myanmar (Burma), Côte d’Ivoire (Ivory Coast), Egypt, Republic of Crimea, Cuba, Democratic Republic of the Congo, Iran, Iraq, Liberia, Libya, Mali, Morocco, Nepal, North Korea, Oman, Qatar, Somalia, Sudan, Syria, Tunisia, Venezuela, Yemen, Zimbabwe; or any jurisdictions in which the sale of cryptocurrencies are prohibited, restricted or unauthorized in any form or manner whether in full or in part under the laws, regulatory requirements or rules in such jurisdiction; or any state, country, or region that is subject to sanctions enforced by the United States, such as the Specially Designed Nationals and Blocked Persons List (“SDN List”) and Consolidated Sanctions List (“Non-SDN Lists”), the United Kingdom, or the European Union.