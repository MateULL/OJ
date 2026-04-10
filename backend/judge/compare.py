from typing import List


def _normalize_output(value: str) -> List[str]:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def compare_output(actual: str, expected: str) -> bool:
    """Default OJ comparison: normalize newlines and ignore trailing spaces/blank tail."""
    return _normalize_output(actual) == _normalize_output(expected)
