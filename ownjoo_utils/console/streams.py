"""Stream output utilities for writing to stdout and stderr.

Provides a simple Output class for writing messages to standard output and error streams.
"""

import sys
from typing import Any, Optional, TextIO


class Output:
    """Simple wrapper for writing to stdout and stderr streams.

    Provides convenient methods for writing to standard output and error streams
    with optional file redirection.

    Attributes:
        stdout: The standard output stream (default: sys.stdout)
        stderr: The standard error stream (default: sys.stderr)
    """

    def __init__(
        self,
        stdout: Optional[TextIO] = None,
        stderr: Optional[TextIO] = None,
    ):
        """Initialize Output with optional custom streams.

        Args:
            stdout: The output stream for normal output. Default: sys.stdout
            stderr: The output stream for error messages. Default: sys.stderr
        """
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def out(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write to standard output stream.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).

        Example:
            >>> output = Output()
            >>> output.out("Hello", "World")
            Hello World
            >>> output.out("Status:", "OK", end=" - done\n")
            Status: OK - done
        """
        print(*args, sep=sep, end=end, file=self.stdout, flush=flush)

    def err(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write to standard error stream.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).

        Example:
            >>> output = Output()
            >>> output.err("Error:", "File not found")
            Error: File not found
            >>> output.err("Status code: 404", flush=True)
            Status code: 404
        """
        print(*args, sep=sep, end=end, file=self.stderr, flush=flush)
