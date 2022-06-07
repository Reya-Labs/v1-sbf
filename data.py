import datetime
import os, os.path
import pandas as pd

from abc import ABCMeta, abstractmethod

from event import MarketEvent


class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of rates for each token requested.

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_rates(self, token, N=1):
        """
        Returns the last N rates from the latest_token list,
        or fewer if less rates are available.
        """
        raise NotImplementedError("Should implement get_latest_rates()")

    @abstractmethod
    def update_rates(self):
        """
        Pushes the latest rate to the latest token structure
        for all tokens in the token list.
        """
        raise NotImplementedError("Should implement update_rates()")

