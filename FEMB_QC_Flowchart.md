# FEMB QC Complete Procedure Flowchart

## Overview

The FEMB (Front-End Motherboard) QC System is a comprehensive Cold Electronics testing platform for the DUNE detector at Brookhaven National Laboratory. This document provides a detailed flowchart of all procedures.

---

## System Startup Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM STARTUP                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Display Safety Warnings                                                  │
│     • "Do not open CTS during LN2 filling"                                  │
│     • "Do not touch LN2 - Risk of serious injury"                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Initialize Configuration Files                                           │
│     • Create init_setup.csv if not exists                                   │
│     • Create femb_info.csv if not exists                                    │
│     • Create femb_info_implement.csv if not exists                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Display Welcome Banner                                                   │
│     "WELCOME TO CTS COLD ELECTRONICS QC SYSTEM"                             │
│     "Brookhaven National Laboratory (BNL)"                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Get Tester Name                                                          │
│     Input: "Please enter your name:"                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. 2nd CE Box Support Structure Check                                       │
│     "Are you preparing the 2nd CE Box Support Structure?"                   │
│     • 'N' - Normal flow (1st CE Box - fresh start)                          │
│     • 'Y' - 2nd CE Box mode (back-to-back testing)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                        ▼                         ▼
              ┌─────────────────┐       ┌─────────────────────────────────┐
              │  1st CE Box     │       │  2nd CE Box Mode                │
              │  (Normal Flow)  │       │  • Show assembly popup (7.png)  │
              │  Continue to    │       │  • Skip LN2 check at startup    │
              │  steps 6-10     │       │  • LN2 check deferred to        │
              └────────┬────────┘       │    after Phase 1                │
                       │                └─────────────┬───────────────────┘
                       │                              │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. Launch Real-Time Monitor                                                 │
