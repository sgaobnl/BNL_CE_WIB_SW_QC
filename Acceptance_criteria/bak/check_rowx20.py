from common import (
    column_letter,
    find_labeled_value,
    find_channel_measurements,
)

def check_row20(rows, file_type):
    """
    Check 3 - Row 20.

    RT and LN use the same criteria.

        A = Test_00_QC_INIT_CHK
        B = ASICDAC_47mV_CHK

        Vdda_P : 35 ~ 40
        Vddo_P : 0.01 ~ 0.1
        Vddp_P : 55 ~ 75

        Search the entire Row 21 for:
            CH0 ~ CH15

        For each channel, extract from the same cell:
            ped    = 500 ~ 1500
            rms    = 2 ~ 10
            posAmp = 6000 ~ 7000
    """

    if file_type not in ("RT", "LN"):
        return False, {
            "fail_code": f"FAIL: unsupported file type: {file_type}"
        }

    return _check_row(
        rows=rows,
        row_number=20,
        expected_col_a="Test_00_QC_INIT_CHK",
        expected_col_b="ASICDAC_47mV_CHK",
        vdda_range=(35, 40),
        vddo_range=(0.01, 0.1),
        vddp_range=(55, 75),
        ped_range=(500, 1500),
        rms_range=(2, 10),
        posamp_range=(6000, 7000),
    )


def _check_row(
    rows,
    row_number,
    expected_col_a,
    expected_col_b,
    vdda_range,
    vddo_range,
    vddp_range,
    ped_range,
    rms_range,
    posamp_range,
):
    row_index = row_number - 1

    if len(rows) <= row_index:
        return False, {
            "fail_code": f"FAIL: row {row_number} is missing"
        }

    row = rows[row_index]

    if len(row) <= 26:
        return False, {
            "fail_code": f"FAIL: row {row_number} is incomplete"
        }

    # A
    if row[0].strip() != expected_col_a:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} column A is incorrect: "
                f"{row[0].strip()}"
            )
        }

    # B
    if row[1].strip() != expected_col_b:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} column B is incorrect: "
                f"{row[1].strip()}"
            )
        }

    # Vdda_P
    vdda_p, vdda_col = find_labeled_value(row, "Vdda_P")
    if vdda_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vdda_P not found"
            )
        }
    
    if not vdda_range[0] <= vdda_p <= vdda_range[1]:
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
        "Vddo_P"
    )
    
    if vddo_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddo_P not found"
            )
        }
    
    if not vddo_range[0] <= vddo_p <= vddo_range[1]:
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
        "Vddp_P"
    )
    
    if vddp_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddp_P not found"
            )
        }
    
    if not vddp_range[0] <= vddp_p <= vddp_range[1]:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddp_P "
                f"out of range: {vddp_p}"
            )
        }

    # --------------------------------------------------
    # Search entire Row 20 for CH0 ~ CH15
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
        if not ped_range[0] <= ped <= ped_range[1]:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} CH{channel_number} "
                    f"({col}) ped out of range: {ped}"
                )
            }
    
        # RMS
        if not rms_range[0] <= rms <= rms_range[1]:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} CH{channel_number} "
                    f"({col}) rms out of range: {rms}"
                )
            }
    
        # posAmp
        if not posamp_range[0] <= posamp <= posamp_range[1]:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} CH{channel_number} "
                    f"({col}) posAmp out of range: {posamp}"
                )
            }

    return True, {
        "fail_code": "",
    
        "Vdda_P": vdda_p,
        "Vdda_P_Column": column_letter(vdda_col),
    
        "Vddo_P": vddo_p,
        "Vddo_P_Column": column_letter(vddo_col),
    
        "Vddp_P": vddp_p,
        "Vddp_P_Column": column_letter(vddp_col),
    }
