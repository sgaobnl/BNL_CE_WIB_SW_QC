import math

from common import (
    column_letter,
    find_labeled_value,
    find_channel_measurements,
)


# ==========================================================
# Row 31 acceptance criteria - RT
# ==========================================================

RT_CRITERIA = {
    # Same voltage ranges as check_row28.py
    "vdda_range": (35, 40),
    "vddo_range": (-0.01, 0.1),
    "vddp_range": (55, 75),

    "rms_range": (8, 16),
}


# ==========================================================
# Row 31 acceptance criteria - LN
# ==========================================================

LN_CRITERIA = {
    # Same voltage ranges as check_row28.py
    "vdda_range": (28, 35),
    "vddo_range": (-0.01, 0.1),
    "vddp_range": (55, 75),

    "rms_range": (5, 100),
}


def check_row31(rows, file_type):
    """
    Check Row 31.

    Column A and Column B are taken directly from Row 31.
    They are only checked for being present/non-empty.

    Vdda_P / Vddo_P / Vddp_P are located by label search.

    Search the entire Row 31 for:
        CH0 ~ CH15

    For the 16 channels:
        ped    = mean +/- 3*STD
        rms    = 2 ~ 10
        posAmp = mean +/- 3*STD

    RT and LN use separate voltage/rms criteria.
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
        row_number=31,
        criteria=criteria,
        file_type=file_type,
    )


def _check_row(
    rows,
    row_number,
    criteria,
    file_type,
):
    row_index = row_number - 1

    # --------------------------------------------------
    # Check row exists
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
    #
    # Use the actual values from this row.
    # --------------------------------------------------

    col_a_value = row[0].strip()
    col_b_value = row[1].strip()

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
    # Find Vdda_P
    # --------------------------------------------------

    vdda_p, vdda_col = find_labeled_value(
        row,
        "Vdda_P",
    )

    if vdda_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vdda_P not found"
            )
        }

    if not (
        criteria["vdda_range"][0]
        <= vdda_p
        <= criteria["vdda_range"][1]
    ):
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vdda_P "
                f"out of range: {vdda_p}"
            )
        }

    # --------------------------------------------------
    # Find Vddo_P
    # --------------------------------------------------

    vddo_p, vddo_col = find_labeled_value(
        row,
        "Vddo_P",
    )

    if vddo_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddo_P not found"
            )
        }

    if not (
        criteria["vddo_range"][0]
        <= vddo_p
        <= criteria["vddo_range"][1]
    ):
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddo_P "
                f"out of range: {vddo_p}"
            )
        }

    # --------------------------------------------------
    # Find Vddp_P
    # --------------------------------------------------

    vddp_p, vddp_col = find_labeled_value(
        row,
        "Vddp_P",
    )

    if vddp_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddp_P not found"
            )
        }

    if not (
        criteria["vddp_range"][0]
        <= vddp_p
        <= criteria["vddp_range"][1]
    ):
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddp_P "
                f"out of range: {vddp_p}"
            )
        }

    # --------------------------------------------------
    # Get all 16 channel measurements first
    # --------------------------------------------------

    channel_measurements = {}

    for channel_number in range(16):

        measurement = find_channel_measurements(
            row,
            channel_number,
        )

        if measurement is None:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} "
                    f"CH{channel_number} not found "
                    "or measurement cannot be parsed"
                )
            }

        channel_measurements[channel_number] = measurement

    # --------------------------------------------------
    # Calculate 16-channel statistics
    # --------------------------------------------------

    ped_values = [
        channel_measurements[channel]["ped"]
        for channel in range(16)
    ]

    posamp_values = [
        channel_measurements[channel]["posAmp"]
        for channel in range(16)
    ]

    ped_mean = _mean(ped_values)
    ped_std = _population_std(ped_values)

    posamp_mean = _mean(posamp_values)
    posamp_std = _population_std(posamp_values)

    ped_lower = ped_mean - 3.0 * ped_std
    ped_upper = ped_mean + 3.0 * ped_std

    posamp_lower = posamp_mean - 3.0 * posamp_std
    posamp_upper = posamp_mean + 3.0 * posamp_std

    # --------------------------------------------------
    # Check all 16 channels
    # --------------------------------------------------

    for channel_number in range(16):

        measurement = channel_measurements[
            channel_number
        ]

        col = column_letter(
            measurement["column"]
        )

        ped = measurement["ped"]
        rms = measurement["rms"]
        posamp = measurement["posAmp"]

        # PED
        if not ped_lower <= ped <= ped_upper:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} "
                    f"CH{channel_number} ({col}) "
                    f"ped out of 3STD range "
                    f"({ped_lower:.6g} ~ "
                    f"{ped_upper:.6g}): {ped}"
                )
            }

        # RMS
        if not (
            criteria["rms_range"][0]
            <= rms
            <= criteria["rms_range"][1]
        ):
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} "
                    f"CH{channel_number} ({col}) "
                    f"rms out of range: {rms}"
                )
            }

        # posAmp
        if not posamp_lower <= posamp <= posamp_upper:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} "
                    f"CH{channel_number} ({col}) "
                    f"posAmp out of 3STD range "
                    f"({posamp_lower:.6g} ~ "
                    f"{posamp_upper:.6g}): {posamp}"
                )
            }

    # --------------------------------------------------
    # All checks passed
    # --------------------------------------------------

    return True, {
        "fail_code": "",
        "file_type": file_type,

        "Column_A": col_a_value,
        "Column_B": col_b_value,

        "Vdda_P": vdda_p,
        "Vdda_P_Column": column_letter(vdda_col),

        "Vddo_P": vddo_p,
        "Vddo_P_Column": column_letter(vddo_col),

        "Vddp_P": vddp_p,
        "Vddp_P_Column": column_letter(vddp_col),

        "Ped_Mean_16CH": ped_mean,
        "Ped_STD_16CH": ped_std,
        "Ped_Lower_3STD": ped_lower,
        "Ped_Upper_3STD": ped_upper,

        "PosAmp_Mean_16CH": posamp_mean,
        "PosAmp_STD_16CH": posamp_std,
        "PosAmp_Lower_3STD": posamp_lower,
        "PosAmp_Upper_3STD": posamp_upper,
    }


def _mean(values):
    if not values:
        raise ValueError(
            "Cannot calculate mean of an empty list."
        )

    return sum(values) / len(values)


def _population_std(values):
    """
    Calculate population standard deviation.

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
