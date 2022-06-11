import unittest
import queue
from execution import SimulatedExecutionHandler
from event import OrderEvent
from datetime import datetime

class TestExecution(unittest.TestCase):

    def setUp(self):

        events_queue = queue.Queue()
        self.executionHandler = SimulatedExecutionHandler(
            events=events_queue
        )

    def test_execute_order(self):

        order = OrderEvent(
            token='aave_usdc',
            direction='LONG',
            timestamp=datetime.utcnow(),
            notional=10000,
            margin=100
        )

        self.executionHandler.execute_order(
            event=order
        )

        fillEvent = self.executionHandler.events.get()

        self.assertEqual(fillEvent.direction, "LONG")
        self.assertEqual(fillEvent.fee, 0.0)
        self.assertEqual(fillEvent.notional, 10000)
        self.assertEqual(fillEvent.margin, 100)
        # todo: test timestamp
        self.assertEqual(fillEvent.token, "aave_usdc")



if __name__ == '__main__':
    unittest.main()


