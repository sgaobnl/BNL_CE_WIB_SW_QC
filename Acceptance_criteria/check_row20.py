from common import (
    column_letter,
    find_labeled_value,
    find_channel_measurements,
)

RT_CRITERIA = {
    "col_a": "Test_00_QC_INIT_CHK",
    "col_b": "ASICDAC_47mV_CHK",
    "vdda_range": (35, 40),
    "vddo_range": (0.01, 0.1),
    "vddp_range": (55, 75),
    "ped_range": (600, 1200),
    "rms_range": (4, 5),
    "posamp_range": (6400, 6900),
}

LN_CRITERIA = {
    "col_a": "Test_00_QC_INIT_CHK",
    "col_b": "ASICDAC_47mV_CHK",
    "vdda_range": (28, 35),
    "vddo_range": (0.01, 0.1),
    "vddp_range": (55, 75),
    "ped_range": (500, 1200),
    "rms_range": (2, 6),
    "posamp_range": (6000, 6300),
}


def check_row20(rows, file_type):
    """Check 3 - Row 20. RT and LN criteria are kept separately."""
    if file_type == "RT":
        criteria = RT_CRITERIA
    elif file_type == "LN":
        criteria = LN_CRITERIA
    else:
        return False, {"fail_code": f"FAIL: unsupported file type: {file_type}"}

    return _check_row(rows, 20, criteria)


def _check_row(rows, row_number, criteria):
    row_index = row_number - 1

    if len(rows) <= row_index:
        return False, {"fail_code": f"FAIL: row {row_number} is missing"}

    row = rows[row_index]

    if len(row) < 2:
        return False, {"fail_code": f"FAIL: row {row_number} is incomplete"}

    if row[0].strip() != criteria["col_a"]:
        return False, {
            "fail_code": f"FAIL: row {row_number} column A is incorrect: {row[0].strip()}"
        }

    if row[1].strip() != criteria["col_b"]:
        return False, {
            "fail_code": f"FAIL: row {row_number} column B is incorrect: {row[1].strip()}"
        }

    supplies = {}
    for label, range_key in (
        ("Vdda_P", "vdda_range"),
        ("Vddo_P", "vddo_range"),
        ("Vddp_P", "vddp_range"),
    ):
        value, col_index = find_labeled_value(row, label)
        if value is None:
            return False, {"fail_code": f"FAIL: row {row_number} {label} not found"}

        low, high = criteria[range_key]
        if not low <= value <= high:
            return False, {
                "fail_code": f"FAIL: row {row_number} {label} out of range: {value}"
            }

        supplies[label] = (value, col_index)

    for channel_number in range(16):
        measurement = find_channel_measurements(row, channel_number)

        if measurement is None:
            return False, {
                "fail_code": (
                    f"FAIL: row {row_number} CH{channel_number} not found "
                    "or measurement cannot be parsed"
                )
            }

        col = column_letter(measurement["column"])
        values = (
            ("ped", measurement["ped"], criteria["ped_range"]),
            ("rms", measurement["rms"], criteria["rms_range"]),
            ("posAmp", measurement["posAmp"], criteria["posamp_range"]),
        )

        for label, value, limits in values:
            if not limits[0] <= value <= limits[1]:
                return False, {
                    "fail_code": (
                        f"FAIL: row {row_number} CH{channel_number} ({col}) "
                        f"{label} out of range: {value}"
                    )
                }

    return True, {
        "fail_code": "",
        "Vdda_P": supplies["Vdda_P"][0],
        "Vdda_P_Column": column_letter(supplies["Vdda_P"][1]),
        "Vddo_P": supplies["Vddo_P"][0],
        "Vddo_P_Column": column_letter(supplies["Vddo_P"][1]),
        "Vddp_P": supplies["Vddp_P"][0],
        "Vddp_P_Column": column_letter(supplies["Vddp_P"][1]),
    }
