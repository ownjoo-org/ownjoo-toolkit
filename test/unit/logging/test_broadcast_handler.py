"""Tests for BroadcastHandler."""

import asyncio
import logging
import unittest

from oj_toolkit.logging.handlers import BroadcastHandler


class TestBroadcastHandler(unittest.IsolatedAsyncioTestCase):
    """Tests for BroadcastHandler."""

    def setUp(self):
        self.handler = BroadcastHandler()
        self.handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))

    def _make_record(self, msg="hello", level=logging.INFO):
        return logging.LogRecord(
            name="test", level=level, pathname="", lineno=0,
            msg=msg, args=(), exc_info=None,
        )

    # ------------------------------------------------------------------
    # subscribe / unsubscribe

    def test_subscribe_returns_queue(self):
        q = self.handler.subscribe()
        self.assertIsInstance(q, asyncio.Queue)

    def test_unsubscribe_removes_queue(self):
        q = self.handler.subscribe()
        self.handler.unsubscribe(q)
        self.assertNotIn(q, self.handler._subscribers)  # pylint: disable=protected-access

    def test_unsubscribe_unknown_queue_is_silent(self):
        q: asyncio.Queue = asyncio.Queue()
        self.handler.unsubscribe(q)  # should not raise

    # ------------------------------------------------------------------
    # emit

    async def test_emit_delivers_to_subscriber(self):
        q = self.handler.subscribe()
        self.handler.emit(self._make_record("test message"))
        msg = q.get_nowait()
        self.assertIn("test message", msg)

    async def test_emit_delivers_to_multiple_subscribers(self):
        q1 = self.handler.subscribe()
        q2 = self.handler.subscribe()
        self.handler.emit(self._make_record("broadcast"))
        self.assertIn("broadcast", q1.get_nowait())
        self.assertIn("broadcast", q2.get_nowait())

    async def test_emit_no_subscribers_is_silent(self):
        # Should not raise when nobody is subscribed
        self.handler.emit(self._make_record("nobody home"))

    async def test_emit_drops_full_queue(self):
        handler = BroadcastHandler(maxsize=1)
        handler.setFormatter(logging.Formatter("%(message)s"))
        q = handler.subscribe()
        handler.emit(self._make_record("first"))   # fills the queue
        handler.emit(self._make_record("second"))  # queue full → dropped, subscriber removed
        self.assertNotIn(q, handler._subscribers)  # pylint: disable=protected-access

    async def test_emit_after_unsubscribe_does_not_deliver(self):
        q = self.handler.subscribe()
        self.handler.unsubscribe(q)
        self.handler.emit(self._make_record("should not arrive"))
        self.assertTrue(q.empty())

    # ------------------------------------------------------------------
    # formatting

    async def test_uses_handler_formatter(self):
        q = self.handler.subscribe()
        self.handler.emit(self._make_record("formatted", level=logging.WARNING))
        msg = q.get_nowait()
        self.assertTrue(msg.startswith("WARNING"))

    async def test_maxsize_respected(self):
        handler = BroadcastHandler(maxsize=3)
        q = handler.subscribe()
        self.assertEqual(q.maxsize, 3)


if __name__ == "__main__":
    unittest.main()
