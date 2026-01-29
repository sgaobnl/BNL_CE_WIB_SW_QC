# FEMB QC Framework Documentation

## Overview

The FEMB (Front-End Motherboard) QC System is a comprehensive Cold Electronics testing platform for the DUNE detector at Brookhaven National Laboratory. It orchestrates multi-phase testing of Front-End Motherboards in a cryogenic environment using the Cold Test System (CTS).

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER (Tester)                                    │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  v
┌─────────────────────────────────────────────────────────────────────────┐
│                    CTS_FEMB_QC_top.py (Main Orchestrator)                │
│                                                                          │
│  - 6-Phase Test Workflow Control                                         │
│  - User Interface & Tester Authentication                                │
│  - Assembly/Disassembly Validation                                       │
│  - Email Notifications                                                   │
└───────┬─────────────────┬─────────────────┬─────────────────┬───────────┘
        │                 │                 │                 │
        v                 v                 v                 v
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│cts_ssh_FEMB.py│ │cts_cryo_uart  │ │  qc_results   │ │  GUI modules  │
│               │ │               │ │               │ │               │
│ - SSH to FEMB │ │ - LN2 Control │ │ - Result      │ │ - Popups      │
│ - Test Exec   │ │ - Temperature │ │   Analysis    │ │ - Email       │
│ - Data Collect│ │ - Warm Gas    │ │ - PASS/FAIL   │ │ - Power Supply│
└───────┬───────┘ └───────────────┘ └───────────────┘ └───────────────┘
        │
        v
┌─────────────────────────────────────────────────────────────────────────┐
│                    Test Data Directory                                   │
│                    /FEMB_QC/Data/<timestamp>/                            │
│                    - Raw CSV test results                                │
│                    - _F (fault) / _P (pass) files                        │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                   [File Detection]
                                │
                                v
┌─────────────────────────────────────────────────────────────────────────┐
│              CTS_Real_Time_Monitor.py (Background Service)               │
│                                                                          │
│  - Monitors Data directory for new files                                 │
│  - Triggers report generation automatically                              │
│  - Processes QC summary signals (500s wait)                              │
│  - Syncs data to network drive                                           │
│  - Sends email notifications with results                                │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                   [Report Generation]
                                │
                                v
┌─────────────────────────────────────────────────────────────────────────┐
│                    QC_report.py / QC_report_all.py                       │
│                                                                          │
│  - 16 Analysis Report Types                                              │
│  - PDF & Markdown Generation                                             │
│  - Per-channel & Per-slot Analysis                                       │
│  - PNG Chart Generation                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Test Phases

The system orchestrates **6 sequential phases**:

### Phase 1: FEMB Installation & Setup (~40-60 min)
- Assembly data collection (HWDB QR, CE box SN, Cover SN)
- FEMB QR code scanning with triple verification
- Bottom slot installation
- Top slot installation (optional)

### Phase 2: Connect FEMB to CTS (~15 min)
- Safety checklist confirmation
- CE structure installation
- Power cable connection
- CTS lock and safety verification

### Phase 3: Warm Checkout (~60-120 min)
- Initial power-up and diagnostics
- Electrical parameter tests
- Noise characterization
- Power consumption measurement
- Result analysis → PASS/FAIL decision

### Phase 4: Warm QC (~120-180 min)
- ADC synchronization tests
- Calibration measurements (6 types)
- Front-end monitoring
- Advanced pattern testing (PLL, sync)
- **QC Summary Signal → Monitor waits 500s → Email sent**

### Phase 5: Cold QC (~180-300 min @ LN2)
- CTS Mode: WARM → COLD (30 min purge)
- Noise measurement in cold
- Temperature stability verification
- Cold ADC/DAC monitoring
- Extended stress testing
- **QC Summary Signal → Monitor waits 500s → Email sent**
- CTS Mode: COLD → WARM (60 min warmup)

### Phase 6: Final Checkout & Disassembly (~40-80 min)
- Final safety inspection
- Disassembly validation (CE box, Cover, Foam box)
- PASS/FAIL sticker application (Green/Red)
- Storage in designated location

---

## Key Components

### Main Scripts

| Script | Purpose |
|--------|---------|
| `CTS_FEMB_QC_top.py` | Main orchestrator - controls entire 6-phase workflow |
| `CTS_Real_Time_Monitor.py` | Background service - monitors files, generates reports, sends emails |
| `QC_report.py` | Report engine - 16 analysis types, PDF/Markdown generation |
| `QC_report_all.py` | CLI wrapper for report generation |

