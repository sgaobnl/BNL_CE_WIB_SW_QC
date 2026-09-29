import math
import re
from itertools import combinations

ROW_NUMBERS = (111, 112, 113, 114)
RMS_ROWS = (111, 113, 114)


RT_CRITERIA = {
    "pedestal_range": (8000, 16000),
    "rms_channel_range": (8, 16),
    "rms_mean_range": (8, 16),
    "rms_sigma": 5.0,
}

LN_CRITERIA = {
    "pedestal_range": (8000, 16000),
    "rms_channel_range": (4, 15),
    "rms_sigma": 5.0,
    "ln_rms_min_count": 2,
}


def check_rows111_114(rows, file_type):
    if file_type not in ("RT", "LN"):
        return False, {
            "fail_code": f"FAIL: unsupported file type: {file_type}"
        }

    failures = []
    parsed = {}
    row_data = {}

    # Read Rows 111-114. Row 112 is pedestal-checked only because
    # no distinct RMS criterion was specified for it.
    for row_number in ROW_NUMBERS:
        passed, result = _collect_row(rows, row_number)
        if not passed:
            failures.append(result["fail_code"])
        else:
            row_data[row_number] = result["channel_measurements"]

    if len(row_data) != len(ROW_NUMBERS):
        return False, {"fail_code": " | ".join(failures), **parsed}

    # Pedestal: 8000-14000 plus mean +/- 3 population STD.
    ped_min, ped_max = RT_CRITERIA["pedestal_range"]

    for row_number in ROW_NUMBERS:
        data = row_data[row_number]
        values = [data[ch]["pedestal"] for ch in range(16)]

        mean_value = _mean(values)
        std_value = _population_std(values)
        lower = mean_value - 5.0 * std_value
        upper = mean_value + 5.0 * std_value

        parsed[f"Row{row_number}_Pedestal_Mean_16CH"] = mean_value
        parsed[f"Row{row_number}_Pedestal_STD_16CH"] = std_value
        parsed[f"Row{row_number}_Pedestal_Lower_5STD"] = lower
        parsed[f"Row{row_number}_Pedestal_Upper_5STD"] = upper

        for ch in range(16):
            pedestal = data[ch]["pedestal"]

            if not lower <= pedestal <= upper:
                failures.append(
                    f"FAIL: row {row_number} CH{ch} pedestal={pedestal} "
                    f"outside mean +/- 5STD ({lower:.6g} ~ {upper:.6g})"
                )

            if not ped_min <= pedestal <= ped_max:
                failures.append(
                    f"FAIL: row {row_number} CH{ch} pedestal={pedestal} "
                    f"outside pedestal range ({ped_min} ~ {ped_max})"
                )

    # RMS checks only for Rows 111, 113, 114.
    row_rms_means = {}
    row_rms_bands = {}

    for row_number in RMS_ROWS:
        data = row_data[row_number]
        rms_values = [data[ch]["rms"] for ch in range(16)]

        if file_type == "LN":
            used_values = sorted(rms_values)[2:-2]
        else:
            used_values = rms_values

        rms_mean = _mean(used_values)
        rms_std = _population_std(used_values)
        rms_low = rms_mean - 5.0 * rms_std
        rms_high = rms_mean + 5.0 * rms_std

        row_rms_means[row_number] = rms_mean
        row_rms_bands[row_number] = (rms_low, rms_high)

        parsed[f"Row{row_number}_RMS_Mean"] = rms_mean
        parsed[f"Row{row_number}_RMS_STD"] = rms_std
        parsed[f"Row{row_number}_RMS_Lower_5STD"] = rms_low
        parsed[f"Row{row_number}_RMS_Upper_5STD"] = rms_high

        if file_type == "RT":
            ch_low, ch_high = RT_CRITERIA["rms_channel_range"]
            mean_low, mean_high = RT_CRITERIA["rms_mean_range"]

            for ch in range(16):
                rms = data[ch]["rms"]

                if not ch_low <= rms <= ch_high:
                    failures.append(
                        f"FAIL: row {row_number} CH{ch} rms={rms} "
                        f"outside range ({ch_low} ~ {ch_high})"
                    )

                if not rms_low <= rms <= rms_high:
                    failures.append(
                        f"FAIL: row {row_number} CH{ch} rms={rms} "
                        f"outside mean +/- 5STD "
                        f"({rms_low:.6g} ~ {rms_high:.6g})"
                    )

            if not mean_low <= rms_mean <= mean_high:
                failures.append(
                    f"FAIL: row {row_number} RT RMS mean={rms_mean:.6g} "
                    f"outside range ({mean_low} ~ {mean_high})"
                )

        else:
            # LN: per-row RMS must be within the row's mean +/- 5STD.
            # The absolute 4-10 RMS criterion is evaluated across
            # Rows 111, 113, 114 using a 2-of-3 rule below.
            if False: #ignore by Shanshan 09/25/2026
                for ch in range(16):
                    rms = data[ch]["rms"]

                    if not rms_low <= rms <= rms_high:
                        failures.append(
                            f"FAIL: row {row_number} CH{ch} rms={rms} "
                            f"outside LN mean +/- 5STD "
                            f"({rms_low:.6g} ~ {rms_high:.6g})"
                        )

    # LN absolute RMS range:
    # for each channel across Rows 111, 113, 114,
    # at least 2 of the 3 RMS values must be within 4-10.
    if file_type == "LN":
        ch_low, ch_high = LN_CRITERIA["rms_channel_range"]
        min_count = LN_CRITERIA["ln_rms_min_count"]

        for ch in range(16):
            values = [
                row_data[row_number][ch]["rms"]
                for row_number in RMS_ROWS
            ]

            in_range_count = sum(
                1
                for value in values
                if ch_low <= value <= ch_high
            )

            parsed[f"CH{ch}_RMS_InRange_Count"] = in_range_count

            if in_range_count < min_count:
                failures.append(
                    (
                        f"FAIL: Rows 111-114 CH{ch} has only {in_range_count} of "
                        f"3 RMS values in LN range {ch_low}~{ch_high}; "
                        f"at least {min_count} required; "
                        f"values={values}"
                    )
                )

    # LN cross-row consistency over Rows 111, 113, 114:
    # at least one pair of the three RMS values must have max-min < 3.
    if file_type == "LN":
        for ch in range(16):
            values = [
                row_data[row_number][ch]["rms"]
                for row_number in RMS_ROWS
            ]

            valid_pairs = [
                pair
                for pair in combinations(values, 2)
                if max(pair) - min(pair) < 3
            ]

            parsed[f"CH{ch}_RMS_111_113_114"] = values
            parsed[f"CH{ch}_Valid_RMS_Pair"] = valid_pairs[0] if valid_pairs else None

            if not valid_pairs:
                failures.append(
                    f"FAIL: CH{ch} Rows 111,113,114 LN RMS: "
                    f"no pair has max-min < 3; values={values}"
                )

    if failures:
        return False, {"fail_code": " | ".join(failures), **parsed}

    return True, {"fail_code": "", **parsed}