│     • Kill old monitoring process (pkill -f CTS_Real_Time_Monitor.py)       │
│     • Launch new terminal with monitor script                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. Email Validation                                                         │
│     • Get receiver email address                                            │
│     • Open shifter log URL in Chrome                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  8. Display Initial Checklist Popups                                         │
│     • 2.png: Discharge Human Body                                           │
│     • 3.png: Initial Check                                                  │
│     • 4.png: Accessory tray #1                                              │
│     • 5.png: Accessory tray #2                                              │
│     • 6.png: CTS Initial Checkout                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  9. CTS Cryogenic System Initialization                                      │
│     • Load CTS configuration from init_setup.csv                            │
│     • Initialize cryobox (cts_cryo_uart)                                    │
│     ┌─────────────────────────────────────────────────────────────────────┐ │
│     │ If connection successful:                                           │ │
│     │   → cryo_auto_mode = True (automatic control)                       │ │
│     │ Else:                                                               │ │
│     │   → cryo_auto_mode = False (manual control mode)                    │ │
│     └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  9-10. LN2 Dewar Level Check (1st CE Box Mode Only)                          │
│        *** SKIPPED for 2nd CE Box Mode - deferred to after Phase 1 ***      │
│        Required level: >= 1000                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                        ▼                         ▼
              ┌─────────────────┐       ┌─────────────────────────────────┐
              │  AUTO MODE      │       │  MANUAL MODE                    │
              │                 │       │                                 │
              │  Read level via │       │  Prompt user to check level    │
              │  cryo.cts_status│       │  manually                       │
              └────────┬────────┘       └─────────────┬───────────────────┘
                       │                              │
                       ▼                              ▼
              ┌─────────────────────────────────────────────────────────────┐
              │  If level < 1000:                                           │
              │    • Show refill popup (8.png)                              │
              │    • Wait for refill confirmation                           │
              │    • Verify level after refill                              │
              │    • Start warm gas purge (20 min background)               │
              │  Else:                                                      │
              │    • Continue to Phase 1                                    │
              └─────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: FEMB Installation & Setup

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PHASE 1: FEMB INSTALLATION & SETUP                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  BOTTOM SLOT INSTALLATION                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1.1 Check Slot Status                                                       │
│      "Will this slot have a FEMB installed?"                                │
│      • 'Y' → Proceed to assembly                                            │
│      • 'EMPTY'/'N' → Mark as EMPTY, skip to TOP slot                        │
│                                                                              │
│  1.2 Pre-Assembly Data Collection (if not empty)                            │
│      • Show visual inspection popup (9.png)                                 │
│      • Collect HWDB QR code (foam box)                                      │
│      • Collect CE box SN (QR scan)                                          │
│      • Collect Cover last 4 digits                                          │
│                                                                              │
│  1.3 FEMB QR Code Scanning (Triple Verification)                            │
│      ┌─────────────────────────────────────────────────────────────────┐    │
│      │  Scan 1: Enter FEMB QR code                                     │    │
│      │  Scan 2: Enter FEMB QR code again                               │    │
│      │  ┌─────────────────────────────────────────────────────────┐    │    │
│      │  │  If Scan 1 == Scan 2:                                   │    │    │
│      │  │    → Accept ID                                          │    │    │
│      │  │  Else:                                                  │    │    │
│      │  │    → Scan 3 & 4 required (must match)                   │    │    │
│      │  └─────────────────────────────────────────────────────────┘    │    │
│      └─────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  1.4 Version Identification                                                  │
│      • If "1826" in ID → HD (Horizontal Drift)                              │
│      • If "1865" in ID → VD (Vertical Drift)                                │
│                                                                              │
│  1.5 Final Confirmation                                                      │
│      "Confirm bottom FEMB SN is {femb_id_0}"                                │
│      • 'y' → Confirm                                                        │
│      • 'n' → Re-scan                                                        │
│                                                                              │
│  1.6 Show Assembly Instructions                                              │
│      • VD: 10.png                                                           │
│      • HD: 12.png                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TOP SLOT INSTALLATION                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  (Repeat same steps 1.1-1.6 for TOP slot)                                   │
│                                                                              │
│  Show Assembly Instructions:                                                 │
│      • VD: 11.png                                                           │
│      • HD: 13.png                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  UPDATE CSV RECORDS                                                          │
│  • Save SLOT0, SLOT1 FEMB IDs                                               │
│  • Save tester name                                                         │
│  • Save assembly data (HWDB, CE box, Cover for both slots)                  │
│  • Format: "Bottom_HWDB=...,Bottom_CE=...,Top_HWDB=...,Top_CE=..."          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  CTS WARM-UP TIME CHECK                                                      │
│  (If warm gas was started in LN2 refill)                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  If remaining_time > 0:                                             │    │
│  │    → Show countdown timer (can skip)                                │    │
│  │    → "Please wait for warm-up before placing CE into chamber"       │    │
│  │  When complete:                                                     │    │
│  │    → Set CTS to IDLE state                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2nd CE BOX MODE: CHAMBER EMPTY CHECK & LN2 CHECK                            │
│  *** Only executes if 2nd CE Box Mode was selected ***                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Step 1: Chamber Empty Loop                                         │    │
│  │    WHILE chamber not empty:                                         │    │
│  │      → "Is the CTS chamber empty? (Previous CE Box removed)"        │    │
│  │      → If 'Y': Break to LN2 check                                   │    │
│  │      → If 'N': "Please complete the former test first"              │    │
│  │                Wait and ask again                                   │    │
│  │                                                                     │    │
│  │  Step 2: LN2 Dewar Level Check (same as startup steps 9-10)         │    │
│  │    → Check dewar level >= 1000                                      │    │
│  │    → AUTO: cryo.cts_status() or MANUAL: user confirmation           │    │
│  │    → If low: Show refill popup, wait for refill, verify             │    │
│  │    → Start warm gas purge if refilled                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 2: Connect FEMB to CTS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 2: CONNECT FEMB TO CTS                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2.1 Safety Check #1                                                         │
│      Type: "I confirm that CTS is EMPTY"                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2.2 Set CTS to IDLE Mode                                                    │
│      • AUTO: cryo.cryo_cmd(mode=b'1')                                       │
│      • MANUAL: Prompt user to set CTS to STATE 1                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2.3 Turn OFF WIB Power Supply                                               │
│      • psu.output_off(1)                                                    │
│      • psu.output_off(2)                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2.4 Safety Check #2                                                         │
│      Type: "I confirm that CTS is in IDLE and WIB_12V is OFF"               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2.5 CE Test Structure Installation                                          │
│      • Show popup (14.png): "Placing CE boxes into crate"                   │
│      • Show popup (15.png): "WIB cable connection"                          │
│      • Show popup (16.png): "Closing CTS cover"                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2.6 Copy Configuration                                                      │
│      • Copy femb_info.csv → femb_info_implement.csv                         │
│      • Send "Assembly Complete" email notification                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 3: Warm QC Test

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 3: WARM QC TEST (~35 min)                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3.1 Power ON WIB                                                            │
│      • psu.set_channel(1, 12.0V, 3.0A, on=True)                             │
│      • psu.set_channel(2, 12.0V, 3.0A, on=True)                             │
│      • Wait 35 seconds for Ethernet communication                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3.2 Test WIB Connection                                                     │
│      • QC_Process(QC_TST_EN=77) - Ping WIB                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3.3 WIB Initialization (<2 min)                                             │
│      • QC_Process(QC_TST_EN=0)                                              │
│      • QC_Process(QC_TST_EN=1)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3.4 FEMB Warm Checkout with Auto-Retry (<3 min)                             │
│      • QC_Process(QC_TST_EN=2)                                              │
│      ┌─────────────────────────────────────────────────────────────────┐    │
│      │  AUTO-RETRY LOOP (max 3 attempts)                               │    │
│      │                                                                 │    │
│      │  For each attempt:                                              │    │
│      │    → Run checkout                                               │    │
│      │    → Check result (check_checkout_result)                       │    │
│      │    → If PASS: Break loop                                        │    │
│      │    → If FAIL & attempts < 3: Auto-retry                         │    │
│      │    → If FAIL & attempts >= 3:                                   │    │
│      │        • Send failure email                                     │    │
│      │        • User choice:                                           │    │
│      │          'r' - Retry once more                                  │    │
│      │          'c' - Continue anyway (not recommended)                │    │
│      │          'e' - Exit to disassembly (goto_disassembly=True)      │    │
│      └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
          ┌─────────────────┐               ┌─────────────────────────┐
          │ goto_disassembly│               │ Continue to Warm QC     │
          │ = True          │               │ Test                    │
          │                 │               └────────────┬────────────┘
          │ Skip remaining  │                            │
          │ QC steps        │                            ▼
          └────────┬────────┘   ┌─────────────────────────────────────────────┐
                   │            │  3.5 FEMB Warm QC Test (<30 min)            │
                   │            │      • QC_Process(QC_TST_EN=3)              │
                   │            │      • Wait for completion                  │
                   │            │      ┌───────────────────────────────────┐  │
                   │            │      │  MANUAL RETRY (no auto-retry)     │  │
                   │            │      │  If FAIL:                         │  │
                   │            │      │    • Show fault files             │  │
                   │            │      │    • Send failure email           │  │
                   │            │      │    • User choice:                 │  │
                   │            │      │      'r' - Retry (~30 min)        │  │
                   │            │      │      'c' - Continue anyway        │  │
                   │            │      │      'e' - Exit to disassembly    │  │
                   │            │      └───────────────────────────────────┘  │
                   │            └─────────────────────────────────────────────┘
                   │                                 │
                   │                                 ▼
                   │            ┌─────────────────────────────────────────────┐
                   │            │  3.6 Shutdown WIB Linux                     │
                   │            │      • QC_Process(QC_TST_EN=6)              │
                   │            └─────────────────────────────────────────────┘
                   │                                 │
                   │                                 ▼
                   │            ┌─────────────────────────────────────────────┐
                   │            │  3.7 Power OFF WIB                          │
                   │            │      • psu.turn_off_all()                   │
                   │            │      • Verify total current < 0.2A          │
                   │            │      • Retry if current still high          │
                   │            └─────────────────────────────────────────────┘
                   │                                 │
                   │                                 ▼
                   │            ┌─────────────────────────────────────────────┐
                   │            │  3.8 Display Results                        │
                   │            │      • handle_qc_results()                  │
                   │            │      • Show per-slot PASS/FAIL              │
                   │            └─────────────────────────────────────────────┘
                   │                                 │
                   └─────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NOTE: QC Summary Email                                                      │
