#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：如何在测试脚本中使用CSV管理器
DUNE WIB Quality Control System
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from function.csv_manager import WIB_QC_CSV_Manager

# ========== 在测试开始时创建CSV管理器 ==========
def example_test01():
    """
    Test01: Serial/TCP/IP Communication 集成示例
    """

    # 1. 创建CSV管理器（在测试开始时）
    wib_id = "WIB_001"  # 从用户输入或配置文件获取
    csv_mgr = WIB_QC_CSV_Manager(
        wib_id=wib_id,
        csv_filepath=f"../report/WIB_{wib_id}_QC_Results.csv"
    )

    # 2. 更新WIB基本信息
    csv_mgr.update_wib_info(
        tester="John Doe",
        test_site="BNL",
        comment="Production QC Test"
    )

    print("\n" + "="*60)
    print("Test01: Serial/TCP/IP Communication")
    print("="*60)

    # 3. UART测试
    print("\n[1/3] UART Test...")
    uart_status = "PASS"  # 实际测试结果
    csv_mgr.update_item("T01_01", uart_status, status=uart_status)

    # 4. TCP/IP测试
    print("[2/3] TCP/IP Test...")
    wib_ip = "192.168.121.1"
    tcp_status = "PASS"
    fw_version = "0x1234"

    # 批量更新TCP相关数据
    csv_mgr.batch_update([
        {"item_id": "T01_02", "value": wib_ip, "status": "PASS"},
        {"item_id": "T01_03", "value": "Connected", "status": tcp_status},
        {"item_id": "T01_04", "value": fw_version, "status": "PASS"}
    ])

    # 5. UDP测试
    print("[3/3] UDP Test...")
    udp_status = "PASS"
    udp_fw = "0x5678"

    csv_mgr.batch_update([
        {"item_id": "T01_05", "value": "Connected", "status": udp_status},
        {"item_id": "T01_06", "value": udp_fw, "status": "PASS"},
        {"item_id": "T01_07", "value": "4 packets received", "status": "PASS"}
    ])

    # 6. 记录WIB功率测量
    v1, c1 = 12.05, 1.85  # 从电源测量获取
    v2, c2 = 12.03, 1.82

    csv_mgr.batch_update([
        {"item_id": "T01_08", "value": v1, "status": "PASS"},
        {"item_id": "T01_09", "value": c1, "status": "PASS"},
        {"item_id": "T01_10", "value": v2, "status": "PASS"},
        {"item_id": "T01_11", "value": c2, "status": "PASS"}
    ])

    # 7. 记录测试总时长
    test_duration = 45.2  # 秒
    csv_mgr.update_item("T01_12", test_duration, status="COMPLETE")

    print(f"\n✓ Test completed. Results saved to: {csv_mgr.get_csv_path()}")


