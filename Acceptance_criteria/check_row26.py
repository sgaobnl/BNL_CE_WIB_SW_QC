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

    "ped_range": (400, 800),
    "rms_range": (8, 16),
    "posamp_range": (8500, 8900),
}


# ==========================================================
# Row 26 acceptance criteria - LN
# ==========================================================

LN_CRITERIA = {
    "col_a": "Test_00_QC_INIT_CHK",
    "col_b": "ASICDAC_CALI_CHK",

    "vdda_range": (80, 90),
    "vddo_range": (15, 25),
    "vddp_range": (50, 60),



    "ped_range": (500, 1200),
    "rms_range": (5, 100),
    "posamp_range": (8100, 8400),
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
    # Column A
    # --------------------------------------------------

    if row[0].strip() != criteria["col_a"]:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"column A is incorrect: "
                f"{row[0].strip()}"
            )
        }

    # --------------------------------------------------
    # Column B
    # --------------------------------------------------

    if row[1].strip() != criteria["col_b"]:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} "
                f"column B is incorrect: "
                f"{row[1].strip()}"
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

        col_index = measurement["column"]
        col = column_letter(col_index)

        ped = measurement["ped"]
        rms = measurement["rms"]
        posamp = measurement["posAmp"]

        # PED
        if not (
            criteria["ped_range"][0]
            <= ped
            <= criteria["ped_range"][1]
        ):
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} "
                    f"CH{channel_number} ({col}) "
                    f"ped out of range: {ped}"
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
        if not (
            criteria["posamp_range"][0]
            <= posamp
            <= criteria["posamp_range"][1]
        ):
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} "
                    f"CH{channel_number} ({col}) "
                    f"posAmp out of range: {posamp}"
                )
            }

    # --------------------------------------------------
    # All Row 26 checks passed
    # --------------------------------------------------

    return True, {
        "fail_code": "",

        "Vdda_P": vdda_p,
        "Vdda_P_Column": column_letter(vdda_col),

        "Vddo_P": vddo_p,
        "Vddo_P_Column": column_letter(vddo_col),

        "Vddp_P": vddp_p,
        "Vddp_P_Column": column_letter(vddp_col),
    }
