import math
import re


CHANNEL_VALUE_PATTERN = re.compile(
    r"\bCH(?P<channel>[0-9]|1[0-5])\b"
    r"\s*(?:=|:|\(|,)?\s*"
    r"(?P<value>[-+]?(?:\d+(?:\.\d*)?|\.\d+))",
    re.IGNORECASE,
)


def check_rows55_56(rows, file_type):
    """
    Check both Row 55 and Row 56.

    For each row independently:
        - Search the entire row for CH0 ~ CH15.
        - Extract one numeric value for each CHx.
        - Calculate the 16-channel mean.
        - Calculate the 16-channel population STD.
        - Require every CHx value to be within:

              mean +/- 3 * population STD

    Both rows must pass.
    All row failures are collected.
    """

    if file_type not in ("RT", "LN"):
        return False, {
            "fail_code": (
                f"FAIL: unsupported file type: {file_type}"
            )
        }

    failures = []
    parsed = {}

    for row_number in (55, 56):
        passed, result = _check_row(
            rows=rows,
            row_number=row_number,
        )

        for key, value in result.items():
            if key != "fail_code":
                parsed[f"Row{row_number}_{key}"] = value

        if not passed:
            failures.append(
                result.get(
                    "fail_code",
                    f"FAIL: row {row_number} failed",
                )
            )

    if failures:
        return False, {
            "fail_code": " | ".join(failures),
            **parsed,
        }

    return True, {
        "fail_code": "",
        **parsed,
    }


def check_row55(rows, file_type):
    """Check Row 55 only."""
    if file_type not in ("RT", "LN"):
        return False, {
            "fail_code": (
                f"FAIL: unsupported file type: {file_type}"
            )
        }

    return _check_row(
        rows=rows,
        row_number=55,
    )


def check_row56(rows, file_type):
    """Check Row 56 only."""
    if file_type not in ("RT", "LN"):
        return False, {
            "fail_code": (
                f"FAIL: unsupported file type: {file_type}"
            )
        }

    return _check_row(
        rows=rows,
        row_number=56,
    )


def _check_row(rows, row_number):
    row_index = row_number - 1

    # --------------------------------------------------
    # Row exists
    # --------------------------------------------------

    if len(rows) <= row_index:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} is missing"
            )
        }

    row = rows[row_index]

    if len(row) < 2:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} is incomplete"
            )
        }

    # --------------------------------------------------
    # Actual Column A / B values
    # --------------------------------------------------

    col_a_value = str(row[0]).strip()
    col_b_value = str(row[1]).strip()

    if not col_a_value:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} column A is empty"
            )
        }

    if not col_b_value:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} column B is empty"
            )
        }

    # --------------------------------------------------
    # Search entire row for CH0 ~ CH15
    # --------------------------------------------------

    channel_values = {}

    for cell in row:
        text = str(cell).strip()

        for match in CHANNEL_VALUE_PATTERN.finditer(text):
            channel_number = int(
                match.group("channel")
            )

            # Keep first occurrence of each channel.
            if channel_number in channel_values:
                continue

            channel_values[channel_number] = float(
                match.group("value")
            )

    # --------------------------------------------------
    # Require all 16 channels
    # --------------------------------------------------

    missing_channels = [
        f"CH{channel}"
        for channel in range(16)
        if channel not in channel_values
    ]

    if missing_channels:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "missing/unreadable channels: "
                + ", ".join(missing_channels)
            )
        }

    # --------------------------------------------------
    # Calculate mean and population STD
    # --------------------------------------------------

    values = [
        channel_values[channel]
        for channel in range(16)
    ]

    mean_value = _mean(values)
    std_value = _population_std(values)

    lower_limit = (
        mean_value - 3.0 * std_value
    )

    upper_limit = (
        mean_value + 3.0 * std_value
    )

    # --------------------------------------------------
    # Check every channel
    # --------------------------------------------------

    failures = []

    for channel in range(16):

        value = channel_values[channel]

        if not lower_limit <= value <= upper_limit:
            failures.append(
                (
                    f"CH{channel}: value={value} "
                    f"outside 3STD range "
                    f"({lower_limit:.6g} ~ "
                    f"{upper_limit:.6g})"
                )
            )

    result = {
        "Column_A": col_a_value,
        "Column_B": col_b_value,

        "CH_Mean_16CH": mean_value,
        "CH_STD_16CH": std_value,
        "CH_Lower_3STD": lower_limit,
        "CH_Upper_3STD": upper_limit,
    }

    # Keep each parsed channel value internally.
    for channel in range(16):
        result[f"CH{channel}"] = (
            channel_values[channel]
        )

    if failures:
        result["fail_code"] = (
            f"FAIL: row {row_number} - "
            + " | ".join(failures)
        )

        return False, result

    result["fail_code"] = ""

    return True, result


def _mean(values):
    if not values:
        raise ValueError(
            "Cannot calculate mean of an empty list."
        )

    return sum(values) / len(values)


def _population_std(values):
    """
    Population standard deviation.

    All 16 channels are treated as the complete population.
    """
    if not values:
        raise ValueError(
            "Cannot calculate STD of an empty list."
        )

    mean = _mean(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    return math.sqrt(variance)
