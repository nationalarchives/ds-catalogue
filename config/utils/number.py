"""
Number formatting utilities.
"""


def format_number(num) -> str:
    try:
        return format(int(num), ",")
    except ValueError:
        return num
