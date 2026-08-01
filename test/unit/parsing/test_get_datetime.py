"""Tests for get_datetime() and TimeFormats."""

import unittest
from datetime import datetime
from typing import Optional

from oj_toolkit.parsing.consts import TimeFormats
from oj_toolkit.parsing.types import get_datetime


class TestGetDatetime(unittest.TestCase):
    """Tests for get_datetime() and TimeFormats."""

    def test_should_get_time_formats(self):
        # setup

        # execute/assess
        for format_str in TimeFormats:
            self.assertIsNotNone(format_str)
            self.assertIsNotNone(format_str.value)

        # teardown

    def test_should_get_datetime_from_str(self):
        # setup
        expected: str = 'Sun, 06 Nov 1994 08:49:37 GMT'

        # execute
        actual: datetime = get_datetime(v=expected)

        # assess
        self.assertIsInstance(actual, datetime)

        # teardown

    def test_should_get_datetime_from_float(self):
        # setup
        expected: float = datetime.now().timestamp()

        # execute
        actual: datetime = get_datetime(v=expected)

        # assess
        self.assertIsInstance(expected, float)
        self.assertIsInstance(actual, datetime)

        # teardown

    def test_should_get_datetime_with_none_value(self):
        # setup
        expected: Optional[datetime] = None

        # execute
        actual = get_datetime(v=None)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_datetime_from_datetime_object(self):
        # setup
        expected: datetime = datetime(2024, 1, 15, 10, 30, 0)

        # execute
        actual = get_datetime(v=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    # Happy path: get_datetime with ISO 8601 format
    def test_should_get_datetime_from_iso_format(self):
        # setup
        expected_str: str = '2024-01-15T10:30:00'

        # execute
        actual = get_datetime(v=expected_str)

        # assess
        self.assertIsInstance(actual, datetime)
        self.assertEqual(actual.year, 2024)
        self.assertEqual(actual.month, 1)
        self.assertEqual(actual.day, 15)

    # Happy path: get_datetime with custom format
    def test_should_get_datetime_with_custom_format(self):
        # setup
        value: str = '15/01/2024 14:30'
        format_str: str = '%d/%m/%Y %H:%M'

        # execute
        actual = get_datetime(v=value, format_str=format_str)

        # assess
        self.assertIsInstance(actual, datetime)
        self.assertEqual(actual.day, 15)
        self.assertEqual(actual.month, 1)

    # Happy path: get_datetime with integer timestamp
    def test_should_get_datetime_from_integer_timestamp(self):
        # setup
        timestamp: int = 1234567890

        # execute
        actual = get_datetime(v=timestamp)

        # assess
        self.assertIsInstance(actual, datetime)
        self.assertEqual(actual.year, 2009)

    # Unhappy path: get_datetime with invalid string
    def test_should_return_none_on_get_datetime_with_invalid_string(self):
        # setup
        value: str = 'not a valid datetime'

        # execute
        actual = get_datetime(v=value)

        # assess
        self.assertIsNone(actual)

    # Unhappy path: get_datetime with invalid timestamp
    def test_should_return_none_on_get_datetime_with_invalid_timestamp(self):
        # setup
        value: float = 999999999999999999.999

        # execute
        actual = get_datetime(v=value)

        # assess
        self.assertIsNone(actual)

    # Edge case: get_datetime with zero timestamp
    def test_should_get_datetime_from_zero_timestamp(self):
        # setup
        value: int = 0

        # execute
        actual = get_datetime(v=value)

        # assess
        self.assertIsInstance(actual, datetime)
        # 0 represents epoch time (1970-01-01)


if __name__ == '__main__':
    unittest.main()
