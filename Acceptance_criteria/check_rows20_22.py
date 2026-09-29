import math

from common import column_letter, find_labeled_value, find_channel_measurements

RT_CRITERIA = {
    20: {"col_a": "Test_00_QC_INIT_CHK", "col_b": "ASICDAC_47mV_CHK", "vdda_range": (30, 40+5), "vddo_range": (-0.05, 0.1), "vddp_range": (55-5, 75+5), "rms_range": (4, 10), "ped_sigma": 4.0, "posamp_sigma": 4.0},
    21: {"col_a": "Test_00_QC_INIT_CHK", "col_b": "ASICDAC_47mV_CHK_x10", "vdda_range": (30, 40+5), "vddo_range": (-0.05, 0.1), "vddp_range": (55-5, 75+5), "rms_range": (2, 10), "ped_sigma": 4.0, "posamp_sigma": 4.0},
    22: {"col_a": "Test_00_QC_INIT_CHK", "col_b": "ASICDAC_47mV_CHK_x18", "vdda_range": (30, 40+5), "vddo_range": (-0.05, 0.1), "vddp_range": (55-5, 75+5), "rms_range": (2, 10), "ped_sigma": 4.0, "posamp_sigma": 4.0},
}

LN_CRITERIA = {
    20: {"col_a": "Test_00_QC_INIT_CHK", "col_b": "ASICDAC_47mV_CHK", "vdda_range": (25-5, 45+5), "vddo_range": (-0.1, 0.5), "vddp_range": (50-15, 85+5), "rms_range": (2, 100), "ped_sigma": 5.0, "posamp_sigma": 5.0},
    21: {"col_a": "Test_00_QC_INIT_CHK", "col_b": "ASICDAC_47mV_CHK_x10", "vdda_range": (25-5, 45+5), "vddo_range": (-0.1, 0.5), "vddp_range": (50-15, 85+5), "rms_range": (2, 100), "ped_sigma": 5.0, "posamp_sigma": 5.0},
    22: {"col_a": "Test_00_QC_INIT_CHK", "col_b": "ASICDAC_47mV_CHK_x18", "vdda_range": (25-5, 45+5), "vddo_range": (-0.1, 0.5), "vddp_range": (50-15, 85+5), "rms_range": (2, 100), "ped_sigma": 5.0, "posamp_sigma": 5.0},
}

def _get_criteria(row_number, file_type):
    if file_type == "RT":
        return RT_CRITERIA.get(row_number)
    if file_type == "LN":
        return LN_CRITERIA.get(row_number)
    return None

def _check_selected_row(rows, row_number, file_type):
    criteria = _get_criteria(row_number, file_type)
    if criteria is None:
        return False, {"fail_code": f"FAIL: unsupported file type or row: {file_type}, {row_number}"}
    return _check_row(rows, row_number, criteria, criteria["ped_sigma"], criteria["posamp_sigma"])

def check_row20(rows, file_type):
    return _check_selected_row(rows, 20, file_type)

def check_row21(rows, file_type):
    return _check_selected_row(rows, 21, file_type)

def check_row22(rows, file_type):
    return _check_selected_row(rows, 22, file_type)

CHECK_FUNCTIONS = {
    "check_row20": check_row20,
    "check_row21": check_row21,
    "check_row22": check_row22,
}

