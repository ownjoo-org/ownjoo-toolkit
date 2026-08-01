"""Tests for dig()."""

import unittest

from oj_toolkit.parsing.types import dig


class TestDig(unittest.TestCase):
    """Tests for dig()."""

    def test_should_get_value_from_list(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = dig(src=['', [expected]], path='[1][0]', exp=str, default='')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_value_from_dict(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = dig(src={'first': 'a', 'second': [expected]}, path='second[0]', exp=str)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_value_with_passed_validator(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = dig(src=expected, exp=str, validator=lambda x, *args, **kwargs: x == expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_handle_get_value_with_invalid_path(self):
        # setup
        src: dict = {'a': {'b': 'c'}}

        # execute
        actual = dig(src=src, path='x.y.z')

        # assess
        # When the path doesn't resolve, jmespath returns None. validate() is still
        # called (no exp given), and DEFAULT_VALIDATOR treats exp=None as "anything
        # passes", so the None value comes back unchanged.
        self.assertIsNone(actual)

        # teardown

    # Happy path: get_value with deeply nested structure
    def test_should_get_value_from_deeply_nested_dict(self):
        # setup
        expected: str = 'deep_value'
        src: dict = {
            'level1': {
                'level2': {
                    'level3': {
                        'target': expected
                    }
                }
            }
        }

        # execute
        actual = dig(src=src, path='level1.level2.level3.target', exp=str)

        # assess
        self.assertEqual(actual, expected)

    def test_should_get_value_from_mixed_dict_list_structure(self):
        # setup
        expected: str = 'mixed_value'
        src: dict = {
            'items': [
                {'id': 1, 'data': 'wrong'},
                {'id': 2, 'data': [expected, 'other']},
            ]
        }

        # execute
        actual = dig(src=src, path='items[1].data[0]', exp=str)

        # assess
        self.assertEqual(actual, expected)

    # Happy path: get_value with falsy extracted values
    def test_should_extract_zero_from_nested_structure(self):
        # setup
        src: dict = {'numbers': [1, 2, 0, 4]}

        # execute
        actual = dig(src=src, path='numbers[2]', exp=int)

        # assess
        self.assertEqual(actual, 0)

    def test_should_extract_empty_list_from_nested_structure(self):
        # setup
        src: dict = {'data': [[], 'other', 'items']}

        # execute
        actual = dig(src=src, path='data[0]', exp=list)

        # assess
        self.assertEqual(actual, [])

    # Unhappy path: get_value with missing intermediate key
    def test_should_return_default_on_missing_intermediate_key(self):
        # setup
        src: dict = {'a': {'b': 'value'}}

        # execute
        actual = dig(src=src, path='x.y.z', exp=str, default='default')

        # assess
        self.assertEqual(actual, 'default')

    # Unhappy path: get_value with mismatched index type
    def test_should_return_default_when_accessing_list_with_string_key(self):
        # setup
        src: dict = {'items': ['a', 'b', 'c']}

        # execute
        actual = dig(src=src, path='items.invalid_index', exp=str, default='default')

        # assess
        self.assertEqual(actual, 'default')

    # Happy path: get_value with no path (post-process source directly)
    def test_should_post_process_source_when_path_is_none(self):
        # setup
        value: str = 'test_string'

        # execute
        actual = dig(src=value, path=None, exp=str)

        # assess
        self.assertEqual(actual, value)

    # Happy path: get_value with no post_processor
    def test_should_return_raw_value_when_no_post_processor(self):
        # setup
        expected: str = 'raw_value'
        src: dict = {'key': expected}

        # execute
        actual = dig(src=src, path='key', post_processor=None)

        # assess
        self.assertEqual(actual, expected)

    # pop: removes terminal key from dict
    def test_should_pop_key_from_dict(self):
        # setup
        src: dict = {'a': 1, 'b': 2}

        # execute
        actual = dig(src=src, path='a', pop=True, exp=int)

        # assess
        self.assertEqual(actual, 1)
        self.assertNotIn('a', src)
        self.assertIn('b', src)

    # pop: removes terminal index from list
    def test_should_pop_index_from_list(self):
        # setup
        src: list = ['x', 'y', 'z']

        # execute
        actual = dig(src=src, path=1, pop=True, exp=str)

        # assess
        self.assertEqual(actual, 'y')
        self.assertEqual(src, ['x', 'z'])

    # pop: removes terminal key from nested structure
    def test_should_pop_nested_key(self):
        # setup
        src: dict = {'outer': {'inner': 42, 'keep': 99}}

        # execute
        actual = dig(src=src, path='outer.inner', pop=True, exp=int)

        # assess
        self.assertEqual(actual, 42)
        self.assertNotIn('inner', src['outer'])
        self.assertIn('keep', src['outer'])

    # pop=False: does not mutate source
    def test_should_not_pop_when_pop_is_false(self):
        # setup
        src: dict = {'a': 1}

        # execute
        actual = dig(src=src, path='a', pop=False, exp=int)

        # assess
        self.assertEqual(actual, 1)
        self.assertIn('a', src)

    # jmespath: simple expression string path
    def test_should_get_value_with_jmespath_string_path(self):
        # setup
        src: dict = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}

        # execute
        actual = dig(src=src, path='users[1].name', exp=str)

        # assess
        self.assertEqual(actual, 'Bob')

    # jmespath: wildcard projection, only expressible via a jmespath string
    def test_should_get_values_with_jmespath_wildcard(self):
        # setup
        src: dict = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}

        # execute
        actual = dig(src=src, path='users[*].name', exp=list)

        # assess
        self.assertEqual(actual, ['Alice', 'Bob'])

    # jmespath: a bare int path is treated as a single-segment path
    def test_should_get_value_with_single_int_path(self):
        # setup
        src: list = ['a', 'b', 'c']

        # execute
        actual = dig(src=src, path=1, exp=str)

        # assess
        self.assertEqual(actual, 'b')

    # jmespath: pop is supported for a simple (unambiguous) string path
    def test_should_pop_with_jmespath_string_path(self):
        # setup
        src: dict = {'outer': {'inner': 42, 'keep': 99}}

        # execute
        actual = dig(src=src, path='outer.inner', pop=True, exp=int)

        # assess
        self.assertEqual(actual, 42)
        self.assertNotIn('inner', src['outer'])
        self.assertIn('keep', src['outer'])

    # jmespath: pop is refused (not silently wrong) for an ambiguous filter expression
    def test_should_refuse_pop_with_ambiguous_jmespath_filter(self):
        # setup
        src: dict = {'items': [{'id': 1}, {'id': 2}]}

        # execute
        actual = dig(src=src, path='items[?id==`2`].id', pop=True, exp=list)

        # assess
        self.assertEqual(actual, [2])
        self.assertEqual(src, {'items': [{'id': 1}, {'id': 2}]})

    # jmespath: keys with special characters need a quoted identifier in the expression
    def test_should_get_value_with_quoted_identifier_for_special_characters(self):
        # setup
        src: dict = {'a-key': {'b': 'value'}}

        # execute
        actual = dig(src=src, path='"a-key".b', exp=str)

        # assess
        self.assertEqual(actual, 'value')

    # an invalid path segment type raises instead of silently returning None
    def test_should_raise_type_error_for_invalid_path_type(self):
        # setup
        src: dict = {'a': 1}

        # execute/assess
        with self.assertRaises(TypeError):
            dig(src=src, path=3.14)

    # fallback: path as a list of candidates tries each in order, first non-None wins
    def test_should_use_first_matching_path_in_fallback_list(self):
        # setup
        src: dict = {'user': {'name': 'Alice'}}

        # execute
        actual = dig(src=src, path=['user.nickname', 'user.name'], exp=str)

        # assess
        self.assertEqual(actual, 'Alice')

    # fallback: if every candidate misses, result is None
    def test_should_return_none_when_no_fallback_path_matches(self):
        # setup
        src: dict = {'user': {'name': 'Alice'}}

        # execute
        actual = dig(src=src, path=['user.nickname', 'user.alias'], exp=str)

        # assess
        self.assertIsNone(actual)

    # fallback: pop only removes the winning candidate's terminal key
    def test_should_pop_only_the_winning_fallback_path(self):
        # setup
        src: dict = {'user': {'name': 'Alice', 'nickname': 'Ali'}}

        # execute
        actual = dig(src=src, path=['user.nickname', 'user.name'], pop=True, exp=str)

        # assess
        self.assertEqual(actual, 'Ali')
        self.assertNotIn('nickname', src['user'])
        self.assertIn('name', src['user'])

    # DEFAULT_VALIDATOR: exp omitted should pass any value through, not crash
    def test_should_not_crash_when_exp_omitted_from_dig(self):
        # setup
        expected: str = 'blah'
        src: dict = {'key': expected}

        # execute
        actual = dig(src=src, path='key')

        # assess
        self.assertEqual(actual, expected)

    # dig() behavior matrix -- rows in the README table map 1:1 to these tests

    # missing path, exp given, no default -> None
    def test_should_return_none_for_missing_path_with_exp_and_no_default(self):
        # setup
        src: dict = {'a': {'b': 'value'}}

        # execute
        actual = dig(src=src, path='x.y.z', exp=str)

        # assess
        self.assertIsNone(actual)

    # found path, value doesn't match exp, no default -> None
    def test_should_return_none_for_dig_result_type_mismatch(self):
        # setup
        src: dict = {'a': 'not-an-int'}

        # execute
        actual = dig(src=src, path='a', exp=int)

        # assess
        self.assertIsNone(actual)

    # found path, value doesn't match exp, default given -> default
    def test_should_return_default_for_dig_result_type_mismatch(self):
        # setup
        src: dict = {'a': 'not-an-int'}

        # execute
        actual = dig(src=src, path='a', exp=int, default=-1)

        # assess
        self.assertEqual(actual, -1)

    # missing path, post_processor=None -> None, default is never consulted
    def test_should_return_none_for_missing_path_with_no_post_processor(self):
        # setup
        src: dict = {'a': 1}

        # execute
        actual = dig(src=src, path='missing', post_processor=None, default='default')

        # assess
        self.assertIsNone(actual)

    # a non-validate() post_processor (e.g. len) receives the found value directly
    def test_should_use_custom_post_processor_function(self):
        # setup
        src: dict = {'response': {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}}

        # execute
        actual = dig(src=src, path='response.users', post_processor=len)

        # assess
        self.assertEqual(actual, 2)

    # pattern= flows through dig() -> validate() and matches
    def test_should_validate_dig_result_with_matching_pattern(self):
        # setup
        src: dict = {'device': {'mac': 'AA:BB:CC:DD:EE:FF'}}

        # execute
        actual = dig(src=src, path='device.mac', exp=str, pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}')

        # assess
        self.assertEqual(actual, 'AA:BB:CC:DD:EE:FF')

    # pattern= flows through dig() -> validate() and falls back to default on mismatch
    def test_should_return_default_for_dig_result_with_non_matching_pattern(self):
        # setup
        src: dict = {'device': {'mac': 'not-a-mac'}}

        # execute
        actual = dig(
            src=src,
            path='device.mac',
            exp=str,
            pattern=r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}',
            default='invalid',
        )

        # assess
        self.assertEqual(actual, 'invalid')

    # a non-type exp passed through dig() is rejected (not raised), falls back to default
    def test_should_return_default_for_dig_with_non_type_expected_type(self):
        # setup
        src: dict = {'a': 'blah'}

        # execute
        actual = dig(src=src, path='a', exp='str', default='fallback')

        # assess
        self.assertEqual(actual, 'fallback')


if __name__ == '__main__':
    unittest.main()
