"""Tests for str_to_list()."""

import unittest

from oj_toolkit.parsing.types import str_to_list


class TestStrToList(unittest.TestCase):
    """Tests for str_to_list()."""

    def test_should_get_list_from_str(self):
        # setup
        expected: list = ['a', 'b', 'c']
        sep: str = ';'

        # execute
        actual = str_to_list(
            v=sep.join(expected),
            separator=sep,
        )

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_none_on_str_to_list_with_empty_separator(self):
        # setup
        value: str = 'a,b,c'

        # execute
        actual = str_to_list(v=value, separator='')

        # assess
        self.assertEqual(value, actual)

        # teardown

    def test_should_return_unchanged_on_str_to_list_with_non_string(self):
        # setup
        expected: int = 123

        # execute
        actual = str_to_list(v=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    # Happy path: str_to_list with various separators
    def test_should_split_with_custom_separator(self):
        # setup
        expected: list = ['hello', 'world', 'test']
        value: str = 'hello|world|test'

        # execute
        actual = str_to_list(v=value, separator='|')

        # assess
        self.assertEqual(expected, actual)

    def test_should_split_single_item(self):
        # setup
        expected: list = ['single']
        value: str = 'single'

        # execute
        actual = str_to_list(v=value)

        # assess
        self.assertEqual(expected, actual)

    def test_should_split_with_spaces(self):
        # setup
        expected: list = ['item1', 'item2', 'item3']
        value: str = 'item1 item2 item3'

        # execute
        actual = str_to_list(v=value, separator=' ')

        # assess
        self.assertEqual(expected, actual)

    # Unhappy path: str_to_list when separator not found
    def test_should_return_list_with_whole_string_when_separator_not_found(self):
        # setup
        value: str = 'noseparatorhere'
        expected: list = ['noseparatorhere']

        # execute
        actual = str_to_list(v=value, separator='|')

        # assess
        self.assertEqual(expected, actual)

    def test_should_return_none_on_str_to_list_with_none_input(self):
        # setup
        # execute
        actual = str_to_list(v=None)

        # assess
        self.assertIsNone(actual)

    # Edge case: str_to_list with single character separator
    def test_should_split_with_single_char_separator(self):
        # setup
        expected: list = ['a', 'b', 'c']
        value: str = 'a,b,c'

        # execute
        actual = str_to_list(v=value, separator=',')

        # assess
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
