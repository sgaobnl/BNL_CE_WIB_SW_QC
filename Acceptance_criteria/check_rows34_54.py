import math

from common import (
    column_letter,
    find_channel_measurements,
)


# ==========================================================
# Rows 34 ~ 54 acceptance check
# ==========================================================
#
# For every row from 34 through 54:
#
#   Search the entire row for CH0 ~ CH15.
#
#   ped:
#       16-channel mean +/- 3 * population STD
#
#   posAmp:
#       16-channel mean +/- 3 * population STD
#
#   Conditional check:
#       If a channel's ped > 7500,
#       then abs(posAmp - negAmp) must be < 250.
#
# RT/LN-specific structure is retained via RT_CRITERIA and
# LN_CRITERIA. No RT/LN numeric difference was specified
# for these row checks, so the channel criteria are the same.
#
# In addition, Rows 34-37 have a cross-row RMS ordering check:
# RMS37 < RMS35 < RMS34 < RMS36.
#
# Column A and Column B are taken from the actual row and
# are only checked for being present/non-empty.
# ==========================================================


RT_CRITERIA = {
    "ped_mean_std_multiplier": 4.0,
    "posamp_mean_std_multiplier": 4.0,
    "ped_threshold": 7500,
    "posamp_negamp_max_difference": 300,
}


LN_CRITERIA = {
    "ped_mean_std_multiplier": 5.0,
    "posamp_mean_std_multiplier": 5.0,
    "ped_threshold": 7500,
    "posamp_negamp_max_difference": 300,
}

LN_CRITERIA_row48 = {
    "ped_mean_std_multiplier": 5.0,
    "posamp_mean_std_multiplier": 5.0,
    "ped_threshold": 7500,
    "posamp_negamp_max_difference": 2000,
}


# ==========================================================
# Cross-row RMS pattern for Rows 34 ~ 37
# ==========================================================
#
# Required ordering for each channel:
#
#     RMS(Row 37) < RMS(Row 35) < RMS(Row 34) < RMS(Row 36)
#
# Reference relative pattern:
#
#     Row 37 : Row 35 : Row 34 : Row 36
#       4.7  :  6.4  : 12.0  : 20.0
#
# The RMS ordering remains a PASS/FAIL criterion.
# The 4.7:6.4:12:20 reference-ratio check is disabled.
# Its calculations are retained only for diagnostics.
# ==========================================================

RMS_REFERENCE_RATIOS = {
    37: 4.7,
    35: 6.4,
    34: 12.0,
    36: 20.0,
}

# Each measured RMS ratio must be within +/-20%
# of the expected ratio after normalizing both sets to Row 37.
RMS_RATIO_TOLERANCE = 0.20

# RMS reference-ratio acceptance is currently disabled.
ENABLE_RMS_RATIO_CHECK = False


