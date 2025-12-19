# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description:
Created Time: 3/20/2019 4:50:34 PM
Last modified: 10/21/2022 5:02:04 PM

"""

import numpy as np
import sys
import os
import string
import time
from datetime import datetime
import struct
import matplotlib.pyplot as plt
import h5py
import datetime
import base64


def generate_report(result_dict):
    """Generate HTML test report for FEMB Checkout Test"""
    print("Generating HTML test report...")
    import pickle

    # Calculate power consumption for all modes
    def calc_power(pwr_data):
        """Calculate total power from power rail data"""
        if not pwr_data or len(pwr_data) < 5:
            return 0.0
        # pwr_data format: [(V, I), (V, I), (V, I), skip[3], (V, I)]
        p_fe = pwr_data[0][0] * pwr_data[0][1] if len(pwr_data[0]) >= 2 else 0
        p_adc = pwr_data[1][0] * pwr_data[1][1] if len(pwr_data[1]) >= 2 else 0
        p_cd = pwr_data[2][0] * pwr_data[2][1] if len(pwr_data[2]) >= 2 else 0
        p_bias = pwr_data[4][0] * pwr_data[4][1] if len(pwr_data[4]) >= 2 else 0
        return p_fe + p_adc + p_cd + p_bias

    # Get power measurements for all three modes
    pwr_seoff = result_dict.get("power_vfe_meas", [(0,0)])
    pwr_sdc = result_dict.get("power_vfe_meas_sdc", [(0,0)])
    pwr_diff = result_dict.get("power_vfe_meas_diff", [(0,0)])

    # Encode response.png as base64 for embedding
    response_png_path = result_dict.get("response.png", "")
    img_base64 = ""
    if response_png_path and os.path.exists(response_png_path):
        with open(response_png_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Get timing information
    timing_dict = result_dict.get("timing_dict", {})
    total_time = result_dict.get("total_test_time", 0)

    # Get test status
    seoff_status = result_dict.get("seoff_test_status", "UNKNOWN")
    seon_status = result_dict.get("seon_test_status", "UNKNOWN")
    diff_status = result_dict.get("diff_test_status", "UNKNOWN")
    data_status = result_dict.get("data_acq_status", "UNKNOWN")

    # Overall test status
    overall_status = "PASS" if all(s == "PASS" for s in [seoff_status, seon_status, diff_status, data_status]) else "FAIL"

    # Build HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FEMB#{result_dict["FEMB_SN"]} Checkout Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .header .status {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 18px;
            margin-top: 10px;
        }}
        .status.pass {{
            background: #10b981;
        }}
        .status.fail {{
            background: #ef4444;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
            border-radius: 8px;
            overflow: hidden;
        }}
        .section-header {{
            background: #f3f4f6;
            padding: 15px 20px;
            border-left: 4px solid #667eea;
            font-size: 20px;
            font-weight: bold;
            color: #1f2937;
        }}
        .section-content {{
            padding: 20px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .info-item {{
            padding: 12px;
            background: #f9fafb;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }}
        .info-label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .info-value {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #e5e7eb;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        tr:nth-child(even) {{
            background: #f9fafb;
        }}
        .power-comparison {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        .power-card {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border: 2px solid #e5e7eb;
            transition: transform 0.2s;
        }}
        .power-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }}
        .power-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        .power-value {{
            font-size: 32px;
            font-weight: bold;
            color: #1f2937;
            margin: 10px 0;
        }}
        .power-unit {{
            font-size: 16px;
            color: #6b7280;
        }}
        .test-status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .test-status.pass {{
            background: #d1fae5;
            color: #065f46;
        }}
        .test-status.fail {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .error-cell {{
            background: #fee2e2 !important;
            color: #991b1b !important;
            font-weight: bold;
        }}
        .warning-icon {{
            color: #dc2626;
            margin-right: 4px;
        }}
        .timing-bar {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}
        .timing-label {{
            min-width: 220px;
            font-weight: 500;
        }}
        .timing-progress {{
            flex: 1;
            height: 24px;
            background: #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            margin: 0 15px;
        }}
        .timing-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
        .timing-value {{
            min-width: 100px;
            text-align: right;
            font-weight: 600;
        }}
        .waveform-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .waveform-container img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .footer {{
            background: #f3f4f6;
            padding: 20px;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FEMB #{result_dict["FEMB_SN"]} Checkout Test Report</h1>
            <div class="status {overall_status.lower()}">{overall_status}</div>
        </div>

        <div class="content">
            <!-- Test Information Section -->
            <div class="section">
                <div class="section-header">Test Information</div>
                <div class="section-content">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">FEMB ID</div>
                            <div class="info-value">{result_dict["FEMB_SN"]}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Date & Time</div>
                            <div class="info-value">{result_dict["datetime"].strftime("%Y-%m-%d %H:%M:%S")}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Tester</div>
                            <div class="info-value">{result_dict["Tester"]}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Temperature</div>
                            <div class="info-value">{result_dict["Env"]}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Input Capacitor (Cd)</div>
                            <div class="info-value">{result_dict["Cd"]}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">WIB TCP Version</div>
                            <div class="info-value">0x{result_dict["WIB_TCP_FW_ver"]:02x}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">WIB UDP Version</div>
                            <div class="info-value">0x{result_dict["WIB_UDP_FW_ver"]:02x}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Total Test Time</div>
                            <div class="info-value">{total_time:.1f}s</div>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Note</div>
                        <div class="info-value">{result_dict["Note"]}</div>
                    </div>
                </div>
            </div>

            <!-- Test Status Section -->
            <div class="section">
                <div class="section-header">Test Status Summary</div>
                <div class="section-content">
                    <table>
                        <tr>
                            <th>Test Phase</th>
                            <th>Status</th>
                            <th>Duration</th>
                        </tr>
                        <tr>
                            <td>SEOFF Mode Power Test</td>
                            <td><span class="test-status {seoff_status.lower()}">{seoff_status}</span></td>
                            <td>{timing_dict.get('05_SEOFF_Test', 0):.1f}s</td>
                        </tr>
                        <tr>
                            <td>SEON (SDC) Mode Power Test</td>
                            <td><span class="test-status {seon_status.lower()}">{seon_status}</span></td>
                            <td>{timing_dict.get('06_SEON_Test', 0):.1f}s</td>
                        </tr>
                        <tr>
                            <td>DIFF Mode Power Test</td>
                            <td><span class="test-status {diff_status.lower()}">{diff_status}</span></td>
                            <td>{timing_dict.get('07_DIFF_Test', 0):.1f}s</td>
                        </tr>
                        <tr>
                            <td>Data Acquisition & Analysis</td>
                            <td><span class="test-status {data_status.lower()}">{data_status}</span></td>
                            <td>{timing_dict.get('08_Data_Acquisition', 0):.1f}s</td>
                        </tr>
                    </table>
                </div>
            </div>"""

    # Add power consumption comparison section
    html_content += f"""
            <!-- Power Consumption Comparison -->
            <div class="section">
                <div class="section-header">Power Consumption Comparison (All Modes)</div>
                <div class="section-content">
                    <div class="power-comparison">
                        <div class="power-card">
                            <h3>SEOFF Mode</h3>
                            <div class="power-value">{calc_power([result_dict.get("power_vfe_meas", (0,0)), result_dict.get("power_vadc_meas", (0,0)), result_dict.get("power_vcd_meas", (0,0)), None, result_dict.get("power_bias_meas", (0,0))]):.3f}</div>
                            <div class="power-unit">Watts</div>
                        </div>
                        <div class="power-card">
                            <h3>SEON (SDC) Mode</h3>
                            <div class="power-value">{calc_power([result_dict.get("power_vfe_meas_sdc", (0,0)), result_dict.get("power_vadc_meas_sdc", (0,0)), result_dict.get("power_vcd_meas_sdc", (0,0)), None, result_dict.get("power_bias_meas_sdc", (0,0))]):.3f}</div>
                            <div class="power-unit">Watts</div>
                        </div>
                        <div class="power-card">
                            <h3>DIFF Mode</h3>
                            <div class="power-value">{calc_power([result_dict.get("power_vfe_meas_diff", (0,0)), result_dict.get("power_vadc_meas_diff", (0,0)), result_dict.get("power_vcd_meas_diff", (0,0)), None, result_dict.get("power_bias_meas_diff", (0,0))]):.3f}</div>
                            <div class="power-unit">Watts</div>
                        </div>
                    </div>

                    <table>
                        <tr>
                            <th>Power Rail</th>
                            <th>V_set (V)</th>
                            <th colspan="3">SEOFF Mode</th>
                            <th colspan="3">SEON (SDC) Mode</th>
                            <th colspan="3">DIFF Mode</th>
                        </tr>
                        <tr>
                            <th></th>
                            <th></th>
                            <th>V_meas (V)</th>
                            <th>I_meas (A)</th>
                            <th>P_meas (W)</th>
                            <th>V_meas (V)</th>
                            <th>I_meas (A)</th>
                            <th>P_meas (W)</th>
                            <th>V_meas (V)</th>
                            <th>I_meas (A)</th>
                            <th>P_meas (W)</th>
                        </tr>"""

    # Add power rail data rows
    rails = [
        ("LArASIC", "power_vfe_ref", "power_vfe_meas", "power_vfe_meas_sdc", "power_vfe_meas_diff"),
        ("ColdADC", "power_vadc_ref", "power_vadc_meas", "power_vadc_meas_sdc", "power_vadc_meas_diff"),
        ("COLDATA", "power_vcd_ref", "power_vcd_meas", "power_vcd_meas_sdc", "power_vcd_meas_diff"),
        ("BIAS", "power_bias_ref", "power_bias_meas", "power_bias_meas_sdc", "power_bias_meas_diff")
    ]

    # Get detailed check results
    detailed_checks = result_dict.get("detailed_checks", {})

    rail_map = {"LArASIC": "FE", "ColdADC": "ADC", "COLDATA": "CD", "BIAS": "BIAS"}

    for rail_name, ref_key, seoff_key, sdc_key, diff_key in rails:
        ref_v = result_dict.get(ref_key, (0, 0))[0]

        seoff_v, seoff_i = result_dict.get(seoff_key, (0, 0))
        seoff_p = seoff_v * seoff_i

        sdc_v, sdc_i = result_dict.get(sdc_key, (0, 0))
        sdc_p = sdc_v * sdc_i

        diff_v, diff_i = result_dict.get(diff_key, (0, 0))
        diff_p = diff_v * diff_i

        # Check for errors in each mode
        rail_key = rail_map[rail_name]

        # SEOFF errors
        seoff_v_error = not detailed_checks.get("SEOFF", {}).get(rail_key, {}).get("voltage", {}).get("pass", True)
        seoff_i_error = not detailed_checks.get("SEOFF", {}).get(rail_key, {}).get("current", {}).get("pass", True)
        seoff_v_class = ' class="error-cell"' if seoff_v_error else ''
        seoff_i_class = ' class="error-cell"' if seoff_i_error else ''
        seoff_p_class = ' class="error-cell"' if (seoff_v_error or seoff_i_error) else ''

        # SEON errors
        seon_v_error = not detailed_checks.get("SEON", {}).get(rail_key, {}).get("voltage", {}).get("pass", True)
        seon_i_error = not detailed_checks.get("SEON", {}).get(rail_key, {}).get("current", {}).get("pass", True)
        seon_v_class = ' class="error-cell"' if seon_v_error else ''
        seon_i_class = ' class="error-cell"' if seon_i_error else ''
        seon_p_class = ' class="error-cell"' if (seon_v_error or seon_i_error) else ''

        # DIFF errors
        diff_v_error = not detailed_checks.get("DIFF", {}).get(rail_key, {}).get("voltage", {}).get("pass", True)
        diff_i_error = not detailed_checks.get("DIFF", {}).get(rail_key, {}).get("current", {}).get("pass", True)
        diff_v_class = ' class="error-cell"' if diff_v_error else ''
        diff_i_class = ' class="error-cell"' if diff_i_error else ''
        diff_p_class = ' class="error-cell"' if (diff_v_error or diff_i_error) else ''

        html_content += f"""
                        <tr>
                            <td><strong>{rail_name}</strong></td>
                            <td>{ref_v:.3f}</td>
                            <td{seoff_v_class}>{seoff_v:.3f}</td>
                            <td{seoff_i_class}>{seoff_i:.3f}</td>
                            <td{seoff_p_class}>{seoff_p:.3f}</td>
                            <td{seon_v_class}>{sdc_v:.3f}</td>
                            <td{seon_i_class}>{sdc_i:.3f}</td>
                            <td{seon_p_class}>{sdc_p:.3f}</td>
                            <td{diff_v_class}>{diff_v:.3f}</td>
                            <td{diff_i_class}>{diff_i:.3f}</td>
                            <td{diff_p_class}>{diff_p:.3f}</td>
                        </tr>"""

    html_content += """
                    </table>
                </div>
            </div>"""

    # Add timing section
    if timing_dict:
        html_content += """
            <!-- Timing Performance -->
            <div class="section">
                <div class="section-header">Test Performance & Timing</div>
                <div class="section-content">"""

        for phase_name, duration in timing_dict.items():
            percentage = (duration / total_time * 100) if total_time > 0 else 0
            html_content += f"""
                    <div class="timing-bar">
                        <div class="timing-label">{phase_name.replace('_', ' ')}</div>
                        <div class="timing-progress">
                            <div class="timing-fill" style="width: {percentage}%">
                                {percentage:.1f}%
                            </div>
                        </div>
                        <div class="timing-value">{duration:.2f}s</div>
                    </div>"""

        html_content += f"""
                    <div class="timing-bar" style="margin-top: 20px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                        <div class="timing-label"><strong>TOTAL TEST TIME</strong></div>
                        <div class="timing-progress">
                            <div class="timing-fill" style="width: 100%; background: #10b981;">
                                100%
                            </div>
                        </div>
                        <div class="timing-value"><strong>{total_time:.2f}s</strong></div>
                    </div>
                </div>
            </div>"""

    # Add configuration section
    html_content += f"""
            <!-- FEMB Configuration -->
            <div class="section">
                <div class="section-header">FEMB Configuration</div>
                <div class="section-content">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">FE Configuration</div>
                            <div class="info-value" style="font-size: 14px;">{result_dict.get("FE_CFG", "N/A")}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">ADC Configuration 0</div>
                            <div class="info-value" style="font-size: 14px;">{result_dict.get("ADC_CFG0", "N/A")}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">ADC Configuration 1</div>
                            <div class="info-value" style="font-size: 14px;">{result_dict.get("ADC_CFG1", "N/A")}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">CD FE Pulse</div>
                            <div class="info-value" style="font-size: 14px;">{result_dict.get("CD_FE_pulse", "N/A")}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Monitoring Parameters -->
            <div class="section">
                <div class="section-header">Monitoring Parameters (ADC Voltage References)</div>
                <div class="section-content">
                    <table>
                        <tr>
                            <th>ASIC #</th>
                            <th>ADC VCMI (mV)</th>
                            <th>ADC VCMO (mV)</th>
                            <th>ADC VREFP (mV)</th>
                            <th>ADC VREFN (mV)</th>
                        </tr>"""

    for asic in [0, 4]:
        adc_meas = result_dict.get(f"ADC{asic:02d}_MeasRef", [None, (0,), (0,), (0,), (0,)])
        vcmi = int(adc_meas[1][0]) if len(adc_meas) > 1 and len(adc_meas[1]) > 0 else 0
        vcmo = int(adc_meas[2][0]) if len(adc_meas) > 2 and len(adc_meas[2]) > 0 else 0
        vrefp = int(adc_meas[3][0]) if len(adc_meas) > 3 and len(adc_meas[3]) > 0 else 0
        vrefn = int(adc_meas[4][0]) if len(adc_meas) > 4 and len(adc_meas[4]) > 0 else 0

        html_content += f"""
                        <tr>
                            <td>{asic}</td>
                            <td>{vcmi}</td>
                            <td>{vcmo}</td>
                            <td>{vrefp}</td>
                            <td>{vrefn}</td>
                        </tr>"""

    html_content += """
                    </table>
                </div>
            </div>"""

    # Add error log section if there are errors
    errors = result_dict.get("error_log", [])
    if errors:
        html_content += """
            <!-- Error Log -->
            <div class="section">
                <div class="section-header" style="border-left-color: #dc2626;">
                    <span class="warning-icon">⚠</span> Error Log
                </div>
                <div class="section-content">
                    <table>
                        <tr>
                            <th>Timestamp</th>
                            <th>Test Phase</th>
                            <th>Error Type</th>
                            <th>Description</th>
                        </tr>"""

        for error in errors:
            html_content += f"""
                        <tr>
                            <td>{error.get("timestamp", "")}</td>
                            <td>{error.get("phase", "")}</td>
                            <td style="color: #dc2626; font-weight: bold;">{error.get("type", "")}</td>
                            <td>{error.get("description", "")}</td>
                        </tr>"""

        html_content += """
                    </table>
                    <div style="margin-top: 15px; padding: 12px; background: #fef2f2; border-left: 4px solid #dc2626; border-radius: 4px; color: #991b1b;">
                        <strong>Note:</strong> The test continued to collect all data despite these errors. Please review and address all errors before approving this FEMB.
                    </div>
                </div>
            </div>"""

    # Add waveform section
    if img_base64:
        html_content += f"""
            <!-- Channel Response Waveforms -->
            <div class="section">
                <div class="section-header">Channel Response Waveforms</div>
                <div class="section-content">
                    <div class="waveform-container">
                        <img src="data:image/png;base64,{img_base64}" alt="Channel Response Waveforms">
                    </div>
                </div>
            </div>"""

    # Footer
    html_content += f"""
        </div>

        <div class="footer">
            Report generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            DUNE WIB Quality Control System | FEMB Checkout Test
            {' | <strong style="color: #dc2626;">ERRORS DETECTED - Review Required</strong>' if errors else ''}
        </div>
    </div>
</body>
</html>"""

    # Save HTML report
    html_filename = result_dict["save_dir"] + "result.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Save result_dict as pickle for backward compatibility
    with open(result_dict["save_dir"] + "result.bin", 'wb') as fp:
        pickle.dump(result_dict, fp)

    print(f"HTML report saved to: {{html_filename}}")
    print(f"Result data saved to: {{result_dict['save_dir']}}result.bin")

    return html_filename


