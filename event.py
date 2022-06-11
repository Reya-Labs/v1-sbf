# event.py

class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding rates data.
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = 'MARKET'



class SignalEvent(Event):

    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, token, direction, timestamp):
        """
        Initialises the SignalEvent.

        Parameters:
        token - Underlying yield bearing pool, e.g. "Aave USDC"
        timestamp - The timestamp at which the signal was generated
        direction - 'LONG' or 'SHORT'.
        """

        self.type = 'SIGNAL'
        self.token = token
        self.timestamp = timestamp
        self.direction = direction


# event.py

class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a token (e.g. "Aave USDC"),
    IRS Swap notional and a direction.
    """

    def __init__(self, token, direction, timestamp, notional, margin):
        """
        Initialises the order event which has
        a IRS notional traded and its direction, 'LONG/VT' or
        'SHORT/FT'.

        VT is considered long since variable takers are long rates
        FT is considered short since fixed takers are short rates

        Parameters:
        token - Underlying yield bearing pool, e.g. "Aave USDC"
        timestamp - The timestamp at which the signal was generated
        direction - 'LONG' or 'SHORT'.
        notional - Non-negative integer for notional amount (margin*leverage) traded
        margin   - Non-negative integer for margin amount (i.e. collateral to support the IRS position)
        """

        self.type = 'ORDER'
        self.token = token
        self.timestamp = timestamp
        self.direction = direction
        self.notional = notional
        self.margin = margin

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print("Order: Token=%s, Timestamp=%s, Notional=%s, Notional=%s, Direction=%s" % \
              (self.token, self.timestamp, self.notional, self.margin, self.direction))




class FillEvent(Event):
    """
    Encapsulates the notion of a Filled IRS swap order, as returned
    from the protocol after executing the trade.

    Stores the IRS notional actually traded and at what fixed rate.

    In addition, stores the fees of the trade collected by liquidity providers.
    """

    def __init__(self, token, fee, timestamp, notional, margin, direction):
        """
        Initialises the FillEvent object. Sets the token, slippage,
        fees, timestamp, notional & direction

        Parameters:
        token - Underlying yield bearing pool, e.g. "Aave USDC"
        timestamp - The timestamp at which the signal was generated
        direction - 'LONG' or 'SHORT'.
        notional - Non-negative integer for notional amount (margin*leverage) traded
        margin   - Non-negative integer for margin amount (i.e. collateral to support the IRS position)
        fee      - fee paid by the trader to the liquidity providers in the IRS Pool
        """

        self.type = 'FILL'
        self.token = token
        self.timestamp = timestamp
        self.direction = direction
        self.notional = notional
        self.margin = margin
        self.fee = fee

        # we can additionally introduce self.slippage to have more realistic market impact calculations