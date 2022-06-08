# portfolio.py

import datetime
import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod
from math import floor

from event import FillEvent, OrderEvent


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



