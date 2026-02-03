# FEMB QC System Logic Table

## Quick Reference Guide
Use labels like `[1.3.2]` to reference specific logic blocks when requesting modifications.

---

## Level 0: Main Phases

| Label | Phase | Description | File |
|-------|-------|-------------|------|
| [0] | SYSTEM STARTUP | Initialize system, checks, configuration | CTS_FEMB_QC_top.py |
| [1] | PHASE 1 | FEMB Installation & Setup | CTS_FEMB_QC_top.py |
| [2] | PHASE 2 | Connect FEMB to CTS | CTS_FEMB_QC_top.py |
| [3] | PHASE 3 | Warm QC Test | CTS_FEMB_QC_top.py |
| [4] | PHASE 4 | Cold QC Test (LN2) | CTS_FEMB_QC_top.py |
| [5] | PHASE 5 | Final Checkout | CTS_FEMB_QC_top.py |
| [6] | PHASE 6 | Disassembly | CTS_FEMB_QC_top.py |
| [7] | ENDING | Cleanup & Exit | CTS_FEMB_QC_top.py |
| [8] | MONITOR | Real-Time Monitor (Background) | CTS_Real_Time_Monitor.py |
| [9] | RESULTS | QC Results Analysis | qc_results.py |

---

## [0] SYSTEM STARTUP

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [0.1] | L1 | Safety Warnings | Always | Display LN2 safety warnings |
| [0.2] | L1 | Init Config Files | Always | Create init_setup.csv, femb_info.csv if not exist |
| [0.3] | L1 | Welcome Banner | Always | Display "WELCOME TO CTS COLD ELECTRONICS QC SYSTEM" |
| [0.4] | L1 | Get Tester Name | Always | Input tester name |
| [0.5] | L1 | 2nd CE Box Check | Always | Ask "Are you preparing the 2nd CE Box?" |
| [0.5.1] | L2 | 1st CE Box Mode | Input = 'N' | is_2nd_ce_box = False, normal flow |
| [0.5.2] | L2 | 2nd CE Box Mode | Input = 'Y' | is_2nd_ce_box = True, show 7.png popup |
| [0.6] | L1 | Launch Monitor | Always | pkill old, launch CTS_Real_Time_Monitor.py |
| [0.7] | L1 | Email Validation | Always | Get receiver email, open shifter log URL |
| [0.8] | L1 | Initial Checklists | Always | Show popups: 2.png, 3.png, 4.png, 5.png, 6.png |
| [0.9] | L1 | CTS Cryo Init | Always | Initialize cts_cryo_uart connection |
| [0.9.1] | L2 | Auto Mode | Connection OK | cryo_auto_mode = True |
| [0.9.2] | L2 | Manual Mode | Connection FAIL | cryo_auto_mode = False |
| [0.10] | L1 | LN2 Dewar Check | NOT is_2nd_ce_box | Check dewar level >= 1000 |
| [0.10.1] | L2 | Auto Check | cryo_auto_mode | Read level via cryo.cts_status() |
| [0.10.2] | L2 | Manual Check | NOT cryo_auto_mode | Prompt user to check manually |
| [0.10.3] | L2 | Refill Required | level < 1000 | Show 8.png, wait refill, verify, warm gas 20min |
| [0.10.4] | L2 | Skip LN2 Check | is_2nd_ce_box | Display "2nd CE BOX MODE - SKIPPING STARTUP LN2 CHECK" |

---

