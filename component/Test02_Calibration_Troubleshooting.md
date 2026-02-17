# TEST02: CALIBRATION PATH CONTROL
## Flow Chart & Troubleshooting Guide

```
                                    ┌─────────┐
                                    │  START  │
                                    └────┬────┘
                                         │
                                         ▼
                        ┌────────────────────────────────┐
                        │  Initialize Power Supply (PSU) │
                        │  - Safe power off first        │
                        │  - CH1: 12V, 3A limit          │
                        │  - CH2: 12V, 3A limit          │
                        └────────────────┬───────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Wait 10 seconds   │
                              │  (Power stabilize)  │
                              └──────────┬──────────┘
                                         │
                                         ▼
                        ┌────────────────────────────────┐
                        │  Measure Initial Power         │
                        │  - CH1: V1_start, C1_start     │
                        │  - CH2: V2_start, C2_start     │
                        └────────────────┬───────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
                    ▼                                         ▼
        ┌───────────────────┐                     ┌───────────────────┐
        │ Voltage OK?       │                     │ Current OK?       │
        │ 11.0V ≤ V ≤ 13.0V │                     │ 0.5A ≤ I ≤ 3.0A   │
        └─────────┬─────────┘                     └─────────┬─────────┘
                  │                                         │
           ┌──────┴──────┐                           ┌──────┴──────┐
           │             │                           │             │
          YES           NO                          YES           NO
           │             │                           │             │
           │             ▼                           │             ▼
           │   ┌─────────────────┐                   │   ┌─────────────────┐
           │   │ TROUBLESHOOT #1 │                   │   │ TROUBLESHOOT #2 │
           │   │ (See below)     │                   │   │ (See below)     │
           │   └─────────────────┘                   │   └─────────────────┘
           │                                         │
           └─────────────────┬───────────────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Wait 20 seconds   │
                  │  (System stabilize) │
                  └──────────┬──────────┘
                             │
                             ▼
                ┌───────────────────────────┐
                │  Initialize Communication │
                │  - TCP_CFG()              │
                │  - CLS_UDP()              │
                │  - RAW_CONV()             │
                └─────────────┬─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TEST SEQUENCE                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   TEST 1      │    │   TEST t1     │    │   TEST t2     │
│ DAC Voltage   │───▶│ Reference V   │───▶│ Path Ctrl A   │
│ Expected: 1V  │    │ Expected:1.65V│    │ Expected:0.5V │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ ADC Readback  │    │ ADC Readback  │    │ ADC Readback  │
│ SLOT 0-3      │    │ SLOT 0-3      │    │ SLOT 0-3      │
│ P8,P7,P6,P4   │    │ P8,P7,P6,P4   │    │ P8,P7,P6,P4   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ 0.9V ≤ V ≤1.1V│    │1.6V ≤ V ≤1.7V│    │0.5V ≤ V ≤0.55V│
│   PASS/FAIL   │    │   PASS/FAIL   │    │   PASS/FAIL   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   TEST t3     │    │   TEST t4     │    │   TEST t5/t6  │
│ Path Ctrl B   │───▶│ LEMO P5 Inj   │───▶│ Test Points   │
│ Expected:0.5V │    │ Expected:0.8V │    │ Expected: 0V  │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        │            ┌───────┴───────┐            │
        │            │   POPUP       │            │
        │            │   Page 7:     │            │
        │            │   Test P5     │            │
        │            │   (7.png)     │            │
        │            └───────┬───────┘            │
        │                    │            ┌───────┴───────┐
        │                    │            │   POPUP       │
        │                    │            │   Page 8:     │
        │                    │            │   Float V     │
        │                    │            │   (8.png)     │
        │                    │            └───────┬───────┘
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ ADC Readback  │    │ ADC Readback  │    │ ADC Readback  │
│ SLOT 0-3      │    │ SLOT 0-3      │    │ SLOT 0-3      │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│0.5V ≤ V ≤0.55V│    │0.7V ≤ V ≤0.85V│    │0.0V ≤ V ≤ 0.5V│
│   PASS/FAIL   │    │   PASS/FAIL   │    │   PASS/FAIL   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                ┌───────────────────────────┐
                │  Measure Final Power      │
                │  - CH1: V1_end, C1_end    │
                │  - CH2: V2_end, C2_end    │
                │  - Total Power calc       │
                └─────────────┬─────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  PSU Safe Power Off │
                   └──────────┬──────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │  Generate HTML Report  │
                 │  WIB_02_Calibration_   │
                 │  report_02.html        │
                 └───────────┬────────────┘
                             │
                             ▼
                        ┌─────────┐
                        │   END   │
                        └─────────┘
```

---

## TROUBLESHOOTING GUIDE

### TROUBLESHOOT #1: VOLTAGE OUT OF RANGE (V < 11.0V or V > 13.0V)

**Possible Causes:**
- PSU not properly connected
- PSU channel not enabled
- Faulty power cable
- PSU malfunction

**Actions:**
1. Check PSU front panel - verify CH1/CH2 are ON
2. Verify power cable connections to WIB
3. Check PSU USB/Serial connection
4. Try manual PSU control to verify operation
5. Replace power cables if damaged

---

### TROUBLESHOOT #2: CURRENT OUT OF RANGE

