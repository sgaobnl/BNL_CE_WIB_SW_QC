import re

SN_LABEL = "FE_OCR_SN"
SN_PATTERN = re.compile(r"^\d{3}_\d{5}$")

def check_serial_number(rows, file_type=None):
    """
    Check 2, Row 5:
        A = FE_OCR_SN
        B = 3digits_5digits
    """
    row_index = 4

    if len(rows) <= row_index:
        return False, {
            "sn": "",
            "fail_code": "FAIL: row 5 is missing",
        }

    row = rows[row_index]

    if len(row) < 2:
        return False, {
            "sn": "",
            "fail_code": "FAIL: row 5 is incomplete",
        }

    if row[0].strip() != SN_LABEL:
        return False, {
            "sn": "",
            "fail_code": "FAIL: SN is incorrect",
        }

    sn = row[1].strip()

    if SN_PATTERN.fullmatch(sn):
        return True, {
            "sn": sn,
            "fail_code": "",
        }

    return False, {
        "sn": sn,
        "fail_code": "FAIL: SN is incorrect",
    }
