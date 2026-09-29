import math
import re

from common import column_letter, find_channel_measurements


# Rows 65-72: RT/LN-specific Column I/J/K criteria.
RT_CRITERIA = {
    65: {"i": (35-5, 45+5), "j": (-0.05, 0.5), "k": (55-5, 65+5)},
    66: {"i": (35-5, 45+5), "j": (-0.05, 0.5), "k": (55-5, 65+5)},
    67: {"i": (35-5, 45+5), "j": (-0.05, 0.5), "k": (55-5, 65+5)},
    68: {"i": (35-5, 45+5), "j": (-0.05, 0.5), "k": (55-5, 65+5)},
    69: {"i": (30-5, 40+5), "j": (-0.05, 0.5), "k": (55-5, 65+5)},
    70: {"i": (70-5, 80+5), "j": (15, 25), "k": (50-5, 60+5)},
    71: {"i": (65-5, 75+5), "j": (5, 15), "k": (52-5, 62+5)},
    72: {"i": (30-5, 40+5), "j": (-0.05, 0.5), "k": (55-5, 65+5)},
}

LN_CRITERIA = {
    65: {"i": (30-5, 50), "j": (-0.5, 0.5+1), "k": (55-5, 65+10)},
    66: {"i": (30-5, 50), "j": (-0.5, 0.5+1), "k": (55-5, 65+10)},
    67: {"i": (30-5, 50), "j": (-0.5, 0.5+1), "k": (55-5, 65+10)},
    68: {"i": (30-5, 50), "j": (-0.5, 0.5+1), "k": (55-5, 65+10)},
    69: {"i": (25-5, 45), "j": (-0.5, 0.5+1), "k": (55-5, 65+10)},
    70: {"i": (80-5, 100), "j": (15-5, 25+5), "k": (50-5, 60+10)},
    71: {"i": (70-5, 90), "j": (5-5, 15+5), "k": (50-5, 60+10)},
    72: {"i": (25-5,45),  "j": (-0.5, 0.5+1), "k": (55-5, 65+10)},
}

CHANNEL_CRITERIA = {
    65: {"ped_min": 7500, "posamp_min": 3500, "amp_diff_max": 300},
    66: {"ped_min": 7500, "posamp_min": 3500, "amp_diff_max": 300},
    67: {"ped_min": 7500, "posamp_min": 3500, "amp_diff_max": 300},
    68: {"ped_min": 7500, "posamp_min": 500, "amp_diff_max": 4000},
    69: {"ped_min": 200, "posamp_min": 1500, "amp_diff_max": None},
    70: {"ped_min": 200, "posamp_min": 1500, "amp_diff_max": None},
    71: {"ped_min": 200, "posamp_min": 1500, "amp_diff_max": None},
    72: {"ped_min": 200, "posamp_min": 1000, "amp_diff_max": None},
}


