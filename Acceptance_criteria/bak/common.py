import re


MEASUREMENT_PATTERN = re.compile(
    r"ped\s*[:=]\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))"
    r".*?"
    r"rms\s*[:=]\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))"
    r".*?"
    r"posAMP\s*[:=]\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))",
    re.IGNORECASE,
)


def parse_measurement_cell(cell):
    """
    Parse a measurement cell containing ped, rms, and posAMP.

    Supported examples:
        ped=650,rms=5.2,posAMP=6500
        ped:650 rms:5.2 posAMP:6500

    Returns None if parsing fails.
    """
    if not cell:
        return None

    match = MEASUREMENT_PATTERN.search(str(cell).strip())

    if not match:
        return None

    return {
        "ped": float(match.group(1)),
        "rms": float(match.group(2)),
        "posAMP": float(match.group(3)),
    }


def to_float(value):
    """
    Extract the first numeric value from a cell.

    Examples:
        "37.5" -> 37.5
        "37.5 mV" -> 37.5
        "Vdda_P=37.5" -> 37.5
    """
    if value is None:
        return None

    match = re.search(
        r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)",
        str(value),
    )

    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def column_letter(index):
    """Convert zero-based index to Excel-style column name."""
    result = ""
    index += 1

    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result

    return result