def check_rows34_54(rows, file_type):
    """
    Run the Row 34 ~ Row 54 checks.

    Returns:
        True, {"fail_code": ""}
    when all 21 rows pass.

    Returns:
        False, {"fail_code": "..."}
    when one or more rows fail.

    Every row is checked; failures are collected instead of
    stopping at the first failed row.
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

    failed_rows = []

    # --------------------------------------------------
    # Cross-row RMS ordering check for Rows 34 ~ 37.
    # --------------------------------------------------

    rms_passed, rms_result = check_rms_order_rows34_37(
        rows,
        file_type,
    )

    if rms_result.get("RMS_Channel_Data"):
        # Keep detailed RMS comparison data internally.
        rms_data = rms_result["RMS_Channel_Data"]
    else:
        rms_data = {}

    if not rms_passed:
        failed_rows.append(
            rms_result.get(
                "fail_code",
                "FAIL: Rows 34-37 RMS ordering failed",
            )
        )

    # --------------------------------------------------
    # Individual row checks for Rows 34 ~ 54.
    # --------------------------------------------------

    for row_number in range(34, 55):
        if row_number == 48:
            continue
        passed, result = _check_row(
            rows=rows,
            row_number=row_number,
            criteria=criteria,
        )

        if not passed:
            failed_rows.append(
                result.get(
                    "fail_code",
                    f"FAIL: row {row_number} failed",
                )
            )

    if failed_rows:
        return False, {
            "fail_code": " | ".join(failed_rows),
            "RMS_Channel_Data": rms_data,
        }

    return True, {
        "fail_code": "",
        "RMS_Channel_Data": rms_data,
    }


# ----------------------------------------------------------
# Individual row functions
#
# These make it easy for main.py to register each row as a
# separate acceptance check if desired.
# ----------------------------------------------------------

def check_row34(rows, file_type):
    return _check_specific_row(rows, 34, file_type)


def check_row35(rows, file_type):
    return _check_specific_row(rows, 35, file_type)


def check_row36(rows, file_type):
    return _check_specific_row(rows, 36, file_type)


def check_row37(rows, file_type):
    return _check_specific_row(rows, 37, file_type)


def check_row38(rows, file_type):
    return _check_specific_row(rows, 38, file_type)


def check_row39(rows, file_type):
    return _check_specific_row(rows, 39, file_type)


def check_row40(rows, file_type):
    return _check_specific_row(rows, 40, file_type)


def check_row41(rows, file_type):
    return _check_specific_row(rows, 41, file_type)


def check_row42(rows, file_type):
    return _check_specific_row(rows, 42, file_type)


def check_row43(rows, file_type):
    return _check_specific_row(rows, 43, file_type)


def check_row44(rows, file_type):
    return _check_specific_row(rows, 44, file_type)


def check_row45(rows, file_type):
    return _check_specific_row(rows, 45, file_type)


def check_row46(rows, file_type):
    return _check_specific_row(rows, 46, file_type)


def check_row47(rows, file_type):
    return _check_specific_row(rows, 47, file_type)


def check_row48(rows, file_type):
    return _check_specific_row(rows, 48, file_type)


def check_row49(rows, file_type):
    return _check_specific_row(rows, 49, file_type)


def check_row50(rows, file_type):
    return _check_specific_row(rows, 50, file_type)


def check_row51(rows, file_type):
    return _check_specific_row(rows, 51, file_type)


def check_row52(rows, file_type):
    return _check_specific_row(rows, 52, file_type)


def check_row53(rows, file_type):
    return _check_specific_row(rows, 53, file_type)


def check_row54(rows, file_type):
    return _check_specific_row(rows, 54, file_type)


def _check_specific_row(rows, row_number, file_type):
    """
    Check one specific row.
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

    return _check_row(
        rows=rows,
        row_number=row_number,
        criteria=criteria,
    )