def generate_report_pdf_old(result_dict):
    """OLD PDF VERSION - Kept for reference"""
    print("Generator the test report (OLD PDF)...")
    from fpdf import FPDF
    import pickle
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.alias_nb_pages()
    print("##### FEMB Checkout Test Report #####")
    pdf.add_page()
    pdf.set_font('Times', 'B', 20)
    pdf.cell(85)
    print(pdf.l_margin)
    pdf.l_margin = pdf.l_margin * 2
    pdf.cell(30, 5, 'FEMB#{} Checkout Test Report'.format(result_dict["FEMB_SN"]), 0, 1, 'C')
    pdf.ln(2)

    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'FEMB ID = {}'.format(result_dict["FEMB_SN"]), 0, 1)

    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Date&Time: %s' % result_dict["datetime"].strftime("%Y-%m-%d %H:%M:%S"), 0, 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Tester: {}'.format(result_dict["Tester"]), 0, 1)

    pdf.cell(30, 5, 'WIB_TCP_Version: 0x{:02x}'.format(result_dict["WIB_TCP_FW_ver"]), 0, 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'WIB_UDP_Version: 0x{:02x}'.format(result_dict["WIB_UDP_FW_ver"]), 0, 1)

    pdf.cell(30, 5, 'Temperature: {}'.format(result_dict["Env"]), 0, 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(result_dict["Cd"]), 0, 1)
    pdf.cell(30, 5, 'Note: {}'.format(result_dict["Note"][0:80]), 0, 1)
    #    for i in range((len(result_dict["Note"])//70) + 1):
    #        if i == 0:
    #            pdf.cell(30, 5, 'Note: {}'.format(result_dict["Note"][i*70:(i+1)*70]), 0, 1)
    #        else:
    #            pdf.cell(30, 5, '      {}'.format(result_dict["Note"][i*70:(i+1)*70]), 0, 1)

    print("# FEMB configuration #")
    pdf.ln(2)
    pdf.cell(70)
    pdf.cell(30, 5, 'FEMB Configuration', 0, 1, 'C')
    pdf.cell(30, 5, 'FE_CFG: {}'.format(result_dict["FE_CFG"]), 0, 1)
    pdf.cell(30, 5, 'ADC_CFG: {}'.format(result_dict["ADC_CFG0"]), 0, 1)
    pdf.cell(30, 5, 'ADC_CFG: {}'.format(result_dict["ADC_CFG1"]), 0, 1)
    pdf.cell(30, 5, 'CD_FE_pulse: {}'.format(result_dict["CD_FE_pulse"]), 0, 1)

    # Generate Power Check table
    print("# Generate Power Check table")
    data = [["Power rail", "V_set /V", "V_meas /V", "I_meas /A", "P_meas /W"],
            ["LArASIC", 0, 0, 0, 0],
            ["ColdADC", 0, 0, 0, 0],
            ["COLDATA", 0, 0, 0, 0],
            [" BIAS  ", 0, 0, 0, 0]
            ]
    data[1][1] = result_dict["power_vfe_ref"][0]
    data[1][2] = result_dict["power_vfe_meas"][0]
    data[1][3] = result_dict["power_vfe_meas"][1]
    data[1][4] = result_dict["power_vfe_meas"][0] * result_dict["power_vfe_meas"][1]
    data[2][1] = result_dict["power_vadc_ref"][0]
    data[2][2] = result_dict["power_vadc_meas"][0]
    data[2][3] = result_dict["power_vadc_meas"][1]
    data[2][4] = result_dict["power_vadc_meas"][0] * result_dict["power_vadc_meas"][1]
    data[3][1] = result_dict["power_vcd_ref"][0]
    data[3][2] = result_dict["power_vcd_meas"][0]
    data[3][3] = result_dict["power_vcd_meas"][1]
    data[3][4] = result_dict["power_vcd_meas"][0] * result_dict["power_vcd_meas"][1]
    data[4][1] = result_dict["power_bias_ref"][0]
    data[4][2] = result_dict["power_bias_meas"][0]
    data[4][3] = result_dict["power_bias_meas"][1]
    data[4][4] = result_dict["power_bias_meas"][0] * result_dict["power_bias_meas"][1]
    femb_pwr_con = data[1][4] + data[2][4] + data[3][4] + data[4][4]

    pdf.ln(2)
    pdf.cell(70)
    pdf.cell(30, 5, 'FE SE OFF Interface Power Consumption (including cable dissipation) = {:0.3f}W'.format(femb_pwr_con), 0, 1, 'C')
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 5
    pdf.set_font('Times', '', 12)
    th = pdf.font_size  # print ("# Text height is the same as current font size")
    pdf.ln(0.4 * th)
    for j in range(len(data)):
        for i in range(len(data[j])):
            if j == 0 or i == 0:
                pdf.cell(col_width, 2 * th, "{}".format(data[j][i]), border=1, align='C')
            else:
                pdf.cell(col_width, 2 * th, "{:0.3f}".format(data[j][i]), border=1, align='C')
        pdf.ln(2 * th)
    pdf.ln(2)
















    #
    #
    # # Generate Power Check table
    # print("# Generate Power Check table [SDC mode]")
    # data = [["Power rail", "V_set /V", "V_meas /V", "I_meas /A", "P_meas /W"],
    #         ["LArASIC", 0, 0, 0, 0],
    #         ["ColdADC", 0, 0, 0, 0],
    #         ["COLDATA", 0, 0, 0, 0],
    #         [" BIAS  ", 0, 0, 0, 0]
    #         ]
    # data[1][1] = result_dict["power_vfe_ref"][0]
    # data[1][2] = result_dict["power_vfe_meas_diff"][0]
    # data[1][3] = result_dict["power_vfe_meas_diff"][1]
    # data[1][4] = result_dict["power_vfe_meas_diff"][0] * result_dict["power_vfe_meas_diff"][1]
    # data[2][1] = result_dict["power_vadc_ref"][0]
    # data[2][2] = result_dict["power_vadc_meas_diff"][0]
    # data[2][3] = result_dict["power_vadc_meas_diff"][1]
    # data[2][4] = result_dict["power_vadc_meas_diff"][0] * result_dict["power_vadc_meas_diff"][1]
    # data[3][1] = result_dict["power_vcd_ref"][0]
    # data[3][2] = result_dict["power_vcd_meas_diff"][0]
    # data[3][3] = result_dict["power_vcd_meas_diff"][1]
    # data[3][4] = result_dict["power_vcd_meas_diff"][0] * result_dict["power_vcd_meas_diff"][1]
    # data[4][1] = result_dict["power_bias_ref"][0]
    # data[4][2] = result_dict["power_bias_meas_diff"][0]
    # data[4][3] = result_dict["power_bias_meas_diff"][1]
    # data[4][4] = result_dict["power_bias_meas_diff"][0] * result_dict["power_bias_meas_diff"][1]
    # femb_pwr_con = data[1][4] + data[2][4] + data[3][4] + data[4][4]
    #
    # pdf.ln(2)
    # pdf.cell(70)
    # pdf.cell(30, 5, 'FE DIFF Interface Power Consumption (including cable dissipation) = {:0.3f}W'.format(femb_pwr_con), 0, 1, 'C')
    # epw = pdf.w - 2 * pdf.l_margin
    # col_width = epw / 5
    # pdf.set_font('Times', '', 12)
    # th = pdf.font_size  # print ("# Text height is the same as current font size")
    # pdf.ln(0.4 * th)
    # for j in range(len(data)):
    #     for i in range(len(data[j])):
    #         if j == 0 or i == 0:
    #             pdf.cell(col_width, 2 * th, "{}".format(data[j][i]), border=1, align='C')
    #         else:
    #             pdf.cell(col_width, 2 * th, "{:0.3f}".format(data[j][i]), border=1, align='C')
    #     pdf.ln(2 * th)
    # pdf.ln(2)







    # Generate Monitoring Check table
    asic = 0
    print("# Generate Monitoring Check table")
    data = [["ASIC# ", "FE Vref", "FE T", "ADC VCMI", "ADC VCMO", "ADC VREFP", "ADC VREFN", ],
            ["{}".format(0), 0, 0, 0, 0, 0, 0],
            ["{}".format(4), 0, 0, 0, 0, 0, 0],
            ]
    asic = 0
    # data[1][1] = int(result_dict["Mon_LArASIC{:02d}_BGR".format(asic)][0])
    # data[1][2] = int(result_dict["Mon_LArASIC{:02d}_Temperature".format(asic)][0])
    data[1][3] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][1][0])
    data[1][4] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][2][0])
    data[1][5] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][3][0])
    data[1][6] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][4][0])

    asic = 4
    # data[2][1] = int(result_dict["Mon_LArASIC{:02d}_BGR".format(asic)][0])
    # data[2][2] = int(result_dict["Mon_LArASIC{:02d}_Temperature".format(asic)][0])
    data[2][3] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][1][0])
    data[2][4] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][2][0])
    data[2][5] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][3][0])
    data[2][6] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][4][0])

    pdf.ln(1)
    pdf.cell(70)
    pdf.cell(30, 5, 'Monitoring path for FE-ADC#0 (unit: mV)', 0, 1, 'C')
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 7
    pdf.set_font('Times', '', 12)
    th = pdf.font_size  # print ("# Text height is the same as current font size")
    pdf.ln(0.4 * th)
    for j in range(len(data)):
        for i in range(len(data[j])):
            if j == 0 or i == 0:
                pdf.cell(col_width, 2 * th, "{}".format(data[j][i]), border=1, align='C')
            else:
                pdf.cell(col_width, 2 * th, "{:0.3f}".format(data[j][i]), border=1, align='C')
        pdf.ln(2 * th)
    pdf.ln(2)
    #######################################################
    pdf.image(result_dict["response.png"], 10, 160, 190)

    filename = result_dict["save_dir"] + "result.pdf"
    pdf.output(filename, 'F')
    pdf.close()

    with open(result_dict["save_dir"] + "result.bin", 'wb') as fp:
        pickle.dump(result_dict, fp)


