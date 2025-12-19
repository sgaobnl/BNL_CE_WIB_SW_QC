# -*- coding: utf-8 -*-
"""
CSV Manager - Unified Test Results Recording System
DUNE WIB Quality Control System

每个测试项目都有特定的固定行来记录参数，测试时更新对应的行

Last modified: 2025-12-19
"""

import csv
import os
from datetime import datetime
import threading

# 线程锁，确保CSV文件更新时的线程安全
csv_lock = threading.Lock()


class WIB_QC_CSV_Manager:
    """
    WIB质量控制CSV管理器
    为每个测试项目预定义固定行，支持增量更新
    """

    def __init__(self, wib_id, csv_filepath=None):
        """
        初始化CSV管理器

        Args:
            wib_id: WIB序列号或ID
            csv_filepath: CSV文件路径，如果未指定则自动生成
        """
        self.wib_id = wib_id

        if csv_filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.csv_filepath = f"../report/WIB_{wib_id}_QC_Results_{timestamp}.csv"
        else:
            self.csv_filepath = csv_filepath

        # 确保report目录存在
        os.makedirs(os.path.dirname(self.csv_filepath), exist_ok=True)

        # 初始化CSV结构
        self._initialize_csv()

    def _initialize_csv(self):
        """初始化CSV文件，创建所有测试项目的固定行结构"""

        # 定义CSV结构
        rows = []

        # ========== 头部信息 ==========
        rows.append(["DUNE WIB Quality Control System - Comprehensive Test Results"])
        rows.append([])
        rows.append(["WIB Information"])
        rows.append(["Parameter", "Value", "Status", "Timestamp"])
        rows.append(["WIB_ID", self.wib_id, "", ""])
        rows.append(["Tester", "", "", ""])
        rows.append(["Test_Site", "", "", ""])
        rows.append(["Start_Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", ""])
        rows.append(["Comment", "", "", ""])
        rows.append([])

        # ========== Test00: Reception Checkout ==========
        rows.append(["=== Test00: Reception Checkout ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T00_01", "Component_Inspection", "", "", "", "", "", ""])
        rows.append(["T00_02", "LTpowerPlay_Config", "", "", "", "", "", ""])
        rows.append(["T00_03", "Power_Ch1_Current", "", "A", "", "0.5", "2.0", ""])
        rows.append(["T00_04", "Power_Ch2_Current", "", "A", "", "0.5", "2.0", ""])
        rows.append(["T00_05", "Front_Panel_Install", "", "", "", "", "", ""])
        rows.append(["T00_06", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test01: Serial/TCP/IP Communication ==========
        rows.append(["=== Test01: Serial/TCP/IP Communication ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T01_01", "UART_Test", "", "", "", "", "", ""])
        rows.append(["T01_02", "WIB_IP_Address", "", "", "", "", "", ""])
        rows.append(["T01_03", "TCP_Connection", "", "", "", "", "", ""])
        rows.append(["T01_04", "TCP_FW_Version", "", "", "", "", "", ""])
        rows.append(["T01_05", "UDP_Connection", "", "", "", "", "", ""])
        rows.append(["T01_06", "UDP_FW_Version", "", "", "", "", "", ""])
        rows.append(["T01_07", "ICMP_Ping_Test", "", "", "", "", "", ""])
        rows.append(["T01_08", "WIB_Power_Ch1_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T01_09", "WIB_Power_Ch1_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T01_10", "WIB_Power_Ch2_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T01_11", "WIB_Power_Ch2_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T01_12", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test02: Calibration Path Control ==========
        rows.append(["=== Test02: Calibration Path Control ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T02_01", "WIB_Power_Ch1_V_Start", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T02_02", "WIB_Power_Ch1_I_Start", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T02_03", "WIB_Power_Ch2_V_Start", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T02_04", "WIB_Power_Ch2_I_Start", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T02_05", "DAC_0_Config", "", "", "", "", "", ""])
        rows.append(["T02_06", "DAC_1_Config", "", "", "", "", "", ""])
        rows.append(["T02_07", "DAC_2_Config", "", "", "", "", "", ""])
        rows.append(["T02_08", "DAC_3_Config", "", "", "", "", "", ""])
        rows.append(["T02_09", "ADC_0_Readback", "", "mV", "", "", "", ""])
        rows.append(["T02_10", "ADC_1_Readback", "", "mV", "", "", "", ""])
        rows.append(["T02_11", "ADC_2_Readback", "", "mV", "", "", "", ""])
        rows.append(["T02_12", "ADC_3_Readback", "", "mV", "", "", "", ""])
        rows.append(["T02_13", "WIB_Power_Ch1_V_End", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T02_14", "WIB_Power_Ch1_I_End", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T02_15", "WIB_Power_Ch2_V_End", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T02_16", "WIB_Power_Ch2_I_End", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T02_17", "Total_Power", "", "W", "", "", "", ""])
        rows.append(["T02_18", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test03_1V: FEMB Power Rail Test (1V) ==========
        rows.append(["=== Test03_1V: FEMB Power Rail Test (1V) ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T03_1V_00", "WIB_Power_Ch1_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T03_1V_01", "WIB_Power_Ch1_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T03_1V_02", "WIB_Power_Ch2_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T03_1V_03", "WIB_Power_Ch2_I", "", "A", "", "0.5", "3.0", ""])

        # 为4个FEMB插槽和5个电源轨创建行
        for slot in range(4):
            for rail in ["FE", "CD", "ADC", "IDLE", "BIAS"]:
                rows.append([f"T03_1V_{slot}{rail}_V", f"Slot{slot}_{rail}_Voltage", "", "V", "", "0.85", "1.15", ""])
                rows.append([f"T03_1V_{slot}{rail}_I", f"Slot{slot}_{rail}_Current", "", "A", "", "", "", ""])

        rows.append(["T03_1V_99", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test03_2V: FEMB Power Rail Test (2V) ==========
        rows.append(["=== Test03_2V: FEMB Power Rail Test (2V) ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T03_2V_00", "WIB_Power_Ch1_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T03_2V_01", "WIB_Power_Ch1_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T03_2V_02", "WIB_Power_Ch2_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T03_2V_03", "WIB_Power_Ch2_I", "", "A", "", "0.5", "3.0", ""])

        for slot in range(4):
            for rail in ["FE", "CD", "ADC", "IDLE", "BIAS"]:
                rows.append([f"T03_2V_{slot}{rail}_V", f"Slot{slot}_{rail}_Voltage", "", "V", "", "1.85", "2.15", ""])
                rows.append([f"T03_2V_{slot}{rail}_I", f"Slot{slot}_{rail}_Current", "", "A", "", "", "", ""])

        rows.append(["T03_2V_99", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test03_3V: FEMB Power Rail Test (3V) ==========
        rows.append(["=== Test03_3V: FEMB Power Rail Test (3V) ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T03_3V_00", "WIB_Power_Ch1_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T03_3V_01", "WIB_Power_Ch1_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T03_3V_02", "WIB_Power_Ch2_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T03_3V_03", "WIB_Power_Ch2_I", "", "A", "", "0.5", "3.0", ""])

        for slot in range(4):
            for rail in ["FE", "CD", "ADC", "IDLE", "BIAS"]:
                rows.append([f"T03_3V_{slot}{rail}_V", f"Slot{slot}_{rail}_Voltage", "", "V", "", "2.85", "3.15", ""])
                rows.append([f"T03_3V_{slot}{rail}_I", f"Slot{slot}_{rail}_Current", "", "A", "", "", "", ""])

        rows.append(["T03_3V_99", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test03_4V: FEMB Power Rail Test (4V) ==========
        rows.append(["=== Test03_4V: FEMB Power Rail Test (4V) ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T03_4V_00", "WIB_Power_Ch1_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T03_4V_01", "WIB_Power_Ch1_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T03_4V_02", "WIB_Power_Ch2_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T03_4V_03", "WIB_Power_Ch2_I", "", "A", "", "0.5", "3.0", ""])

        for slot in range(4):
            for rail in ["FE", "CD", "ADC", "IDLE", "BIAS"]:
                rows.append([f"T03_4V_{slot}{rail}_V", f"Slot{slot}_{rail}_Voltage", "", "V", "", "3.85", "4.15", ""])
                rows.append([f"T03_4V_{slot}{rail}_I", f"Slot{slot}_{rail}_Current", "", "A", "", "", "", ""])

        rows.append(["T03_4V_99", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test05: I2C Device Search ==========
        rows.append(["=== Test05: I2C Device Search ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T05_00", "WIB_Power_Ch1_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T05_01", "WIB_Power_Ch1_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T05_02", "WIB_Power_Ch2_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T05_03", "WIB_Power_Ch2_I", "", "A", "", "0.5", "3.0", ""])

        # I2C Devices
        rows.append(["T05_10", "SI5342_0x6b", "", "", "", "", "", ""])
        rows.append(["T05_11", "SI5344_0x6b", "", "", "", "", "", ""])
        rows.append(["T05_12", "TCA9546ADR_0x70", "", "", "", "", "", ""])
        rows.append(["T05_13", "LTC2991_0x48", "", "", "", "", "", ""])
        rows.append(["T05_14", "LTC2991_0x49", "", "", "", "", "", ""])
        rows.append(["T05_15", "LTC2991_0x4a", "", "", "", "", "", ""])
        rows.append(["T05_16", "LTC2991_0x4b", "", "", "", "", "", ""])
        rows.append(["T05_17", "LTC2990_0x4e", "", "", "", "", "", ""])
        rows.append(["T05_18", "TCA6424_0x22", "", "", "", "", "", ""])
        rows.append(["T05_19", "TCA642_0x23", "", "", "", "", "", ""])
        rows.append(["T05_20", "LTC2499_0x15", "", "", "", "", "", ""])
        rows.append(["T05_21", "INA226_0x46", "", "", "", "", "", ""])
        rows.append(["T05_22", "AD7414A_0x49", "", "", "", "", "", ""])
        rows.append(["T05_23", "AD7414A_0x4a", "", "", "", "", "", ""])
        rows.append(["T05_24", "AD7414A_0x4d", "", "", "", "", "", ""])
        rows.append(["T05_25", "SODIMM_0x51", "", "", "", "", "", ""])
        rows.append(["T05_26", "LTC2991_0x48_2", "", "", "", "", "", ""])
        rows.append(["T05_27", "LTC2991_0x4c", "", "", "", "", "", ""])
        rows.append(["T05_28", "LTC2991_0x4e_2", "", "", "", "", "", ""])
        rows.append(["T05_29", "DAC7574_0x4c", "", "", "", "", "", ""])
        rows.append(["T05_30", "DAC7574_0x4d", "", "", "", "", "", ""])
        rows.append(["T05_31", "DAC7574_0x4e", "", "", "", "", "", ""])
        rows.append(["T05_32", "DAC7574_0x4f", "", "", "", "", "", ""])
        rows.append(["T05_33", "LTC2977_0x5c", "", "", "", "", "", ""])
        rows.append(["T05_34", "DAC7574_0x4c_2", "", "", "", "", "", ""])
        rows.append(["T05_35", "DAC7574_0x4d_2", "", "", "", "", "", ""])
        rows.append(["T05_36", "24LC64SN_0x50", "", "", "", "", "", ""])
        rows.append(["T05_37", "ADN2814_0x40", "", "", "", "", "", ""])
        rows.append(["T05_99", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test06: PTB Interface Path ==========
        rows.append(["=== Test06: PTB Interface Path ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])
        rows.append(["T06_00", "WIB_Power_Ch1_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T06_01", "WIB_Power_Ch1_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T06_02", "WIB_Power_Ch2_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T06_03", "WIB_Power_Ch2_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T06_04", "Ping_192.168.121.1", "", "", "", "", "", ""])
        rows.append(["T06_05", "Ping_192.168.121.2", "", "", "", "", "", ""])
        rows.append(["T06_10", "SI5342_Selection", "", "", "", "", "", ""])
        rows.append(["T06_11", "SI5344_Config", "", "", "", "", "", ""])
        rows.append(["T06_12", "FP_BK_Interface", "", "", "", "", "", ""])
        rows.append(["T06_99", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Test052: I2C Sensor Information ==========
        rows.append(["=== Test052: I2C Sensor Information ==="])
        rows.append(["Item", "Parameter", "Value", "Unit", "Status", "Min", "Max", "Timestamp"])

        # WIB Power
        rows.append(["T052_00", "WIB_Power_Ch1_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T052_01", "WIB_Power_Ch1_I", "", "A", "", "0.5", "3.0", ""])
        rows.append(["T052_02", "WIB_Power_Ch2_V", "", "V", "", "11.0", "13.0", ""])
        rows.append(["T052_03", "WIB_Power_Ch2_I", "", "A", "", "0.5", "3.0", ""])

        # LTC2499 Temperatures (6 sensors)
        rows.append(["T052_10", "LTC2499_BRD0_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_11", "LTC2499_BRD1_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_12", "LTC2499_BRD2_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_13", "LTC2499_BRD3_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_14", "LTC2499_WIB1_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_15", "LTC2499_WIB2_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_16", "LTC2499_WIB3_Temp", "", "°C", "", "", "", ""])

        # INA226
        rows.append(["T052_20", "INA226_Vbus", "", "V", "", "", "", ""])
        rows.append(["T052_21", "INA226_Current", "", "A", "", "", "", ""])

        # AD7414 Temperatures (3 sensors)
        rows.append(["T052_30", "AD7414_0x4A_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_31", "AD7414_0x49_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_32", "AD7414_0x4D_Temp", "", "°C", "", "", "", ""])

        # LTC2991_0x48 (10 measurements)
        rows.append(["T052_40", "LTC2991_0x48_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_41", "LTC2991_0x48_V0.85_V", "", "V", "", "", "", ""])
        rows.append(["T052_42", "LTC2991_0x48_V0.85_I", "", "A", "", "", "", ""])
        rows.append(["T052_43", "LTC2991_0x48_V5.0_V", "", "V", "", "", "", ""])
        rows.append(["T052_44", "LTC2991_0x48_V5.0_I", "", "A", "", "", "", ""])
        rows.append(["T052_45", "LTC2991_0x48_V2.5_V", "", "V", "", "", "", ""])
        rows.append(["T052_46", "LTC2991_0x48_V2.5_I", "", "A", "", "", "", ""])
        rows.append(["T052_47", "LTC2991_0x48_V1.8_V", "", "V", "", "", "", ""])
        rows.append(["T052_48", "LTC2991_0x48_V1.8_I", "", "A", "", "", "", ""])
        rows.append(["T052_49", "LTC2991_0x48_VCC", "", "V", "", "", "", ""])

        # LTC2990_0x4C (6 measurements)
        rows.append(["T052_50", "LTC2990_0x4C_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_51", "LTC2990_0x4C_V1.2_V", "", "V", "", "", "", ""])
        rows.append(["T052_52", "LTC2990_0x4C_V3.3_V", "", "V", "", "", "", ""])
        rows.append(["T052_53", "LTC2990_0x4C_VCC", "", "V", "", "", "", ""])
        rows.append(["T052_54", "LTC2990_0x4C_V1.2_I", "", "A", "", "", "", ""])
        rows.append(["T052_55", "LTC2990_0x4C_V3.3_I", "", "A", "", "", "", ""])

        # LTC2990_0x4E (6 measurements)
        rows.append(["T052_60", "LTC2990_0x4E_Temp", "", "°C", "", "", "", ""])
        rows.append(["T052_61", "LTC2990_0x4E_V0.9_V", "", "V", "", "", "", ""])
        rows.append(["T052_62", "LTC2990_0x4E_VCCPSPLL_1.2_V", "", "V", "", "", "", ""])
        rows.append(["T052_63", "LTC2990_0x4E_PSDDR4_V", "", "V", "", "", "", ""])
        rows.append(["T052_64", "LTC2990_0x4E_VCC", "", "V", "", "", "", ""])
        rows.append(["T052_65", "LTC2990_0x4E_V0.9_I", "", "A", "", "", "", ""])

        rows.append(["T052_99", "Test_Duration", "", "s", "", "", "", ""])
        rows.append([])

        # ========== Footer ==========
        rows.append([])
        rows.append(["Generated by DUNE WIB QC System"])
        rows.append([f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
        rows.append(["Last Updated: ", ""])

        # 写入CSV文件
        with csv_lock:
            with open(self.csv_filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)

        print(f"✓ CSV initialized: {self.csv_filepath}")

    def update_item(self, item_id, value, status="", timestamp=None):
        """
        更新指定测试项目的值

        Args:
            item_id: 测试项目ID (例如: "T00_01", "T01_03", "T03_1V_0FE_V")
            value: 测试值
            status: 测试状态 (PASS/FAIL/WARNING等)
            timestamp: 时间戳，如果未指定则使用当前时间
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with csv_lock:
            # 读取所有行
            with open(self.csv_filepath, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

            # 查找并更新对应的行
            updated = False
            for i, row in enumerate(rows):
                if len(row) > 0 and row[0] == item_id:
                    # 找到对应行，更新值
                    if len(row) >= 8:
                        row[2] = str(value)  # Value
                        row[4] = status      # Status
                        row[7] = timestamp   # Timestamp
                    else:
                        # 扩展行到足够长度
                        while len(row) < 8:
                            row.append("")
                        row[2] = str(value)
                        row[4] = status
                        row[7] = timestamp

                    rows[i] = row
                    updated = True
                    break

            if not updated:
                print(f"⚠ Warning: Item ID '{item_id}' not found in CSV")
                return False

            # 更新"Last Updated"时间戳
            for i, row in enumerate(rows):
                if len(row) > 0 and row[0] == "Last Updated: ":
                    row[1] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    rows[i] = row
                    break

            # 写回CSV文件
            with open(self.csv_filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)

            return True

    def update_wib_info(self, tester="", test_site="", comment=""):
        """
        更新WIB基本信息

        Args:
            tester: 测试人员
            test_site: 测试地点
            comment: 备注
        """
        with csv_lock:
            with open(self.csv_filepath, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

            for i, row in enumerate(rows):
                if len(row) > 0:
                    if row[0] == "Tester":
                        row[1] = tester
                        rows[i] = row
                    elif row[0] == "Test_Site":
                        row[1] = test_site
                        rows[i] = row
                    elif row[0] == "Comment":
                        row[1] = comment
                        rows[i] = row

            with open(self.csv_filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)

    def batch_update(self, updates):
        """
        批量更新多个测试项目

        Args:
            updates: 字典列表，每个字典包含 {"item_id": "xxx", "value": xxx, "status": "xxx"}

        Example:
            csv_mgr.batch_update([
                {"item_id": "T01_02", "value": "192.168.121.1", "status": "PASS"},
                {"item_id": "T01_03", "value": "Connected", "status": "PASS"},
                {"item_id": "T01_08", "value": 12.05, "status": "PASS"}
            ])
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with csv_lock:
            # 读取所有行
            with open(self.csv_filepath, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

            # 创建item_id到更新数据的映射
            update_map = {item["item_id"]: item for item in updates}

            # 更新所有匹配的行
            for i, row in enumerate(rows):
                if len(row) > 0 and row[0] in update_map:
                    update_data = update_map[row[0]]

                    # 扩展行到足够长度
                    while len(row) < 8:
                        row.append("")

                    row[2] = str(update_data.get("value", ""))
                    row[4] = update_data.get("status", "")
                    row[7] = timestamp
                    rows[i] = row

            # 更新"Last Updated"时间戳
            for i, row in enumerate(rows):
                if len(row) > 0 and row[0] == "Last Updated: ":
                    row[1] = timestamp
                    rows[i] = row
                    break

            # 写回CSV文件
            with open(self.csv_filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)

    def get_csv_path(self):
        """返回CSV文件路径"""
        return self.csv_filepath


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 创建CSV管理器
    csv_mgr = WIB_QC_CSV_Manager(wib_id="WIB_SN_12345")

    # 更新WIB信息
    csv_mgr.update_wib_info(tester="John Doe", test_site="BNL", comment="Production test")

    # 单个更新示例
    csv_mgr.update_item("T00_01", "PASS", status="PASS")
    csv_mgr.update_item("T00_03", 1.25, status="PASS")

    # 批量更新示例
    csv_mgr.batch_update([
        {"item_id": "T01_02", "value": "192.168.121.1", "status": "PASS"},
        {"item_id": "T01_03", "value": "Connected", "status": "PASS"},
        {"item_id": "T01_08", "value": 12.05, "status": "PASS"},
        {"item_id": "T01_09", "value": 1.85, "status": "PASS"}
    ])

    print(f"\n✓ CSV file created and updated: {csv_mgr.get_csv_path()}")
