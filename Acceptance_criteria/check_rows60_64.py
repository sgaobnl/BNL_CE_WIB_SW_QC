# ==========================================================
# Rows 60 ~ 64 acceptance criteria
#
# Only Columns C, D, and E are checked.
#
# Row 60:
#   C gain (mV/ADC bit): -19.5 ~ -18.5
#   D INL: < 0.5%
#   E: 61
#
# Row 61:
#   C gain (mV/ADC bit): -8.5 ~ -8.0
#   D INL: < 0.5%
#   E: 63
#
# Row 62:
#   C gain (mV/ADC bit): -15.0 ~ -14.1
#   D INL: < 0.5%
#   E: 63
#
# Row 63:
#   C gain (mV/ADC bit): -5.0 ~ -4.5
#   D INL: < 0.5%
#   E: 63
#
# Row 64:
#   Same criteria as Row 60.
# ==========================================================

import re


CRITERIA = {
    60: {
        "gain_range": (-20, -17),
        "inl_max": 1.0,
        "e_value": 61,
    },
    61: {
        "gain_range": (-8.5-0.5, -8.0+0.5),
        "inl_max": 1.0,
        "e_value": 63,
    },
    62: {
        "gain_range": (-15.0-0.5, -14+0.5),
        "inl_max": 1.0,
        "e_value": 63,
    },
    63: {
        "gain_range": (-5.0-0.2, -4.5+0.2),
        "inl_max": 1.0,
        "e_value": 63,
    },
    64: {
        "gain_range": (-20, -17),
        "inl_max": 1,
        "e_value": 61,
    },
}


def check_rows60_64(rows, file_type=None):
    """
    Check Rows 60 ~ 64.

    All five rows are checked even if one fails.
    """
    failures = []
    parsed = {}

    for row_number in range(60, 65):
        passed, result = _check_row(
            rows,
            row_number,
            CRITERIA[row_number],
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


def check_row60(rows, file_type=None):
    return _check_row(rows, 60, CRITERIA[60])


def check_row61(rows, file_type=None):
    return _check_row(rows, 61, CRITERIA[61])


def check_row62(rows, file_type=None):
    return _check_row(rows, 62, CRITERIA[62])


def check_row63(rows, file_type=None):
    return _check_row(rows, 63, CRITERIA[63])


def check_row64(rows, file_type=None):
    return _check_row(rows, 64, CRITERIA[64])


def _check_row(rows, row_number, criteria):
    row_index = row_number - 1

    if len(rows) <= row_index:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} is missing"
            )
        }

    row = rows[row_index]

    # Need Columns A-E so Column C/D/E can be accessed.
    if len(row) <= 4:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "does not contain columns C-E"
            )
        }

    # --------------------------------------------------
    # Column C: Gain
    # --------------------------------------------------

    gain_raw = str(row[2]).strip()

    if not gain_raw:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "column C gain is empty"
            ),
            "Gain": gain_raw,
        }

    gain = _to_float(gain_raw)

    if gain is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"column C gain is not numeric: "
                f"{gain_raw}"
            ),
            "Gain": gain_raw,
        }

    gain_low, gain_high = criteria["gain_range"]

    if not gain_low <= gain <= gain_high:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"column C gain out of range "
                f"({gain_low} ~ {gain_high}): "
                f"{gain}"
            ),
            "Gain": gain,
        }

    # --------------------------------------------------
    # Column D: INL
    # --------------------------------------------------

    inl_raw = str(row[3]).strip()

    if not inl_raw:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "column D INL is empty"
            ),
            "Gain": gain,
            "INL": inl_raw,
        }

    inl = _to_float(inl_raw)

    if inl is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"column D INL is not numeric: "
                f"{inl_raw}"
            ),
            "Gain": gain,
            "INL": inl_raw,
        }

    inl_limit = criteria["inl_max"]

    if not inl < inl_limit:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"column D INL must be < "
                f"{inl_limit}%: {inl}%"
            ),
            "Gain": gain,
            "INL": inl,
        }

    # --------------------------------------------------
    # Column E: exact value
    # --------------------------------------------------

    e_raw = str(row[4]).strip().split("=")[-1]

    if not e_raw:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "column E is empty"
            ),
            "Gain": gain,
            "INL": inl,
            "E": e_raw,
        }

    e_value = _to_float(e_raw)

    if e_value is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"column E is not numeric: "
                f"{e_raw}"
            ),
            "Gain": gain,
            "INL": inl,
            "E": e_raw,
        }

    expected_e = criteria["e_value"]

    if e_value != expected_e:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"column E must be {expected_e}: "
                f"{e_value}"
            ),
            "Gain": gain,
            "INL": inl,
            "E": e_value,
        }

    return True, {
        "fail_code": "",
        "Gain": gain,
        "INL": inl,
        "E": e_value,
    }


def _to_float(value):
    """
    Convert a numeric or numeric-with-units string to float.

    Examples:
        -18.9
        -18.9 mV/ADC bit
        0.15%
    """
    if value is None:
        return None

    text = str(value).strip()

    try:
        return float(text)
    except ValueError:
        pass

    match = re.search(
        r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)",
        text,
    )

    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None
