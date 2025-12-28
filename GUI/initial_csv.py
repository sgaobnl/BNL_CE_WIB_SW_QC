
def check_csv():
    if 'tester' not in csv_data:
        csv_data['tester'] = 'sgao'
    else:
        csv_data['tester'] = input_name
    if 'SLOT0' not in csv_data:
        csv_data['SLOT0'] = 'H01'
    else:
        csv_data['tester'] = femb_id_0
    if 'SLOT1' not in csv_data:
        csv_data['SLOT1'] = 'H02'
    else:
        csv_data['tester'] = femb_id_1