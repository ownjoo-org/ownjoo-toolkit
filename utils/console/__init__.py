"""Terminal and console output utilities.

Provides simple, efficient classes for writing to standard output and error streams,
with support for colored output using ANSI escape codes, chainable colored text builders,
and formatting utilities for tables, boxes, and status displays.
"""

from utils.console.box import Box, in_box
from utils.console.colored_text import ColoredText
from utils.console.colors import Color
from utils.console.status import (
    progress_bar,
    status_badge,
    status_line,
    status_wrapped,
)
from utils.console.streams import Output
from utils.console.table import Table, tabulated

__all__ = [
    "Output",
    "Color",
    "ColoredText",
    "Table",
    "tabulated",
    "Box",
    "in_box",
    "status_line",
    "progress_bar",
    "status_badge",
    "status_wrapped",
]