def data_ana(femb_data):
    chn_rmss = []
    chn_peds = []
    chn_pkps = []
    chn_pkns = []
    chn_onewfs = []
    chn_avgwfs = []

    for chipi in range(8):
        plsn = (len(femb_data[chipi][0]) // 512) - 10
        if plsn > 100:
            psln = 100

        for i in range(plsn):
            if i == 0:
                avg_wf = np.array(femb_data[chipi][0][0:512]) & 0xffff
            else:
                avg_wf = avg_wf + (np.array(femb_data[chipi][0][512 * i:512 * i + 512]) & 0xffff)
        avg_wf = avg_wf // plsn
        posp = np.where(avg_wf == np.max(avg_wf))[0][0] + 512 - 50

        for chn in range(16):
            peddata = []
            chndata = femb_data[chipi][chn][posp:]
            one_wf = chndata[0:512]
            for i in range(plsn):
                peddata += chndata[100 + 512 * i: 270 + 512 * i]
                if i == 0:
                    avg_wf = np.array(chndata[0:512]) & 0xffff
                else:
                    avg_wf = avg_wf + (np.array(chndata[512 * i:512 * i + 512]) & 0xffff)
            avg_wf = avg_wf // plsn

            rms = np.std(peddata)
            ped = int(np.mean(peddata))
            peakp = np.max(avg_wf)
            peakn = np.min(avg_wf)

            chn_rmss.append(rms)
            chn_peds.append(ped)
            chn_pkps.append(peakp)
            chn_pkns.append(peakn)
            chn_onewfs.append(one_wf)
            chn_avgwfs.append(avg_wf)
    return chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_onewfs, chn_avgwfs


def FEMB_SUB_PLOT(ax, x, y, title, xlabel, ylabel, color='b', marker='.', atwinx=False, ylabel_twx="", e=None):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (atwinx):
        ax.errorbar(x, y, e, marker=marker, color=color)
        y_min = int(np.min(y)) - 1000
        y_max = int(np.max(y)) + 1000
        ax.set_ylim([y_min, y_max])
        ax2 = ax.twinx()
        ax2.set_ylabel(ylabel_twx)
        ax2.set_ylim([int((y_min / 16384.0) * 2048), int((y_max / 16384.0) * 2048)])
    else:
        ax.plot(x, y, marker=marker, color=color)


def FEMB_PLOT(chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_onewfs, chn_avgwfs, save_dir):
    #    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10, 6))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    plt.ylim(0, 5)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
    chns = range(128)
    FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number",
                  ylabel="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_pkps, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number",
                  ylabel="ADC / bin", color='b', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_pkns, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number",
                  ylabel="ADC / bin", color='g', marker='.')
    for chni in chns:
        if chni != 500:
            ts = 300
            x = (np.arange(125)) * 0.5
            y1 = chn_onewfs[chni]
            y3 = chn_onewfs[chni][25:75] + chn_onewfs[chni][ts - 50:ts + 25]

            y4 = chn_onewfs[chni][25:75] + chn_onewfs[chni][ts - 50:ts + 25]

            # print(y1)
            # print(y3)
            # print(y4)
            FEMB_SUB_PLOT(ax3, x, y3, title="Waveform Overlap (1 cycle)", xlabel="Time", ylabel="ADC /bin",
                          color='C%d' % (chni % 9))
            FEMB_SUB_PLOT(ax4, x, y4, title="Averaging(100 Cycles) Waveform Overlap", xlabel="Time",
                          ylabel="ADC /bin", color='C%d' % (chni % 9))

    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
    fn = save_dir + "response.png"
    plt.savefig(fn)
    plt.close()
    return fn


