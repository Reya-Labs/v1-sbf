import queue


class EventLoop(object):

    # todo: add docs

    def __init__(self, events, rates, strategy, portfolio, executionHandler):

        self.events = events
        self.rates = rates
        self.strategy = strategy
        self.portfolio = portfolio
        self.executionHandler = executionHandler

    def run_outer_loop(self):

        while True:
            # Update the rates (specific backtest code, as opposed to live trading)
            if self.rates.continue_backtest:
                self.rates.update_rates()
            else:
                break

        self.run_inner_loop()

    def run_inner_loop(self):

        # Handle the events

        while True:
            try:
                event = self.events.get(False)
            except queue.Empty:
                break
            else:
                if event is not None:
                    if event.type == 'MARKET':
                        self.strategy.calculate_signals(event=event)
                        self.portfolio.update_timeindex(event=event)

                    elif event.type == 'SIGNAL':
                        self.portfolio.update_signal(event=event)

                    elif event.type == 'ORDER':
                        self.executionHandler.execute_order(event=event)

                    elif event.type == 'FILL':
                        self.portfolio.update_fill(event=event)