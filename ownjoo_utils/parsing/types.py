"""Parsing and type validation utilities for common data conversions.

This module provides functions to safely parse and validate values, including:
- String to list conversion with custom separators
- Datetime parsing from multiple formats
- Nested value extraction from dicts/lists
- Generic validation with custom converters and validators
"""

import logging
from datetime import datetime
from typing import Any, Callable, Optional, Type, Union, Iterable

from ownjoo_utils.parsing.consts import DEFAULT_SEPARATOR, DEFAULT_VALIDATOR, TimeFormats, DEFAULT_CONVERTER

logger = logging.getLogger(__name__)


def str_to_list(v: Optional[str] = None, separator: str = DEFAULT_SEPARATOR, **kwargs) -> Optional[list[str]]:
    """Convert a string to a list by splitting on a separator.

    Args:
        v: The string to split. If not a string, returns unchanged.
        separator: The delimiter to split on (default: comma). Empty string returns value unchanged.
        **kwargs: Additional keyword arguments (unused, for compatibility).

    Returns:
        A list of strings if v is a non-empty string with valid separator, otherwise the original value.

    Example:
        >>> str_to_list('a,b,c')
        ['a', 'b', 'c']
        >>> str_to_list('a;b;c', separator=';')
        ['a', 'b', 'c']
        >>> str_to_list(None)
        None
    """
    if not isinstance(v, str) or separator == '':
        return v
    if not isinstance(separator, str):
        separator = DEFAULT_SEPARATOR
    return v.split(separator)


def get_datetime(
        v: Union[None, datetime, float, str] = None,
        *args,
        format_str: Optional[str] = None,
        **kwargs
) -> Optional[datetime]:
    """Parse a value into a datetime object from multiple input formats.

    Supports parsing from:
    - datetime objects (returned as-is)
    - Numeric timestamps (seconds since epoch)
    - Strings matching known time formats (ISO 8601, HTTP date, custom format)

    Args:
        v: The value to parse. Can be None, datetime, float/int timestamp, or string.
        format_str: Optional custom datetime format string (strptime format). If provided, attempts parsing with this format first.
        **kwargs: Additional keyword arguments (unused, for compatibility).

    Returns:
        A datetime object if parsing succeeds, otherwise None.
        Logs exceptions at ERROR level if multiple formats parse to different values.

    Supported Formats:
        - ISO 8601: 'YYYY-MM-DDTHH:MM:SS'
        - HTTP: 'Sun, 06 Nov 1994 08:49:37 GMT'
        - Date and time: 'YYYY/MM/DD HH:MM:SS'
        - Custom format via format_str parameter

    Example:
        >>> get_datetime('2024-01-15T10:30:00')
        datetime.datetime(2024, 1, 15, 10, 30)
        >>> get_datetime(1234567890)
        datetime.datetime(2009, 2, 13, 23, 31, 30)
        >>> get_datetime('Sun, 06 Nov 1994 08:49:37 GMT')
        datetime.datetime(1994, 11, 6, 8, 49, 37)
    """
    result: Optional[datetime] = v
    _last_result: Optional[datetime] = None
    if v is None:
        pass
    elif isinstance(v, (float, int)):  # if number treat as a timestamp (seconds from epoch)
        try:
            result = datetime.fromtimestamp(v)
            if not _last_result:
                _last_result = result
            elif _last_result != result:
                raise ValueError(f'Found conflicting timestamp: previous: {_last_result}, current: {result}')
        except Exception as exc_num:
            logger.exception(f'Failed to parse {v=} as timestamp: {exc_num}')
    elif isinstance(format_str, str):
        try:
            result = datetime.strptime(v, format_str)
        except Exception as exc_str:
            logger.exception(f'Failed to parse {v=} as {format_str}: {exc_str}')
    elif isinstance(v, str):
        for time_format in TimeFormats:  # if str try to parse the str from a known format
            try:
                result = datetime.strptime(v, time_format.value)
                if not _last_result:
                    _last_result = result
                elif _last_result != result:
                    raise ValueError(f'Found conflicting timestamp: previous: {_last_result}, current: {result}')
                break
            except Exception as exc_str:
                logger.exception(f'Failed to parse {v=} as {time_format.value} ({time_format}): {exc_str}')
    return result