def FEMB_CHKOUT_Input(SN = '4', rootdir = 'D:/Warm_Integrated_Board/Report/'):
    tester = 'lke'
    femb_sn = SN # int(input("please input FEMB SN (000-999): "))
    env = 'RT'
    note = 'for WIB QC' #input("A short note (<80 letters):")
    ToyTPC = '0pF'
    save_dir = rootdir + "FEMB{}_{}_{}/".format(femb_sn, env, ToyTPC)
    if (os.path.exists(save_dir)):
        print("Folder exist, please check the entering infomation...")
        exit_en = "n"
        if ("Y" in exit_en) or ("y" in exit_en):
            input("hit any button and then 'Enter' to exit")
            exit()
        else:
            i = 0
            while (True):
                i = i + 1
                fd_new = save_dir[:-1] + "_R{:03d}/".format(i)
                if (os.path.exists(fd_new)):
                    pass
                else:
                    try:
                        os.makedirs(fd_new)
                    except OSError:
                        print("Error to create folder %s" % fd_new)
                        input("hit any button and then 'Enter' to exit")
                        sys.exit()
                    save_dir = fd_new
                    break
    else:
        try:
            os.makedirs(save_dir)
        except OSError:
            print("Error to create folder %s" % save_dir)
            input("hit any button and then 'Enter' to exit")
            sys.exit()
    return femb_sn, env, ToyTPC, save_dir, tester, note


