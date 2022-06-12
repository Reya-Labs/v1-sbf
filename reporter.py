from abc import ABCMeta, abstractmethod


class Report(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_report(self):
        """
        Generates a report based on the results of the backtest
        """

        raise NotImplementedError("Should implement generate_report()")