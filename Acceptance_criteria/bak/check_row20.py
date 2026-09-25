from common import (
    parse_measurement_cell,
    column_letter,
    to_float,
)


def check_row20(rows, file_type):
    """
    Check 3 - Row 20.

    RT and LN use the same criteria.

        A = Test_00_QC_INIT_CHK
        B = ASICDAC_47mV_CHK

        D = Vdda_P : 35 ~ 40
        E = Vddo_P : 0.01 ~ 0.1
        F = Vddp_P : 55 ~ 75

        L ~ AA:
            ped    = 500 ~ 1500
            rms    = 2 ~ 10
            posAMP = 6000 ~ 7000
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

    # AA = column index 26
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

    # D = Vdda_P
    vdda_p = to_float(row[3])

    if vdda_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vdda_P "
                f"is not numeric: {row[3]}"
            )
        }

    if not vdda_range[0] <= vdda_p <= vdda_range[1]:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vdda_P "
                f"out of range: {vdda_p}"
            )
        }

    # E = Vddo_P
    vddo_p = to_float(row[4])

    if vddo_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddo_P "
                f"is not numeric: {row[4]}"
            )
        }

    if not vddo_range[0] <= vddo_p <= vddo_range[1]:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddo_P "
                f"out of range: {vddo_p}"
            )
        }

    # F = Vddp_P
    vddp_p = to_float(row[5])

    if vddp_p is None:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddp_P "
                f"is not numeric: {row[5]}"
            )
        }

    if not vddp_range[0] <= vddp_p <= vddp_range[1]:
        return False, {
            "fail_code": (
                f"FAIL: row {row_number} Vddp_P "
                f"out of range: {vddp_p}"
            )
        }

    # L ~ AA
    for col_index in range(11, 27):
        col = column_letter(col_index)
        measurement = parse_measurement_cell(row[col_index])

        if measurement is None:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} column {col} "
                    "measurement cannot be parsed"
                )
            }

        ped = measurement["ped"]
        rms = measurement["rms"]
        posamp = measurement["posAMP"]

        if not ped_range[0] <= ped <= ped_range[1]:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} {col} "
                    f"ped out of range: {ped}"
                )
            }

        if not rms_range[0] <= rms <= rms_range[1]:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} {col} "
                    f"rms out of range: {rms}"
                )
            }

        if not posamp_range[0] <= posamp <= posamp_range[1]:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} {col} "
                    f"posAMP out of range: {posamp}"
                )
            }

    return True, {
        "fail_code": "",
        "Vdda_P": vdda_p,
        "Vddo_P": vddo_p,
        "Vddp_P": vddp_p,
    }