def check_rows65_72(rows, file_type):
    """Check all rows 65-72; collect all failures."""
    criteria = _get_file_criteria(file_type)
    if criteria is None:
        return False, {
            "fail_code": f"FAIL: unsupported file type: {file_type}"
        }

    failures = []
    parsed = {}

    for row_number in range(65, 73):
        passed, result = _check_row(
            rows,
            row_number,
            criteria[row_number],
            CHANNEL_CRITERIA[row_number],
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

    return (
        (False, {"fail_code": " | ".join(failures), **parsed})
        if failures
        else (True, {"fail_code": "", **parsed})
    )


def check_row65(rows, file_type):
    return _check_specific(rows, file_type, 65)


def check_row66(rows, file_type):
    return _check_specific(rows, file_type, 66)


def check_row67(rows, file_type):
    return _check_specific(rows, file_type, 67)


def check_row68(rows, file_type):
    return _check_specific(rows, file_type, 68)


def check_row69(rows, file_type):
    return _check_specific(rows, file_type, 69)


def check_row70(rows, file_type):
    return _check_specific(rows, file_type, 70)


def check_row71(rows, file_type):
    return _check_specific(rows, file_type, 71)


def check_row72(rows, file_type):
    return _check_specific(rows, file_type, 72)


def _check_specific(rows, file_type, row_number):
    criteria = _get_file_criteria(file_type)
    if criteria is None:
        return False, {
            "fail_code": f"FAIL: unsupported file type: {file_type}"
        }

    return _check_row(
        rows,
        row_number,
        criteria[row_number],
        CHANNEL_CRITERIA[row_number],
    )


def _get_file_criteria(file_type):
    if file_type == "RT":
        return RT_CRITERIA
    if file_type == "LN":
        return LN_CRITERIA
    return None


def _check_row(rows, row_number, criteria, channel_criteria):
    row_index = row_number - 1

    if len(rows) <= row_index:
        return False, {
            "fail_code": f"FAIL: row {row_number} is missing"
        }

    row = rows[row_index]

    if len(row) < 11:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "does not contain columns I-K"
            )
        }

    failures = []

    # --------------------------------------------------
    # Columns I, J, K
    # Numeric value is taken from the right side of '='.
    # --------------------------------------------------

    i_value = _value_right_of_equals(row[8])
    if criteria["i"] is not None:
        if i_value is None:
            failures.append(
                f"Column I is not numeric: {row[8]}"
            )
        else:
            low, high = criteria["i"]
            if not low <= i_value <= high:
                failures.append(
                    f"Column I={i_value} outside range ({low} ~ {high})"
                )

    j_value = _value_right_of_equals(row[9])
    if j_value is None:
        failures.append(
            f"Column J is not numeric: {row[9]}"
        )
    else:
        low, high = criteria["j"]
        if not low <= j_value <= high:
            failures.append(
                f"Column J={j_value} outside range ({low} ~ {high})"
            )

    k_value = _value_right_of_equals(row[10])
    if k_value is None:
        failures.append(
            f"Column K is not numeric: {row[10]}"
        )
    else:
        low, high = criteria["k"]
        if not low <= k_value <= high:
            failures.append(
                f"Column K={k_value} outside range ({low} ~ {high})"
            )

    # --------------------------------------------------
    # L:AA, CH0-CH15
    # --------------------------------------------------

    channel_measurements = {}

    for channel_number in range(16):
        measurement = _find_channel_in_l_to_aa(
            row,
            channel_number,
        )

        if measurement is None:
            failures.append(
                f"CH{channel_number} not found or measurement cannot be parsed"
            )
        else:
            channel_measurements[channel_number] = measurement

    ped_mean = ped_std = ped_lower = ped_upper = None
    posamp_mean = posamp_std = posamp_lower = posamp_upper = None

    if len(channel_measurements) == 16:
        ped_values = [
            channel_measurements[ch]["ped"]
            for ch in range(16)
        ]
        posamp_values = [
            channel_measurements[ch]["posAmp"]
            for ch in range(16)
        ]

        ped_mean = _mean(ped_values)
        ped_std = _population_std(ped_values)
        ped_lower = ped_mean - 4.0 * ped_std
        ped_upper = ped_mean + 4.0 * ped_std

        posamp_mean = _mean(posamp_values)
        posamp_std = _population_std(posamp_values)
        posamp_lower = posamp_mean - 4.0 * posamp_std
        posamp_upper = posamp_mean + 4.0 * posamp_std

        for channel_number in range(16):
            measurement = channel_measurements[channel_number]
            ped = measurement["ped"]
            posamp = measurement["posAmp"]
            negamp = measurement.get("negAmp")
            col = column_letter(measurement["column"])

            # PED: mean +/- 4 STD
            if not ped_lower <= ped <= ped_upper:
                failures.append(
                    f"CH{channel_number} ({col}) ped={ped} "
                    f"outside 4STD range "
                    f"({ped_lower:.6g} ~ {ped_upper:.6g})"
                )

            # PED minimum
            if ped <= channel_criteria["ped_min"]:
                failures.append(
                    f"CH{channel_number} ({col}) ped={ped} "
                    f"must be > {channel_criteria['ped_min']}"
                )

            # posAmp: mean +/- 4 STD
            if not posamp_lower <= posamp <= posamp_upper:
                failures.append(
                    f"CH{channel_number} ({col}) posAmp={posamp} "
                    f"outside 4STD range "
                    f"({posamp_lower:.6g} ~ {posamp_upper:.6g})"
                )

            # posAmp minimum
            if posamp <= channel_criteria["posamp_min"]:
                failures.append(
                    f"CH{channel_number} ({col}) posAmp={posamp} "
                    f"must be > {channel_criteria['posamp_min']}"
                )

            # Conditional posAmp / negAmp difference for Rows 65-68.
            if channel_criteria["amp_diff_max"] is not None:
                if ped > channel_criteria["ped_min"]:
                    if negamp is None:
                        failures.append(
                            f"CH{channel_number} ({col}) "
                            "negAmp could not be parsed"
                        )
                    else:
                        difference = abs(posamp - negamp)
                        if not difference < channel_criteria["amp_diff_max"]:
                            failures.append(
                                f"CH{channel_number} ({col}) "
                                f"|posAmp-negAmp|={difference:.6g} "
                                f"must be < "
                                f"{channel_criteria['amp_diff_max']}"
                            )

    result = {
        "Column_I": i_value,
        "Column_J": j_value,
        "Column_K": k_value,
        "Ped_Mean_16CH": ped_mean,
        "Ped_STD_16CH": ped_std,
        "Ped_Lower_4STD": ped_lower,
        "Ped_Upper_4STD": ped_upper,
        "PosAmp_Mean_16CH": posamp_mean,
        "PosAmp_STD_16CH": posamp_std,
        "PosAmp_Lower_4STD": posamp_lower,
        "PosAmp_Upper_4STD": posamp_upper,
    }

    result["fail_code"] = (
        f"FAIL: row {row_number} - " + " | ".join(failures)
        if failures
        else ""
    )

    return (False, result) if failures else (True, result)


def _find_channel_in_l_to_aa(row, channel_number):
    """
    Search only Columns L:AA for the requested CHx.
    """
    channel_pattern = re.compile(
        rf"\bCH{channel_number}\b",
        re.IGNORECASE,
    )

    for col_index in range(11, min(27, len(row))):
        text = str(row[col_index]).strip()

        if not channel_pattern.search(text):
            continue

        measurement = find_channel_measurements(
            [text],
            channel_number,
        )

        if measurement is None:
            return None

        measurement["column"] = col_index
        return measurement

    return None


def _value_right_of_equals(value):
    """
    Extract the numeric value on the right side of '='.

    Examples:
        'Vdda_P=38.5' -> 38.5
        'value = -0.005' -> -0.005
    """
    if value is None:
        return None

    text = str(value).strip()

    if "=" in text:
        text = text.rsplit("=", 1)[1].strip()

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


def _mean(values):
    if not values:
        raise ValueError(
            "Cannot calculate mean of an empty list."
        )

    return sum(values) / len(values)


def _population_std(values):
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