### Utility Modules

| Module | Purpose |
|--------|---------|
| `qc_results.py` | Result analysis, PASS/FAIL determination, summary generation |
| `qc_utils.py` | Timing functions, fault file checking |
| `cts_ssh_FEMB.py` | SSH communication to FEMB hardware |
| `cts_cryo_uart.py` | CTS cryogenic system control |
| `QC_tools.py` | Data analysis tools |
| `QC_check.py` | Hardware validation checks |

### GUI Modules

| Module | Purpose |
|--------|---------|
| `GUI/pop_window.py` | Visual instruction popups |
| `GUI/send_email.py` | Email notification system |
| `GUI/Rigol_DP800.py` | Power supply control |
| `GUI/State_List.py` | Test state/phase selection |

---

## Data Flow

### 1. Test Execution
```
CTS_FEMB_QC_top.py
    │
    ├──> cts_ssh_FEMB.py (Execute tests on FEMB hardware)
    │
    └──> Raw test data saved to:
         /FEMB_QC/Data/<timestamp>/FEMB_<slot>_<test>.csv
```

### 2. Background Monitoring & QC Summary
```
CTS_Real_Time_Monitor.py (runs in background)
    │
    ├──> Detects new test files → Calls QC_report_all.py
    │
    ├──> When t16 file detected (final test item):
    │    1. Complete t16 report generation
    │    2. Wait 500 seconds for all reports to complete
    │    3. Read FEMB info from femb_info_implement.csv
    │    4. Analyze test results (qc_results.py)
    │    5. Generate summary with per-slot FEMB status
    │    6. Send email with attachment
    │
    └──> Sync data to network path
```

### 4. Report Generation
```
QC_report_all.py → QC_report.py
    │
    └──> Generated reports saved to:
         /FEMB_QC/Report/<timestamp>/
         ├── N0.md (Slot 0 results)
         ├── N1.md (Slot 1 results)
         ├── images/*.png
         └── combined.pdf
```

---

## Directory Structure

```
/mnt/data/FEMB_QC/
├── Data/                              # Raw test data (input)
│   ├── FEMB_QC_<TIMESTAMP>/
│   │   ├── FEMB_0_CHK_s0_t1.csv      # Check test - Slot 0
│   │   ├── FEMB_0_WQ_s0_t2.csv       # Warm QC - Slot 0
│   │   ├── FEMB_1_WQ_s1_t2.csv       # Warm QC - Slot 1
│   │   ├── *.bin                      # Binary data files
│   │   └── logs/
│   └── last_scan_results.txt
│
└── Report/                            # Generated reports (output)
    └── FEMB_QC_<TIMESTAMP>/
        ├── FEMB_0_F_S0.csv           # FAULT file - Slot 0 (generated)
        ├── FEMB_0_P_S0.csv           # PASS file - Slot 0 (generated)
        ├── N0.md, N1.md              # Markdown reports
        ├── images/*.png
        └── combined.pdf
```

**Note:** The `_F_` (fault) and `_P_` (pass) result files are generated by `QC_report_all.py` and saved in the **Report** directory, not the Data directory.

---

## File Naming Convention

```
FEMB_<SLOT>_<TEST>_<DETAILS>.csv

Examples:
FEMB_0_CHK_s0_t1.csv     → Check test, Slot 0, task 1
FEMB_0_WQ_s0_t2.csv      → Warm QC, Slot 0, task 2
FEMB_0_LQ_s0_t4.csv      → Cold QC (LN2), Slot 0, task 4
FEMB_0_F_S0.csv          → FAULT file for Slot 0
FEMB_0_P_S0.csv          → PASS file for Slot 0
```

---

## Result Analysis

### QCResult Structure (qc_results.py)
```python
class QCResult:
    fault_files = []           # All fault files detected
    pass_files = []            # All pass files detected
    slot_status = {            # Per-slot results
        '0': (passed, femb_id),
        '1': (passed, femb_id),
    }
    slot_files = {             # Files grouped by slot
        '0': {'faults': [...], 'passes': [...]},
        '1': {'faults': [...], 'passes': [...]},
    }
    total_faults = 0
    total_passes = 0
```

### PASS/FAIL Logic
1. Scan test directory for `*_F.*` (fault) and `*_P.*` (pass) files
2. Group files by slot using filename patterns: `FEMB_<SLOT>_`, `_S<SLOT>_`
3. **Slot PASSES if:** Zero fault files detected for that slot
4. **Slot FAILS if:** Any fault files exist for that slot
5. **Overall PASS if:** All installed slots pass
6. **Overall FAIL if:** Any installed slot has faults

