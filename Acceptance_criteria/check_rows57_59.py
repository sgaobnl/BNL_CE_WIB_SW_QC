# ==========================================================
# Rows 57 ~ 59 acceptance criteria
#
# ONLY COLUMN C is checked.
#
# Row 57:
#   RT: 1150 ~ 1250
#   LN: 1130 ~ 1200
#
# Row 58:
#   RT: 800 ~ 1000
#   LN: 230 ~ 330
#
# Row 59:
#   Same as Row 57 with +/-10 tolerance:
#   RT: 1140 ~ 1260
#   LN: 1120 ~ 1210
# ==========================================================


RT_CRITERIA = {
    57: (1150, 1250),
    58: (800, 1000),
    59: (1140, 1260),
}


LN_CRITERIA = {
    57: (1130, 1200),
    58: (230, 330),
    59: (1120, 1210),
}


def check_rows57_59(rows, file_type):
    """
    Check Column C only for Rows 57, 58, and 59.

    All three rows are checked even if one fails.
    """

    if file_type == "RT":
        criteria = RT_CRITERIA

    elif file_type == "LN":
        criteria = LN_CRITERIA

    else:
        return False, {
            "fail_code": (
                f"FAIL: unsupported file type: {file_type}"
            )
        }

    failures = []
    parsed = {}

    for row_number in (57, 58, 59):

        passed, result = _check_row(
            rows=rows,
            row_number=row_number,
            value_range=criteria[row_number],
        )

        if "Column_C" in result:
            parsed[f"Row{row_number}_Column_C"] = (
                result["Column_C"]
            )

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


def check_row57(rows, file_type):
    """Check Row 57, Column C only."""
    return _check_specific_row(
        rows,
        file_type,
        57,
    )


def check_row58(rows, file_type):
    """Check Row 58, Column C only."""
    return _check_specific_row(
        rows,
        file_type,
        58,
    )


def check_row59(rows, file_type):
    """Check Row 59, Column C only."""
    return _check_specific_row(
        rows,
        file_type,
        59,
    )


def _check_specific_row(
    rows,
    file_type,
    row_number,
):
    if file_type == "RT":
        criteria = RT_CRITERIA

    elif file_type == "LN":
        criteria = LN_CRITERIA

    else:
        return False, {
            "fail_code": (
                f"FAIL: unsupported file type: {file_type}"
            )
        }

    return _check_row(
        rows=rows,
        row_number=row_number,
        value_range=criteria[row_number],
    )


def _check_row(
    rows,
    row_number,
    value_range,
):
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

    # Column C = zero-based index 2
    if len(row) <= 2:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} column C is missing"
            )
        }

    raw_value = str(row[2]).strip()

    if not raw_value:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} column C is empty"
            )
        }

    # --------------------------------------------------
    # Convert Column C to a number
    # --------------------------------------------------

    try:
        value = float(raw_value)

    except ValueError:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} column C "
                f"is not numeric: {raw_value}"
            ),
            "Column_C": raw_value,
        }

    # --------------------------------------------------
    # Apply range
    # --------------------------------------------------

    low, high = value_range

    if not low <= value <= high:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} column C "
                f"out of range ({low} ~ {high}): {value}"
            ),
            "Column_C": value,
        }

    return True, {
        "fail_code": "",
        "Column_C": value,
    }
