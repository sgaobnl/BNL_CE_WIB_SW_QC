import math
import re
from itertools import combinations


# ==========================================================
# Rows 105-110
#
# Search Columns C:R for CH0-CH15.
# Cell format:
#     CHx=(pedestal=...;rms=...)
#
# Pedestal:
#     16-channel mean +/- 4 * population STD
#
# Groups:
#   105-107:
#       pedestal = 8000-10000
#       RT RMS / mean = 8-16
#       LN RMS = 4-10
#       LN mean = 4-10
#
#   108-110:
#       pedestal = 500-2000
#       RT RMS / mean = 8-16
#       LN RMS = 4-10
#       LN mean = 4-10
#
# RT:
#   - every channel in RMS range
#   - every channel in row mean +/- 5 STD
#   - every row RMS mean in RT mean range
#   - for each channel across Rows 105-110:
#         max(RMS) - min(RMS) < 2
#
# LN:
#   - each 3-row group uses 2-of-3 because the specified
#     groups contain 4 rows
#   - at least 2 of 4 RMS values per channel in LN range
#   - at least 2 of 4 RMS values per channel within the
#     corresponding row mean +/- 5 STD band
#   - at least 2 of 3 row RMS means in LN mean range
#   - across Rows 105-110, at least one set of 4 of the
#     6 RMS values must have max-min < 2
# ==========================================================


RT_105_107_CRITERIA = {
    "pedestal_range": (8000, 10000),
    "rms_sigma": 5.0,
    "rms_channel_range": (8, 16),
    "rms_mean_range": (8, 16),
}

LN_105_107_CRITERIA = {
    "pedestal_range": (8000, 10000),
    "rms_sigma": 5.0,
    "rms_channel_range": (2, 100),
    "rms_mean_range": (2, 100),
    "ln_min_count": 0,
}

RT_108_110_CRITERIA = {
    "pedestal_range": (200, 2000),
    "rms_sigma": 5.0,
    "rms_channel_range": (8, 16),
    "rms_mean_range": (8, 16),
}

LN_108_110_CRITERIA = {
    "pedestal_range": (200, 2500),
    "rms_sigma": 5.0,
    "rms_channel_range": (2, 100),
    "rms_mean_range": (2, 100),
    "ln_min_count": 0,
}


def check_rows105_110(rows, file_type):
    failures = []
    parsed = {}

    for row_numbers, rt_criteria, ln_criteria, group_name in (
        (
            (105, 106, 107),
            RT_105_107_CRITERIA,
            LN_105_107_CRITERIA,
            "105-107",
        ),
        (
            (108, 109, 110),
            RT_108_110_CRITERIA,
            LN_108_110_CRITERIA,
            "108-110",
        ),
    ):
        passed, result = _check_group(
            rows,
            file_type,
            row_numbers,
            rt_criteria,
            ln_criteria,
            group_name,
        )

        if not passed:
            failures.append(
                result.get(
                    "fail_code",
                    f"FAIL: group {group_name}",
                )
            )

        for key, value in result.items():
            if key != "fail_code":
                parsed[f"{group_name}_{key}"] = value

    # Six-row channel RMS consistency
    passed, result = _check_six_row_rms_difference(
        rows,
        file_type,
    )

    if not passed:
        failures.append(
            result.get(
                "fail_code",
                "FAIL: Rows 105-110 RMS difference check",
            )
        )

    for key, value in result.items():
        if key != "fail_code":
            parsed[key] = value

    if failures:
        return False, {
            "fail_code": " | ".join(failures),
            **parsed,
        }

    return True, {
        "fail_code": "",
        **parsed,
    }


