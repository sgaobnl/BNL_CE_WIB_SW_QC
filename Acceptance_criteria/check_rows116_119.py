import math
import re

# ==========================================================
# Combined checks for Rows 116 and 119
# ==========================================================

#ROW_NUMBER = 116

CHANNELS = tuple(range(16))

WORST_INL_MAX = 1.01

LIN_RANGE_CHARGE_MIN_116 = 78.0
LIN_RANGE_CHARGE_MIN_119 = 178.0

NUMBER = '[-+]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][-+]?\\d+)?'

def _find_channel_data(row, channel):
    """
    Search the complete row for one CHx record.

    The parser is intentionally format-flexible because Row 116
    is different from the CHx=(pedestal=...;rms=...) format used
    in earlier checks.
    """
    channel_pattern = re.compile(f'\\bCH{channel}\\b', re.IGNORECASE)
    gain_pattern = re.compile(f'\\bgain\\b\\s*(?:=|:)?\\s*({NUMBER})', re.IGNORECASE)
    worst_inl_pattern = re.compile(f'\\bworst(?:INL|_INL)\\b\\s*(?:=|:)?\\s*({NUMBER})', re.IGNORECASE)
    lin_charge_pattern = re.compile(f'\\bl[inrR]*ange(?:[_ ]?charge)?\\b\\s*(?:=|:)?\\s*({NUMBER})', re.IGNORECASE)
    for cell in row:
        text = str(cell).strip()
        if not channel_pattern.search(text):
            continue
        gain_match = gain_pattern.search(text)
        worst_match = worst_inl_pattern.search(text)
        charge_match = lin_charge_pattern.search(text)
        if gain_match is not None and worst_match is not None and (charge_match is not None):
            return {'gain': float(gain_match.group(1)), 'worstINL': float(worst_match.group(1)), 'linRageCharge': float(charge_match.group(1))}
        try:
            center = row.index(cell)
        except ValueError:
            center = 0
        neighborhood = ' '.join((str(v) for v in row[max(0, center - 2):min(len(row), center + 5)]))
        gain_match = gain_pattern.search(neighborhood)
        worst_match = worst_inl_pattern.search(neighborhood)
        charge_match = lin_charge_pattern.search(neighborhood)
        if gain_match is not None and worst_match is not None and (charge_match is not None):
            return {'gain': float(gain_match.group(1)), 'worstINL': float(worst_match.group(1)), 'linRageCharge': float(charge_match.group(1))}
    return None

def _mean(values):
    if not values:
        raise ValueError('Cannot calculate mean of an empty list.')
    return sum(values) / len(values)

def _population_std(values):
    if not values:
        raise ValueError('Cannot calculate population STD of an empty list.')
    mean = _mean(values)
    variance = sum(((value - mean) ** 2 for value in values)) / len(values)
    return math.sqrt(variance)

def check_row116(rows, file_type):
    ROW_NUMBER=116
    if file_type not in ('RT', 'LN'):
        return (False, {'fail_code': f'FAIL: unsupported file type: {file_type}'})
    row_index = ROW_NUMBER - 1
    if len(rows) <= row_index:
        return (False, {'fail_code': 'FAIL: row 116 is missing'})
    row = rows[row_index]
    channel_data = {}
    failures = []
    for channel in CHANNELS:
        parsed = _find_channel_data(row, channel)
        if parsed is None:
            failures.append(f'FAIL: row 116 CH{channel} gain/worstINL/linRageCharge could not be parsed')
        else:
            channel_data[channel] = parsed
    if len(channel_data) != 16:
        return (False, {'fail_code': ' | '.join(failures)})
    for channel in CHANNELS:
        data = channel_data[channel]
        worst_inl = data['worstINL']
        lin_range_charge = data['linRageCharge']
        if not worst_inl < WORST_INL_MAX:
            failures.append(f'FAIL: row 116 CH{channel} worstINL={worst_inl} must be < {WORST_INL_MAX}')
        if not lin_range_charge > LIN_RANGE_CHARGE_MIN_116:
            failures.append(f'FAIL: row 116 CH{channel} linRageCharge={lin_range_charge} must be > {LIN_RANGE_CHARGE_MIN_116}')
    all_gains = [channel_data[ch]['gain'] for ch in CHANNELS]
    if file_type == 'RT':
        gain_channels = [ch for ch in CHANNELS if ch not in (0, 8)]
    else:
        gain_channels = list(CHANNELS)
    gain_values = [channel_data[ch]['gain'] for ch in gain_channels]
    gain_mean = _mean(gain_values)
    gain_std = _population_std(gain_values)
    gain_lower = gain_mean - 4.0 * gain_std
    gain_upper = gain_mean + 4.0 * gain_std
    for channel in gain_channels:
        gain = channel_data[channel]['gain']
        if not gain_lower <= gain <= gain_upper:
            failures.append(f'FAIL: row 116 CH{channel} gain={gain} outside gain mean +/- 4STD ({gain_lower:.6g} ~ {gain_upper:.6g})')
    if file_type == 'RT':
        ch0_gain = channel_data[0]['gain']
        ch8_gain = channel_data[8]['gain']
        rt_high_limit = gain_mean + 2.0
        if not ch0_gain < rt_high_limit:
            failures.append(f'FAIL: row 116 CH0 gain={ch0_gain} must be < gain mean + 2 ({rt_high_limit:.6g})')
        if not ch8_gain < rt_high_limit:
            failures.append(f'FAIL: row 116 CH8 gain={ch8_gain} must be < gain mean + 2 ({rt_high_limit:.6g})')
    result = {'fail_code': '', 'file_type': file_type, 'Gain_Mean': gain_mean, 'Gain_STD': gain_std, 'Gain_Lower_4STD': gain_lower, 'Gain_Upper_4STD': gain_upper, 'RT_CH0_Gain_Limit_Mean_Plus_2': gain_mean + 2.0 if file_type == 'RT' else '', 'RT_CH0_Gain': channel_data[0]['gain'] if file_type == 'RT' else '', 'RT_CH8_Gain': channel_data[8]['gain'] if file_type == 'RT' else '', 'Gain_Channels_Used': ','.join((f'CH{ch}' for ch in gain_channels)), 'All_Gain_Mean_16CH': _mean(all_gains), 'All_Gain_STD_16CH': _population_std(all_gains)}
    for channel in CHANNELS:
        result[f'CH{channel}_Gain'] = channel_data[channel]['gain']
        result[f'CH{channel}_WorstINL'] = channel_data[channel]['worstINL']
        result[f'CH{channel}_linRageCharge'] = channel_data[channel]['linRageCharge']
    if failures:
        result['fail_code'] = ' | '.join(failures)
        return (False, result)
    return (True, result)