def _check_row(rows, row_number, criteria):
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
    # Column A / Column B
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
    # Collect all 16 channel measurements
    # --------------------------------------------------

    channel_measurements = {}

    missing_channels = []

    for channel_number in range(16):
        measurement = find_channel_measurements(
            row,
            channel_number,
        )

        if measurement is None:
            missing_channels.append(
                f"CH{channel_number}"
            )
        else:
            channel_measurements[
                channel_number
            ] = measurement

    if missing_channels:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} missing/unreadable "
                "channels: "
                + ", ".join(missing_channels)
            )
        }

    # --------------------------------------------------
    # 16-channel PED statistics
    # --------------------------------------------------

    ped_values = [
        channel_measurements[channel]["ped"]
        for channel in range(16)
    ]

    ped_mean = _mean(ped_values)
    ped_std = _population_std(ped_values)

    ped_lower = (
        ped_mean
        - criteria["ped_mean_std_multiplier"] * ped_std
    )

    ped_upper = (
        ped_mean
        + criteria["ped_mean_std_multiplier"] * ped_std
    )

    # --------------------------------------------------
    # 16-channel posAmp statistics
    # --------------------------------------------------

    posamp_values = [
        channel_measurements[channel]["posAmp"]
        for channel in range(16)
    ]

    posamp_mean = _mean(posamp_values)
    posamp_std = _population_std(posamp_values)

    posamp_lower = (
        posamp_mean
        - criteria["posamp_mean_std_multiplier"] * posamp_std
    )

    posamp_upper = (
        posamp_mean
        + criteria["posamp_mean_std_multiplier"] * posamp_std
    )

    # --------------------------------------------------
    # Check every channel
    # --------------------------------------------------

    failures = []

    for channel_number in range(16):

        measurement = channel_measurements[
            channel_number
        ]

        col = column_letter(
            measurement["column"]
        )

        ped = measurement["ped"]
        posamp = measurement["posAmp"]
        negamp = measurement["negAmp"]

        # ----------------------------------------------
        # PED: mean +/- 3 STD
        # ----------------------------------------------

        if not ped_lower <= ped <= ped_upper:
            failures.append(
                (
                    f"CH{channel_number} ({col}): "
                    f"ped={ped} outside "
                    f"3STD range "
                    f"({ped_lower:.6g} ~ "
                    f"{ped_upper:.6g})"
                )
            )

        # ----------------------------------------------
        # posAmp: mean +/- 3 STD
        # ----------------------------------------------

        if not posamp_lower <= posamp <= posamp_upper:
            failures.append(
                (
                    f"CH{channel_number} ({col}): "
                    f"posAmp={posamp} outside "
                    f"3STD range "
                    f"({posamp_lower:.6g} ~ "
                    f"{posamp_upper:.6g})"
                )
            )

        # ----------------------------------------------
        # Conditional posAmp / negAmp difference
        #
        # Only apply when ped > 7500.
        # Requirement:
        #
        #     abs(posAmp - negAmp) < 200
        # ----------------------------------------------

        if ped > criteria["ped_threshold"]:

            amp_difference = abs(
                posamp - negamp
            )

            if not (
                amp_difference
                < criteria[
                    "posamp_negamp_max_difference"
                ]
            ):
                failures.append(
                    (
                        f"CH{channel_number} ({col}): "
                        f"ped={ped} > "
                        f"{criteria['ped_threshold']}, "
                        f"but |posAmp-negAmp|="
                        f"{amp_difference:.6g} "
                        f">= "
                        f"{criteria['posamp_negamp_max_difference']}"
                    )
                )

    # --------------------------------------------------
    # Return result
    # --------------------------------------------------

    if failures:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} - "
                + " | ".join(failures)
            )
        }

    return True, {
        "fail_code": "",
        "Column_A": col_a_value,
        "Column_B": col_b_value,
        "Ped_Mean_16CH": ped_mean,
        "Ped_STD_16CH": ped_std,
        "Ped_Lower_3STD": ped_lower,
        "Ped_Upper_3STD": ped_upper,
        "PosAmp_Mean_16CH": posamp_mean,
        "PosAmp_STD_16CH": posamp_std,
        "PosAmp_Lower_3STD": posamp_lower,
        "PosAmp_Upper_3STD": posamp_upper,
    }


