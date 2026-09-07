def check_row_count(rows, file_type=None):
    """Check 1: file must contain exactly 133 rows."""
    expected_row_count = 133
    actual_count = len(rows)

    if actual_count == expected_row_count:
        return True, {
            "row_count": actual_count,
            "fail_code": "",
        }

    return False, {
        "row_count": actual_count,
        "fail_code": "FAIL: incomplete test report",
    }