def _check_group(
    rows,
    file_type,
    row_numbers,
    rt_criteria,
    ln_criteria,
    group_name,
):
    if file_type == "RT":
        criteria = rt_criteria
    elif file_type == "LN":
        criteria = ln_criteria
    else:
        return False, {
            "fail_code": (
                f"FAIL: unsupported file type: {file_type}"
            )
        }

    failures = []
    parsed = {}
    row_data = {}

    for row_number in row_numbers:
        passed, result = _collect_row(
            rows,
            row_number,
        )

        if not passed:
            failures.append(result["fail_code"])
        else:
            row_data[row_number] = result[
                "channel_measurements"
            ]

    if len(row_data) != len(row_numbers):
        return False, {
            "fail_code": " | ".join(failures),
            **parsed,
        }

    # Pedestal checks
    ped_min, ped_max = criteria["pedestal_range"]

    for row_number in row_numbers:
        data = row_data[row_number]

        ped_values = [
            data[ch]["pedestal"]
            for ch in range(16)
        ]

        ped_mean = _mean(ped_values)
        ped_std = _population_std(ped_values)

        ped_low = ped_mean - 4.0 * ped_std
        ped_high = ped_mean + 4.0 * ped_std

        parsed[f"Row{row_number}_Pedestal_Mean_16CH"] = ped_mean
        parsed[f"Row{row_number}_Pedestal_STD_16CH"] = ped_std
        parsed[f"Row{row_number}_Pedestal_Lower_4STD"] = ped_low
        parsed[f"Row{row_number}_Pedestal_Upper_4STD"] = ped_high

        for ch in range(16):
            pedestal = data[ch]["pedestal"]

            if not ped_low <= pedestal <= ped_high:
                failures.append(
                    (
                        f"FAIL: row {row_number} CH{ch} "
                        f"pedestal={pedestal} outside mean +/- 4STD "
                        f"({ped_low:.6g} ~ {ped_high:.6g})"
                    )
                )

            if not ped_min <= pedestal <= ped_max:
                failures.append(
                    (
                        f"FAIL: row {row_number} CH{ch} "
                        f"pedestal={pedestal} outside pedestal range "
                        f"({ped_min} ~ {ped_max})"
                    )
                )

    # RMS row statistics
    row_rms_means = {}
    row_rms_bands = {}

    for row_number in row_numbers:
        data = row_data[row_number]

        rms_values = [
            data[ch]["rms"]
            for ch in range(16)
        ]

        if file_type == "LN":
            used_values = sorted(rms_values)[2:-2]
        else:
            used_values = rms_values

        rms_mean = _mean(used_values)
        rms_std = _population_std(used_values)

        rms_low = (
            rms_mean
            - criteria["rms_sigma"] * rms_std
        )
        rms_high = (
            rms_mean
            + criteria["rms_sigma"] * rms_std
        )

        row_rms_means[row_number] = rms_mean
        row_rms_bands[row_number] = (
            rms_low,
            rms_high,
        )

        parsed[f"Row{row_number}_RMS_Mean"] = rms_mean
        parsed[f"Row{row_number}_RMS_STD"] = rms_std
        parsed[f"Row{row_number}_RMS_Lower_5STD"] = rms_low
        parsed[f"Row{row_number}_RMS_Upper_5STD"] = rms_high

        if file_type == "RT":
            ch_low, ch_high = criteria["rms_channel_range"]
            mean_low, mean_high = criteria["rms_mean_range"]

            for ch in range(16):
                rms = data[ch]["rms"]

                if not ch_low <= rms <= ch_high:
                    failures.append(
                        (
                            f"FAIL: row {row_number} CH{ch} "
                            f"rms={rms} outside range "
                            f"({ch_low} ~ {ch_high})"
                        )
                    )

                if not rms_low <= rms <= rms_high:
                    failures.append(
                        (
                            f"FAIL: row {row_number} CH{ch} "
                            f"rms={rms} outside mean +/- 5STD "
                            f"({rms_low:.6g} ~ {rms_high:.6g})"
                        )
                    )

            if not mean_low <= rms_mean <= mean_high:
                failures.append(
                    (
                        f"FAIL: row {row_number} RT RMS mean="
                        f"{rms_mean:.6g} outside range "
                        f"({mean_low} ~ {mean_high})"
                    )
                )

    # LN uses the practical 2-of-3 rule for these 3-row groups.
    if file_type == "LN":
        ch_low, ch_high = criteria["rms_channel_range"]
        mean_low, mean_high = criteria["rms_mean_range"]
        min_count = criteria["ln_min_count"]

        for ch in range(16):
            in_range_count = 0
            in_band_count = 0
            values = []

            for row_number in row_numbers:
                rms = row_data[row_number][ch]["rms"]
                values.append(rms)

                if ch_low <= rms <= ch_high:
                    in_range_count += 1

                band_low, band_high = row_rms_bands[row_number]

                if band_low <= rms <= band_high:
                    in_band_count += 1

            if in_range_count < min_count:
                failures.append(
                    (
                        f"FAIL: group {group_name} CH{ch} "
                        f"has only {in_range_count} of "
                        f"{len(row_numbers)} RMS values in range "
                        f"{ch_low}~{ch_high}; at least "
                        f"{min_count} required; values={values}"
                    )
                )

            if in_band_count < min_count:
                failures.append(
                    (
                        f"FAIL: group {group_name} CH{ch} "
                        f"has only {in_band_count} of "
                        f"{len(row_numbers)} RMS values within "
                        "corresponding row mean +/- 5STD; "
                        f"at least {min_count} required; values={values}"
                    )
                )

        ln_mean_pass_count = sum(
            1
            for row_number in row_numbers
            if mean_low <= row_rms_means[row_number] <= mean_high
        )

        if ln_mean_pass_count < min_count:
            mean_values = [
                row_rms_means[row_number]
                for row_number in row_numbers
            ]

            failures.append(
                (
                    f"FAIL: group {group_name} only "
                    f"{ln_mean_pass_count} of {len(row_numbers)} "
                    f"LN RMS means in range {mean_low}~{mean_high}; "
                    f"at least {min_count} required; values={mean_values}"
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


def _check_six_row_rms_difference(rows, file_type):
    failures = []
    channel_data = {}

    for ch in range(16):
        values = []

        for row_number in range(105, 111):
            row_index = row_number - 1

            if len(rows) <= row_index:
                failures.append(
                    (
                        f"FAIL: row {row_number} missing "
                        "for six-row RMS difference check"
                    )
                )
                break

            measurement = _parse_channel_cell_from_row(
                rows[row_index],
                ch,
            )

            if measurement is None:
                failures.append(
                    (
                        f"FAIL: CH{ch} row {row_number} "
                        "RMS could not be parsed"
                    )
                )
                break

            values.append(measurement["rms"])

        if len(values) != 6:
            continue

        max_difference = max(values) - min(values)

        if file_type == "RT":
            if not max_difference < 3:
                failures.append(
                    (
                        f"FAIL: CH{ch} Rows 105-110 RT RMS "
                        f"max difference={max_difference:.6g}; "
                        "must be < 2; "
                        f"values={values}"
                    )
                )

            channel_data[ch] = {
                "values": values,
                "max_difference": max_difference,
            }

        elif file_type == "LN":
            valid_subset = None

            for subset in combinations(values, 2):
                subset_difference = max(subset) - min(subset)

                if subset_difference < 3:
                    valid_subset = {
                        "values": subset,
                        "max_difference": subset_difference,
                    }
                    break

            if valid_subset is None:
                failures.append(
                    (
                        f"FAIL: CH{ch} Rows 105-110 LN RMS "
                        "no set of 2 of 6 values has "
                        f"maximum difference < 3; values={values}"
                    )
                )

            channel_data[ch] = {
                "values": values,
                "valid_four_of_six": valid_subset,
            }

        else:
            return False, {
                "fail_code": (
                    f"FAIL: unsupported file type: {file_type}"
                )
            }

    if failures:
        return False, {
            "fail_code": " | ".join(failures),
            "Rows105_110_RMS_Channel_Data": channel_data,
        }

    return True, {
        "fail_code": "",
        "Rows105_110_RMS_Channel_Data": channel_data,
    }


def _collect_row(rows, row_number):
    row_index = row_number - 1

    if len(rows) <= row_index:
        return False, {
            "fail_code": f"FAIL: row {row_number} is missing"
        }

    row = rows[row_index]
    measurements = {}

    for ch in range(16):
        measurement = _parse_channel_cell_from_row(
            row,
            ch,
        )

        if measurement is None:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} CH{ch} "
                    "not found or pedestal/rms could not be parsed "
                    "in Columns C:R"
                )
            }

        measurements[ch] = measurement

    return True, {
        "channel_measurements": measurements,
    }


def _parse_channel_cell_from_row(row, expected_channel):
    for column_index in range(2, min(18, len(row))):
        parsed = _parse_channel_cell(
            row[column_index],
            expected_channel,
        )

        if parsed is not None:
            parsed["column"] = column_index
            return parsed

    return None


def _parse_channel_cell(cell, expected_channel):
    text = str(cell).strip()

    if re.search(
        rf"\bCH{expected_channel}\b",
        text,
        re.IGNORECASE,
    ) is None:
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
        "pedestal": float(
            pedestal_match.group("value")
        ),
        "rms": float(
            rms_match.group("value")
        ),
    }


def _mean(values):
    if not values:
        raise ValueError(
            "Cannot calculate mean of empty list."
        )

    return sum(values) / len(values)


def _population_std(values):
    if not values:
        raise ValueError(
            "Cannot calculate STD of empty list."
        )

    mean = _mean(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    return math.sqrt(variance)


CHECK_FUNCTIONS = {
    "check_rows105_110": check_rows105_110,
}
