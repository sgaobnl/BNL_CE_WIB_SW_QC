# -*- coding: utf-8 -*-
"""
CSV Export Module
DUNE WIB Quality Control System

Export detailed test results to CSV format for analysis and archiving.

Last modified: 2025-12-18
"""

import csv
import os
from datetime import datetime


def export_test0401_to_csv(result_dict, csv_filename=None):
    """
    Export Test0401 (FEMB Pulse Test) results to CSV

    Args:
        result_dict: Dictionary containing all test results
        csv_filename: Optional custom filename, otherwise auto-generated

    Returns:
        str: Path to the saved CSV file
    """
    # Generate filename if not provided
    if csv_filename is None:
        femb_sn = result_dict.get("FEMB_SN", "Unknown")
        timestamp = result_dict.get("datetime", datetime.now()).strftime("%Y%m%d_%H%M%S")
        csv_filename = result_dict["save_dir"] + f"FEMB{femb_sn}_Test0401_{timestamp}.csv"

    # Prepare data rows
    data_rows = []

    # ===== HEADER INFORMATION =====
    data_rows.append(["DUNE WIB Quality Control - FEMB Pulse Test (Test0401)"])
    data_rows.append([])
    data_rows.append(["Test Information"])
    data_rows.append(["Parameter", "Value", "Unit", "Status", "Notes"])
    data_rows.append(["FEMB Serial Number", result_dict.get("FEMB_SN", ""), "", "", ""])
    data_rows.append(["Test Date", result_dict.get("datetime", "").strftime("%Y-%m-%d %H:%M:%S") if result_dict.get("datetime") else "", "", "", ""])
    data_rows.append(["Tester", result_dict.get("Tester", ""), "", "", ""])
    data_rows.append(["Environment", result_dict.get("Env", ""), "", "", ""])
    data_rows.append(["Input Capacitor", result_dict.get("Cd", ""), "", "", ""])
    data_rows.append(["WIB TCP FW Version", f"0x{result_dict.get('WIB_TCP_FW_ver', 0):02x}", "", "", ""])
    data_rows.append(["WIB UDP FW Version", f"0x{result_dict.get('WIB_UDP_FW_ver', 0):02x}", "", "", ""])
    data_rows.append(["Total Test Time", f"{result_dict.get('total_test_time', 0):.2f}", "seconds", "", ""])
    data_rows.append([])

    # ===== POWER RAIL MEASUREMENTS - SEOFF MODE =====
    data_rows.append(["SEOFF Mode Power Measurements"])
    data_rows.append(["Power Rail", "V_set (V)", "V_meas (V)", "I_meas (A)", "P_meas (W)", "Status", "Expected I (A)", "Tolerance (A)"])

    rails_info = [
        ("LArASIC", "power_vfe_ref", "power_vfe_meas"),
        ("ColdADC", "power_vadc_ref", "power_vadc_meas"),
        ("COLDATA", "power_vcd_ref", "power_vcd_meas"),
        ("BIAS", "power_bias_ref", "power_bias_meas")
    ]

    seoff_total_power = 0
    for rail_name, ref_key, meas_key in rails_info:
        ref = result_dict.get(ref_key, (0, 0))
        meas = result_dict.get(meas_key, (0, 0))
        v_set = ref[0] if len(ref) >= 1 else 0
        i_ref = ref[1] if len(ref) >= 2 else 0
        v_meas = meas[0] if len(meas) >= 1 else 0
        i_meas = meas[1] if len(meas) >= 2 else 0
        p_meas = v_meas * i_meas
        seoff_total_power += p_meas

        # Check status (will be updated with actual check later)
        status = result_dict.get(f"seoff_{rail_name.lower()}_status", "")

        data_rows.append([
            rail_name,
            f"{v_set:.3f}",
            f"{v_meas:.3f}",
            f"{i_meas:.3f}",
            f"{p_meas:.3f}",
            status,
            f"{i_ref:.3f}",
            "See config"
        ])

    data_rows.append(["TOTAL SEOFF", "", "", "", f"{seoff_total_power:.3f}", "", "", ""])
    data_rows.append([])

    # ===== POWER RAIL MEASUREMENTS - SEON (SDC) MODE =====
    data_rows.append(["SEON (SDC) Mode Power Measurements"])
    data_rows.append(["Power Rail", "V_set (V)", "V_meas (V)", "I_meas (A)", "P_meas (W)", "Status", "Expected I (A)", "Tolerance (A)"])

    seon_total_power = 0
    for rail_name, ref_key, _ in rails_info:
        meas_key = ref_key.replace("_ref", "_meas_sdc")
        ref = result_dict.get(ref_key, (0, 0))
        meas = result_dict.get(meas_key, (0, 0))
        v_set = ref[0] if len(ref) >= 1 else 0
        i_ref = ref[1] if len(ref) >= 2 else 0
        v_meas = meas[0] if len(meas) >= 1 else 0
        i_meas = meas[1] if len(meas) >= 2 else 0
        p_meas = v_meas * i_meas
        seon_total_power += p_meas

        status = result_dict.get(f"seon_{rail_name.lower()}_status", "")

        data_rows.append([
            rail_name,
            f"{v_set:.3f}",
            f"{v_meas:.3f}",
            f"{i_meas:.3f}",
            f"{p_meas:.3f}",
            status,
            f"{i_ref:.3f}",
            "See config"
        ])

    data_rows.append(["TOTAL SEON", "", "", "", f"{seon_total_power:.3f}", "", "", ""])
    data_rows.append([])

    # ===== POWER RAIL MEASUREMENTS - DIFF MODE =====
    data_rows.append(["DIFF Mode Power Measurements"])
    data_rows.append(["Power Rail", "V_set (V)", "V_meas (V)", "I_meas (A)", "P_meas (W)", "Status", "Expected I (A)", "Tolerance (A)"])

    diff_total_power = 0
    for rail_name, ref_key, _ in rails_info:
        meas_key = ref_key.replace("_ref", "_meas_diff")
        ref = result_dict.get(ref_key, (0, 0))
        meas = result_dict.get(meas_key, (0, 0))
        v_set = ref[0] if len(ref) >= 1 else 0
        i_ref = ref[1] if len(ref) >= 2 else 0
        v_meas = meas[0] if len(meas) >= 1 else 0
        i_meas = meas[1] if len(meas) >= 2 else 0
        p_meas = v_meas * i_meas
        diff_total_power += p_meas

        status = result_dict.get(f"diff_{rail_name.lower()}_status", "")

        data_rows.append([
            rail_name,
            f"{v_set:.3f}",
            f"{v_meas:.3f}",
            f"{i_meas:.3f}",
            f"{p_meas:.3f}",
            status,
            f"{i_ref:.3f}",
            "See config"
        ])

    data_rows.append(["TOTAL DIFF", "", "", "", f"{diff_total_power:.3f}", "", "", ""])
    data_rows.append([])

    # ===== ADC MONITORING PARAMETERS =====
    data_rows.append(["ADC Monitoring Parameters"])
    data_rows.append(["ASIC #", "VCMI (mV)", "VCMO (mV)", "VREFP (mV)", "VREFN (mV)", "Status"])

    for asic in [0, 4]:
        adc_meas = result_dict.get(f"ADC{asic:02d}_MeasRef", [None, (0,), (0,), (0,), (0,)])
        vcmi = int(adc_meas[1][0]) if len(adc_meas) > 1 and len(adc_meas[1]) > 0 else 0
        vcmo = int(adc_meas[2][0]) if len(adc_meas) > 2 and len(adc_meas[2]) > 0 else 0
        vrefp = int(adc_meas[3][0]) if len(adc_meas) > 3 and len(adc_meas[3]) > 0 else 0
        vrefn = int(adc_meas[4][0]) if len(adc_meas) > 4 and len(adc_meas[4]) > 0 else 0

        status = result_dict.get(f"adc{asic:02d}_status", "")

        data_rows.append([
            f"{asic}",
            f"{vcmi}",
            f"{vcmo}",
            f"{vrefp}",
            f"{vrefn}",
            status
        ])

    data_rows.append([])

    # ===== TIMING INFORMATION =====
    data_rows.append(["Test Performance & Timing"])
    data_rows.append(["Phase", "Duration (s)", "Percentage (%)", "Status", "Max Allowed (s)"])

    timing_dict = result_dict.get("timing_dict", {})
    total_time = result_dict.get("total_test_time", 0)

    for phase_name, duration in timing_dict.items():
        percentage = (duration / total_time * 100) if total_time > 0 else 0
        status = ""  # Will be filled by threshold check
        data_rows.append([
            phase_name,
            f"{duration:.2f}",
            f"{percentage:.1f}",
            status,
            "See config"
        ])

    data_rows.append(["TOTAL", f"{total_time:.2f}", "100.0", "", ""])
    data_rows.append([])

    # ===== TEST STATUS SUMMARY =====
    data_rows.append(["Test Status Summary"])
    data_rows.append(["Test Phase", "Status", "Duration (s)"])
    data_rows.append(["SEOFF Mode Power Test", result_dict.get("seoff_test_status", "UNKNOWN"), f"{timing_dict.get('05_SEOFF_Test', 0):.1f}"])
    data_rows.append(["SEON (SDC) Mode Power Test", result_dict.get("seon_test_status", "UNKNOWN"), f"{timing_dict.get('06_SEON_Test', 0):.1f}"])
    data_rows.append(["DIFF Mode Power Test", result_dict.get("diff_test_status", "UNKNOWN"), f"{timing_dict.get('07_DIFF_Test', 0):.1f}"])
    data_rows.append(["Data Acquisition & Analysis", result_dict.get("data_acq_status", "UNKNOWN"), f"{timing_dict.get('08_Data_Acquisition', 0):.1f}"])
    data_rows.append([])

    # ===== CONFIGURATION INFORMATION =====
    data_rows.append(["FEMB Configuration"])
    data_rows.append(["Parameter", "Value"])
    data_rows.append(["FE Configuration", result_dict.get("FE_CFG", "")])
    data_rows.append(["ADC Configuration 0", result_dict.get("ADC_CFG0", "")])
    data_rows.append(["ADC Configuration 1", result_dict.get("ADC_CFG1", "")])
    data_rows.append(["CD FE Pulse", result_dict.get("CD_FE_pulse", "")])
    data_rows.append([])

    # ===== ERROR LOG (if any) =====
    errors = result_dict.get("error_log", [])
    if errors:
        data_rows.append(["Error Log"])
        data_rows.append(["Timestamp", "Error Type", "Description"])
        for error in errors:
            data_rows.append([
                error.get("timestamp", ""),
                error.get("type", ""),
                error.get("description", "")
            ])
        data_rows.append([])

    # ===== NOTES =====
    data_rows.append(["Notes"])
    data_rows.append([result_dict.get("Note", "")])
    data_rows.append([])
    data_rows.append(["Generated by DUNE WIB QC System - Test0401"])
    data_rows.append([f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])

    # Write to CSV file
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data_rows)

    print(f"CSV file saved to: {csv_filename}")
    return csv_filename


