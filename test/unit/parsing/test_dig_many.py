"""Tests for dig_many()."""

import unittest

from oj_toolkit.parsing.types import dig_many


class TestDigMany(unittest.TestCase):
    """Tests for dig_many()."""

    # dig_many: extract several fields, bypassing post-processing to get raw values
    def test_should_extract_multiple_fields_with_dig_many(self):
        # setup
        src: dict = {'user': {'name': 'Alice', 'age': 30}}

        # execute
        actual = dig_many(src, paths={'name': 'user.name', 'age': 'user.age'}, post_processor=None)

        # assess
        self.assertEqual(actual, {'name': 'Alice', 'age': 30})

    # dig_many: a per-key spec dict overrides the common kwargs for just that key
    def test_should_override_kwargs_per_key_in_dig_many(self):
        # setup
        # 'age' is deliberately not a str, so it would fail the common exp=str
        # validation unless its own spec's exp=int override actually takes effect
        src: dict = {'user': {'name': 'Alice', 'age': 30}}

        # execute
        actual = dig_many(
            src,
            paths={
                'name': 'user.name',
                'age': {'path': 'user.age', 'exp': int},
            },
            exp=str,
        )

        # assess
        self.assertEqual(actual, {'name': 'Alice', 'age': 30})
        self.assertIsInstance(actual['age'], int)


if __name__ == '__main__':
    unittest.main()