def check_row119(rows, file_type):
    ROW_NUMBER=119
    if file_type not in ('RT', 'LN'):
        return (False, {'fail_code': f'FAIL: unsupported file type: {file_type}'})
    row_index = ROW_NUMBER - 1
    if len(rows) <= row_index:
        return (False, {'fail_code': 'FAIL: row 119 is missing'})
    row = rows[row_index]
    channel_data = {}
    failures = []
    for channel in CHANNELS:
        parsed = _find_channel_data(row, channel)
        if parsed is None:
            failures.append(f'FAIL: row 119 CH{channel} gain/worstINL/linRageCharge could not be parsed')
        else:
            channel_data[channel] = parsed
    if len(channel_data) != 16:
        return (False, {'fail_code': ' | '.join(failures)})
    for channel in CHANNELS:
        worst_inl = channel_data[channel]['worstINL']
        lin_range_charge = channel_data[channel]['linRageCharge']
        if not worst_inl < WORST_INL_MAX:
            failures.append(f'FAIL: row 119 CH{channel} worstINL={worst_inl} must be < {WORST_INL_MAX}')
        if not lin_range_charge > LIN_RANGE_CHARGE_MIN_119:
            failures.append(f'FAIL: row 119 CH{channel} linRageCharge={lin_range_charge} must be > {LIN_RANGE_CHARGE_MIN_119}')
    all_gain_values = [channel_data[channel]['gain'] for channel in CHANNELS]
    if file_type == 'RT':
        gain_channels = [channel for channel in CHANNELS if channel not in (0, 8)]
    else:
        gain_channels = list(CHANNELS)
    gain_values = [channel_data[channel]['gain'] for channel in gain_channels]
    gain_mean = _mean(gain_values)
    gain_std = _population_std(gain_values)
    gain_lower = gain_mean - 4.0 * gain_std
    gain_upper = gain_mean + 4.0 * gain_std
    for channel in gain_channels:
        gain = channel_data[channel]['gain']
        if not gain_lower <= gain <= gain_upper:
            failures.append(f'FAIL: row 119 CH{channel} gain={gain} outside gain mean +/- 4STD ({gain_lower:.6g} ~ {gain_upper:.6g})')
    rt_special_limit = gain_mean + 5.0
    if file_type == 'RT':
        ch0_gain = channel_data[0]['gain']
        ch8_gain = channel_data[8]['gain']
        if not ch0_gain < rt_special_limit:
            failures.append(f'FAIL: row 119 CH0 gain={ch0_gain} must be < RT gain mean + 2 ({rt_special_limit:.6g})')
        if not ch8_gain < rt_special_limit:
            failures.append(f'FAIL: row 119 CH8 gain={ch8_gain} must be < RT gain mean + 2 ({rt_special_limit:.6g})')
    result = {'fail_code': '', 'file_type': file_type, 'Gain_Mean': gain_mean, 'Gain_STD': gain_std, 'Gain_Lower_4STD': gain_lower, 'Gain_Upper_4STD': gain_upper, 'Gain_Channels_Used': ','.join((f'CH{channel}' for channel in gain_channels)), 'All_Gain_Mean_16CH': _mean(all_gain_values), 'All_Gain_STD_16CH': _population_std(all_gain_values), 'RT_CH0_CH8_Gain_Limit_Mean_Plus_2': rt_special_limit if file_type == 'RT' else ''}
    for channel in CHANNELS:
        result[f'CH{channel}_Gain'] = channel_data[channel]['gain']
        result[f'CH{channel}_WorstINL'] = channel_data[channel]['worstINL']
        result[f'CH{channel}_linRageCharge'] = channel_data[channel]['linRageCharge']
    if failures:
        result['fail_code'] = ' | '.join(failures)
        return (False, result)
    return (True, result)

CHECK_FUNCTIONS = {
    "check_row116": check_row116,
    "check_row119": check_row119,
}