## [1] PHASE 1: FEMB Installation & Setup

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [1.1] | L1 | BOTTOM SLOT Install | Always | Process bottom slot |
| [1.1.1] | L2 | Check Slot Status | Always | Ask "Will this slot have a FEMB installed?" |
| [1.1.1.1] | L3 | Mark Empty | Input = 'EMPTY'/'N' | femb_id_0 = 'EMPTY', skip to TOP |
| [1.1.1.2] | L3 | Proceed Assembly | Input = 'Y' | Continue to data collection |
| [1.1.2] | L2 | Visual Inspection | Slot not empty | Show 9.png popup |
| [1.1.3] | L2 | Collect HWDB QR | Slot not empty | Scan foam box QR code |
| [1.1.4] | L2 | Collect CE Box SN | Slot not empty | Scan CE box QR code |
| [1.1.5] | L2 | Collect Cover ID | Slot not empty | Input cover last 4 digits |
| [1.1.6] | L2 | FEMB QR Scan | Slot not empty | Triple verification scan |
| [1.1.6.1] | L3 | Scan Match | Scan1 == Scan2 | Accept ID |
| [1.1.6.2] | L3 | Scan Mismatch | Scan1 != Scan2 | Require Scan3 & Scan4, must match |
| [1.1.7] | L2 | Version ID | Slot not empty | Detect HD (1826) or VD (1865) |
| [1.1.8] | L2 | Final Confirm | Slot not empty | Confirm FEMB SN |
| [1.1.9] | L2 | Assembly Popup | Slot not empty | VD: 10.png, HD: 12.png |
| [1.2] | L1 | TOP SLOT Install | Always | Same as [1.1.x] for TOP slot |
| [1.2.1] | L2 | Assembly Popup | Slot not empty | VD: 11.png, HD: 13.png |
| [1.3] | L1 | Update CSV | Always | Save SLOT0, SLOT1, tester, assembly data |
| [1.4] | L1 | Warm-Up Time Check | warm_gas_started | Show countdown timer if remaining > 0 |
| [1.5] | L1 | 2nd CE Box Chamber Check | is_2nd_ce_box | **NEW: Before Phase 2** |
| [1.5.1] | L2 | Chamber Empty Loop | is_2nd_ce_box | WHILE not empty: ask "Is chamber empty?" |
| [1.5.1.1] | L3 | Not Empty | Input = 'N' | Print "please complete former test", loop |
| [1.5.1.2] | L3 | Empty | Input = 'Y' | Break to LN2 check |
| [1.5.2] | L2 | LN2 Dewar Check | is_2nd_ce_box | Same logic as [0.10] |
| [1.5.3] | L2 | New Shifter Check | is_2nd_ce_box | Ask "Are you a new shifter (Y/N)" |
| [1.5.3.1] | L3 | Not New Shifter | Input = 'N' | Continue with current tester info |
| [1.5.3.2] | L3 | New Shifter | Input = 'Y' | Update email address and tester name |

---

## [2] PHASE 2: Connect FEMB to CTS

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [2.1] | L1 | Safety Check #1 | Always | Type: "I confirm that CTS is EMPTY" |
| [2.2] | L1 | Set CTS IDLE | Always | AUTO: cryo.cryo_cmd(mode=b'1'), MANUAL: prompt |
| [2.3] | L1 | WIB Power OFF | Always | psu.output_off(1), psu.output_off(2) |
| [2.4] | L1 | Safety Check #2 | Always | Type: "I confirm CTS is IDLE and WIB_12V is OFF" |
| [2.5] | L1 | CE Installation | Always | Show popups: 14.png, 15.png, 16.png |
| [2.6] | L1 | Copy Config | Always | Copy femb_info.csv → femb_info_implement.csv |
| [2.7] | L1 | Send Email | Always | Send "Assembly Complete" notification |

---

## [3] PHASE 3: Warm QC Test (~35 min)

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [3.1] | L1 | Power ON WIB | Always | psu.set_channel(1,2, 12V, 3A, on=True), wait 35s |
| [3.2] | L1 | Test WIB Ping | Always | QC_Process(QC_TST_EN=77) |
| [3.3] | L1 | WIB Init | Always | QC_Process(QC_TST_EN=0), QC_Process(QC_TST_EN=1) |
| [3.4] | L1 | Warm Checkout | Always | QC_Process(QC_TST_EN=2) with auto-retry |
| [3.4.1] | L2 | Auto-Retry Loop | Max 3 attempts | Run checkout, check result |
| [3.4.1.1] | L3 | Pass | Result OK | Break loop |
| [3.4.1.2] | L3 | Fail & Retry | Attempts < 3 | Auto-retry |
| [3.4.1.3] | L3 | Fail Max | Attempts >= 3 | Send email, user choice (r/c/e) |
| [3.4.2] | L2 | User Choice | 3 attempts failed | 'r' retry, 'c' continue, 'e' exit to disassembly |
| [3.4.3] | L2 | Exit Flag | Input = 'e' | goto_disassembly = True |
| [3.5] | L1 | Warm QC Test | NOT goto_disassembly | QC_Process(QC_TST_EN=3) ~30 min |
| [3.5.1] | L2 | Manual Retry | On failure | No auto-retry, user choice (r/c/e) |
| [3.6] | L1 | Shutdown WIB | Always | QC_Process(QC_TST_EN=6) |
| [3.7] | L1 | Power OFF WIB | Always | psu.turn_off_all(), verify current < 0.2A |
| [3.8] | L1 | Display Results | Always | handle_qc_results(), show per-slot PASS/FAIL |