# ========== Test03 集成示例 ==========
def example_test03_1v():
    """
    Test03_1V: FEMB Power Rail Test (1V) 集成示例
    """

    wib_id = "WIB_001"
    csv_mgr = WIB_QC_CSV_Manager(
        wib_id=wib_id,
        csv_filepath=f"../report/WIB_{wib_id}_QC_Results.csv"
    )

    print("\n" + "="*60)
    print("Test03_1V: FEMB Power Rail Test (1V)")
    print("="*60)

    # 1. 记录WIB电源测量
    v1_wib, c1_wib = 12.05, 2.15
    v2_wib, c2_wib = 12.03, 2.12

    csv_mgr.batch_update([
        {"item_id": "T03_1V_00", "value": v1_wib, "status": "PASS"},
        {"item_id": "T03_1V_01", "value": c1_wib, "status": "PASS"},
        {"item_id": "T03_1V_02", "value": v2_wib, "status": "PASS"},
        {"item_id": "T03_1V_03", "value": c2_wib, "status": "PASS"}
    ])

    # 2. 测试4个FEMB插槽，每个插槽5个电源轨
    for slot in range(4):
        print(f"\nTesting FEMB Slot {slot}...")

        # 模拟从WIB读取的电源轨数据
        # pwr_info = tcp.femb_pwr_rd(femb=slot)
        # 这里使用模拟数据
        rail_data = {
            "FE":   (1.02, 0.85),   # (Voltage, Current)
            "CD":   (1.01, 0.32),
            "ADC":  (1.03, 1.25),
            "IDLE": (1.00, 0.15),
            "BIAS": (1.01, 0.08)
        }

        # 批量更新该插槽的所有电源轨数据
        updates = []
        for rail, (v_meas, i_meas) in rail_data.items():
            # 检查是否在阈值范围内
            v_min, v_max = 0.85, 1.15  # 1V ± 0.15V
            v_status = "PASS" if v_min <= v_meas <= v_max else "FAIL"

            updates.append({
                "item_id": f"T03_1V_{slot}{rail}_V",
                "value": v_meas,
                "status": v_status
            })
            updates.append({
                "item_id": f"T03_1V_{slot}{rail}_I",
                "value": i_meas,
                "status": "PASS"
            })

        csv_mgr.batch_update(updates)

    # 3. 记录测试总时长
    csv_mgr.update_item("T03_1V_99", 120.5, status="COMPLETE")

    print(f"\n✓ Test completed. Results saved to: {csv_mgr.get_csv_path()}")


# ========== Test02 集成示例 ==========
def example_test02():
    """
    Test02: Calibration Path Control 集成示例
    """

    wib_id = "WIB_001"
    csv_mgr = WIB_QC_CSV_Manager(
        wib_id=wib_id,
        csv_filepath=f"../report/WIB_{wib_id}_QC_Results.csv"
    )

    print("\n" + "="*60)
    print("Test02: Calibration Path Control")
    print("="*60)

    # 1. 测试开始时的WIB功率
    v1_start, c1_start = 12.05, 1.85
    v2_start, c2_start = 12.03, 1.82

    csv_mgr.batch_update([
        {"item_id": "T02_01", "value": v1_start, "status": "PASS"},
        {"item_id": "T02_02", "value": c1_start, "status": "PASS"},
        {"item_id": "T02_03", "value": v2_start, "status": "PASS"},
        {"item_id": "T02_04", "value": c2_start, "status": "PASS"}
    ])

    # 2. DAC配置和ADC读回
    dac_configs = [0x1234, 0x5678, 0x9ABC, 0xDEF0]
    adc_readbacks = [1250, 2500, 3750, 5000]  # mV

    updates = []
    for i in range(4):
        updates.append({"item_id": f"T02_{5+i:02d}", "value": f"0x{dac_configs[i]:04X}", "status": "SET"})
        updates.append({"item_id": f"T02_{9+i:02d}", "value": adc_readbacks[i], "status": "PASS"})

    csv_mgr.batch_update(updates)

    # 3. 测试结束时的WIB功率
    v1_end, c1_end = 12.04, 1.86
    v2_end, c2_end = 12.02, 1.83
    total_power = (v1_end * c1_end) + (v2_end * c2_end)

    csv_mgr.batch_update([
        {"item_id": "T02_13", "value": v1_end, "status": "PASS"},
        {"item_id": "T02_14", "value": c1_end, "status": "PASS"},
        {"item_id": "T02_15", "value": v2_end, "status": "PASS"},
        {"item_id": "T02_16", "value": c2_end, "status": "PASS"},
        {"item_id": "T02_17", "value": round(total_power, 3), "status": "PASS"},
        {"item_id": "T02_18", "value": 85.3, "status": "COMPLETE"}
    ])

    print(f"\n✓ Test completed. Results saved to: {csv_mgr.get_csv_path()}")


if __name__ == "__main__":
    print("="*60)
    print("CSV Manager Integration Examples")
    print("="*60)

    # 运行示例
    # example_test01()
    # example_test02()
    example_test03_1v()
