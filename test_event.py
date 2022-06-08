import unittest
from event import MarketEvent, FillEvent, OrderEvent, SignalEvent
from datetime import datetime

TOKEN = "Aave USDC"
TIMESTAMP = datetime(2021, 11, 28, 23, 55, 59, 342380)
DIRECTION = "LONG"

class TestEvent(unittest.TestCase):


    def setUp(self):

        self.marketEvent = MarketEvent()
        self.signalEvent = SignalEvent(
            token=TOKEN,
            direction=DIRECTION,
            timestamp=TIMESTAMP
        )
        self.orderEvent = OrderEvent(
            token=TOKEN,
            timestamp=TIMESTAMP,
            notional=1000,
            direction=DIRECTION
        )

        self.fillEvent = FillEvent(
            token=TOKEN,
            slippage=0,
            fee=0,
            timestamp=TIMESTAMP,
            notional=1000,
            direction=DIRECTION
        )


    def test_events(self):

        self.assertEqual(self.marketEvent.type, 'MARKET')

        self.assertEqual(self.signalEvent.type, 'SIGNAL')
        self.assertEqual(self.signalEvent.token, TOKEN)
        self.assertEqual(self.signalEvent.direction, DIRECTION)
        self.assertEqual(self.signalEvent.timestamp, TIMESTAMP)

        self.assertEqual(self.orderEvent.type, 'ORDER')
        self.assertEqual(self.orderEvent.timestamp, TIMESTAMP)
        self.assertEqual(self.orderEvent.notional, 1000)
        self.assertEqual(self.orderEvent.direction, DIRECTION)

        self.assertEqual(self.fillEvent.type, 'FILL')
        self.assertEqual(self.fillEvent.token, TOKEN)
        self.assertEqual(self.fillEvent.timestamp, TIMESTAMP)
        self.assertEqual(self.fillEvent.notional, 1000)
        self.assertEqual(self.fillEvent.fee, 0)
        self.assertEqual(self.fillEvent.slippage, 0)



if __name__ == '__main__':
    unittest.main()