def pwr_chk(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias, use_config=True):
    """
    Check power rail measurements against expected values

    Args:
        pwr_info: Power measurement data [(V, I), (V, I), (V, I), skip, (V, I)]
        v_fe, v_adc, v_cd, v_bias: Expected voltage values
        iref_fe, iref_adc, iref_cd, iref_bias: Reference current values
        use_config: Whether to use thresholds from config file (default: True)

    Returns:
        (int, dict): (overall_pass, detailed_results)
            overall_pass: 1 if all checks passed, 0 if any failed
            detailed_results: Dictionary with per-rail status and error messages
    """
    # Load thresholds from config if requested
    if use_config:
        try:
            import sys
            import os
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from config.test_thresholds import (
                VOLTAGE_TOLERANCE,
                CURRENT_THRESHOLDS,
                check_voltage_in_range,
                check_current_in_range
            )
        except ImportError:
            print("Warning: Could not load config/test_thresholds.py, using hardcoded values")
            use_config = False

    # Use hardcoded values if config not available
    if not use_config:
        VOLTAGE_TOLERANCE = 0.2
        CURRENT_THRESHOLDS = {
            "FE": {"tolerance": 0.1, "I_ref_alt": 0.63, "tolerance_alt": 0.1},
            "ADC": {"tolerance": 0.2},
            "CD": {"tolerance": 0.1},
            "BIAS": {"tolerance": 0.1}
        }

    pwr_en = 1
    detailed_results = {
        "FE": {"voltage": {"pass": True, "error": ""}, "current": {"pass": True, "error": ""}},
        "ADC": {"voltage": {"pass": True, "error": ""}, "current": {"pass": True, "error": ""}},
        "CD": {"voltage": {"pass": True, "error": ""}, "current": {"pass": True, "error": ""}},
        "BIAS": {"voltage": {"pass": True, "error": ""}, "current": {"pass": True, "error": ""}}
    }

    # Check voltages
    rails = [
        ("FE", v_fe, pwr_info[0][0], 0),
        ("ADC", v_adc, pwr_info[1][0], 1),
        ("CD", v_cd, pwr_info[2][0], 2),
        ("BIAS", v_bias, pwr_info[4][0], 4)
    ]

    for rail_name, v_set, v_meas, idx in rails:
        if abs(v_set - v_meas) > VOLTAGE_TOLERANCE:
            error_msg = f"V_set={v_set:.3f}V, V_meas={v_meas:.3f}V (tolerance: ±{VOLTAGE_TOLERANCE}V)"
            print(f"\033[31mPower rail for {rail_name}, {error_msg}, please check connection\033[0m")
            detailed_results[rail_name]["voltage"]["pass"] = False
            detailed_results[rail_name]["voltage"]["error"] = error_msg
            pwr_en = 0

    # Check currents
    current_checks = [
        ("FE", iref_fe, pwr_info[0][1], 0),
        ("ADC", iref_adc, pwr_info[1][1], 1),
        ("CD", iref_cd, pwr_info[2][1], 2),
        ("BIAS", iref_bias, pwr_info[4][1], 4)
    ]

    for rail_name, i_ref, i_meas, idx in current_checks:
        tolerance = CURRENT_THRESHOLDS[rail_name]["tolerance"]

        # Special handling for FE - check alternative reference
        if rail_name == "FE":
            i_ref_alt = CURRENT_THRESHOLDS["FE"].get("I_ref_alt", 0.63)
            tol_alt = CURRENT_THRESHOLDS["FE"].get("tolerance_alt", 0.1)

            if abs(i_ref - i_meas) > tolerance and abs(i_ref_alt - i_meas) > tol_alt:
                error_msg = f"I_ref={i_ref:.3f}A, I_meas={i_meas:.3f}A (tolerance: ±{tolerance}A, alt ref: {i_ref_alt:.3f}±{tol_alt}A)"
                print(f"\033[31mPower rail for {rail_name}, {error_msg}, please check connection\033[0m")
                detailed_results[rail_name]["current"]["pass"] = False
                detailed_results[rail_name]["current"]["error"] = error_msg
                pwr_en = 0
        else:
            if abs(i_ref - i_meas) > tolerance:
                error_msg = f"I_ref={i_ref:.3f}A, I_meas={i_meas:.3f}A (tolerance: ±{tolerance}A)"
                print(f"\033[31mPower rail for {rail_name}, {error_msg}, please check connection\033[0m")
                detailed_results[rail_name]["current"]["pass"] = False
                detailed_results[rail_name]["current"]["error"] = error_msg
                pwr_en = 0

    return pwr_en, detailed_results