**Current TOO LOW (I < 0.5A):**
- WIB not powered properly
- WIB not fully seated in slot
- Faulty WIB board
- Power connector not fully inserted

**Current TOO HIGH (I > 3.0A):**
- Short circuit on WIB
- Component failure on WIB
- Wrong voltage setting
- **WARNING: IMMEDIATELY POWER OFF if current exceeds limit!**

**Actions:**
1. Power off and reseat WIB board
2. Inspect WIB for visible damage/burns
3. Check for foreign objects/debris
4. Verify correct power connector orientation

---

### TROUBLESHOOT #3: DAC VOLTAGE TEST FAIL (Test 1)
**Expected: 0.9V ≤ V ≤ 1.1V for all slots**

**Possible Causes:**
- DAC chip (U12) malfunction
- TCP communication failure
- ADC readback error
- Calibration path damaged

**Actions:**
1. Verify TCP connection (run Test01 first)
2. Check DAC SPI signals with oscilloscope
3. Measure DAC output directly at test points
4. If single slot fails, check path to that FEMB connector

---

### TROUBLESHOOT #4: REFERENCE VOLTAGE TEST FAIL (Test t1)
**Expected: 1.6V ≤ V ≤ 1.7V for all slots**

**Possible Causes:**
- Reference voltage generator failure
- CAL_PULSE_GEN switch not responding
- Path selection issue

**Actions:**
1. Measure 1.65V reference at source
2. Check CAL_PULSE_GEN control signal
3. Verify switch IC operation

---

### TROUBLESHOOT #5: PATH CONTROL TEST FAIL (Test t2/t3)
**Expected: 0.5V ≤ V ≤ 0.55V**

**Possible Causes:**
- DAC_SRC_SEL switch failure
- Cross-talk between slots
- Signal path discontinuity

**Test Configuration:**
- Test t2: SLOT0/2 = output (1), SLOT1/3 = input (0)
- Test t3: SLOT0/2 = input (0), SLOT1/3 = output (1)

**Actions:**
1. Check DAC_SRC_SEL_BRD0-3 control signals
2. Verify switch IC (analog multiplexer) operation
3. Check for solder bridges on switch ICs
4. If specific slot fails, trace path from DAC to that slot

---

### TROUBLESHOOT #6: LEMO P5 INJECTION TEST FAIL (Test t4)
**Expected: 0.7V ≤ V ≤ 0.85V**

**Possible Causes:**
- LEMO P5 connector damaged
- External calibration pulse path issue
- Test cable not connected (check Page 7 popup image)

**Actions:**
1. Follow instructions in Page 7 popup
2. Verify LEMO P5 cable connection
3. Check LEMO connector for damage
4. Test continuity of calibration cable

---

### TROUBLESHOOT #7: TEST POINTS FAIL (Test t5/t6)
**Expected: 0.0V ≤ V ≤ 0.5V (floating/disconnected state)**

**Possible Causes:**
- Residual voltage on path
- Switch not fully disconnecting
- Leakage current
- Test probe still connected (check Page 8 popup image)

**Actions:**
1. Follow instructions in Page 8 popup
2. Remove all test probes from test points
3. Wait additional time for capacitors to discharge
4. Check for high-impedance path issues

---

### TROUBLESHOOT #8: COMMUNICATION ERROR

**Symptoms:**
- TCP_CFG() timeout
- ADC readback returns 0 or invalid values
- tcp_poke/tcp_peek errors

**Possible Causes:**
- Network connection lost
- WIB FPGA not responding
- IP address conflict

**Actions:**
1. Run Test01 to verify communication
2. Check Ethernet cable connection
3. Ping WIB IP address manually
4. Power cycle WIB and retry

---

## PORT MAPPING REFERENCE

| SLOT   | ADC Channel | Port | FEMB Connector |
|--------|-------------|------|----------------|
| SLOT0  | ADC0        | P8   | FEMB Slot 0    |
| SLOT1  | ADC1        | P7   | FEMB Slot 1    |
| SLOT2  | ADC2        | P6   | FEMB Slot 2    |
| SLOT3  | ADC3        | P4   | FEMB Slot 3    |

---

## TEST THRESHOLD SUMMARY

| Test Name              | Min (V) | Max (V) | Description          |
|------------------------|---------|---------|----------------------|
| DAC Voltage Test       | 0.90    | 1.10    | 1V DAC output        |
| Reference Voltage      | 1.60    | 1.70    | 1.65V reference      |
| Path Control A         | 0.50    | 0.55    | SLOT0/2 → SLOT1/3    |
| Path Control B         | 0.50    | 0.55    | SLOT1/3 → SLOT0/2    |
| LEMO P5 Injection      | 0.70    | 0.85    | External cal pulse   |
| Test Points            | 0.00    | 0.50    | Floating state       |

### Power Thresholds

| Parameter              | Min     | Max     | Description          |
|------------------------|---------|---------|----------------------|
| Power CH1/CH2 Voltage  | 11.0 V  | 13.0 V  | 12V nominal          |
| Power CH1/CH2 Current  | 0.5 A   | 3.0 A   | Normal operation     |
| Total Power            | 4.0 W   | 30.0 W  | Both channels        |