│  • Sent automatically by CTS_Real_Time_Monitor.py                           │
│  • Triggers when t16 file is detected                                       │
│  • Waits 500 seconds for reports to complete                                │
│  • Includes per-slot FEMB results                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 4: Cold QC Test (LN2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: COLD QC TEST (LN2) (~90 min)                     │
│                    (Skip if goto_disassembly = True)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.1 CTS Cool Down Procedure                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                        ▼                         ▼
              ┌─────────────────────────┐ ┌─────────────────────────────────┐
              │  AUTO MODE              │ │  MANUAL MODE                    │
              │                         │ │                                 │
              │  4.1a Cold Gas Pre-cool │ │  Instructions:                  │
              │  (5 min)                │ │  • Set CTS to STATE 3 (Cold Gas)│
              │  cryo.cryo_coldgas(5)   │ │  • Wait 5 min countdown         │
              │                         │ │                                 │
              │  4.1b LN2 Immersion     │ │  • Set CTS to STATE 4 (Immerse) │
              │  cryo.cryo_immerse()    │ │  • Wait for LN2 to reach        │
              │  Wait for Level 3/4     │ │    LEVEL 3 or 4                 │
              │  (~30 min)              │ │  • Timer countdown              │
              │                         │ │                                 │
              │  4.1c Status Check      │ │  Confirm:                       │
              │  tc_level, dewar_level  │ │  • LN2 level reached            │
              │  = cryo.cts_status()    │ │  • Heat LED is OFF              │
              └────────────┬────────────┘ └─────────────┬───────────────────┘
                           │                            │
                           └──────────────┬─────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.2 Load Cold QC Configuration                                              │
│      • infoln = cts.read_csv_to_dict(csv_file_implement, 'LN')              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.3 Power ON WIB                                                            │
│      • psu.set_channel(1, 12.0V, 3.0A, on=True)                             │
│      • psu.set_channel(2, 12.0V, 3.0A, on=True)                             │
│      • Wait 35 seconds                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.4 WIB Connection & Initialization                                         │
│      • QC_Process(QC_TST_EN=77) - Ping WIB                                  │
│      • QC_Process(QC_TST_EN=0)  - Init                                      │
│      • QC_Process(QC_TST_EN=1)  - Init                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.5 Cold Checkout with Auto-Retry (<3 min)                                  │
│      • QC_Process(QC_TST_EN=2)                                              │
│      • Auto-retry up to 3 attempts                                          │
│      • If all fail: Send email, proceed to Cold QC anyway                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.6 CTS Level Monitoring (AUTO mode only)                                   │
│      • Check tc_level >= 3                                                  │
│      • Warn if level low                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.7 FEMB Cold QC Test (<30 min)                                             │
│      • QC_Process(QC_TST_EN=3)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.8 Shutdown WIB Linux & Power OFF                                          │
│      • QC_Process(QC_TST_EN=6)                                              │
│      • psu.turn_off_all()                                                   │
│      • Verify current < 0.2A (retry if needed)                              │
│      • Manual intervention if 5 attempts fail                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.9 Check Cold QC Results                                                   │
│      • handle_qc_results() with Cold QC paths                               │
│      ┌─────────────────────────────────────────────────────────────────┐    │
│      │  If FAIL:                                                       │    │
│      │    • Show fault files                                           │    │
│      │    • Send failure email                                         │    │
│      │    • User choice:                                               │    │
│      │      'r' - Retry Cold QC (~30 min)                              │    │
│      │      'c' - Continue to warm-up anyway                           │    │
│      │      'e' - Exit to warm-up then disassembly                     │    │
│      └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4.10 CTS WARM-UP (Direct Control - No Notices)                              │
│       ┌─────────────────────────────────────────────────────────────────┐   │
│       │  AUTO MODE:                                                     │   │
│       │    • cryo.cryo_warmgas(waitminutes=cts_warmup_wait//60)         │   │
│       │    • Set CTS to STATE 1 (IDLE)                                  │   │
│       │                                                                 │   │
│       │  MANUAL MODE:                                                   │   │
│       │    • "Set CTS to STATE 2 (Warm Gas)"                            │   │
│       │    • Timer countdown (~60 min)                                  │   │
│       │    • "Set CTS to STATE 1 (IDLE) when ready"                     │   │
│       └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 5: Final Checkout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PHASE 5: FINAL CHECKOUT (<35 min)                        │
│                     (Skip if goto_disassembly = True)                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5.1 Power ON WIB                                                            │
│      • psu.set_channel(1, 12.0V, 3.0A, on=True)                             │
│      • psu.set_channel(2, 12.0V, 3.0A, on=True)                             │
│      • Wait 35 seconds                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5.2 WIB Connection & Initialization                                         │
│      • QC_Process(QC_TST_EN=77) - Ping                                      │
│      • QC_Process(QC_TST_EN=0)  - Init                                      │
│      • QC_Process(QC_TST_EN=1)  - Init                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5.3 Final Checkout with Auto-Retry (<3 min)                                 │
│      • QC_Process(QC_TST_EN=5)                                              │
│      • Auto-retry up to 3 attempts                                          │
│      • Same retry logic as Warm Checkout                                    │
│      • User choice on failure: 'r' retry, 'c' continue, 'e' exit            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5.4 Shutdown WIB Linux                                                      │
│      • QC_Process(QC_TST_EN=6)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5.5 Generate & Send Overall QC Summary Email                                │
│      • Collect all test paths (Warm, Cold, Final)                           │
│      • analyze_test_results() on all paths                                  │
│      • generate_qc_summary() → save to file                                 │
│      • Email content includes:                                              │
│        - Total Fault/Pass files                                             │
│        - Overall PASS/FAIL                                                  │
│        - Per-slot FEMB results                                              │
│        - Next steps                                                         │
│      • Send email with attachment                                           │
│      • Delete summary file after sending                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5.6 Power OFF WIB                                                           │
│      • safe_power_off(psu)                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 6: Disassembly

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 6: DISASSEMBLY                                │
│               (Always execute if selected OR goto_disassembly=True)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  If goto_disassembly = True:                                                 │
│    Display: "ENTERING DISASSEMBLY DUE TO TEST FAILURE"                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6.1 Disassembly Preparation                                                 │
│      • "Remove and disassemble the FEMB CE boxes"                           │
│      • Show popup (17.png): "Move CE boxes out of chamber"                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6.2 Read Assembly Data                                                      │
│      • Parse comment field from csv_file_implement                          │
│      • Extract: Bottom/Top HWDB, CE box SN, Cover, FEMB SN                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6.3 Get QC Test Results                                                     │
│      • analyze_test_results() on all test paths                             │
│      • Determine PASS/FAIL for each slot                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6.4 DISASSEMBLE TOP SLOT                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  If TOP slot not EMPTY:                                                      │
│                                                                              │
│  6.4a Show Disassembly Validation Popup                                      │
│       ┌─────────────────────────────────────────────────────────────────┐   │
│       │  show_disassembly_validation_popup()                            │   │
│       │                                                                 │   │
│       │  Display:                                                       │   │
│       │    • Image (VD: 18.png, HD: 20.png) at 45% screen height        │   │
│       │    • Test Result Banner:                                        │   │
│       │      - PASS: Green background, "✓ TOP SLOT - TEST RESULT: PASS" │   │
│       │      - FAIL: Red background, "✗ TOP SLOT - TEST RESULT: FAIL"   │   │
│       │                                                                 │   │
│       │  ID Verification Table:                                         │   │
│       │    ┌──────────────┬──────────────┬──────────────┬────────┐      │   │
│       │    │ Component    │ Original ID  │ Scan/Enter   │ Status │      │   │
│       │    ├──────────────┼──────────────┼──────────────┼────────┤      │   │
│       │    │ FEMB ID      │ {femb_sn}    │ [_________]  │ ⏳/✓/✗ │      │   │
│       │    │ CE Box SN    │ {ce_box_sn}  │ [_________]  │ ⏳/✓/✗ │      │   │
│       │    │ Cover (last4)│ {cover_last4}│ [_________]  │ ⏳/✓/✗ │      │   │
│       │    │ Foam Box QR  │ {hwdb_qr}    │ [_________]  │ ⏳/✓/✗ │      │   │
│       │    └──────────────┴──────────────┴──────────────┴────────┘      │   │
│       │                                                                 │   │
│       │  Real-time Validation:                                          │   │
│       │    • Match: Green background, ✓                                 │   │
│       │    • Mismatch: Red background, ✗                                │   │
│       │    • Empty: White background, ⏳                                 │   │
│       │                                                                 │   │
│       │  Submit Button (positioned at bottom-right):                     │   │
│       │    • Only closes when ALL IDs match                             │   │
│       │    • Shows error on left side if IDs don't match                │   │
│       └─────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  6.4b Verify Results                                                         │
│       • If all IDs match: "TOP slot ID verification complete!"              │
│       • If mismatch: Fall back to terminal validation                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6.5 DISASSEMBLE BOTTOM SLOT                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  If BOTTOM slot not EMPTY:                                                   │
│                                                                              │
│  (Same process as TOP slot)                                                  │
│  • Images: VD: 19.png, HD: 21.png                                           │
│  • show_disassembly_validation_popup()                                      │
│  • Verify all IDs match                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6.6 Accessory Return Confirmation                                           │
│      • Show popup (23.png): "Return Accessories to Original Position"       │
│      • Type "confirm" to continue                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Ending Stage

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ENDING STAGE                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Close Power Supply Connection                                            │
│     • psu.close()                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Display Completion Message                                               │
│     "QC TEST CYCLE COMPLETED!"                                              │
│     "Please prepare for the next test cycle."                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Final Results Review                                                     │
│     • Display all test paths collected during this run                      │
│     • Show summary of paths:                                                │
│       - Warm Checkout Data/Report                                           │
│       - Warm QC Data/Report                                                 │
│       - Cold Checkout Data/Report                                           │
│       - Cold QC Data/Report                                                 │
│       - Final Checkout Data/Report                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Network Upload Information                                               │
│     • Display network upload path                                           │
│     • Display FEMB IDs                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Exit                                                                     │
│     • Wait for user to type "Exit"                                          │
│     • close_terminal()                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CTS_Real_Time_Monitor.py - Background Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CTS_Real_Time_Monitor.py (Background)                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  INITIALIZATION                                                              │
│  • Load configuration from init_setup.csv                                   │
│  • Set target folder: {top_path}/FEMB_QC/Data                               │
│  • Create Report directory if not exists                                    │
│  • Load previous scan results from last_scan_results.txt                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  MAIN MONITORING LOOP (every 5 seconds)                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. Scan target_folder for all files                                │    │
│  │  2. Calculate new_files = current_files - previous_files            │    │
│  │  3. Save current scan results                                       │    │
│  │  4. For each new file:                                              │    │
│  │     • Copy to network immediately (copy_file_to_network)            │    │
│  │     • Check for slot indicators (_S0, _S1, _S2, _S3)                 │    │
│  │     • Check for test item (_t1 through _t16)                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  REPORT GENERATION TRIGGER                                                   │
│  When _t{N} file detected:                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. Wait for file to be fully written                               │    │
│  │     • t6: wait 30 seconds per slot (large .bin files)               │    │
│  │     • Other: wait 7 seconds per slot                                │    │
│  │                                                                     │    │
│  │  2. Run report generation:                                          │    │
│  │     python3 QC_report_all.py {path} -n {slots} -t {item}            │    │
│  │                                                                     │    │
│  │  3. Sync data to network:                                           │    │
│  │     • sync_to_network(raw_dir, report_dir)                          │    │
│  │                                                                     │    │
│  │  4. Open reports in browser:                                        │    │
│  │     • open_reports(data_dir)                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QC SUMMARY TRIGGER (when _t16 detected)                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  process_qc_summary_after_t16(report_path):                         │    │
│  │                                                                     │    │
│  │  1. Wait 500 seconds for all reports to complete                    │    │
│  │                                                                     │    │
│  │  2. Read FEMB info from femb_info_implement.csv                     │    │
│  │                                                                     │    │
│  │  3. Determine QC type (Warm QC or Cold QC) from path                │    │
│  │                                                                     │    │
│  │  4. Report path constructed using QC_report.py formula:             │    │
│  │     report_path = top_path + '/FEMB_QC/Report/' +                   │    │
│  │                   path.split("/")[-3] + '/' +                       │    │
│  │                   path.split("/")[-2] + '/'                         │    │
│  │                                                                     │    │
│  │  5. Analyze test results (only .md and .html files):                │    │
│  │     qc_result = analyze_test_results([report_path], inform)         │    │
│  │     • Count _F_ files as faults, _P_ files as passes                │    │
│  │     • Identify slots using _S0 (bottom), _S1 (top)                  │    │
│  │     • Track test items _t1_ through _t16_                           │    │
│  │     • Report missing test items as faults                           │    │
│  │                                                                     │    │
│  │  6. Generate summary file:                                          │    │
│  │     generate_qc_summary(qc_type, inform, qc_result, summary_path)   │    │
│  │                                                                     │    │
│  │  7. Build email with per-slot results:                              │    │
│  │     - Total Fault/Pass Files                                        │    │
│  │     - Overall PASS/FAIL                                             │    │
│  │     - Bottom Slot0: {femb_id} - PASS/FAIL                           │    │
│  │     - Top Slot1: {femb_id} - PASS/FAIL                              │    │
│  │     - Missing test items (if any)                                   │    │
│  │     - Next Steps (based on QC type)                                 │    │
│  │                                                                     │    │
│  │  8. Send email with attachment:                                     │    │
│  │     send_email_with_attachment(...)                                 │    │
│  │                                                                     │    │
│  │  9. Delete summary file after sending                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## QC Test Items (t1-t16)

| Item | Test Name | Description |
|------|-----------|-------------|
| t1 | PWR_consumption | Power consumption analysis |
| t2 | PWR_cycle | Power cycling test |
| t3 | LCCHKPULSE | Cold pulse check |
| t4 | CHKPULSE | Warm pulse check |
| t5 | RMS_report | RMS noise analysis (bypasses SE ON gain 4.7) |
| t6 | CALI_report | Calibration measurements (6 types) |
| t7 | FE_MON_report | Front-end monitoring |
| t8 | FE_DAC_MON_report | Front-end DAC monitoring |
| t9 | femb_adc_sync_pat | ADC sync pattern |
| t10 | PLL_scan | PLL scan analysis |
| t11-t16 | Various | Additional tests |

---

## Result File Patterns

```
File Types Analyzed:
  • Only .md and .html files are counted for QC results

PASS Files:  *_P_*  (e.g., FEMB_WQ_P_S0.md)
FAULT Files: *_F_*  (e.g., FEMB_WQ_F_S0.md)

Slot Identification:
  *_S0* → Slot 0 (Bottom)
  *_S1* → Slot 1 (Top)

Test Item Tracking:
  • Files must contain _t1_, _t2_, _t3_, ... _t16_ for test item identification
  • All 16 test items (t1-t16) must be present for a slot to fully pass
  • Missing test items are reported as faults in the summary

Example Analysis:
  File: FEMB_WQ_F_S0_t5.md
    → Slot 0 (Bottom), Test Item 5, FAULT
  File: FEMB_WQ_P_S1_t12.html
    → Slot 1 (Top), Test Item 12, PASS
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ERROR HANDLING FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────┐
│  Test Fails           │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────────┐
│  Display Fault Files                                              │
│  • Show which files contain errors                                │
│  • Group by slot                                                  │
└───────────────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────────┐
│  Send Failure Email Notification                                  │
│  • Include test site and timestamp                                │
│  • "Awaiting operator decision"                                   │
└───────────────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────────┐
│  User Decision                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  'r' - Retry the test                                       │  │
│  │        → Loop back to test execution                        │  │
│  │                                                             │  │
│  │  'c' - Continue anyway (not recommended)                    │  │
│  │        → Proceed to next phase                              │  │
│  │                                                             │  │
│  │  'e' - Exit to disassembly                                  │  │
│  │        → Set goto_disassembly = True                        │  │
│  │        → Skip remaining QC phases                           │  │
│  │        → Go directly to Phase 6 (Disassembly)               │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

---

## CTS Control States

| State | Name | Description |
|-------|------|-------------|
| 1 | IDLE | Default/standby state |
| 2 | Warm Gas | Warm gas purge for drying/heating |
| 3 | Cold Gas | Cold gas pre-cooling |
| 4 | LN2 Immersion | Liquid nitrogen immersion |

---

## Configuration Files

### init_setup.csv
```csv
Test_Site,BNL
QC_data_root_folder,/mnt/data
Rigol_PS_for_WIB,True
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
tester,<name>
comment,Bottom_HWDB=...,Bottom_CE=...,Top_HWDB=...,Top_CE=...,...
```

---

## Directory Structure

```
/mnt/data/FEMB_QC/
├── Data/                                 # Raw test data (input to QC_report_all.py)
│   ├── FEMB_QC_<TIMESTAMP>/
│   │   ├── FEMB_0_CHK_s0_t1.csv         # Raw test data
│   │   ├── FEMB_0_WQ_s0_t2.csv
│   │   ├── FEMB_1_WQ_s1_t2.csv
│   │   ├── *.bin                         # Binary data files
│   │   └── logs/
│   └── last_scan_results.txt
│
└── Report/                               # Generated reports (output from QC_report_all.py)
    └── FEMB_QC_<TIMESTAMP>/
        ├── FEMB_0_F_S0.csv              # FAULT file (generated by QC_reports)
        ├── FEMB_0_P_S0.csv              # PASS file (generated by QC_reports)
        ├── N0.md, N1.md                 # Markdown reports
        ├── images/*.png                 # Chart images
        └── combined.pdf
```

**Important Path Flow:**
```
CTS_Real_Time_Monitor.py detects new file in Data/
    │
    ▼
Calls: python3 QC_report_all.py {Data_path} -n {slots} -t {item}
    │
    ▼
QC_report_all.py:
    • Receives Data path as input (fdir = args.folder)
    • Creates QC_reports(fdir, fembs)
    • Report path formula (line 46):
      savedir = top_path + '/FEMB_QC/Report/' + fdir.split("/")[-3] + '/' + fdir.split("/")[-2] + '/'
    • Creates _F_ (fault) and _P_ (pass) .md/.html files in Report directory
    │
    ▼
When _t16 detected in real_time_monitor():
    │
    ▼
process_qc_summary_after_t16(report_path):
    • Report path constructed using same formula as QC_report.py:
      qc_report_path = top_path + '/FEMB_QC/Report/' + path.split("/")[-3] + '/' + path.split("/")[-2] + '/'
    • Analyzes only .md and .html files
    • Identifies _F_ (fault) and _P_ (pass) patterns
    • Tracks slots using _S0 (bottom), _S1 (top)
    • Validates all 16 test items (_t1_ through _t16_) are present
```

---

## Version Information

- **Repository:** BNL_CE_WIB_SW_QC
- **Branch:** CTS_2025
- **Last Updated:** January 29, 2026

### Recent Changes (Jan 29, 2026)
- **2nd CE Box Mode**: Updated workflow - LN2 check skipped at startup, chamber empty check and LN2 check added before Phase 2
- **QC Results Analysis**: Now only counts .md and .html files, uses _P_ and _F_ patterns, tracks test items t1-t16, reports missing items as faults
- **Report Path**: Uses QC_report.py formula for consistent path construction
- **Disassembly Popup**: Button repositioned to bottom-right, image size reduced to 45%

---

## Contact

For issues or questions, contact the BNL Cold Electronics QC team.
