"""Shared helpers for the test/ua/ visual demo scripts."""

from oj_toolkit.console.colors import Color


def colored_bordered_box(box, color):
    """Color all box borders (top, bottom, sides) while keeping text plain.

    Args:
        box: Box instance to color
        color: ANSI color code (e.g., Color.BLUE, Color.GREEN)

    Returns:
        String with colored borders and plain text
    """
    lines = str(box).split('\n')
    result = []

    # Characters used for borders (ASCII and Unicode)
    border_chars = set('+-═║╔╗╚╝╭╮╰╯┌┐└┘├┤┬┴┼│─')

    for line in lines:
        if not line:
            result.append(line)
            continue

        # Check if this is a border line (only contains border chars and spaces)
        if all(c in border_chars for c in line.strip()):
            # Top or bottom border - color entire line
            result.append(color + line + Color.RESET)
        elif any(c in '|║' for c in line):
            # Content line with side borders - color the borders, keep text plain
            # Find the positions of the border characters (| or ║)
            side_chars = [i for i, c in enumerate(line) if c in '|║']

            if len(side_chars) >= 2:
                first_pos = side_chars[0]
                last_pos = side_chars[-1]

                left_border = color + line[:first_pos+1] + Color.RESET
                content = line[first_pos+1:last_pos]
                right_border = color + line[last_pos:] + Color.RESET
                result.append(left_border + content + right_border)
            else:
                result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)