---

## [4] PHASE 4: Cold QC Test (LN2) (~90 min)

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [4.0] | L1 | Skip Check | goto_disassembly | Skip entire Phase 4 |
| [4.1] | L1 | CTS Cool Down | NOT goto_disassembly | Start cooling procedure |
| [4.1.1] | L2 | Auto Cold Gas | cryo_auto_mode | cryo.cryo_coldgas(5) - 5 min pre-cool |
| [4.1.2] | L2 | Auto LN2 Immerse | cryo_auto_mode | cryo.cryo_immerse(), wait Level 3/4 |
| [4.1.3] | L2 | Manual Cold Gas | NOT cryo_auto_mode | Prompt: Set CTS to STATE 3, wait 5 min |
| [4.1.4] | L2 | Manual Immerse | NOT cryo_auto_mode | Prompt: Set CTS to STATE 4, wait Level 3/4 |
| [4.1.5] | L2 | Status Check | Always | Verify LN2 level, heat LED OFF |
| [4.2] | L1 | Load Cold Config | Always | Read csv_file_implement with 'LN' |
| [4.3] | L1 | Power ON WIB | Always | psu.set_channel(1,2, 12V, 3A, on=True), wait 35s |
| [4.4] | L1 | WIB Init | Always | QC_Process(77), QC_Process(0), QC_Process(1) |
| [4.5] | L1 | Cold Checkout | Always | QC_Process(QC_TST_EN=2) with auto-retry |
| [4.5.1] | L2 | Auto-Retry | Max 3 attempts | Same as [3.4.1] |
| [4.6] | L1 | Level Monitor | cryo_auto_mode | Check tc_level >= 3, warn if low |
| [4.7] | L1 | Cold QC Test | Always | QC_Process(QC_TST_EN=3) ~30 min |
| [4.8] | L1 | Shutdown & Off | Always | QC_Process(6), psu.turn_off_all() |
| [4.9] | L1 | Check Results | Always | handle_qc_results(), user choice on fail |
| [4.10] | L1 | CTS Warm-Up | Always | Start warm-up procedure |
| [4.10.1] | L2 | Auto Warm-Up | cryo_auto_mode | cryo.cryo_warmgas(minutes), set IDLE |
| [4.10.2] | L2 | Manual Warm-Up | NOT cryo_auto_mode | Prompt: STATE 2, countdown, then STATE 1 |

---

## [5] PHASE 5: Final Checkout (~35 min)

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [5.0] | L1 | Skip Check | goto_disassembly | Skip entire Phase 5 |
| [5.1] | L1 | Power ON WIB | NOT goto_disassembly | psu.set_channel(1,2, 12V, 3A), wait 35s |
| [5.2] | L1 | WIB Init | Always | QC_Process(77), QC_Process(0), QC_Process(1) |
| [5.3] | L1 | Final Checkout | Always | QC_Process(QC_TST_EN=5) with auto-retry |
| [5.3.1] | L2 | Auto-Retry | Max 3 attempts | Same as [3.4.1] |
| [5.3.2] | L2 | User Choice | 3 attempts failed | 'r' retry, 'c' continue, 'e' exit |
| [5.4] | L1 | Shutdown WIB | Always | QC_Process(QC_TST_EN=6) |
| [5.5] | L1 | QC Summary Email | Always | Collect paths, analyze, send email with attachment |
| [5.6] | L1 | Power OFF WIB | Always | safe_power_off(psu) |

---

