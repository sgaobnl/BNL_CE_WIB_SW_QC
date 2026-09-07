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
    if value is None:
        return None
    match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", str(value))
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None

def find_labeled_value(row, label):
    """
    Find the first cell containing label (case-insensitive) and
    extract the first numeric value appearing after the label.
    Returns (value, zero_based_column_index) or (None, None).
    """
    if row is None:
        return None, None

    label_lower = label.lower()

    for col_index, cell in enumerate(row):
        text = str(cell).strip()
        text_lower = text.lower()

        if label_lower not in text_lower:
            continue

        pos = text_lower.find(label_lower)
        value = to_float(text[pos + len(label):])

        if value is not None:
            return value, col_index

    return None, None


def find_channel_measurements(row, channel_number):
    """
    Search the entire row for a cell containing CH0 ~ CH15,
    then extract ped, rms, and posAmp from that same cell.

    Returns:
        {
            "column": column_index,
            "ped": float,
            "rms": float,
            "posAmp": float,
        }

    Returns None if the channel or measurements cannot be found.
    """
    if not 0 <= channel_number <= 15:
        return None

    # Exact channel match prevents CH1 from matching CH10, CH11, etc.
    channel_pattern = re.compile(
        rf"\bCH{channel_number}\b",
        re.IGNORECASE,
    )

    for col_index, cell in enumerate(row):
        text = str(cell).strip()

        if not channel_pattern.search(text):
            continue

        measurement = parse_measurement_cell(text)

        if measurement is None:
            return None

        return {
            "column": col_index,
            "ped": measurement["ped"],
            "rms": measurement["rms"],
            "posAmp": measurement["posAMP"],
        }

    return None


def column_letter(index):
    """
    Convert zero-based column index to Excel-style column name.

        0  -> A
        1  -> B
        11 -> L
        26 -> AA
    """
    result = ""
    index += 1

    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result

    return result
