"""Tests for validate()."""

import re
import unittest
from typing import Optional

from oj_toolkit.parsing.types import validate


class TestValidate(unittest.TestCase):
    """Tests for validate()."""

    def test_should_get_validated_type(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = validate(v=expected, exp=str, default='')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_default_type(self):
        # setup
        expected: str = ''

        # execute
        actual = validate(v=[], exp=str, default=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_list_from_str(self):
        # setup
        expected: list = ['a', 'b', 'c']
        abc: str = ','.join(expected)

        # execute
        actual = validate(v=abc, exp=list)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_dict(self):
        # setup
        expected: dict = {0: 'a', 1: 'b', 2: 'c'}

        # execute
        actual = validate(v=expected, exp=dict)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_default_dict(self):
        # setup
        expected: dict = {}

        # execute
        actual = validate(v='not a dict', exp=dict, default={})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_none(self):
        # setup
        expected: Optional[dict] = None

        # execute
        actual = validate(v='not a dict', exp=dict)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_with_validator(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = validate(v=expected, exp=str, validator=lambda x, *args, **kwargs: x == expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_default_on_validation_fail(self):
        # setup
        expected: str = ''

        # execute
        actual = validate(v='blah', exp=str, validator=lambda x, *args, **kwargs: x is None, default=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_with_converter(self):
        # setup
        expected: str = 'blah'
        unwanted: str = '_more'

        # execute
        actual = validate(
            v=f'{expected}{unwanted}',
            exp=str,
            converter=lambda x, *args, **kwargs: x.removesuffix(unwanted),
            validator=lambda x, *args, **kwargs: x == expected,
        )

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_validate_none_value_with_default(self):
        # setup
        expected: str = 'default'

        # execute
        actual = validate(v=None, exp=str, default=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    # Happy path: validate with falsy values
    def test_should_validate_zero_as_integer(self):
        # setup
        value: int = 0

        # execute
        actual = validate(v=value, exp=int)

        # assess
        self.assertEqual(actual, 0)
        self.assertIsInstance(actual, int)

    def test_should_validate_empty_string(self):
        # setup
        value: str = ''

        # execute
        actual = validate(v=value, exp=str)

        # assess
        self.assertEqual(actual, '')
        self.assertIsInstance(actual, str)

    def test_should_validate_false_boolean(self):
        # setup
        value: bool = False

        # execute
        actual = validate(v=value, exp=bool)

        # assess
        self.assertEqual(actual, False)
        self.assertIsInstance(actual, bool)

    # Unhappy path: validate with converter that raises exception
    def test_should_return_default_when_converter_raises_exception(self):
        # setup
        def failing_converter(v, **kwargs):
            raise ValueError('Conversion failed')

        expected: str = 'default_value'

        # execute
        actual = validate(v='test', converter=failing_converter, exp=str, default=expected)

        # assess
        self.assertEqual(actual, expected)

    # Unhappy path: validate with validator that raises exception
    def test_should_return_default_when_validator_raises_exception(self):
        # setup
        def failing_validator(v, *args, **kwargs):
            raise ValueError('Validation failed')

        expected: str = 'default_value'

        # execute
        actual = validate(v='test', exp=str, validator=failing_validator, default=expected)

        # assess
        self.assertEqual(actual, expected)

    # Edge case: validate with None as default (explicit)
    def test_should_allow_none_as_default_value(self):
        # setup
        # execute
        actual = validate(v=[], exp=str, default=None)

        # assess
        self.assertIsNone(actual)

    # Edge case: validate with no explicit default (should return None)
    def test_should_return_none_when_validation_fails_with_no_default(self):
        # setup
        # execute
        actual = validate(v=[], exp=str)

        # assess
        self.assertIsNone(actual)

    # DEFAULT_VALIDATOR: exp omitted should pass any value through, not crash
    def test_should_not_crash_when_exp_omitted_from_validate(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = validate(v=expected)

        # assess
        self.assertEqual(actual, expected)

    # DEFAULT_VALIDATOR: a non-type garbage expected_type is rejected, not raised
    def test_should_return_false_for_non_type_expected_type(self):
        # setup
        # execute
        actual = validate(v='blah', exp='str', default='fallback')

        # assess
        self.assertEqual(actual, 'fallback')

    # pattern: matching regex passes the value through
    def test_should_validate_with_matching_pattern(self):
        # setup
        expected: str = 'AA:BB:CC:DD:EE:FF'

        # execute
        actual = validate(v=expected, exp=str, pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}')

        # assess
        self.assertEqual(actual, expected)

    # pattern: non-matching regex falls back to default
    def test_should_return_default_with_non_matching_pattern(self):
        # setup
        expected: str = 'invalid'

        # execute
        actual = validate(
            v='not-a-mac',
            exp=str,
            pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}',
            default=expected,
        )

        # assess
        self.assertEqual(actual, expected)

    # pattern: a pre-compiled re.Pattern is accepted directly
    def test_should_accept_precompiled_pattern(self):
        # setup
        expected: str = 'abc123'

        # execute
        actual = validate(v=expected, exp=str, pattern=re.compile(r'[a-z]+\d+'))

        # assess
        self.assertEqual(actual, expected)

    # pattern: is only checked against str results, not other types
    def test_should_ignore_pattern_for_non_str_result(self):
        # setup
        expected: list = ['a', 'b']

        # execute
        actual = validate(v=expected, exp=list, pattern=r'.*')

        # assess
        self.assertEqual(actual, expected)

    # Intentional: exp=bool/int/float do NOT auto-coerce strings -- callers must pass
    # their own converter= if they want e.g. 'yes' -> True or '42' -> 42.
    def test_should_not_auto_coerce_string_to_bool(self):
        # setup
        expected: bool = False

        # execute
        actual = validate(v='yes', exp=bool, default=expected)

        # assess
        self.assertEqual(actual, expected)

    def test_should_not_auto_coerce_string_to_int(self):
        # setup
        expected: int = 0

        # execute
        actual = validate(v='42', exp=int, default=expected)

        # assess
        self.assertEqual(actual, expected)

    def test_should_not_auto_coerce_string_to_float(self):
        # setup
        expected: float = 0.0

        # execute
        actual = validate(v='9.5', exp=float, default=expected)

        # assess
        self.assertEqual(actual, expected)

    # Coercion is still available on demand via an explicit converter=
    def test_should_coerce_string_to_int_with_explicit_converter(self):
        # setup
        expected: int = 42

        # execute
        actual = validate(v='42', exp=int, converter=int)

        # assess
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