def _check_row(rows, row_number, criteria, ped_sigma=4.0, posamp_sigma=4.0):
    row_index = row_number - 1
    if len(rows) <= row_index:
        return (False, {'fail_code': f'FAIL: row {row_number} is missing'})
    row = rows[row_index]
    if len(row) < 2:
        return (False, {'fail_code': f'FAIL: row {row_number} is incomplete'})
    if row[0].strip() != criteria['col_a']:
        return (False, {'fail_code': f'FAIL: row {row_number} column A is incorrect: {row[0].strip()}'})
    if row[1].strip() != criteria['col_b']:
        return (False, {'fail_code': f'FAIL: row {row_number} column B is incorrect: {row[1].strip()}'})
    supplies = {}
    for label, range_key in (('Vdda_P', 'vdda_range'), ('Vddo_P', 'vddo_range'), ('Vddp_P', 'vddp_range')):
        value, col_index = find_labeled_value(row, label)
        if value is None:
            return (False, {'fail_code': f'FAIL: row {row_number} {label} not found'})
        low, high = criteria[range_key]
        if not low <= value <= high:
            return (False, {'fail_code': f'FAIL: row {row_number} {label} out of range: {value}'})
        supplies[label] = (value, col_index)
    channel_measurements = {}
    for channel_number in range(16):
        measurement = find_channel_measurements(row, channel_number)
        if measurement is None:
            return (False, {'fail_code': f'FAIL: row {row_number} CH{channel_number} not found or measurement cannot be parsed'})
        channel_measurements[channel_number] = measurement
    ped_values = [channel_measurements[channel]['ped'] for channel in range(16)]
    ped_mean = _mean(ped_values)
    ped_std = _population_std(ped_values)
    ped_lower = ped_mean - ped_sigma * ped_std
    ped_upper = ped_mean + ped_sigma * ped_std
    posamp_values = [channel_measurements[channel]['posAmp'] for channel in range(16)]
    posamp_mean = _mean(posamp_values)
    posamp_std = _population_std(posamp_values)
    posamp_lower = posamp_mean - posamp_sigma * posamp_std
    posamp_upper = posamp_mean + posamp_sigma * posamp_std
    for channel_number in range(16):
        measurement = channel_measurements[channel_number]
        col_index = measurement['column']
        col = column_letter(col_index)
        ped = measurement['ped']
        rms = measurement['rms']
        posamp = measurement['posAmp']
        if not ped_lower <= ped <= ped_upper:
            return (False, {'fail_code': f'FAIL: row {row_number} CH{channel_number} ({col}) ped out of 4STD range ({ped_lower:.6g} ~ {ped_upper:.6g}): {ped}'})
        if not criteria['rms_range'][0] <= rms <= criteria['rms_range'][1]:
            return (False, {'fail_code': f'FAIL: row {row_number} CH{channel_number} ({col}) rms out of range: {rms}'})
        if not posamp_lower <= posamp <= posamp_upper:
            return (False, {'fail_code': f'FAIL: row {row_number} CH{channel_number} ({col}) posAmp out of 4STD range ({posamp_lower:.6g} ~ {posamp_upper:.6g}): {posamp}'})
    return (True, {'fail_code': '', 'Ped_Mean_16CH': ped_mean, 'Ped_STD_16CH': ped_std, 'Ped_Lower_4STD': ped_lower, 'Ped_Upper_4STD': ped_upper, 'PosAmp_Mean_16CH': posamp_mean, 'PosAmp_STD_16CH': posamp_std, 'PosAmp_Lower_4STD': posamp_lower, 'PosAmp_Upper_4STD': posamp_upper, 'Vdda_P': supplies['Vdda_P'][0], 'Vdda_P_Column': column_letter(supplies['Vdda_P'][1]), 'Vddo_P': supplies['Vddo_P'][0], 'Vddo_P_Column': column_letter(supplies['Vddo_P'][1]), 'Vddp_P': supplies['Vddp_P'][0], 'Vddp_P_Column': column_letter(supplies['Vddp_P'][1])})

def _mean(values):
    if not values:
        raise ValueError('Cannot calculate mean of an empty list.')
    return sum(values) / len(values)

def _population_std(values):
    """
    Calculate population standard deviation.
    """
    if not values:
        raise ValueError('Cannot calculate STD of an empty list.')
    mean = _mean(values)
    variance = sum(((value - mean) ** 2 for value in values)) / len(values)
    return math.sqrt(variance)