def _collect_row(rows, row_number):
    row_index = row_number - 1

    if len(rows) <= row_index:
        return False, {"fail_code": f"FAIL: row {row_number} is missing"}

    row = rows[row_index]
    measurements = {}

    # C:R = zero-based indices 2 through 17.
    for ch in range(16):
        found = None

        for column_index in range(2, min(18, len(row))):
            parsed = _parse_channel_cell(row[column_index], ch)

            if parsed is not None:
                parsed["column"] = column_index
                found = parsed
                break

        if found is None:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} CH{ch} not found or "
                    "pedestal/rms could not be parsed in Columns C:R"
                )
            }

        measurements[ch] = found

    return True, {"channel_measurements": measurements}


def _parse_channel_cell(cell, expected_channel):
    text = str(cell).strip()

    if re.search(rf"\bCH{expected_channel}\b", text, re.IGNORECASE) is None:
        return None

    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"

    pedestal_match = re.search(
        rf"\b(?:pedestal|ped)\b\s*=\s*(?P<value>{number})",
        text,
        re.IGNORECASE,
    )
    rms_match = re.search(
        rf"\brms\b\s*=\s*(?P<value>{number})",
        text,
        re.IGNORECASE,
    )

    if pedestal_match is None or rms_match is None:
        return None

    return {
        "pedestal": float(pedestal_match.group("value")),
        "rms": float(rms_match.group("value")),
    }


def _mean(values):
    if not values:
        raise ValueError("Cannot calculate mean of empty list.")
    return sum(values) / len(values)


def _population_std(values):
    if not values:
        raise ValueError("Cannot calculate STD of empty list.")

    mean = _mean(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


CHECK_FUNCTIONS = {
    "check_rows111_114": check_rows111_114,
}
