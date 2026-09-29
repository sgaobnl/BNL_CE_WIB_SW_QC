import math

from common import (
    column_letter,
    find_labeled_value,
    find_channel_measurements,
)


# ==========================================================
# Row 26 acceptance criteria - RT
# ==========================================================

RT_CRITERIA = {
    "col_a": "Test_00_QC_INIT_CHK",
    "col_b": "ASICDAC_CALI_CHK",

    "vdda_range": (75, 90),
    "vddo_range": (15, 25),
    "vddp_range": (45, 55),

    "rms_range": (8, 20),
}


# ==========================================================
# Row 26 acceptance criteria - LN
# ==========================================================

LN_CRITERIA = {
    "col_a": "Test_00_QC_INIT_CHK",
    "col_b": "ASICDAC_CALI_CHK",

    "vdda_range": (80, 90+10),
    "vddo_range": (15, 25+15),
    "vddp_range": (45, 60),



    "rms_range": (2, 100),
}


def check_row26(rows, file_type):
    """
    Row 26 acceptance check.

        RT:
        A = Test_00_QC_INIT_CHK
        B = ASICDAC_CALI_CHK
        Vdda_P = 75 ~ 90
        Vddo_P = 15 ~ 25
        Vddp_P = 45 ~ 50
        CH0 ~ CH15:
            ped    = 600 ~ 1200
            rms    = 2 ~ 10
            posAmp = 8500 ~ 8900

    LN:
        A = Test_00_QC_INIT_CHK
        B = ASICDAC_CALI_CHK
        Vdda_P = 28 ~ 35
        Vddo_P = 0.01 ~ 0.1
        Vddp_P = 50 ~ 60
        CH0 ~ CH15:
            ped    = 600 ~ 1200
            rms    = 2 ~ 10
            posAmp = 8100 ~ 8400
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
        row_number=26,
        criteria=criteria,
    )


def _check_row(
    rows,
    row_number,
    criteria,
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
    # Vdda_P
    # --------------------------------------------------

    vdda_p, vdda_col = find_labeled_value(
        row,
        "Vdda_P",
    )

    if vdda_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "Vdda_P not found"
            )
        }

    if not (
        criteria["vdda_range"][0]
        <= vdda_p
        <= criteria["vdda_range"][1]
    ):
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"Vdda_P out of range: {vdda_p}"
            )
        }

    # --------------------------------------------------
    # Vddo_P
    # --------------------------------------------------

    vddo_p, vddo_col = find_labeled_value(
        row,
        "Vddo_P",
    )

    if vddo_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "Vddo_P not found"
            )
        }

    if not (
        criteria["vddo_range"][0]
        <= vddo_p
        <= criteria["vddo_range"][1]
    ):
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"Vddo_P out of range: {vddo_p}"
            )
        }

    # --------------------------------------------------
    # Vddp_P
    # --------------------------------------------------

    vddp_p, vddp_col = find_labeled_value(
        row,
        "Vddp_P",
    )

    if vddp_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                "Vddp_P not found"
            )
        }

    if not (
        criteria["vddp_range"][0]
        <= vddp_p
        <= criteria["vddp_range"][1]
    ):
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"Vddp_P out of range: {vddp_p}"
            )
        }

    # --------------------------------------------------
    # Search entire Row 26 for CH0 ~ CH15
    # --------------------------------------------------

    # --------------------------------------------------
    # Collect all 16 channel measurements first
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
    # Calculate 16-channel PED statistics
    #
    # Acceptance range:
    #     mean +/- 3 * population STD
    # --------------------------------------------------

    ped_values = [
        channel_measurements[channel]["ped"]
        for channel in range(16)
    ]

    ped_mean = _mean(ped_values)
    ped_std = _population_std(ped_values)

    ped_lower = ped_mean - 4.0 * ped_std
    ped_upper = ped_mean + 4.0 * ped_std

    # --------------------------------------------------
    # Calculate 16-channel posAmp statistics
    #
    # Acceptance range:
    #     mean +/- 3 * population STD
    # --------------------------------------------------

    posamp_values = [
        channel_measurements[channel]["posAmp"]
        for channel in range(16)
    ]

    posamp_mean = _mean(posamp_values)
    posamp_std = _population_std(posamp_values)

    posamp_lower = posamp_mean - 4.0 * posamp_std
    posamp_upper = posamp_mean + 4.0 * posamp_std

    # --------------------------------------------------
    # Check all 16 channels
    # --------------------------------------------------

    for channel_number in range(16):

        measurement = channel_measurements[
            channel_number
        ]

        col_index = measurement["column"]
        col = column_letter(col_index)

        ped = measurement["ped"]
        rms = measurement["rms"]
        posamp = measurement["posAmp"]

        # PED: mean +/- 3 STD
        if not ped_lower <= ped <= ped_upper:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} "
                    f"CH{channel_number} ({col}) "
                    f"ped out of 4STD range "
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

        # posAmp: mean +/- 3 STD
        if not posamp_lower <= posamp <= posamp_upper:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} "
                    f"CH{channel_number} ({col}) "
                    f"posAmp out of 4STD range "
                    f"({posamp_lower:.6g} ~ "
                    f"{posamp_upper:.6g}): {posamp}"
                )
            }

    return True, {
        "fail_code": "",
        "Ped_Mean_16CH": ped_mean,
        "Ped_STD_16CH": ped_std,
        "Ped_Lower_4STD": ped_lower,
        "Ped_Upper_4STD": ped_upper,
        "PosAmp_Mean_16CH": posamp_mean,
        "PosAmp_STD_16CH": posamp_std,
        "PosAmp_Lower_4STD": posamp_lower,
        "PosAmp_Upper_4STD": posamp_upper,

        "Vdda_P": vdda_p,
        "Vdda_P_Column": column_letter(vdda_col),

        "Vddo_P": vddo_p,
        "Vddo_P_Column": column_letter(vddo_col),

        "Vddp_P": vddp_p,
        "Vddp_P_Column": column_letter(vddp_col),
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
