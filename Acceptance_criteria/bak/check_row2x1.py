from common import (
    parse_measurement_cell,
    column_letter,
    to_float,
)


def check_row21(rows, file_type):
    """
    Check 4 - Row 21.

    This preserves the previously specified row-21 criteria.

    A = Test_00_QC_INIT_CHK
    B = ASICDAC_47mV_CHK_x10
    D = Vdda_P : 35 ~ 40

    L ~ AA:
        ped    = 500 ~ 1500
        rms    = 2 ~ 10
        posAMP = 3000 ~ 3500
    """

    if file_type not in ("RT", "LN"):
        return False, {
            "fail_code": f"FAIL: unsupported file type: {file_type}"
        }

    row_number = 21
    row_index = row_number - 1

    if len(rows) <= row_index:
        return False, {
            "fail_code": "FAIL: row 21 is missing"
        }

    row = rows[row_index]

    if len(row) <= 26:
        return False, {
            "fail_code": "FAIL: row 21 is incomplete"
        }

    if row[0].strip() != "Test_00_QC_INIT_CHK":
        return False, {
            "fail_code": "FAIL: row 21 column A is incorrect"
        }

    if row[1].strip() != "ASICDAC_47mV_CHK_x10":
        return False, {
            "fail_code": "FAIL: row 21 column B is incorrect"
        }

    # D = Vdda_P
    vdda_p = to_float(row[3])

    if vdda_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row 21 Vdda_P "
                f"is not numeric: {row[3]}"
            )
        }

    if not 35 <= vdda_p <= 40:
        return False, {
            "fail_code": (
                f"FAIL: row 21 Vdda_P "
                f"out of range: {vdda_p}"
            )
        }

    # L ~ AA
    for col_index in range(11, 27):
        col = column_letter(col_index)
        measurement = parse_measurement_cell(row[col_index])

        if measurement is None:
            return False, {
                "fail_code": (
                    f"FAIL: row 21 column {col} "
                    "measurement cannot be parsed"
                )
            }

        ped = measurement["ped"]
        rms = measurement["rms"]
        posamp = measurement["posAMP"]

        if not 500 <= ped <= 1500:
            return False, {
                "fail_code": (
                    f"FAIL: row 21 {col} "
                    f"ped out of range: {ped}"
                )
            }

        if not 2 <= rms <= 10:
            return False, {
                "fail_code": (
                    f"FAIL: row 21 {col} "
                    f"rms out of range: {rms}"
                )
            }

        if not 3000 <= posamp <= 3500:
            return False, {
                "fail_code": (
                    f"FAIL: row 21 {col} "
                    f"posAMP out of range: {posamp}"
                )
            }

    return True, {
        "fail_code": "",
        "Vdda_P": vdda_p,
    }
