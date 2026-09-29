import re

MEASUREMENT_PATTERN = re.compile(
    r"ped\s*[:=]\s*([-+]?\d*\.?\d+)"
    r".*?rms\s*[:=]\s*([-+]?\d*\.?\d+)"
    r".*?posAMP\s*[:=]\s*([-+]?\d*\.?\d+)",
    re.IGNORECASE,
)

NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"


def parse_measurement_cell(cell):
    if not cell:
        return None

    text = str(cell).strip()
    match = MEASUREMENT_PATTERN.search(text)
    if not match:
        return None

    result = {
        "ped": float(match.group(1)),
        "rms": float(match.group(2)),
        "posAmp": float(match.group(3)),
    }

    neg_match = re.search(
        rf"\bnegAmp\b\s*[:=]\s*({NUMBER})",
        text,
        re.IGNORECASE,
    )
    if neg_match:
        result["negAmp"] = float(neg_match.group(1))

    return result


def find_channel_measurements(row, channel_number):
    """Search an entire row for CHx and return parsed measurements."""
    channel_pattern = re.compile(
        rf"\bCH{channel_number}\b",
        re.IGNORECASE,
    )

    for column_index, cell in enumerate(row):
        text = str(cell).strip()
        if not channel_pattern.search(text):
            continue

        measurement = parse_measurement_cell(text)
        if measurement is None:
            # Accept pedestal naming as well as ped and allow fields in any order.
            ped_match = re.search(
                rf"\b(?:pedestal|ped)\b\s*[=:]\s*({NUMBER})",
                text,
                re.IGNORECASE,
            )
            rms_match = re.search(
                rf"\brms\b\s*[=:]\s*({NUMBER})",
                text,
                re.IGNORECASE,
            )
            pos_match = re.search(
                rf"\bposAmp\b\s*[=:]\s*({NUMBER})",
                text,
                re.IGNORECASE,
            )
            if ped_match and rms_match and pos_match:
                measurement = {
                    "ped": float(ped_match.group(1)),
                    "rms": float(rms_match.group(1)),
                    "posAmp": float(pos_match.group(1)),
                }
                neg_match = re.search(
                    rf"\bnegAmp\b\s*[=:]\s*({NUMBER})",
                    text,
                    re.IGNORECASE,
                )
                if neg_match:
                    measurement["negAmp"] = float(neg_match.group(1))

        if measurement is not None:
            measurement["column"] = column_index
            return measurement

    return None


def find_labeled_value(row, label):
    """Find LABEL=value in a row; return (float_value, column_index)."""
    pattern = re.compile(
        rf"\b{re.escape(label)}\b\s*[=:]\s*({NUMBER})",
        re.IGNORECASE,
    )

    for column_index, cell in enumerate(row):
        text = str(cell).strip()
        match = pattern.search(text)
        if match:
            return float(match.group(1)), column_index

    return None, None


def column_letter(index):
    result = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result