## [6] PHASE 6: Disassembly

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [6.0] | L1 | Entry Check | goto_disassembly | Display "ENTERING DISASSEMBLY DUE TO TEST FAILURE" |
| [6.1] | L1 | Preparation | Always | Show 17.png: "Move CE boxes out of chamber" |
| [6.2] | L1 | Read Assembly Data | Always | Parse comment field from csv_file_implement |
| [6.3] | L1 | Get QC Results | Always | analyze_test_results() on all test paths |
| [6.4] | L1 | TOP Slot Disassembly | TOP != EMPTY | Disassemble TOP slot |
| [6.4.1] | L2 | Validation Popup | Always | show_disassembly_validation_popup() |
| [6.4.1.1] | L3 | Image Display | Always | VD: 18.png, HD: 20.png at 45% height |
| [6.4.1.2] | L3 | Result Banner | Always | Green PASS or Red FAIL |
| [6.4.1.3] | L3 | ID Verification | Always | Scan: FEMB, CE Box, Cover, Foam Box QR |
| [6.4.1.4] | L3 | Real-time Match | On input | Green=match, Red=mismatch, White=empty |
| [6.4.1.5] | L3 | Submit Button | Bottom-right | Only closes when ALL IDs match |
| [6.4.2] | L2 | Verify Results | Always | Check all IDs match |
| [6.5] | L1 | BOTTOM Slot Disassembly | BOTTOM != EMPTY | Same as [6.4.x], images: VD: 19.png, HD: 21.png |
| [6.6] | L1 | Accessory Return | Always | Show 23.png, type "confirm" |

---

## [7] ENDING STAGE

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [7.1] | L1 | Close PSU | Always | psu.close() |
| [7.2] | L1 | Completion Message | Always | Display "QC TEST CYCLE COMPLETED!" |
| [7.3] | L1 | Results Review | Always | Display all test paths collected |
| [7.4] | L1 | Network Info | Always | Display network path and FEMB IDs |
| [7.5] | L1 | Exit | Always | Wait for "Exit" input, close_terminal() |

---

## [8] CTS_Real_Time_Monitor.py (Background)

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [8.1] | L1 | Initialization | Always | Load config, set target folder, create dirs |
| [8.2] | L1 | Main Loop | Every 5s | Scan for new files |
| [8.2.1] | L2 | Detect New Files | new_files found | current_files - previous_files |
| [8.2.2] | L2 | Network Copy | For each new file | copy_file_to_network(file_path) |
| [8.2.3] | L2 | Slot Detection | For each new file | Check _S0, _S1, _S2, _S3 |
| [8.2.4] | L2 | Test Item Detection | For each new file | Check _t{N} in filename |
| [8.3] | L1 | Report Generation | _t{N} detected | Call QC_report_all.py |
| [8.3.1] | L2 | Wait for File | _t6 | Wait 30s per slot (large .bin) |
| [8.3.2] | L2 | Wait for File | Other _t | Wait 7s per slot |
| [8.3.3] | L2 | Run Report | Always | python3 QC_report_all.py {path} -n {slots} -t {item} |
| [8.4] | L1 | QC Summary Trigger | _t16 detected | process_qc_summary_after_t16(report_path) |
| [8.4.1] | L2 | Construct Path | Always | top_path + '/FEMB_QC/Report/' + path[-3] + '/' + path[-2] + '/' |
| [8.4.2] | L2 | Wait Reports | Always | Wait 500 seconds |
| [8.4.3] | L2 | Read FEMB Info | Always | Parse femb_info_implement.csv |
| [8.4.4] | L2 | Determine QC Type | Always | Check path for WQ/LQ/Warm/Cold |
| [8.4.5] | L2 | Analyze Results | Always | analyze_test_results([report_path], inform) |
| [8.4.6] | L2 | Generate Summary | Always | generate_qc_summary() |
| [8.4.7] | L2 | Send Email | Always | send_email_with_attachment() |
| [8.4.8] | L2 | Cleanup | Always | Delete summary file after send |

---

## [9] qc_results.py - QC Results Analysis

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [9.1] | L1 | QCResult Class | Always | Store fault_files, pass_files, slot_status |
| [9.1.1] | L2 | Track Tests | Always | tests_found set, slot_missing_tests dict |
| [9.2] | L1 | analyze_test_results() | Called | Main analysis function |
| [9.2.1] | L2 | File Filter | Always | Only process .md and .html files |
| [9.2.2] | L2 | Slot Detection | Always | _S0 = slot0 (bottom), _S1 = slot1 (top) |
| [9.2.3] | L2 | Fault Detection | _F_ in filename | Mark as fault, add to fault_files |
| [9.2.4] | L2 | Pass Detection | _P_ in filename | Mark as pass, add to pass_files |
| [9.2.5] | L2 | Test Item Extract | Always | regex _t(\d+) to get test number |
| [9.2.6] | L2 | Track Per-Slot | Always | slot_files[slot]['tests_found'].add(test_num) |
| [9.2.7] | L2 | Missing Test Check | After scan | Compare tests_found vs {1..16} |
| [9.2.7.1] | L3 | Missing Found | tests_found != all 16 | Add to slot_missing_tests, mark as fault |
| [9.3] | L1 | generate_qc_summary() | Called | Generate summary text file |
| [9.3.1] | L2 | Per-Slot Status | Always | List FEMB ID, PASS/FAIL for each slot |
| [9.3.2] | L2 | Missing Tests | If any | List missing test items per slot |