def pwr_chk_old(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias):
    """OLD VERSION - kept for compatibility"""
    result, _ = pwr_chk(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias, use_config=False)
    return result


'''

tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()

now = datetime.datetime.now()
rootdir ="D:/Warm_Integrated_Board/Report/"

print ("Initial experiment start...")
result_dict ={} 
result_dict["datetime"] = now
result_dict["rootdir"] = rootdir

print("01")
ver = tcp.wib_ver()
print("011")   
if (ver[1] == 0x100):
    print ("TCP link built.")

result_dict["WIB_TCP_FW_ver"] = ver[1]
print("02")
longcable = False 
if longcable: 
    print ("Long cable is in use...")
    tcp.tcp_poke(addr=0x08, data=longcable)
    if (tcp.tcp_peek(addr=0x08) == longcable):
        pass
    else:
        print("Configuration for long cable is error, please check, exit anyway.")
        input ("hit any button and then 'Enter' to exit")
        exit()
else:
    print ("Short cable is in use...")
    tcp.tcp_poke(addr=0x08, data=longcable)
    if tcp.tcp_peek(addr=0x08) == longcable:
        pass
    else:
        print("Configuration for short cable is error, please check, exit anyway.")
        input ("hit any button and then 'Enter' to exit")
        exit()
print("03")
udpver = udp.read_reg_wib(reg=0x100)
if (udpver == 0x1A5):
    print ("UDP link built.")
result_dict["WIB_UDP_FW_ver"] = udpver

femb = int(input("FEMB (0-3): "))
#femb=0
if femb == 0:
    tcp.link_cs = 0
elif femb == 1:
    tcp.link_cs = 2
elif femb == 2:
    tcp.link_cs = 4
elif femb == 3:
    tcp.link_cs = 6
print("04")
femb_sn, env, toytpc, save_dir, tester, note = FEMB_CHKOUT_Input(rootdir)
result_dict["FEMB_SN"] = femb_sn
result_dict["Env"] = env 
result_dict["Cd"] = toytpc 
result_dict["save_dir"] = save_dir 
result_dict["Tester"] =  tester
result_dict["Note"] = note 

################################################################################################
##power consumption
print ("Turn on FEMB on WIB slot {}".format(femb))
v_fe=3.0
v_adc=3.5
v_cd=2.8
v_bias = 5.0
iref_fe=0.42
iref_adc=1.29
iref_cd=0.18
iref_bias =0.05

tcp.femb_pwr_set(femb=femb, pwr_on=0)
time.sleep(5)

tcp.femb_pwr_set(femb=femb, pwr_on=1, v_fe=v_fe, v_adc=v_adc, v_cd=v_cd)
time.sleep(2)
tcp.set_fe_board(sts=0,snc=0,sg0=0,sg1=0,st0=1,st1=1,swdac=0,dac=0x0)
tcp.femb_cfg()
time.sleep(2)
for i in range(5):
    pwr_info = tcp.femb_pwr_rd(femb=femb)
    time.sleep(.2)
pwr_info = tcp.femb_pwr_rd(femb=femb)
time.sleep(1)
pwr_info = tcp.femb_pwr_rd(femb=femb)
pwr_info = tcp.femb_pwr_rd(femb=femb)
pwr_info = tcp.femb_pwr_rd(femb=femb)
pwr_en = pwr_chk(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias)
if pwr_en ==0 :
    tcp.femb_pwr_set(femb=femb, pwr_on=0)
    input ("hit any button and then 'Enter' to exit")
    exit()
    print ("Turn FEMB off and exit...")
else:
    print ("FEMB power consumption is in the normal range")
result_dict["power_vfe_ref"] =  (v_fe,  iref_fe)
result_dict["power_vadc_ref"] = (v_adc, iref_adc)
result_dict["power_vcd_ref"] =  (v_cd,  iref_cd,)
result_dict["power_bias_ref"] = (v_bias,iref_bias)

##########1#####################################################################################
#FEMB configuration: 14mV/fC, 200mV BL, 2.0us, single-ended, 500pA, ASICDAC=0x10, Cali_enable, SDC off,
result_dict["FE_CFG"] = "14mV/fC, 900mV BL, 2.0us, SE_OFF, 500pA, ASIC_CAL, ASICDAC=0x10"
result_dict["ADC_CFG0"] = "CMOS reference set to default, Auto Calibration, "  
result_dict["ADC_CFG1"] = "SE, SDC off, offset_binary_format, Auto Calibration, "  
result_dict["CD_FE_pulse"] = "500 samples/pulse, CD Addr0x06:0x30,0x07:0x00, 0x08:0x38, 0x09:0x80"  

print ("Measure monitoring parameters")
tcp.set_fe_board(sts=0,snc=0,sg0=0,sg1=0,st0=1,st1=1,swdac=0,dac=0x0)
tcp.femb_cfg()
#for asic in range(8):
for asic in [0, 4]:
    print ("Measure ASIC {}".format(asic))
    tmp = tcp.femb_adc_mon_cs(femb_no=femb, adc_no=asic)
    result_dict["ADC{:02d}_SetRef".format(asic)] = tmp[1]
    result_dict["ADC{:02d}_MeasRef".format(asic)] = tmp[0]
    tmp = tcp.femb_fe_mon_cs(femb_no=femb, ext_lemo=0, rst_fe=1, mon_type=2, mon_chip = asic)
    result_dict["Mon_LArASIC{:02d}_BGR".format(asic)] = tmp
    tmp = tcp.femb_fe_mon_cs(femb_no=femb, ext_lemo=0, rst_fe=1, mon_type=1, mon_chip = asic)
    result_dict["Mon_LArASIC{:02d}_Temperature".format(asic)] = tmp
#    print (result_dict["ADC{:02d}_MeasRef".format(asic)]) 


print ("Start FEMB configuration: 14mV/fC, 900mV BL, 2.0us, single-ended, 500pA, ASICDAC=0x10, Cali_enable, SDC off")
tcp.set_fe_reset()
tcp.set_fe_board(sts=0,snc=0,sg0=0,sg1=0,st0=1,st1=1,swdac=1,dac=0x10)
tcp.femb_cfg()

#check channel response
print ("Check channel response")
#tcp.cd_fe_cali()
#tcp.fc_act_cal() #enalbe LArASIC calibration

hdf_fp = save_dir + "rawdata.h5"
result_dict["H5"] = hdf_fp

udp.write_reg_wib_checked(2, 1)
time.sleep(1)
print("Enable UDP data stream")
udp.write_reg_wib_checked(2, 1)
time.sleep(1)
ASICs = 8

#to avoid potential cache data in PC
asic=0
wib_asic = (((femb << 16) & 0x000F0000) + ((asic << 8) & 0xFF00))
udp.write_reg_wib_checked(7, 0x80000000)
udp.write_reg_wib_checked(7, wib_asic | 0x80000000)
udp.write_reg_wib_checked(7, wib_asic)
time.sleep(0.01)
data = udp.get_rawdata_packets(val=1000)

femb_data = []
dset = [ [] for i in range(128)]
while True:
    if os.path.isfile(hdf_fp):
        os.remove(hdf_fp)
    with h5py.File(hdf_fp, "a") as f:
        for asic in range(ASICs):
            print("FEMB{} ASIC{} is selected".format(femb, asic))
            asic = asic & 0x0F
            wib_asic = (((femb << 16) & 0x000F0000) + ((asic << 8) & 0xFF00))
            udp.write_reg_wib_checked(7, 0x80000000)
            udp.write_reg_wib_checked(7, wib_asic | 0x80000000)
            udp.write_reg_wib_checked(7, wib_asic)
            time.sleep(0.01)
        #    fn = "Rawdata_" + data_time + "_" + strin + "_FEMB{}_ASIC{}".format(femb,asic) + ".bin"
        #    if "RMS" in strin:
        #        val = 20000
        #    else:
            val = 1000
            data = udp.get_rawdata_packets(val=val)
            chip_data = conv.raw_conv_feedloc(data)
            if chip_data != None:
                end_while = True
                femb_data.append(chip_data)
                for i in range(16):
                    dset[i] = f.create_dataset('CH{}'.format(asic*16 + i), (len(chip_data[i]),), maxshape=(None,), dtype='u2', chunks=True) 
                    dset[i][:] = chip_data[i]
            else:
                end_while = False
        print ("Start data analysis...")
        ana = data_ana(femb_data)
        if end_while:
            break

print ("Measure power consumption...")
pwr_info = tcp.femb_pwr_rd(femb=femb)
result_dict["power_vfe_ref"] =  (v_fe,  iref_fe)
result_dict["power_vadc_ref"] = (v_adc, iref_adc)
result_dict["power_vcd_ref"] =  (v_cd,  iref_cd,)
result_dict["power_bias_ref"] = (v_bias,iref_bias)
result_dict["power_vfe_meas"] =  pwr_info[0]
result_dict["power_vadc_meas"] = pwr_info[1]
result_dict["power_vcd_meas"] =  pwr_info[2]
result_dict["power_bias_meas"] = pwr_info[3]


fn = FEMB_PLOT(ana[0],ana[1],ana[2],ana[3],ana[4],ana[5],save_dir)
result_dict["response.png"] = fn
generate_report(result_dict)

print ("Turn FEMB off")
tcp.femb_pwr_set(femb=femb, pwr_on=0)

print ("Test is done...")
print ("Report is saved at {}".format(result_dict["save_dir"]))

#
'''