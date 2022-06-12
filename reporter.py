from abc import ABCMeta, abstractmethod


class Reporter(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_report(self):
        """
        Generates a report based on the results of the backtest
        """

        raise NotImplementedError("Should implement generate_report()")


class SimpleBacktestReporter(Reporter):


    def __init__(self, backtest_results_df, summary_stats):

        self.backtest_results_df = backtest_results_df
        self.summary_stats = summary_stats

    def generate_report(self):

        print("here")