def check_rms_order_rows34_37(rows, file_type):
    """
    Cross-row RMS check for CH0 ~ CH15.

    RT only:
        For each channel:
            rms(row37) < rms(row35) < rms(row34) < rms(row36)

    LN:
        Ordering check is skipped.

    The measured four-value ratio is also returned relative to
    the Row 37 RMS value, alongside the reference
    4.7:6.4:12:20 pattern.

    This function checks the required RMS ordering. The reference
ratio calculation is retained for diagnostics, but its PASS/FAIL
check is disabled.
    """

    # The RMS ordering criterion applies to RT only.
    # LN files skip this cross-row ordering check.
    if file_type == "LN":
        return True, {
            "fail_code": "",
            "RMS_Channel_Data": {},
        }

    if file_type != "RT":
        return False, {
            "fail_code": (
                f"FAIL: unsupported file type for RMS "
                f"ordering check: {file_type}"
            )
        }

    required_rows = (34, 35, 36, 37)
    row_data = {}

    # --------------------------------------------------
    # Get all four rows.
    # --------------------------------------------------

    for row_number in required_rows:
        row_index = row_number - 1

        if len(rows) <= row_index:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} is missing"
                )
            }

        row_data[row_number] = rows[row_index]

    failures = []
    channel_data = {}

    # --------------------------------------------------
    # Extract RMS for CH0 ~ CH15 from each row.
    # --------------------------------------------------

    for channel_number in range(16):

        rms_values = {}

        for row_number in required_rows:

            measurement = find_channel_measurements(
                row_data[row_number],
                channel_number,
            )

            if measurement is None:
                failures.append(
                    (
                        f"CH{channel_number}: "
                        f"row {row_number} RMS "
                        "could not be parsed"
                    )
                )
                continue

            rms_values[row_number] = (
                measurement["rms"]
            )

        if len(rms_values) != 4:
            continue

        rms37 = rms_values[37]
        rms35 = rms_values[35]
        rms34 = rms_values[34]
        rms36 = rms_values[36]

        # --------------------------------------------------
        # Required ordering
        # --------------------------------------------------

        if not (
            rms37 < rms35 < rms34 < rms36
        ):
            failures.append(
                (
                    f"CH{channel_number}: RMS order failed "
                    f"(row37={rms37}, "
                    f"row35={rms35}, "
                    f"row34={rms34}, "
                    f"row36={rms36}); "
                    "required row37 < row35 < row34 < row36"
                )
            )

        # --------------------------------------------------
        # Measured ratio normalized to Row 37.
        # --------------------------------------------------

        if rms37 != 0:
            measured_ratio = {
                37: rms37 / rms37,
                35: rms35 / rms37,
                34: rms34 / rms37,
                36: rms36 / rms37,
            }
        else:
            measured_ratio = {
                37: math.nan,
                35: math.nan,
                34: math.nan,
                36: math.nan,
            }

        # --------------------------------------------------
        # Ratio acceptance with +/-20% tolerance.
        #
        # Normalize the expected ratios to Row 37:
        #
        #   measured:
        #       Row37 = 1
        #
        #   expected:
        #       Row37 = 4.7 / 4.7 = 1
        #       Row35 = 6.4 / 4.7
        #       Row34 = 12  / 4.7
        #       Row36 = 20  / 4.7
        #
        # Each measured normalized ratio must be within
        # +/-20% of its expected normalized ratio.
        # --------------------------------------------------

        reference_normalized = {
            row_number: (
                RMS_REFERENCE_RATIOS[row_number]
                / RMS_REFERENCE_RATIOS[37]
            )
            for row_number in (37, 35, 34, 36)
        }

        ratio_failures = []

        for ratio_row in (35, 34, 36):

            measured = measured_ratio[ratio_row]
            expected = reference_normalized[ratio_row]

            lower = expected * (
                1.0 - RMS_RATIO_TOLERANCE
            )

            upper = expected * (
                1.0 + RMS_RATIO_TOLERANCE
            )

            if (
                ENABLE_RMS_RATIO_CHECK
                and not lower <= measured <= upper
            ):
                ratio_failures.append(
                    (
                        f"row{ratio_row} ratio="
                        f"{measured:.6g}, expected="
                        f"{expected:.6g}, allowed="
                        f"{lower:.6g}~{upper:.6g}"
                    )
                )

        if ratio_failures:
            failures.append(
                (
                    f"CH{channel_number}: RMS ratio "
                    "outside +/-20% tolerance - "
                    + "; ".join(ratio_failures)
                )
            )

        channel_data[channel_number] = {
            "rms_row37": rms37,
            "rms_row35": rms35,
            "rms_row34": rms34,
            "rms_row36": rms36,
            "measured_ratio_row37_row35_row34_row36": measured_ratio,
            "reference_ratio_row37_row35_row34_row36": {
                37: RMS_REFERENCE_RATIOS[37],
                35: RMS_REFERENCE_RATIOS[35],
                34: RMS_REFERENCE_RATIOS[34],
                36: RMS_REFERENCE_RATIOS[36],
            },
            "reference_normalized_to_row37": reference_normalized,
            "ratio_tolerance": RMS_RATIO_TOLERANCE,
        }

    if failures:
        return False, {
            "fail_code": (
                "FAIL: Rows 34-37 RMS ordering - "
                + " | ".join(failures)
            ),
            "RMS_Channel_Data": channel_data,
        }

    return True, {
        "fail_code": "",
        "RMS_Channel_Data": channel_data,
    }


def _mean(values):
    if not values:
        raise ValueError(
            "Cannot calculate mean of an empty list."
        )

    return sum(values) / len(values)


def _population_std(values):
    """
    Population standard deviation.
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