def validate(
        v: Any,
        exp: Type = None,
        default: Any = None,
        converter: Callable = None,
        validator: Optional[Callable] = DEFAULT_VALIDATOR,
        **kwargs
) -> Any:
    """Validate and optionally convert a value with a custom converter and validator.

    This is a generic validation utility that:
    1. Converts the value using a converter function (with automatic selection for common types)
    2. Validates the result using a validator function
    3. Returns the result if valid, otherwise returns the default value

    Args:
        v: The value to validate.
        exp: Expected type of the value. If None, no type conversion is attempted.
        default: The value to return if validation fails or v is None. Default: None.
        converter: Custom converter function. If None, one is selected based on exp:
            - exp=list: uses str_to_list
            - exp=datetime: uses get_datetime
            - otherwise: uses DEFAULT_CONVERTER (pass-through)
        validator: Custom validator function(result, exp, **kwargs) -> bool.
            If None, uses DEFAULT_VALIDATOR (isinstance check).
        **kwargs: Additional arguments passed to converter and validator functions.

    Returns:
        The converted and validated value, or the default value if validation fails.
        Returns None if no default is specified and validation fails.

    Example:
        >>> validate('123', exp=int, converter=int)
        123
        >>> validate('invalid', exp=int, default=0)
        0
        >>> validate('a,b,c', exp=list)
        ['a', 'b', 'c']
    """
    result: Any = v
    is_valid_result: bool = False

    # check pre-defined converters
    if not isinstance(converter, Callable):
        if exp is list:
            converter = str_to_list
        elif exp is datetime:
            converter = get_datetime
        else:
            converter = DEFAULT_CONVERTER  # pass through

    # convert values as needed
    try:
        result = converter(v, exp, **kwargs)
    except Exception as exc_str:
        logger.debug(f'Failed to parse {v=} with converter {converter}: {exc_str}', exc_info=True)

    # check validator
    if not validator:
        validator = DEFAULT_VALIDATOR

    try:
        is_valid_result = validator(result, exp, **kwargs)
    except Exception as exc_validation:
        logger.debug(f'Failed validation: {validator=}: {exc_validation=}', exc_info=True)

    if is_valid_result:
        return result
    else:
        return default


def get_value(
        src: Union[dict, Iterable],
        path: Union[None, int, list, str] = None,
        post_processor: Callable = validate,
        **kwargs
) -> Optional[Any]:
    """Extract and post-process a value from a nested data structure.

    Recursively navigates through nested dicts and lists using a path of keys/indices,
    then post-processes the result with a callable (default: validate).

    Args:
        src: A dict or list to navigate. If path is None, treated as a single value to post-process.
        path: List of keys (str) and indices (int/float) to navigate the structure.
            Example: ['data', 0, 'value'] extracts src['data'][0]['value']
            If None, src is treated as a single value to post-process.
        post_processor: Callable to post-process the found value. Default: validate().
            If None, the raw value is returned without post-processing.
        **kwargs: Additional arguments passed to post_processor function.

    Returns:
        The post-processed value, or None if extraction fails or no post-processor is specified.
        If path navigation fails (KeyError, IndexError, TypeError), logs and returns the post-processed src.

    Example:
        >>> src = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
        >>> get_value(src, path=['users', 0, 'name'])
        'Alice'
        >>> get_value(src, path=['users', 1, 'name'], exp=str)
        'Bob'
    """
    result: Any = None
    try:
        keydex: Union[None, float, int, str] = path.pop(0) if path and isinstance(path, list) else None
        result = src[keydex]
    except (IndexError, KeyError, TypeError) as exc_val:
        logger.debug(f'ERROR extracting {path=} from {src=}: {exc_val=}', exc_info=True)
    if path and isinstance(result, (dict, list)):  # keep digging if needed
        return get_value(src=result, path=path, **kwargs)
    elif isinstance(post_processor, Callable):  # call the post-processor if needed
        return post_processor(result or src, **kwargs)
    else:
        return result  # return found value without post-processing
