import math
import re
RMS_ORDER_GAP_A = 2
RMS_ORDER_GAP_B = 2
RMS_ORDER_GAP_C = 2
RT_73_76_CRITERIA = {'pedestal_range': (8000, 10000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (8, 25), 'rms_mean_range': (8, 16)}
LN_73_76_CRITERIA = {'pedestal_range': (8000, 10000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (4, 10), 'rms_mean_range': (4, 10), 'ln_range_min_count': 1, 'ln_band_min_count': 1}
RT_77_80_CRITERIA = {'pedestal_range': (8000, 10000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (5, 12), 'rms_mean_range': (5, 9)}
LN_77_80_CRITERIA = {'pedestal_range': (8000, 10000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (2, 6), 'rms_mean_range': (2.5, 6), 'ln_range_min_count': 1, 'ln_band_min_count': 1}
RT_81_84_CRITERIA = {'pedestal_range': (8000, 10000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (15, 35), 'rms_mean_range': (15, 35)}
LN_81_84_CRITERIA = {'pedestal_range': (8000, 13000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (7, 16), 'rms_mean_range': (7, 16), 'ln_range_min_count': 1, 'ln_band_min_count': 1}
RT_85_88_CRITERIA = {'pedestal_range': (8000, 10000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (3, 10), 'rms_mean_range': (3, 10)}
LN_85_88_CRITERIA = {'pedestal_range': (8000, 10000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (1, 5), 'rms_mean_range': (2, 5), 'ln_range_min_count': 1, 'ln_band_min_count': 1}
RT_89_92_CRITERIA = {'pedestal_range': (500, 2000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (8, 25), 'rms_mean_range': (8, 16)}
LN_89_92_CRITERIA = {'pedestal_range': (200, 3500), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (4, 10), 'rms_mean_range': (4, 10), 'ln_range_min_count': 1, 'ln_band_min_count': 1}
RT_93_96_CRITERIA = {'pedestal_range': (400, 2000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (5, 12), 'rms_mean_range': (5, 9)}
LN_93_96_CRITERIA = {'pedestal_range': (200, 3500), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (2, 6), 'rms_mean_range': (3, 6), 'ln_range_min_count': 1, 'ln_band_min_count': 1}
RT_97_100_CRITERIA = {'pedestal_range': (500, 3000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (15, 35), 'rms_mean_range': (15, 35)}
LN_97_100_CRITERIA = {'pedestal_range': (200, 3500), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (7, 16), 'rms_mean_range': (7, 16), 'ln_range_min_count': 1, 'ln_band_min_count': 1}
RT_101_104_CRITERIA = {'pedestal_range': (400, 2000), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (3, 10), 'rms_mean_range': (3, 10)}
LN_101_104_CRITERIA = {'pedestal_range': (200, 3500), 'ped_sigma': 4.0, 'rms_sigma': 5.0, 'rms_channel_range': (1, 5), 'rms_mean_range': (2, 5), 'ln_range_min_count': 1, 'ln_band_min_count': 1}

def _parse_channel_cell(cell, expected_channel):
    text = str(cell).strip()
    if re.search(f'\\bCH{expected_channel}\\b', text, re.IGNORECASE) is None:
        return None
    number = '[-+]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)'
    pedestal_match = re.search(f'\\b(?:pedestal|ped)\\b\\s*=\\s*(?P<value>{number})', text, re.IGNORECASE)
    rms_match = re.search(f'\\brms\\b\\s*=\\s*(?P<value>{number})', text, re.IGNORECASE)
    if pedestal_match is None or rms_match is None:
        return None
    return {'pedestal': float(pedestal_match.group('value')), 'rms': float(rms_match.group('value'))}

def _collect_row(rows, row_number):
    row_index = row_number - 1
    if len(rows) <= row_index:
        return (False, {'fail_code': f'FAIL: row {row_number} is missing'})
    row = rows[row_index]
    measurements = {}
    for channel in range(16):
        found = None
        for column_index in range(2, min(18, len(row))):
            parsed = _parse_channel_cell(row[column_index], channel)
            if parsed is not None:
                parsed['column'] = column_index
                found = parsed
                break
        if found is None:
            return (False, {'fail_code': f'FAIL: row {row_number} CH{channel} not found or pedestal/rms could not be parsed in Columns C:R'})
        measurements[channel] = found
    return (True, {'channel_measurements': measurements})

def _mean(values):
    return sum(values) / len(values)

def _population_std(values):
    mean = _mean(values)
    return math.sqrt(sum(((value - mean) ** 2 for value in values)) / len(values))

def _check_group(rows, file_type, start_row, rt_criteria, ln_criteria, order_rows):
    if file_type == 'RT':
        criteria = rt_criteria
    elif file_type == 'LN':
        criteria = ln_criteria
    else:
        return (False, {'fail_code': f'FAIL: unsupported file type: {file_type}'})
    row0, row1, row2, row3 = order_rows
    failures = []
    parsed = {}
    row_data = {}
    for row_number in range(start_row, start_row + 4):
        passed, result = _collect_row(rows, row_number)
        if not passed:
            failures.append(result['fail_code'])
        else:
            row_data[row_number] = result['channel_measurements']
    if len(row_data) != 4:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    ped_low_limit, ped_high_limit = criteria['pedestal_range']
    for row_number in range(start_row, start_row + 4):
        data = row_data[row_number]
        pedestal_values = [data[ch]['pedestal'] for ch in range(16)]
        pedestal_mean = _mean(pedestal_values)
        pedestal_std = _population_std(pedestal_values)
        pedestal_low = pedestal_mean - criteria['ped_sigma'] * pedestal_std
        pedestal_high = pedestal_mean + criteria['ped_sigma'] * pedestal_std
        parsed[f'Row{row_number}_Pedestal_Mean_16CH'] = pedestal_mean
        parsed[f'Row{row_number}_Pedestal_STD_16CH'] = pedestal_std
        parsed[f'Row{row_number}_Pedestal_Lower_4STD'] = pedestal_low
        parsed[f'Row{row_number}_Pedestal_Upper_4STD'] = pedestal_high
        for ch in range(16):
            pedestal = data[ch]['pedestal']
            if not pedestal_low <= pedestal <= pedestal_high:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside mean +/- 4STD ({pedestal_low:.6g} ~ {pedestal_high:.6g})')
            if not ped_low_limit <= pedestal <= ped_high_limit:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside pedestal range ({ped_low_limit} ~ {ped_high_limit})')
    row_rms_means = {}
    row_rms_bands = {}
    for row_number in range(start_row, start_row + 4):
        data = row_data[row_number]
        rms_values = [data[ch]['rms'] for ch in range(16)]
        if file_type == 'LN':
            used_values = sorted(rms_values)[2:-2]
        else:
            used_values = rms_values
        rms_mean = _mean(used_values)
        rms_std = _population_std(used_values)
        rms_low = rms_mean - criteria['rms_sigma'] * rms_std
        rms_high = rms_mean + criteria['rms_sigma'] * rms_std
        row_rms_means[row_number] = rms_mean
        row_rms_bands[row_number] = (rms_low, rms_high)
        parsed[f'Row{row_number}_RMS_Mean'] = rms_mean
        parsed[f'Row{row_number}_RMS_STD'] = rms_std
        parsed[f'Row{row_number}_RMS_Lower_5STD'] = rms_low
        parsed[f'Row{row_number}_RMS_Upper_5STD'] = rms_high
        if file_type == 'RT':
            ch_low, ch_high = criteria['rms_channel_range']
            for ch in range(16):
                rms = data[ch]['rms']
                if not ch_low <= rms <= ch_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside range ({ch_low} ~ {ch_high})')
                if not rms_low <= rms <= rms_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside mean +/- 5STD ({rms_low:.6g} ~ {rms_high:.6g})')
    if file_type == 'RT':
        mean_low, mean_high = criteria['rms_mean_range']
        for row_number in range(start_row, start_row + 4):
            rms_mean = row_rms_means[row_number]
            if not mean_low <= rms_mean <= mean_high:
                failures.append(f'FAIL: row {row_number} RT RMS mean={rms_mean:.6g} outside range ({mean_low} ~ {mean_high})')
    if file_type == 'LN':
        ch_low, ch_high = criteria['rms_channel_range']
        for ch in range(16):
            in_range_count = 0
            in_band_count = 0
            values = []
            for row_number in range(start_row, start_row + 4):
                rms = row_data[row_number][ch]['rms']
                values.append(rms)
                if ch_low <= rms <= ch_high:
                    in_range_count += 1
                band_low, band_high = row_rms_bands[row_number]
                if band_low <= rms <= band_high:
                    in_band_count += 1
            if False: #ignore by Shanshan
                if in_range_count < 1:
                    failures.append(f'FAIL:Row{row_number-4}  Row{row_number-4} CH{ch} has only {in_range_count} of 4 RMS values inside allowed range {ch_low}~{ch_high}; at least 1 in-range values are required; values={values}')
                if in_band_count < 1:
                    failures.append(f'FAIL:Row{row_number-4}  Row{row_number-4} CH{ch} has only {in_band_count} of 4 RMS values within corresponding row mean +/- 5STD; at least 1 required; values={values}')
        mean_low, mean_high = criteria['rms_mean_range']
        ln_mean_pass_count = sum((1 for row_number in range(start_row, start_row + 4) if mean_low <= row_rms_means[row_number] <= mean_high))
        if ln_mean_pass_count < 1:
            mean_values = [row_rms_means[row_number] for row_number in range(start_row, start_row + 4)]
            failures.append(f'FAIL: only {ln_mean_pass_count} of 4 LN RMS means are within ({mean_low} ~ {mean_high}); at least 1 required; values={mean_values}')
    condition_a = row_rms_means[row2] - RMS_ORDER_GAP_A < row_rms_means[row0]
    condition_b = row_rms_means[row0] - RMS_ORDER_GAP_B < row_rms_means[row3]
    condition_c = row_rms_means[row3] - RMS_ORDER_GAP_C < row_rms_means[row1]
    if file_type == 'LN': #ingore by shanshan
        pass
    else:
        if not (condition_a and condition_b and condition_c):
            failures.append(f'FAIL: RMS mean ordering Row{row2}-A={row_rms_means[row2] - RMS_ORDER_GAP_A:.6g} < Row{row0}={row_rms_means[row0]:.6g}; Row{row0}-B={row_rms_means[row0] - RMS_ORDER_GAP_B:.6g} < Row{row3}={row_rms_means[row3]:.6g}; Row{row3}-C={row_rms_means[row3] - RMS_ORDER_GAP_C:.6g} < Row{row1}={row_rms_means[row1]:.6g}')
        parsed['RMS_Mean_Ordering'] = f'Row{row2}-A={row_rms_means[row2] - RMS_ORDER_GAP_A:.6g} < Row{row0}={row_rms_means[row0]:.6g}; Row{row0}-B={row_rms_means[row0] - RMS_ORDER_GAP_B:.6g} < Row{row3}={row_rms_means[row3]:.6g}; Row{row3}-C={row_rms_means[row3] - RMS_ORDER_GAP_C:.6g} < Row{row1}={row_rms_means[row1]:.6g}'
    if failures:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    return (True, {'fail_code': '', **parsed})

def check_rows73_76(rows, file_type):
    if file_type == 'RT':
        criteria = RT_73_76_CRITERIA
    elif file_type == 'LN':
        criteria = LN_73_76_CRITERIA
    else:
        return (False, {'fail_code': f'FAIL: unsupported file type: {file_type}'})
    failures = []
    parsed = {}
    row_data = {}
    for row_number in range(73, 77):
        passed, result = _collect_row(rows, row_number)
        if not passed:
            failures.append(result['fail_code'])
        else:
            row_data[row_number] = result['channel_measurements']
    if len(row_data) != 4:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    for row_number in range(73, 77):
        data = row_data[row_number]
        pedestal_values = [data[ch]['pedestal'] for ch in range(16)]
        pedestal_mean = _mean(pedestal_values)
        pedestal_std = _population_std(pedestal_values)
        pedestal_low = pedestal_mean - criteria['ped_sigma'] * pedestal_std
        pedestal_high = pedestal_mean + criteria['ped_sigma'] * pedestal_std
        parsed[f'Row{row_number}_Pedestal_Mean_16CH'] = pedestal_mean
        parsed[f'Row{row_number}_Pedestal_STD_16CH'] = pedestal_std
        parsed[f'Row{row_number}_Pedestal_Lower_4STD'] = pedestal_low
        parsed[f'Row{row_number}_Pedestal_Upper_4STD'] = pedestal_high
        for ch in range(16):
            pedestal = data[ch]['pedestal']
            if not pedestal_low <= pedestal <= pedestal_high:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside mean +/- 4STD ({pedestal_low:.6g} ~ {pedestal_high:.6g})')
            ped_min, ped_max = criteria['pedestal_range']
            if not ped_min <= pedestal <= ped_max:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside pedestal range ({ped_min} ~ {ped_max})')
    row_rms_means = {}
    row_rms_bands = {}
    for row_number in range(73, 77):
        data = row_data[row_number]
        rms_values = [data[ch]['rms'] for ch in range(16)]
        if file_type == 'LN':
            used_values = sorted(rms_values)[2:-2]
        else:
            used_values = rms_values
        rms_mean = _mean(used_values)
        rms_std = _population_std(used_values)
        rms_low = rms_mean - criteria['rms_sigma'] * rms_std
        rms_high = rms_mean + criteria['rms_sigma'] * rms_std
        row_rms_means[row_number] = rms_mean
        row_rms_bands[row_number] = (rms_low, rms_high)
        parsed[f'Row{row_number}_RMS_Mean'] = rms_mean
        parsed[f'Row{row_number}_RMS_STD'] = rms_std
        parsed[f'Row{row_number}_RMS_Lower_5STD'] = rms_low
        parsed[f'Row{row_number}_RMS_Upper_5STD'] = rms_high
        if file_type == 'RT':
            ch_low, ch_high = criteria['rms_channel_range']
            for ch in range(16):
                rms = data[ch]['rms']
                if not ch_low <= rms <= ch_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside range ({ch_low} ~ {ch_high})')
                if not rms_low <= rms <= rms_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside mean +/- 5STD ({rms_low:.6g} ~ {rms_high:.6g})')
        if file_type == 'RT':
            mean_low, mean_high = criteria['rms_mean_range']
            if not mean_low <= rms_mean <= mean_high:
                failures.append(f'FAIL: row {row_number} RT RMS mean={rms_mean:.6g} outside range ({mean_low} ~ {mean_high})')
    if file_type == 'LN':
        ch_low, ch_high = criteria['rms_channel_range']
        for ch in range(16):
            in_range_count = 0
            in_band_count = 0
            values = []
            for row_number in range(73, 77):
                rms = row_data[row_number][ch]['rms']
                values.append(rms)
                if ch_low <= rms <= ch_high:
                    in_range_count += 1
                band_low, band_high = row_rms_bands[row_number]
                if band_low <= rms <= band_high:
                    in_band_count += 1
            if False: #ignore by Shanshan
                if in_range_count < 1:
                    failures.append(f'FAIL:Row{row_number-4}  CH{ch} has only {in_range_count} of 4 RMS values inside allowed range {ch_low}~{ch_high}; at least 1 in-range values are required; values={values}')
                if in_band_count < criteria['ln_band_min_count']:
                    failures.append(f'FAIL:Row{row_number-4}  CH{ch} has only {in_band_count} of 4 RMS values within corresponding row mean +/- 5STD; at least 1 required; values={values}')
    if file_type == 'LN':
        mean_low, mean_high = criteria['rms_mean_range']
        ln_mean_pass_count = sum((1 for row_number in range(73, 77) if mean_low <= row_rms_means[row_number] <= mean_high))
        if ln_mean_pass_count < 1:
            mean_values = [row_rms_means[row_number] for row_number in range(73, 77)]
            failures.append(f'FAIL: only {ln_mean_pass_count} of 4 LN RMS means are within ({mean_low} ~ {mean_high}); at least 1 required; values={mean_values}')
    condition_a = row_rms_means[75] - RMS_ORDER_GAP_A < row_rms_means[73]
    condition_b = row_rms_means[73] - RMS_ORDER_GAP_B < row_rms_means[76]
    condition_c = row_rms_means[76] - RMS_ORDER_GAP_C < row_rms_means[74]
    if file_type == 'LN': #ingore by shanshan
        pass
    else:

        if not (condition_a and condition_b and condition_c):
            failures.append(f'FAIL: RMS mean ordering Row75-A={row_rms_means[75] - RMS_ORDER_GAP_A:.6g} < Row73={row_rms_means[73]:.6g}; Row73-B={row_rms_means[73] - RMS_ORDER_GAP_B:.6g} < Row76={row_rms_means[76]:.6g}; Row76-C={row_rms_means[76] - RMS_ORDER_GAP_C:.6g} < Row74={row_rms_means[74]:.6g}')
        parsed['RMS_Mean_Ordering'] = f'Row75-A={row_rms_means[75] - RMS_ORDER_GAP_A:.6g} < Row73={row_rms_means[73]:.6g}; Row73-B={row_rms_means[73] - RMS_ORDER_GAP_B:.6g} < Row76={row_rms_means[76]:.6g}; Row76-C={row_rms_means[76] - RMS_ORDER_GAP_C:.6g} < Row74={row_rms_means[74]:.6g}'
    if failures:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    return (True, {'fail_code': '', **parsed})

def check_rows77_80(rows, file_type):
    if file_type == 'RT':
        criteria = RT_77_80_CRITERIA
    elif file_type == 'LN':
        criteria = LN_77_80_CRITERIA
    else:
        return (False, {'fail_code': f'FAIL: unsupported file type: {file_type}'})
    failures = []
    parsed = {}
    row_data = {}
    for row_number in range(77, 81):
        passed, result = _collect_row(rows, row_number)
        if not passed:
            failures.append(result['fail_code'])
        else:
            row_data[row_number] = result['channel_measurements']
    if len(row_data) != 4:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    for row_number in range(77, 81):
        data = row_data[row_number]
        pedestal_values = [data[ch]['pedestal'] for ch in range(16)]
        pedestal_mean = _mean(pedestal_values)
        pedestal_std = _population_std(pedestal_values)
        pedestal_low = pedestal_mean - criteria['ped_sigma'] * pedestal_std
        pedestal_high = pedestal_mean + criteria['ped_sigma'] * pedestal_std
        parsed[f'Row{row_number}_Pedestal_Mean_16CH'] = pedestal_mean
        parsed[f'Row{row_number}_Pedestal_STD_16CH'] = pedestal_std
        parsed[f'Row{row_number}_Pedestal_Lower_4STD'] = pedestal_low
        parsed[f'Row{row_number}_Pedestal_Upper_4STD'] = pedestal_high
        for ch in range(16):
            pedestal = data[ch]['pedestal']
            if not pedestal_low <= pedestal <= pedestal_high:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside mean +/- 4STD ({pedestal_low:.6g} ~ {pedestal_high:.6g})')
            ped_min, ped_max = criteria['pedestal_range']
            if not ped_min <= pedestal <= ped_max:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside pedestal range ({ped_min} ~ {ped_max})')
    row_rms_means = {}
    row_rms_bands = {}
    for row_number in range(77, 81):
        data = row_data[row_number]
        rms_values = [data[ch]['rms'] for ch in range(16)]
        if file_type == 'LN':
            used_values = sorted(rms_values)[2:-2]
        else:
            used_values = rms_values
        rms_mean = _mean(used_values)
        rms_std = _population_std(used_values)
        rms_low = rms_mean - criteria['rms_sigma'] * rms_std
        rms_high = rms_mean + criteria['rms_sigma'] * rms_std
        row_rms_means[row_number] = rms_mean
        row_rms_bands[row_number] = (rms_low, rms_high)
        parsed[f'Row{row_number}_RMS_Mean'] = rms_mean
        parsed[f'Row{row_number}_RMS_STD'] = rms_std
        parsed[f'Row{row_number}_RMS_Lower_5STD'] = rms_low
        parsed[f'Row{row_number}_RMS_Upper_5STD'] = rms_high
        if file_type == 'RT':
            ch_low, ch_high = criteria['rms_channel_range']
            for ch in range(16):
                rms = data[ch]['rms']
                if not ch_low <= rms <= ch_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside range ({ch_low} ~ {ch_high})')
                if not rms_low <= rms <= rms_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside mean +/- 5STD ({rms_low:.6g} ~ {rms_high:.6g})')
        if file_type == 'RT':
            mean_low, mean_high = criteria['rms_mean_range']
            if not mean_low <= rms_mean <= mean_high:
                failures.append(f'FAIL: row {row_number} RT RMS mean={rms_mean:.6g} outside range ({mean_low} ~ {mean_high})')
    if file_type == 'LN':
        ch_low, ch_high = criteria['rms_channel_range']
        for ch in range(16):
            in_range_count = 0
            in_band_count = 0
            values = []
            for row_number in range(77, 81):
                rms = row_data[row_number][ch]['rms']
                values.append(rms)
                if ch_low <= rms <= ch_high:
                    in_range_count += 1
                band_low, band_high = row_rms_bands[row_number]
                if band_low <= rms <= band_high:
                    in_band_count += 1
            if False: #ignore by Shanshan
                if in_range_count < 1:
                    failures.append(f'FAIL:Row{row_number-4}  CH{ch} has only {in_range_count} of 4 RMS values inside allowed range {ch_low}~{ch_high}; at least 1 in-range values are required; values={values}')
                if in_band_count < criteria['ln_band_min_count']:
                    failures.append(f'FAIL:Row{row_number-4}  CH{ch} has only {in_band_count} of 4 RMS values within corresponding row mean +/- 5STD; at least 1 required; values={values}')
    if file_type == 'LN':
        mean_low, mean_high = criteria['rms_mean_range']
        ln_mean_pass_count = sum((1 for row_number in range(77, 81) if mean_low <= row_rms_means[row_number] <= mean_high))
        if ln_mean_pass_count < 1:
            mean_values = [row_rms_means[row_number] for row_number in range(77, 81)]
            failures.append(f'FAIL: only {ln_mean_pass_count} of 4 LN RMS means are within ({mean_low} ~ {mean_high}); at least 1 required; values={mean_values}')
    condition_a = row_rms_means[79] - RMS_ORDER_GAP_A < row_rms_means[77]
    condition_b = row_rms_means[77] - RMS_ORDER_GAP_B < row_rms_means[80]
    condition_c = row_rms_means[80] - RMS_ORDER_GAP_C < row_rms_means[78]
    if file_type == 'LN': #ingore by shanshan
        pass
    else:
        if not (condition_a and condition_b and condition_c):
            failures.append(f'FAIL: RMS mean ordering Row79-A={row_rms_means[79] - RMS_ORDER_GAP_A:.6g} < Row77={row_rms_means[77]:.6g}; Row77-B={row_rms_means[77] - RMS_ORDER_GAP_B:.6g} < Row80={row_rms_means[80]:.6g}; Row80-C={row_rms_means[80] - RMS_ORDER_GAP_C:.6g} < Row78={row_rms_means[78]:.6g}')
        parsed['RMS_Mean_Ordering'] = f'Row79-A={row_rms_means[79] - RMS_ORDER_GAP_A:.6g} < Row77={row_rms_means[77]:.6g}; Row77-B={row_rms_means[77] - RMS_ORDER_GAP_B:.6g} < Row80={row_rms_means[80]:.6g}; Row80-C={row_rms_means[80] - RMS_ORDER_GAP_C:.6g} < Row78={row_rms_means[78]:.6g}'
    if failures:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    return (True, {'fail_code': '', **parsed})

def check_rows81_84(rows, file_type):
    if file_type == 'RT':
        criteria = RT_81_84_CRITERIA
    elif file_type == 'LN':
        criteria = LN_81_84_CRITERIA
    else:
        return (False, {'fail_code': f'FAIL: unsupported file type: {file_type}'})
    failures = []
    parsed = {}
    row_data = {}
    for row_number in range(81, 85):
        passed, result = _collect_row(rows, row_number)
        if not passed:
            failures.append(result['fail_code'])
        else:
            row_data[row_number] = result['channel_measurements']
    if len(row_data) != 4:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    for row_number in range(81, 85):
        data = row_data[row_number]
        pedestal_values = [data[ch]['pedestal'] for ch in range(16)]
        pedestal_mean = _mean(pedestal_values)
        pedestal_std = _population_std(pedestal_values)
        pedestal_low = pedestal_mean - criteria['ped_sigma'] * pedestal_std
        pedestal_high = pedestal_mean + criteria['ped_sigma'] * pedestal_std
        parsed[f'Row{row_number}_Pedestal_Mean_16CH'] = pedestal_mean
        parsed[f'Row{row_number}_Pedestal_STD_16CH'] = pedestal_std
        parsed[f'Row{row_number}_Pedestal_Lower_4STD'] = pedestal_low
        parsed[f'Row{row_number}_Pedestal_Upper_4STD'] = pedestal_high
        for ch in range(16):
            pedestal = data[ch]['pedestal']
            if not pedestal_low <= pedestal <= pedestal_high:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside mean +/- 4STD ({pedestal_low:.6g} ~ {pedestal_high:.6g})')
            ped_min, ped_max = criteria['pedestal_range']
            if not ped_min <= pedestal <= ped_max:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside pedestal range ({ped_min} ~ {ped_max})')
    row_rms_means = {}
    row_rms_bands = {}
    for row_number in range(81, 85):
        data = row_data[row_number]
        rms_values = [data[ch]['rms'] for ch in range(16)]
        if file_type == 'LN':
            used_values = sorted(rms_values)[2:-2]
        else:
            used_values = rms_values
        rms_mean = _mean(used_values)
        rms_std = _population_std(used_values)
        rms_low = rms_mean - criteria['rms_sigma'] * rms_std
        rms_high = rms_mean + criteria['rms_sigma'] * rms_std
        row_rms_means[row_number] = rms_mean
        row_rms_bands[row_number] = (rms_low, rms_high)
        parsed[f'Row{row_number}_RMS_Mean'] = rms_mean
        parsed[f'Row{row_number}_RMS_STD'] = rms_std
        parsed[f'Row{row_number}_RMS_Lower_5STD'] = rms_low
        parsed[f'Row{row_number}_RMS_Upper_5STD'] = rms_high
        if file_type == 'RT':
            ch_low, ch_high = criteria['rms_channel_range']
            for ch in range(16):
                rms = data[ch]['rms']
                if not ch_low <= rms <= ch_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside range ({ch_low} ~ {ch_high})')
                if not rms_low <= rms <= rms_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside mean +/- 5STD ({rms_low:.6g} ~ {rms_high:.6g})')
        if file_type == 'RT':
            mean_low, mean_high = criteria['rms_mean_range']
            if not mean_low <= rms_mean <= mean_high:
                failures.append(f'FAIL: row {row_number} RT RMS mean={rms_mean:.6g} outside range ({mean_low} ~ {mean_high})')
    if file_type == 'LN':
        ch_low, ch_high = criteria['rms_channel_range']
        for ch in range(16):
            in_range_count = 0
            in_band_count = 0
            values = []
            for row_number in range(81, 85):
                rms = row_data[row_number][ch]['rms']
                values.append(rms)
                if ch_low <= rms <= ch_high:
                    in_range_count += 1
                band_low, band_high = row_rms_bands[row_number]
                if band_low <= rms <= band_high:
                    in_band_count += 1
            if False: #ignore by Shanshan
                if in_range_count < 1:
                    failures.append(f'FAIL:Row{row_number-4}  CH{ch} has only {in_range_count} of 4 RMS values inside allowed range {ch_low}~{ch_high}; at least 1 in-range values are required; values={values}')
                if in_band_count < criteria['ln_band_min_count']:
                    failures.append(f'FAIL:Row{row_number-4}  CH{ch} has only {in_band_count} of 4 RMS values within corresponding row mean +/- 5STD; at least 1 required; values={values}')
    if file_type == 'LN':
        mean_low, mean_high = criteria['rms_mean_range']
        ln_mean_pass_count = sum((1 for row_number in range(81, 85) if mean_low <= row_rms_means[row_number] <= mean_high))
        if ln_mean_pass_count < 1:
            mean_values = [row_rms_means[row_number] for row_number in range(81, 85)]
            failures.append(f'FAIL: only {ln_mean_pass_count} of 4 LN RMS means are within ({mean_low} ~ {mean_high}); at least 1 required; values={mean_values}')
    condition_a = row_rms_means[83] - RMS_ORDER_GAP_A < row_rms_means[81]
    condition_b = row_rms_means[81] - RMS_ORDER_GAP_B < row_rms_means[84]
    condition_c = row_rms_means[84] - RMS_ORDER_GAP_C < row_rms_means[82]

    if file_type == 'LN': #ingore by shanshan
        pass
    else:
        if not (condition_a and condition_b and condition_c):
            failures.append(f'FAIL: RMS mean ordering Row83-A={row_rms_means[83] - RMS_ORDER_GAP_A:.6g} < Row81={row_rms_means[81]:.6g}; Row81-B={row_rms_means[81] - RMS_ORDER_GAP_B:.6g} < Row84={row_rms_means[84]:.6g}; Row84-C={row_rms_means[84] - RMS_ORDER_GAP_C:.6g} < Row82={row_rms_means[82]:.6g}')
        parsed['RMS_Mean_Ordering'] = f'Row83-A={row_rms_means[83] - RMS_ORDER_GAP_A:.6g} < Row81={row_rms_means[81]:.6g}; Row81-B={row_rms_means[81] - RMS_ORDER_GAP_B:.6g} < Row84={row_rms_means[84]:.6g}; Row84-C={row_rms_means[84] - RMS_ORDER_GAP_C:.6g} < Row82={row_rms_means[82]:.6g}'
    if failures:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    return (True, {'fail_code': '', **parsed})

def check_rows85_88(rows, file_type):
    if file_type == 'RT':
        criteria = RT_85_88_CRITERIA
    elif file_type == 'LN':
        criteria = LN_85_88_CRITERIA
    else:
        return (False, {'fail_code': f'FAIL: unsupported file type: {file_type}'})
    failures = []
    parsed = {}
    row_data = {}
    for row_number in range(85, 89):
        passed, result = _collect_row(rows, row_number)
        if not passed:
            failures.append(result['fail_code'])
        else:
            row_data[row_number] = result['channel_measurements']
    if len(row_data) != 4:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    for row_number in range(85, 89):
        data = row_data[row_number]
        pedestal_values = [data[ch]['pedestal'] for ch in range(16)]
        pedestal_mean = _mean(pedestal_values)
        pedestal_std = _population_std(pedestal_values)
        pedestal_low = pedestal_mean - criteria['ped_sigma'] * pedestal_std
        pedestal_high = pedestal_mean + criteria['ped_sigma'] * pedestal_std
        parsed[f'Row{row_number}_Pedestal_Mean_16CH'] = pedestal_mean
        parsed[f'Row{row_number}_Pedestal_STD_16CH'] = pedestal_std
        parsed[f'Row{row_number}_Pedestal_Lower_4STD'] = pedestal_low
        parsed[f'Row{row_number}_Pedestal_Upper_4STD'] = pedestal_high
        for ch in range(16):
            pedestal = data[ch]['pedestal']
            if not pedestal_low <= pedestal <= pedestal_high:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside mean +/- 4STD ({pedestal_low:.6g} ~ {pedestal_high:.6g})')
            ped_min, ped_max = criteria['pedestal_range']
            if not ped_min <= pedestal <= ped_max:
                failures.append(f'FAIL: row {row_number} CH{ch} pedestal={pedestal} outside pedestal range ({ped_min} ~ {ped_max})')
    row_rms_means = {}
    row_rms_bands = {}
    for row_number in range(85, 89):
        data = row_data[row_number]
        rms_values = [data[ch]['rms'] for ch in range(16)]
        if file_type == 'LN':
            used_values = sorted(rms_values)[2:-2]
        else:
            used_values = rms_values
        rms_mean = _mean(used_values)
        rms_std = _population_std(used_values)
        rms_low = rms_mean - criteria['rms_sigma'] * rms_std
        rms_high = rms_mean + criteria['rms_sigma'] * rms_std
        row_rms_means[row_number] = rms_mean
        row_rms_bands[row_number] = (rms_low, rms_high)
        parsed[f'Row{row_number}_RMS_Mean'] = rms_mean
        parsed[f'Row{row_number}_RMS_STD'] = rms_std
        parsed[f'Row{row_number}_RMS_Lower_5STD'] = rms_low
        parsed[f'Row{row_number}_RMS_Upper_5STD'] = rms_high
        if file_type == 'RT':
            ch_low, ch_high = criteria['rms_channel_range']
            for ch in range(16):
                rms = data[ch]['rms']
                if not ch_low <= rms <= ch_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside range ({ch_low} ~ {ch_high})')
                if not rms_low <= rms <= rms_high:
                    failures.append(f'FAIL: row {row_number} CH{ch} rms={rms} outside mean +/- 5STD ({rms_low:.6g} ~ {rms_high:.6g})')
        if file_type == 'RT':
            mean_low, mean_high = criteria['rms_mean_range']
            if not mean_low <= rms_mean <= mean_high:
                failures.append(f'FAIL: row {row_number} RT RMS mean={rms_mean:.6g} outside range ({mean_low} ~ {mean_high})')
    if file_type == 'LN':
        ch_low, ch_high = criteria['rms_channel_range']
        for ch in range(16):
            in_range_count = 0
            in_band_count = 0
            values = []
            for row_number in range(85, 89):
                rms = row_data[row_number][ch]['rms']
                values.append(rms)
                if ch_low <= rms <= ch_high:
                    in_range_count += 1
                band_low, band_high = row_rms_bands[row_number]
                if band_low <= rms <= band_high:
                    in_band_count += 1
            if False: #ignore by Shanshan
                if in_range_count < 1:
                    failures.append(f'FAIL:Row{row_number-4}  CH{ch} has only {in_range_count} of 4 RMS values inside allowed range {ch_low}~{ch_high}; at least 1 in-range values are required; values={values}')
                if in_band_count < criteria['ln_band_min_count']:
                    failures.append(f'FAIL:Row{row_number-4}  CH{ch} has only {in_band_count} of 4 RMS values within corresponding row mean +/- 5STD; at least 1 required; values={values}')
    if file_type == 'LN':
        mean_low, mean_high = criteria['rms_mean_range']
        ln_mean_pass_count = sum((1 for row_number in range(85, 89) if mean_low <= row_rms_means[row_number] <= mean_high))
        if ln_mean_pass_count < 1:
            mean_values = [row_rms_means[row_number] for row_number in range(85, 89)]
            failures.append(f'FAIL: only {ln_mean_pass_count} of 4 LN RMS means are within ({mean_low} ~ {mean_high}); at least 1 required; values={mean_values}')
    condition_a = row_rms_means[87] - RMS_ORDER_GAP_A < row_rms_means[85]
    condition_b = row_rms_means[85] - RMS_ORDER_GAP_B < row_rms_means[88]
    condition_c = row_rms_means[88] - RMS_ORDER_GAP_C < row_rms_means[86]

    if file_type == 'LN': #ingore by shanshan
        pass
    else:
        if not (condition_a and condition_b and condition_c):
            failures.append(f'FAIL: RMS mean ordering Row87-A={row_rms_means[87] - RMS_ORDER_GAP_A:.6g} < Row85={row_rms_means[85]:.6g}; Row85-B={row_rms_means[85] - RMS_ORDER_GAP_B:.6g} < Row88={row_rms_means[88]:.6g}; Row88-C={row_rms_means[88] - RMS_ORDER_GAP_C:.6g} < Row86={row_rms_means[86]:.6g}')
        parsed['RMS_Mean_Ordering'] = f'Row87-A={row_rms_means[87] - RMS_ORDER_GAP_A:.6g} < Row85={row_rms_means[85]:.6g}; Row85-B={row_rms_means[85] - RMS_ORDER_GAP_B:.6g} < Row88={row_rms_means[88]:.6g}; Row88-C={row_rms_means[88] - RMS_ORDER_GAP_C:.6g} < Row86={row_rms_means[86]:.6g}'
    if failures:
        return (False, {'fail_code': ' | '.join(failures), **parsed})
    return (True, {'fail_code': '', **parsed})

def check_rows89_92(rows, file_type):
    return _check_group(rows, file_type, 89, RT_89_92_CRITERIA, LN_89_92_CRITERIA, (89, 90, 91, 92))

def check_rows93_96(rows, file_type):
    return _check_group(rows, file_type, 93, RT_93_96_CRITERIA, LN_93_96_CRITERIA, (93, 94, 95, 96))

def check_rows97_100(rows, file_type):
    return _check_group(rows, file_type, 97, RT_97_100_CRITERIA, LN_97_100_CRITERIA, (97, 98, 99, 100))

def check_rows101_104(rows, file_type):
    return _check_group(rows, file_type, 101, RT_101_104_CRITERIA, LN_101_104_CRITERIA, (101, 102, 103, 104))
CHECK_FUNCTIONS = {'check_rows73_76': check_rows73_76, 'check_rows77_80': check_rows77_80, 'check_rows81_84': check_rows81_84, 'check_rows85_88': check_rows85_88, 'check_rows89_92': check_rows89_92, 'check_rows93_96': check_rows93_96, 'check_rows97_100': check_rows97_100, 'check_rows101_104': check_rows101_104}