def export_reception_checkout_to_csv(log_dict, csv_filename=None):
    """
    Export Reception Checkout results to CSV

    Args:
        log_dict: Dictionary containing reception checkout results
        csv_filename: Optional custom filename

    Returns:
        str: Path to the saved CSV file
    """
    if csv_filename is None:
        wib_id = log_dict.get("WIB QR ID", "Unknown").replace("/", "-")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"report/Reception_Checkout_{wib_id}_{timestamp}.csv"

    data_rows = []

    # Header
    data_rows.append(["DUNE WIB Quality Control - Reception Checkout (Test00)"])
    data_rows.append([])
    data_rows.append(["Test Information"])
    data_rows.append(["Parameter", "Value", "Status", "Threshold"])
    data_rows.append(["WIB QR ID", log_dict.get("WIB QR ID", ""), "", ""])
    data_rows.append(["Tester Name", log_dict.get("Tester Name", ""), "", ""])
    data_rows.append(["Test Date", log_dict.get("date01", ""), "", ""])
    data_rows.append(["Total Time", f"{log_dict.get('Time_Consumption', 0)}", "seconds", ""])
    data_rows.append([])

    # Test Steps
    data_rows.append(["Inspection Steps"])
    data_rows.append(["Step", "Description", "Status", "Timestamp"])
    data_rows.append(["1", "Component Inspection", log_dict.get("Component Inspection", ""), log_dict.get("item1_date", "")])
    data_rows.append(["2", "LTpowerPlay Configuration", log_dict.get("LTpowerPlay", ""), log_dict.get("item2_date", "")])
    data_rows.append(["3", "Initial Power Check", "Completed", log_dict.get("Power Check Date", "")])
    data_rows.append(["4", "Front Panel Installation", log_dict.get("Front_Panel", ""), log_dict.get("item3_date", "")])
    data_rows.append([])

    # Power Check Data
    data_rows.append(["Power Check Measurements"])
    data_rows.append(["Channel", "Current (A)", "Status", "Min (A)", "Max (A)"])
    data_rows.append(["Channel 1", f"{log_dict.get('Power Check channel 1', 0):.3f}", "", "0.5", "2.0"])
    data_rows.append(["Channel 2", f"{log_dict.get('Power Check channel 2', 0):.3f}", "", "0.5", "2.0"])
    data_rows.append([])

    data_rows.append(["Generated by DUNE WIB QC System - Test00"])
    data_rows.append([f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])

    # Write CSV
    os.makedirs(os.path.dirname(csv_filename) if os.path.dirname(csv_filename) else ".", exist_ok=True)
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data_rows)

    print(f"CSV file saved to: {csv_filename}")
    return csv_filename