---

## GUI Components (pop_window.py)

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [G.1] | L1 | show_image_popup() | Called | Display fullscreen image with Confirm button |
| [G.2] | L1 | show_checkbox_popup() | Called | Display checkbox options with image |
| [G.3] | L1 | show_disassembly_validation_popup() | Called | ID verification popup |
| [G.3.1] | L2 | Layout | Always | Button at bottom-right (packed first) |
| [G.3.2] | L2 | Image Size | Always | 75% of screen height |
| [G.3.2.1] | L3 | Text Box Width | Always | 75 characters (3x original) |
| [G.3.3] | L2 | ID Grid | Always | 4 rows: FEMB, CE Box, Cover, Foam Box |
| [G.3.4] | L2 | Real-time Validation | On input | KeyRelease/FocusOut triggers check |
| [G.3.4.1] | L3 | ID Normalize | On compare | replace('/', '_') for both scanned and original |
| [G.3.5] | L2 | Submit Logic | On click | Only close if ALL match, else show error |

---

## Utility Functions (qc_utils.py)

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [U.1] | L1 | save_qc_paths() | Called | Save data/report paths to JSON |
| [U.2] | L1 | load_qc_paths() | Called | Load paths from JSON |
| [U.3] | L1 | countdown_timer() | Called | Display countdown with skip option |
| [U.4] | L1 | timer_count() | Called | Count-up timer with exit option |
| [U.5] | L1 | check_fault_files() | Called | Check _F_ and _P_ files in paths |
| [U.6] | L1 | check_checkout_result() | Called | Return True if no fault files |
| [U.7] | L1 | QC_Process() | Called | Execute QC test with error handling |
| [U.7.1] | L2 | Success | Result OK | Return data_path, report_path |
| [U.7.2] | L2 | Critical Fail | CRITICAL_CURRENT_FAILURE | Send email, return None, None |
| [U.7.3] | L2 | Issue | Result None | User choice: '139' terminate, '2' retest |
| [U.8] | L1 | close_terminal() | Called | Close gnome-terminal/konsole |

---

## CTS Control (cts_cryo_uart.py)

| Label | Level | Logic | Condition | Action |
|-------|-------|-------|-----------|--------|
| [C.1] | L1 | init connection | Called | Connect to CTS cryobox via serial |
| [C.2] | L1 | cts_status() | Called | Return (tc_level, dewar_level) |
| [C.3] | L1 | cryo_cmd() | Called | Send command: mode b'1'-b'4' |
| [C.3.1] | L2 | STATE 1 | mode=b'1' | IDLE |
| [C.3.2] | L2 | STATE 2 | mode=b'2' | Warm Gas |
| [C.3.3] | L2 | STATE 3 | mode=b'3' | Cold Gas |
| [C.3.4] | L2 | STATE 4 | mode=b'4' | LN2 Immersion |
| [C.4] | L1 | cryo_coldgas() | Called | Pre-cool with cold gas for N minutes |
| [C.5] | L1 | cryo_immerse() | Called | Start LN2 immersion |
| [C.6] | L1 | cryo_warmgas() | Called | Warm-up with warm gas for N minutes |

---

## Example Usage

When you want to modify something, just tell me the label:

- "Modify [0.10.3] to change refill threshold from 1000 to 800"
- "Update [3.4.1] to increase auto-retry from 3 to 5 attempts"
- "Change [G.3.2] image size from 45% to 50%"
- "Add new step after [1.5.1.2] to send notification email"
- "Fix [9.2.7] to also check for test items t17 and t18"

---

## Version

- **Last Updated:** January 29, 2026
- **Labels Valid For:** CTS_2025 branch
