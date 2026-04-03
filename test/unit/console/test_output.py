"""Tests for console output utilities."""

import io
import unittest

from ownjoo_utils.console import Output


class TestOutput(unittest.TestCase):
    """Tests for the Output class."""

    def test_should_write_to_stdout(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("Hello", "World")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "Hello World\n")

    def test_should_write_to_stderr(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.err("Error", "Message")

        # assess
        self.assertEqual(stderr_capture.getvalue(), "Error Message\n")

    def test_should_use_custom_separator(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("a", "b", "c", sep=";")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "a;b;c\n")

    def test_should_use_custom_end(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("message", end=" - done\n")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "message - done\n")

    def test_should_write_multiple_values(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("Status:", 200, "OK")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "Status: 200 OK\n")

    def test_should_convert_non_string_to_string(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("Count:", 42, "Items:", 3.14)

        # assess
        self.assertEqual(stdout_capture.getvalue(), "Count: 42 Items: 3.14\n")

    def test_should_write_empty_string_to_stdout(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "\n")

    def test_should_write_empty_string_to_stderr(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.err("")

        # assess
        self.assertEqual(stderr_capture.getvalue(), "\n")

    def test_should_separate_stdout_and_stderr(self):
        # setup
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        output = Output(stdout=stdout_capture, stderr=stderr_capture)

        # execute
        output.out("to stdout")
        output.err("to stderr")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "to stdout\n")
        self.assertEqual(stderr_capture.getvalue(), "to stderr\n")

    def test_should_write_without_newline(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("no newline", end="")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "no newline")

    def test_should_write_multiple_lines(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("line1")
        output.out("line2")
        output.out("line3")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "line1\nline2\nline3\n")

    def test_err_should_respect_custom_separator(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.err("code", "message", "details", sep="|")

        # assess
        self.assertEqual(stderr_capture.getvalue(), "code|message|details\n")


if __name__ == "__main__":
    unittest.main()
