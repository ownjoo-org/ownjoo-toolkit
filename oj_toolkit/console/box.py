"""Box and frame building utilities.

Provides the Box class for wrapping text in decorative boxes with multiple
border styles, and the @in_box decorator for wrapping function output.
"""

import sys
from functools import wraps
from typing import Callable

from oj_toolkit.console.colors import Color
from oj_toolkit.console.terminal import (
    border_chars,
    pad_visible,
    select_style,
    visible_width,
)


class Box:
    """Builder for wrapping text in decorative boxes.

    Accumulates lines of text and renders them in a decorative box with
    configurable borders, padding, and optional title.

    Attributes:
        style: Border style ('auto', 'ascii', 'rounded', 'double', 'single', 'solid', 'none').
        padding: Number of spaces inside the box.
        width: Optional fixed box width (auto-calculates if None).
        title: Optional title displayed in the top border.
        border_color: Optional ANSI color code (e.g. Color.RED) applied to border
            characters only -- title and content keep whatever styling the caller
            already applied to them.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        style: str = "auto",
        padding: int = 1,
        width: int | None = None,
        title: str | None = None,
        border_color: str = "",
    ):
        """Initialize Box with style and configuration.

        Args:
            style: Border style. Default: 'auto' (detects terminal capabilities).
            padding: Inner padding in spaces. Default: 1.
            width: Optional fixed width. Default: None (auto-calculate).
            title: Optional title for top border. Default: None.
            border_color: Optional ANSI color code applied only to border
                characters (corners, edges, fill) -- e.g. Color.RED. Default: none.
        """
        self.style = select_style(style, "ascii", "rounded")
        self.padding = padding
        self.width = width
        self.title = title
        self.border_color = border_color
        self.lines = []

    def _b(self, text: str) -> str:
        """Wrap border-only text in border_color, if set."""
        if not self.border_color:
            return text
        return self.border_color + text + Color.RESET

    def add_line(self, text: str) -> "Box":
        """Add a line of text to the box.

        Args:
            text: Text to add (may contain ANSI codes).

        Returns:
            Self for method chaining.
        """
        self.lines.append(str(text))
        return self

    def add_lines(self, lines: list[str]) -> "Box":
        """Add multiple lines to the box.

        Args:
            lines: List of text strings.

        Returns:
            Self for method chaining.
        """
        for line in lines:
            self.add_line(line)
        return self

    def _calculate_content_width(self) -> int:
        """Calculate the maximum content width from all lines."""
        if not self.lines:
            return 0
        return max(visible_width(line) for line in self.lines)

    def _get_box_width(self) -> int:
        """Get the total box width including borders and padding."""
        if self.width:
            return self.width

        # Content width + padding on both sides + borders
        content_width = self._calculate_content_width()
        return content_width + (self.padding * 2) + 2

    def __str__(self) -> str:  # pylint: disable=too-many-locals
        """Render box as string with borders.

        Returns:
            Multi-line string with box drawn around content.
        """
        chars = border_chars(self.style)
        tl, tr, bl, br, top, bot, left, right, _cross = chars[:9]  # Use first 9 chars for box rendering

        box_width = self._get_box_width()
        inner_width = box_width - 2  # Account for left/right borders

        lines = []

        # Top border with optional title
        # Note: Titles work best with Unicode styles, ASCII may not have space
        if self.title and tl != "+" and tl != " ":
            # Unicode title box: [TL] Title [TR]
            # For ASCII, just skip the title
            # (4 fixed chars around the title -- 2 spaces + tl + tr -- but tl/tr
            # are outside inner_width, so only the 2 spaces come out of it here)
            # visible_width, not len(), so an ANSI-colored title doesn't throw
            # off the width math the same way plain len() would.
            title_space = inner_width - visible_width(self.title) - 2
            if title_space > 0:
                # Border segments colored individually so the title's own
                # styling (if any) survives untouched in the middle.
                top_line = (
                    self._b(tl + " ")
                    + self.title
                    + self._b(" " + (top * title_space) + tr)
                )
            else:
                top_line = self._b(tl + (top * inner_width) + tr)
        else:
            top_line = self._b(tl + (top * inner_width) + tr)

        lines.append(top_line)

        # Content lines
        if self.lines:
            for line in self.lines:
                padded = pad_visible(
                    line, inner_width - (self.padding * 2), align="left"
                )
                content = (
                    self._b(left)
                    + (" " * self.padding)
                    + padded
                    + (" " * self.padding)
                    + self._b(right)
                )
                lines.append(content)
        else:
            # Empty box with just padding
            padding_line = self._b(left) + (" " * inner_width) + self._b(right)
            lines.append(padding_line)

        # Bottom border
        bottom_line = self._b(bl + (bot * inner_width) + br)
        lines.append(bottom_line)

        return "\n".join(lines)

    def out(self, sep: str = "", end: str = "\n", flush: bool = False) -> None:
        """Print box to stdout.

        Args:
            sep: Separator (unused, for compatibility). Default: "".
            end: String appended after output (default: newline).
            flush: Whether to force flush (default: False).
        """
        print(str(self), sep=sep, end=end, file=sys.stdout, flush=flush)

    def err(self, sep: str = "", end: str = "\n", flush: bool = False) -> None:
        """Print box to stderr.

        Args:
            sep: Separator (unused, for compatibility). Default: "".
            end: String appended after output (default: newline).
            flush: Whether to force flush (default: False).
        """
        print(str(self), sep=sep, end=end, file=sys.stderr, flush=flush)


def in_box(
    style: str = "auto",
    padding: int = 1,
    width: int | None = None,
    title: str | None = None,
    border_color: str = "",
) -> Callable:
    """Decorator to wrap function output in a box.

    Wraps a function's return value in a decorative box.
    The function should return a string or list of strings.

    Args:
        style: Box style ('auto', 'ascii', 'rounded', 'double', 'single', 'solid', 'none').
            'auto' detects terminal capabilities. Default: 'auto'.
        padding: Number of spaces to pad inside the box. Default: 1.
        width: Optional box width. If None, auto-calculates based on content.
        title: Optional title to display in the top border.
        border_color: Optional ANSI color code for border characters only.

    Returns:
        Decorator function.

    Example:
        >>> from oj_toolkit.console import in_box
        >>> @in_box(style='double', title="Result")
        ... def show_result():
        ...     return "Success!"
        >>> show_result()  # Prints in double-line box with title
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            result = func(*args, **kwargs)

            # Handle different return types
            if result is None:
                lines = []
            elif isinstance(result, str):
                lines = [result]
            elif isinstance(result, (list, tuple)):
                lines = [str(item) for item in result]
            else:
                lines = [str(result)]

            # Create and populate box
            box = Box(
                style=style,
                padding=padding,
                width=width,
                title=title,
                border_color=border_color,
            )
            for line in lines:
                box.add_line(line)

            # Print the box
            box.out()

        return wrapper

    return decorator