---

## Report Types (QC_report.py)

| Task | Report Type | Description |
|------|-------------|-------------|
| t1 | PWR_consumption_report | Power consumption analysis |
| t2 | PWR_cycle_report | Power cycling test |
| t3 | LCCHKPULSE | Cold pulse check |
| t4 | CHKPULSE | Warm pulse check |
| t5 | RMS_report | RMS noise analysis |
| t6 | CALI_report_1-6 | Calibration measurements |
| t7 | FE_MON_report | Front-end monitoring |
| t8 | FE_DAC_MON_report | Front-end DAC monitoring |
| t9 | femb_adc_sync_pat_report | ADC sync pattern |
| t10 | PLL_scan_report | PLL scan analysis |

### Bypass Conditions
- **SELC 5nA test:** Bypassed due to accuracy limitations
- **SE ON, gain 4.7 mV/fC:** Bypassed in RMS analysis

---

## Configuration Files

### init_setup.csv
```csv
Test_Site,BNL
QC_data_root_folder,/mnt/data
Rigol_PS_for_WIB,True
Rigol_PS_ID,USB0::0x1AB1::0x0E11::DP8C184550857::INSTR
CTS_LN2_Fill_Wait,1800
CTS_Warmup_Wait,3600
Network_Upload_Path,/data/rtss/femb
email_sender,bnlr216@gmail.com
email_receiver,lke@bnl.gov
```

### femb_info.csv / femb_info_implement.csv
```csv
SLOT0,<FEMB_ID_0>
SLOT1,<FEMB_ID_1>
test_site,BNL
tester,<tester_name>
comment,Bottom_HWDB=...,Bottom_CE=...,Top_HWDB=...,Top_CE=...
```

---

## Email Notification Flow

```
┌─────────────────────────────────┐
│ Test item t16 file detected     │
│ (final test item in QC cycle)   │
└────────┬────────────────────────┘
         │
         v
┌─────────────────────────────────┐
│ CTS_Real_Time_Monitor.py        │
│ process_qc_summary_after_t16()  │
│                                 │
│ 1. Generate t16 report          │
│ 2. Wait 500 seconds             │
│ 3. Read femb_info_implement.csv │
│ 4. analyze_test_results()       │
│ 5. generate_qc_summary()        │
│ 6. Build email with per-slot    │
│    FEMB results                 │
│ 7. Send email with attachment   │
└─────────────────────────────────┘
```

### Email Content Example
```
Warm QC Test Completed

Test Site: BNL
Timestamp: 2026-01-28 10:30:00

Summary:
  Total Fault Files: 0
  Total Pass Files: 24
  Overall Result: PASS

FEMB Results:
  Bottom Slot0: IO-1826-1-00001 - PASS
  Top Slot1: IO-1826-1-00002 - PASS

Next Steps:
  1. Switch CTS to COLD mode for 5 minutes
  2. Switch to IMMERSE mode
  3. Wait for LN2 to reach Level 3
  4. Double confirm heat LED is OFF

Detailed summary is attached.
```

---

## Running the System

### 1. Start Real-Time Monitor (Background)
```bash
# In separate terminal
python3 CTS_Real_Time_Monitor.py
```

### 2. Start Main QC Script
```bash
python3 CTS_FEMB_QC_top.py
```

### 3. Manual Report Generation
```bash
# Generate specific reports
python3 QC_report_all.py /path/to/data -n 0 1 -t 1 2 3

# Arguments:
#   /path/to/data  - Data directory
#   -n 0 1         - FEMB slots (0, 1, 2, 3)
#   -t 1 2 3       - Task numbers (1-16)
```

---

## Error Handling

### Test Failure → Retry Workflow
```
Test Failed
    │
    v
Display fault files to user
    │
    v
Options:
  'r' - Retry (re-run same phase)
  'c' - Continue (mark failed, proceed)
  'e' - Exit (abort testing)
```

### Hardware Issues
- SSH/UART timeout → Prompt for reconnection
- LN2 level low → Refill with verification loop
- Temperature out of range → Abort phase with guidance

### File/Network Issues
- Missing directory → Auto-created
- Network sync failure → Continue locally with warning
- Report generation error → Continue with warning

---

## Version Information

- **Repository:** BNL_CE_WIB_SW_QC
- **Branch:** CTS_2025
- **Last Updated:** January 2026

---

## Contact

For issues or questions, contact the BNL Cold Electronics QC team.
