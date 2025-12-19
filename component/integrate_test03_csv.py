#!/usr/bin/env python3
"""
快速集成Test03 2V/3V/4V的CSV记录功能
"""

import re

# 要处理的文件和对应的电压标识
files_to_process = [
    ("Test03_power_rail_for_FEMB_2V.py", "2V"),
    ("Test03_power_rail_for_FEMB_3V.py", "3V"),
    ("Test03_power_rail_for_FEMB_4V.py", "4V")
]

# FEMB电源轨CSV更新代码模板
femb_csv_update = """
# Update CSV with FEMB power rail measurements
if rp_dict.csv_manager:
    VOLTAGE_TOLERANCE = 0.15
    updates = []

    # Process all 4 slots
    slot_dicts = [
        (0, rp_dict.log03_femb_slot0),
        (1, rp_dict.log03_femb_slot1),
        (2, rp_dict.log03_femb_slot2),
        (3, rp_dict.log03_femb_slot3)
    ]

    for slot, slot_dict in slot_dicts:
        # Process all 5 rails (FE, CD, ADC, IDLE, BIAS)
        rails = ['fe', 'cd', 'adc', 'idle', 'bias']
        rail_names = ['FE', 'CD', 'ADC', 'IDLE', 'BIAS']

        for rail, rail_name in zip(rails, rail_names):
            v_set = float(slot_dict.get(f'v_{rail}', set_v))
            v_meas = float(slot_dict.get(f'V_{rail}_meas', 0))
            i_meas = float(slot_dict.get(f'I_{rail}_meas', 0))

            # Check voltage within tolerance
            v_status = "PASS" if abs(v_meas - v_set) <= VOLTAGE_TOLERANCE else "FAIL"

            updates.append({
                "item_id": f"T03_{VOLTAGE_ID}_{slot}{rail_name}_V",
                "value": round(v_meas, 3),
                "status": v_status
            })
            updates.append({
                "item_id": f"T03_{VOLTAGE_ID}_{slot}{rail_name}_I",
                "value": round(i_meas, 3),
                "status": "PASS"
            })

    rp_dict.csv_manager.batch_update(updates)"""

# 测试时长CSV更新代码模板
duration_csv_update = """
# Update CSV with test duration
if rp_dict.csv_manager:
    rp_dict.csv_manager.update_item("T03_{VOLTAGE_ID}_99", test_duration, status="COMPLETE")"""

for filepath, voltage_id in files_to_process:
    print(f"\nProcessing {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经添加了FEMB CSV更新
    if f"T03_{voltage_id}_" in content and "rp_dict.csv_manager.batch_update(updates)" in content:
        print(f"  ✓ FEMB CSV updates already present")
    else:
        # 在打印slot数据后添加FEMB CSV更新
        pattern = r"(print\(rp_dict\.log03_femb_slot3\)\n)"
        replacement = r"\1" + femb_csv_update.replace("{VOLTAGE_ID}", voltage_id)
        content = re.sub(pattern, replacement, content)
        print(f"  ✓ Added FEMB CSV updates")

    # 检查是否已经添加了测试时长CSV更新
    if f"T03_{voltage_id}_99" in content:
        print(f"  ✓ Duration CSV update already present")
    else:
        # 在测试时长记录后添加CSV更新
        pattern = r"(rp_dict\.log03_femb_slot0\['test_duration'\] = test_duration\n)"
        replacement = r"\1" + duration_csv_update.replace("{VOLTAGE_ID}", voltage_id) + "\n"
        content = re.sub(pattern, replacement, content)
        print(f"  ✓ Added duration CSV update")

    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("\n✓ All Test03 versions updated!")
