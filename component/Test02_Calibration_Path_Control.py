## =========================================
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from function.cls_udp import CLS_UDP
from function.tcp_cfg import TCP_CFG
from function.raw_convertor import RAW_CONV
import datetime
import file.report_dict as rp_dict
import GUI.pop_window as pop
from function.csv_manager import WIB_QC_CSV_Manager
t1 = time.time()
import function.Rigol_DP800 as rigol
# Image paths for instruction popups
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'GUI', 'output_pngs')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def print_header(msg):
    print("\033[35m" + "=" * 60 + "\033[0m")
    print("\033[35m" + msg + "\033[0m")
    print("\033[35m" + "=" * 60 + "\033[0m")

def print_pass(msg):
    print("\033[32m" + msg + "\033[0m")

def print_fail(msg):
    print("\033[31m" + msg + "\033[0m")

def print_warning(msg):
    print("\033[33m" + msg + "\033[0m")

# ============================================================================
# TROUBLESHOOTING MESSAGES
# ============================================================================
TROUBLESHOOT = {
    "voltage_low": """
┌─────────────────────────────────────────────────────────────┐
│  TROUBLESHOOT: VOLTAGE OUT OF RANGE (V < 11.0V)             │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • PSU not properly connected                               │
│  • PSU channel not enabled                                  │
│  • Faulty power cable                                       │
│                                                             │
│  Actions:                                                   │
│  1. Check PSU front panel - verify CH1/CH2 are ON           │
│  2. Verify power cable connections to WIB                   │
│  3. Check PSU USB/Serial connection                         │
│  4. Replace power cables if damaged                         │
└─────────────────────────────────────────────────────────────┘
""",
    "voltage_high": """
┌─────────────────────────────────────────────────────────────┐
│  TROUBLESHOOT: VOLTAGE OUT OF RANGE (V > 13.0V)             │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • PSU voltage setting incorrect                            │
│  • PSU malfunction                                          │
│                                                             │
│  Actions:                                                   │
│  1. Check PSU voltage setting (should be 12V)               │
│  2. Verify PSU calibration                                  │
│  3. Try different PSU if available                          │
└─────────────────────────────────────────────────────────────┘
""",
    "current_low": """
┌─────────────────────────────────────────────────────────────┐
│  TROUBLESHOOT: CURRENT TOO LOW (I < 0.5A)                   │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • WIB not powered properly                                 │
│  • WIB not fully seated in slot                             │
│  • Faulty WIB board                                         │
│  • Power connector not fully inserted                       │
│                                                             │
│  Actions:                                                   │
│  1. Power off and reseat WIB board                          │
│  2. Verify correct power connector orientation              │
│  3. Inspect power connector pins                            │
│  4. Check WIB for visible damage                            │
└─────────────────────────────────────────────────────────────┘
""",
    "current_high": """
┌─────────────────────────────────────────────────────────────┐
│  ⚠️  WARNING: CURRENT TOO HIGH (I > 3.0A)                    │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • Short circuit on WIB                                     │
│  • Component failure on WIB                                 │
│  • Wrong voltage setting                                    │
│                                                             │
│  ⚠️  IMMEDIATELY POWER OFF!                                  │
│                                                             │
│  Actions:                                                   │
│  1. POWER OFF IMMEDIATELY                                   │
│  2. Inspect WIB for visible damage/burns                    │
│  3. Check for foreign objects/debris                        │
│  4. DO NOT retry without inspection                         │
└─────────────────────────────────────────────────────────────┘
""",
    "dac_voltage": """
┌─────────────────────────────────────────────────────────────┐
│  TROUBLESHOOT: DAC VOLTAGE TEST FAIL                        │
│  Expected: 0.9V ≤ V ≤ 1.1V                                  │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • DAC chip (U12) malfunction                               │
│  • TCP communication failure                                │
│  • ADC readback error                                       │
│  • Calibration path damaged                                 │
│                                                             │
│  Actions:                                                   │
│  1. Verify TCP connection (run Test01 first)                │
│  2. Check DAC SPI signals with oscilloscope                 │
│  3. Measure DAC output directly at test points              │
│  4. If single slot fails, check path to that connector      │
└─────────────────────────────────────────────────────────────┘
""",
    "reference_voltage": """
┌─────────────────────────────────────────────────────────────┐
│  TROUBLESHOOT: REFERENCE VOLTAGE TEST FAIL                  │
│  Expected: 1.6V ≤ V ≤ 1.7V                                  │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • Reference voltage generator failure                      │
│  • CAL_PULSE_GEN switch not responding                      │
│  • Path selection issue                                     │
│                                                             │
│  Actions:                                                   │
│  1. Measure 1.65V reference at source                       │
│  2. Check CAL_PULSE_GEN control signal                      │
│  3. Verify switch IC operation                              │
└─────────────────────────────────────────────────────────────┘
""",
    "path_control": """
┌─────────────────────────────────────────────────────────────┐
│  TROUBLESHOOT: PATH CONTROL TEST FAIL                       │
│  Expected: 0.5V ≤ V ≤ 0.55V                                 │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • DAC_SRC_SEL switch failure                               │
│  • Cross-talk between slots                                 │
│  • Signal path discontinuity                                │
│                                                             │
│  Actions:                                                   │
│  1. Check DAC_SRC_SEL_BRD0-3 control signals                │
│  2. Verify switch IC (analog multiplexer) operation         │
│  3. Check for solder bridges on switch ICs                  │
│  4. Trace path from DAC to failing slot                     │
└─────────────────────────────────────────────────────────────┘
""",
    "lemo_p5": """
┌─────────────────────────────────────────────────────────────┐
│  TROUBLESHOOT: LEMO P5 INJECTION TEST FAIL                  │
│  Expected: 0.7V ≤ V ≤ 0.85V                                 │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • LEMO P5 connector damaged                                │
│  • External calibration pulse path issue                    │
│  • Test cable not connected properly                        │
│                                                             │
│  Actions:                                                   │
│  1. Check LEMO P5 cable connection                          │
│  2. Verify LEMO connector for damage                        │
│  3. Test continuity of calibration cable                    │
│  4. Try different test cable                                │
└─────────────────────────────────────────────────────────────┘
""",
    "test_points": """
┌─────────────────────────────────────────────────────────────┐
│  TROUBLESHOOT: TEST POINTS FAIL                             │
│  Expected: 0.0V ≤ V ≤ 0.5V (floating state)                 │
├─────────────────────────────────────────────────────────────┤
│  Possible Causes:                                           │
│  • Residual voltage on path                                 │
│  • Switch not fully disconnecting                           │
│  • Leakage current                                          │
│  • Test probe still connected                               │
│                                                             │
│  Actions:                                                   │
│  1. Remove all test probes from test points                 │
│  2. Wait for capacitors to discharge                        │
│  3. Check for high-impedance path issues                    │
└─────────────────────────────────────────────────────────────┘
"""
}

# Port mapping for display
PORT_MAP = {0: "P8", 1: "P7", 2: "P6", 3: "P4"}
SLOT_NAMES = ["SLOT0", "SLOT1", "SLOT2", "SLOT3"]

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================
def validate_power(voltage, current, channel):
    """Validate power measurements and show troubleshooting if failed"""
    v_ok = 11.0 <= voltage <= 13.0
    c_ok = 0.5 <= current <= 3.0

    if not v_ok:
        if voltage < 11.0:
            print_fail(f"  ✗ CH{channel} Voltage FAIL: {voltage:.3f}V (< 11.0V)")
            print(TROUBLESHOOT["voltage_low"])
        else:
            print_fail(f"  ✗ CH{channel} Voltage FAIL: {voltage:.3f}V (> 13.0V)")
            print(TROUBLESHOOT["voltage_high"])
    else:
        print_pass(f"  ✓ CH{channel} Voltage PASS: {voltage:.3f}V")

    if not c_ok:
        if current < 0.5:
            print_fail(f"  ✗ CH{channel} Current FAIL: {current:.3f}A (< 0.5A)")
            print(TROUBLESHOOT["current_low"])
        else:
            print_fail(f"  ✗ CH{channel} Current FAIL: {current:.3f}A (> 3.0A)")
            print(TROUBLESHOOT["current_high"])
    else:
        print_pass(f"  ✓ CH{channel} Current PASS: {current:.3f}A")

    return v_ok and c_ok

def validate_adc_test(slot_values, test_name, min_v, max_v, troubleshoot_key):
    """Validate ADC readback values and show troubleshooting if failed"""
    all_pass = True
    failed_slots = []

    print(f"\n  {test_name} Results (Expected: {min_v}V - {max_v}V):")
    print("  " + "-" * 50)

    for i, value in enumerate(slot_values):
        in_range = min_v <= value <= max_v
        status = "PASS" if in_range else "FAIL"

        if in_range:
            print_pass(f"    {SLOT_NAMES[i]} ({PORT_MAP[i]}): {value:.4f}V - {status}")
        else:
            print_fail(f"    {SLOT_NAMES[i]} ({PORT_MAP[i]}): {value:.4f}V - {status}")
            all_pass = False
            failed_slots.append((SLOT_NAMES[i], PORT_MAP[i], value))

    if not all_pass:
        print(TROUBLESHOOT[troubleshoot_key])
        print_warning(f"  Failed slots: {', '.join([f'{s[0]}({s[1]})={s[2]:.4f}V' for s in failed_slots])}")

    return all_pass, failed_slots

def retry_prompt(test_name):
    """Prompt user for retry, skip, or exit"""
    print_warning(f"\n  {test_name} has failures.")
    print("  Options:")
    print("    [R] Retry this test")
    print("    [S] Skip and continue")
    print("    [E] Exit test")

    while True:
        choice = input("  Enter choice (R/S/E): ").strip().upper()
        if choice in ['R', 'S', 'E']:
            return choice
        print("  Invalid choice. Please enter R, S, or E.")


psu = rigol.RigolDP800()
psu.safe_power_off()
print_header("Test02: Calibration Path Control - Power On")
print("Turn FM on")
psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
time.sleep(10)

# Measure initial power with validation
print("\n[Step 1] Initial Power Measurement")
v1_start, c1_start = psu.measure(1)
v2_start, c2_start = psu.measure(2)
print(f"Initial Power - Ch1: {v1_start:.3f}V {c1_start:.3f}A, Ch2: {v2_start:.3f}V {c2_start:.3f}A")

# Validate initial power
ch1_ok = validate_power(v1_start, c1_start, 1)
ch2_ok = validate_power(v2_start, c2_start, 2)

if not (ch1_ok and ch2_ok):
    choice = retry_prompt("Initial Power Check")
    if choice == 'E':
        print_fail("Test aborted by user.")
        psu.safe_power_off()
        sys.exit(1)
    elif choice == 'R':
        # Re-measure
        v1_start, c1_start = psu.measure(1)
        v2_start, c2_start = psu.measure(2)
        print(f"Re-measured: Ch1: {v1_start:.3f}V {c1_start:.3f}A, Ch2: {v2_start:.3f}V {c2_start:.3f}A")

# Record initial power measurements
rp_dict.log05_Cal['power_ch1_voltage_start'] = round(v1_start, 3)
rp_dict.log05_Cal['power_ch1_current_start'] = round(c1_start, 3)
rp_dict.log05_Cal['power_ch2_voltage_start'] = round(v2_start, 3)
rp_dict.log05_Cal['power_ch2_current_start'] = round(c2_start, 3)

# Update CSV with initial power measurements
if rp_dict.csv_manager:
    v1_status = "PASS" if 11.0 <= v1_start <= 13.0 else "FAIL"
    c1_status = "PASS" if 0.5 <= c1_start <= 3.0 else "FAIL"
    v2_status = "PASS" if 11.0 <= v2_start <= 13.0 else "FAIL"
    c2_status = "PASS" if 0.5 <= c2_start <= 3.0 else "FAIL"

    rp_dict.csv_manager.batch_update([
        {"item_id": "T02_01", "value": round(v1_start, 3), "status": v1_status},
        {"item_id": "T02_02", "value": round(c1_start, 3), "status": c1_status},
        {"item_id": "T02_03", "value": round(v2_start, 3), "status": v2_status},
        {"item_id": "T02_04", "value": round(c2_start, 3), "status": c2_status}
    ])

time.sleep(20)

time.sleep(1)

# Begin
tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()
now = datetime.datetime.now()
import component.temp as initial
initial

def Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 1):
    DAC_step = 0.00003125
    dac_bit = format(int(set_v / DAC_step), '016b')
    tcp.tcp_poke(addr=0x10, data=0x04)
    time.sleep(0.05)
    tcp.tcp_poke(addr=0x10, data=0x06)
    tcp.tcp_poke(addr=0x10, data=0x04)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    tcp.tcp_poke(addr=0x10, data=0x00)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    for i in dac_bit:
        if i == '0':
            tcp.tcp_poke(addr=0x10, data=0x00)
            tcp.tcp_poke(addr=0x10, data=0x02)
            tcp.tcp_poke(addr=0x10, data=0x00)
        else:
            tcp.tcp_poke(addr=0x10, data=0x01)
            tcp.tcp_poke(addr=0x10, data=0x03)
            tcp.tcp_poke(addr=0x10, data=0x01)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    switch_combine = ((CAL_PULSE_GEN << 4) | (DAC_SRC_SEL_BRD3 << 3) | (DAC_SRC_SEL_BRD2 << 2) | (DAC_SRC_SEL_BRD1 << 1) | (DAC_SRC_SEL_BRD0 << 0))
    switch = (switch_combine << 16 | 4)
    tcp.tcp_poke(addr=0x10, data=switch)

def Set_switch(CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 1, Mon_PULSE_SEL = 1):
    switch_combine = ((CAL_PULSE_GEN << 4) | (DAC_SRC_SEL_BRD3 << 3) | (DAC_SRC_SEL_BRD2 << 2) | (DAC_SRC_SEL_BRD1 << 1) | (DAC_SRC_SEL_BRD0 << 0))
    switch = (switch_combine << 16 | 4)

# def config_switch()
    tcp.tcp_poke(addr=0x12, data=Mon_PULSE_SEL)
    tcp.tcp_poke(addr=0x10, data=switch)

def WIB_ADC_read():
    tcp.tcp_poke(addr=0x11, data=0x01)
    time.sleep(0.05)
    tcp.tcp_poke(addr=0x11, data=0x00)
    channel_Value_0_1 = tcp.tcp_peek(addr = 0x13)
    adc0_v = ((channel_Value_0_1 >>16)&0xffff)*2.5/16384.0
    adc1_v = (channel_Value_0_1 & 0xffff)*2.5/16384.0
    channel_Value_2_3 = tcp.tcp_peek(addr = 0x14)
    adc2_v = ((channel_Value_2_3 >>16)&0xffff)*2.5/16384.0
    adc3_v = (channel_Value_2_3 & 0xffff)*2.5/16384.0
    return adc0_v, adc1_v, adc2_v, adc3_v



# ============================================================================
# TEST 1: DAC Voltage Test (Expected: 1V)
# ============================================================================
test1_pass = False
while True:
    print_header("[Step 2] Test 1: DAC Voltage Test")
    Set_DAC(set_v = 1)
    time.sleep(0.5)
    slot0, slot1, slot2, slot3 = WIB_ADC_read()
    time.sleep(0.5)

    # test 1 V, expected output [1 1 1 1]
    Set_switch(CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 1, Mon_PULSE_SEL = 1)
    time.sleep(0.5)
    Set_DAC(set_v = 1)
    Set_DAC(set_v = 1)
    Set_DAC(set_v = 1)
    Set_DAC(set_v = 1)
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    time.sleep(1)
    slot0, slot1, slot2, slot3 = WIB_ADC_read()

    # Validate DAC Voltage Test
    test1_pass, test1_failed = validate_adc_test(
        [slot0, slot1, slot2, slot3],
        "Test 1: DAC Voltage (1V)",
        0.9, 1.1,
        "dac_voltage"
    )

    rp_dict.log05_Cal['1v_slot_0_P8'] = round(slot0, 4)
    rp_dict.log05_Cal['1v_slot_1_P7'] = round(slot1, 4)
    rp_dict.log05_Cal['1v_slot_2_P6'] = round(slot2, 4)
    rp_dict.log05_Cal['1v_slot_3_P4'] = round(slot3, 4)

    # Update CSV with DAC configuration and ADC readback
    if rp_dict.csv_manager:
        t1_status = "PASS" if test1_pass else "FAIL"
        rp_dict.csv_manager.batch_update([
            {"item_id": "T02_05", "value": "0x0001", "status": "SET"},  # DAC 0 config
            {"item_id": "T02_06", "value": "0x0001", "status": "SET"},  # DAC 1 config
            {"item_id": "T02_07", "value": "0x0001", "status": "SET"},  # DAC 2 config
            {"item_id": "T02_08", "value": "0x0001", "status": "SET"},  # DAC 3 config
            {"item_id": "T02_09", "value": round(slot0, 4), "status": t1_status},  # ADC 0
            {"item_id": "T02_10", "value": round(slot1, 4), "status": t1_status},  # ADC 1
            {"item_id": "T02_11", "value": round(slot2, 4), "status": t1_status},  # ADC 2
            {"item_id": "T02_12", "value": round(slot3, 4), "status": t1_status}   # ADC 3
        ])

    if test1_pass:
        break  # Test passed, continue to next
    else:
        choice = retry_prompt("Test 1: DAC Voltage")
        if choice == 'R':
            print_warning("  Retrying Test 1...")
            continue  # Retry the test
        elif choice == 'E':
            print_fail("Test aborted by user.")
            psu.safe_power_off()
            sys.exit(1)
        else:  # 'S' - Skip
            print_warning("  Skipping Test 1...")
            break

time.sleep(0.5)

# ============================================================================
# TEST t1: Reference Voltage Test (Expected: 1.65V)
# ============================================================================
test_t1_pass = False
while True:
    print_header("[Step 3] Test t1: Reference Voltage Test")
    Set_switch(CAL_PULSE_GEN = 0, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 1, Mon_PULSE_SEL = 1)
    time.sleep(1)
    WIB_ADC_read()
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 0)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 0)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 0)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 0)
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    time.sleep(1)
    slot0, slot1, slot2, slot3 = WIB_ADC_read()

    # Validate Reference Voltage Test
    test_t1_pass, test_t1_failed = validate_adc_test(
        [slot0, slot1, slot2, slot3],
        "Test t1: Reference Voltage (1.65V)",
        1.6, 1.7,
        "reference_voltage"
    )

    rp_dict.log05_Cal['1_6v_slot_0_P8'] = round(slot0, 4)
    rp_dict.log05_Cal['1_6v_slot_1_P7'] = round(slot1, 4)
    rp_dict.log05_Cal['1_6v_slot_2_P6'] = round(slot2, 4)
    rp_dict.log05_Cal['1_6v_slot_3_P4'] = round(slot3, 4)

    if test_t1_pass:
        break  # Test passed, continue to next
    else:
        choice = retry_prompt("Test t1: Reference Voltage")
        if choice == 'R':
            print_warning("  Retrying Test t1...")
            continue  # Retry the test
        elif choice == 'E':
            print_fail("Test aborted by user.")
            psu.safe_power_off()
            sys.exit(1)
        else:  # 'S' - Skip
            print_warning("  Skipping Test t1...")
            break

# ============================================================================
# TEST t2: Path Control Test A (SLOT0/2 output, SLOT1/3 input)
# ============================================================================
test_t2_pass = False
while True:
    print_header("[Step 4] Test t2: Path Control A (SLOT0/2 → SLOT1/3)")
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 0)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 0)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 0)
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    time.sleep(1)
    slot0, slot1, slot2, slot3 = WIB_ADC_read()

    # Validate Path Control Test A
    test_t2_pass, test_t2_failed = validate_adc_test(
        [slot0, slot1, slot2, slot3],
        "Test t2: Path Control A (0.5V)",
        0.5, 0.55,
        "path_control"
    )

    rp_dict.log05_Cal['0123_slot_0_P8'] = round(slot0, 4)
    rp_dict.log05_Cal['0123_slot_1_P7'] = round(slot1, 4)
    rp_dict.log05_Cal['0123_slot_2_P6'] = round(slot2, 4)
    rp_dict.log05_Cal['0123_slot_3_P4'] = round(slot3, 4)

    if test_t2_pass:
        break  # Test passed, continue to next
    else:
        choice = retry_prompt("Test t2: Path Control A")
        if choice == 'R':
            print_warning("  Retrying Test t2...")
            continue  # Retry the test
        elif choice == 'E':
            print_fail("Test aborted by user.")
            psu.safe_power_off()
            sys.exit(1)
        else:  # 'S' - Skip
            print_warning("  Skipping Test t2...")
            break

# ============================================================================
# TEST t3: Path Control Test B (SLOT0/2 input, SLOT1/3 output)
# ============================================================================
test_t3_pass = False
while True:
    print_header("[Step 5] Test t3: Path Control B (SLOT1/3 → SLOT0/2)")
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    time.sleep(1)
    slot0, slot1, slot2, slot3 = WIB_ADC_read()

    # Validate Path Control Test B
    test_t3_pass, test_t3_failed = validate_adc_test(
        [slot0, slot1, slot2, slot3],
        "Test t3: Path Control B (0.5V)",
        0.5, 0.55,
        "path_control"
    )

    rp_dict.log05_Cal['3210_slot_0_P8'] = round(slot0, 4)
    rp_dict.log05_Cal['3210_slot_1_P7'] = round(slot1, 4)
    rp_dict.log05_Cal['3210_slot_2_P6'] = round(slot2, 4)
    rp_dict.log05_Cal['3210_slot_3_P4'] = round(slot3, 4)

    if test_t3_pass:
        break  # Test passed, continue to next
    else:
        choice = retry_prompt("Test t3: Path Control B")
        if choice == 'R':
            print_warning("  Retrying Test t3...")
            continue  # Retry the test
        elif choice == 'E':
            print_fail("Test aborted by user.")
            psu.safe_power_off()
            sys.exit(1)
        else:  # 'S' - Skip
            print_warning("  Skipping Test t3...")
            break

# ============================================================================
# TEST t4: LEMO P5 Injection Test (Expected: 0.8V)
# ============================================================================
test_t4_pass = False
first_t4_attempt = True
while True:
    print_header("[Step 6] Test t4: LEMO P5 Injection Test")
    if first_t4_attempt:
        pop.show_image_popup(
            title="Page 7: Test P5",
            image_path=os.path.join(IMG_DIR, "7.png") if os.path.exists(os.path.join(IMG_DIR, "7.png")) else None
        )
        first_t4_attempt = False

    Set_DAC(set_v = 1, CAL_PULSE_GEN = 0, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 0, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
    Set_DAC(set_v = 1, CAL_PULSE_GEN = 0, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    time.sleep(1)
    slot0, slot1, slot2, slot3 = WIB_ADC_read()

    # Validate LEMO P5 Injection Test
    test_t4_pass, test_t4_failed = validate_adc_test(
        [slot0, slot1, slot2, slot3],
        "Test t4: LEMO P5 Injection (0.8V)",
        0.7, 0.85,
        "lemo_p5"
    )

    rp_dict.log05_Cal['P5_slot_0_P8'] = round(slot0, 4)
    rp_dict.log05_Cal['P5_slot_1_P7'] = round(slot1, 4)
    rp_dict.log05_Cal['P5_slot_2_P6'] = round(slot2, 4)
    rp_dict.log05_Cal['P5_slot_3_P4'] = round(slot3, 4)

    if test_t4_pass:
        break  # Test passed, continue to next
    else:
        choice = retry_prompt("Test t4: LEMO P5 Injection")
        if choice == 'R':
            print_warning("  Retrying Test t4...")
            continue  # Retry the test
        elif choice == 'E':
            print_fail("Test aborted by user.")
            psu.safe_power_off()
            sys.exit(1)
        else:  # 'S' - Skip
            print_warning("  Skipping Test t4...")
            break

# ============================================================================
# TEST t5/t6: Test Points (Floating state, Expected: 0V)
# ============================================================================
test_t5_pass = False
first_t5_attempt = True
while True:
    print_header("[Step 7] Test t5/t6: Test Points (Floating)")
    if first_t5_attempt:
        pop.show_image_popup(
            title="Page 8: Test Float Voltage",
            image_path=os.path.join(IMG_DIR, "8.png") if os.path.exists(os.path.join(IMG_DIR, "8.png")) else None
        )
        first_t5_attempt = False

    Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 0)
    time.sleep(0.5)
    Set_switch(CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 0, Mon_PULSE_SEL = 0)
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    WIB_ADC_read()
    time.sleep(1.5)
    slot0, slot1, slot2, slot3 = WIB_ADC_read()

    # Validate Test Points
    test_t5_pass, test_t5_failed = validate_adc_test(
        [slot0, slot1, slot2, slot3],
        "Test t5/t6: Test Points (0V)",
        0.0, 0.5,
        "test_points"
    )

    rp_dict.log05_Cal['TP_slot_0_P8'] = round(slot0, 4)
    rp_dict.log05_Cal['TP_slot_1_P7'] = round(slot1, 4)
    rp_dict.log05_Cal['TP_slot_2_P6'] = round(slot2, 4)
    rp_dict.log05_Cal['TP_slot_3_P4'] = round(slot3, 4)
    tcp.tcp_cmd_io(cmd=0x02, aux=0, addr=0x08, data=0xFFFFFFFF)

    if test_t5_pass:
        break  # Test passed, continue to next
    else:
        choice = retry_prompt("Test t5/t6: Test Points")
        if choice == 'R':
            print_warning("  Retrying Test t5/t6...")
            continue  # Retry the test
        elif choice == 'E':
            print_fail("Test aborted by user.")
            psu.safe_power_off()
            sys.exit(1)
        else:  # 'S' - Skip
            print_warning("  Skipping Test t5/t6...")
            break

# ============================================================================
# FINAL POWER MEASUREMENT
# ============================================================================
print_header("[Step 8] Final Power Measurement")
v1_end, c1_end = psu.measure(1)
v2_end, c2_end = psu.measure(2)
print(f"Final Power - Ch1: {v1_end:.3f}V {c1_end:.3f}A, Ch2: {v2_end:.3f}V {c2_end:.3f}A")

# Validate final power
ch1_end_ok = validate_power(v1_end, c1_end, 1)
ch2_end_ok = validate_power(v2_end, c2_end, 2)

# Record final power measurements
rp_dict.log05_Cal['power_ch1_voltage_end'] = round(v1_end, 3)
rp_dict.log05_Cal['power_ch1_current_end'] = round(c1_end, 3)
rp_dict.log05_Cal['power_ch2_voltage_end'] = round(v2_end, 3)
rp_dict.log05_Cal['power_ch2_current_end'] = round(c2_end, 3)

# Calculate total power
total_power = (v1_end * c1_end) + (v2_end * c2_end)
rp_dict.log05_Cal['total_power'] = round(total_power, 3)

t2 = time.time()
test_duration = round(t2-t1, 3)

rp_dict.log05_Cal['Communication_Time_Consumption'] = test_duration

# ============================================================================
# TEST SUMMARY
# ============================================================================
print_header("Test02: Calibration Path Control - SUMMARY")

# Collect all test results
all_tests = [
    ("Test 1: DAC Voltage (1V)", test1_pass),
    ("Test t1: Reference Voltage (1.65V)", test_t1_pass),
    ("Test t2: Path Control A", test_t2_pass),
    ("Test t3: Path Control B", test_t3_pass),
    ("Test t4: LEMO P5 Injection", test_t4_pass),
    ("Test t5/t6: Test Points", test_t5_pass),
    ("Final Power Check", ch1_end_ok and ch2_end_ok),
]

print("\n  Test Results:")
print("  " + "=" * 50)
passed_count = 0
failed_count = 0
for test_name, test_result in all_tests:
    if test_result:
        print_pass(f"    [PASS] {test_name}")
        passed_count += 1
    else:
        print_fail(f"    [FAIL] {test_name}")
        failed_count += 1

print("  " + "=" * 50)
overall_pass = failed_count == 0
if overall_pass:
    print_pass(f"\n  OVERALL RESULT: PASS ({passed_count}/{len(all_tests)} tests passed)")
else:
    print_fail(f"\n  OVERALL RESULT: FAIL ({failed_count} test(s) failed)")

print(f"\n  Test Duration: {test_duration} seconds")
print(f"  Total Power: {total_power:.3f} W")

# Update CSV with final power measurements and test duration
if rp_dict.csv_manager:
    v1_end_status = "PASS" if 11.0 <= v1_end <= 13.0 else "FAIL"
    c1_end_status = "PASS" if 0.5 <= c1_end <= 3.0 else "FAIL"
    v2_end_status = "PASS" if 11.0 <= v2_end <= 13.0 else "FAIL"
    c2_end_status = "PASS" if 0.5 <= c2_end <= 3.0 else "FAIL"

    rp_dict.csv_manager.batch_update([
        {"item_id": "T02_13", "value": round(v1_end, 3), "status": v1_end_status},
        {"item_id": "T02_14", "value": round(c1_end, 3), "status": c1_end_status},
        {"item_id": "T02_15", "value": round(v2_end, 3), "status": v2_end_status},
        {"item_id": "T02_16", "value": round(c2_end, 3), "status": c2_end_status},
        {"item_id": "T02_17", "value": round(total_power, 3), "status": "PASS"},
        {"item_id": "T02_18", "value": test_duration, "status": "COMPLETE"}
    ])
# time < 40 seconds

psu.safe_power_off()

import os

# === Setup relative path to ../file/Calibration_report_02.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_02_Calibration_report_02.html")
print(target_file_path)

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Collect values
cal = rp_dict.log05_Cal

# Define test thresholds for validation
test_configs = [
    {
        "name": "DAC Voltage Test",
        "description": "Test Four SLOT with DAC voltage (1V expected)",
        "slots": ['1v_slot_0_P8', '1v_slot_1_P7', '1v_slot_2_P6', '1v_slot_3_P4'],
        "min": 0.9, "max": 1.1
    },
    {
        "name": "Reference Voltage Test",
        "description": "Test Four SLOT with Ref voltage (1.65V expected)",
        "slots": ['1_6v_slot_0_P8', '1_6v_slot_1_P7', '1_6v_slot_2_P6', '1_6v_slot_3_P4'],
        "min": 1.6, "max": 1.7
    },
    {
        "name": "Path Control Test A",
        "description": "SLOT0/2 output, SLOT1/3 input with DAC voltage",
        "slots": ['0123_slot_0_P8', '0123_slot_1_P7', '0123_slot_2_P6', '0123_slot_3_P4'],
        "min": 0.5, "max": 0.55
    },
    {
        "name": "Path Control Test B",
        "description": "SLOT0/2 input, SLOT1/3 output with DAC voltage",
        "slots": ['3210_slot_0_P8', '3210_slot_1_P7', '3210_slot_2_P6', '3210_slot_3_P4'],
        "min": 0.5, "max": 0.55
    },
    {
        "name": "LEMO P5 Injection Test",
        "description": "Test LEMO P5 Calibration pulse injection",
        "slots": ['P5_slot_0_P8', 'P5_slot_1_P7', 'P5_slot_2_P6', 'P5_slot_3_P4'],
        "min": 0.7, "max": 0.85
    },
    {
        "name": "Test Points",
        "description": "Test Points measurement",
        "slots": ['TP_slot_0_P8', 'TP_slot_1_P7', 'TP_slot_2_P6', 'TP_slot_3_P4'],
        "min": 0.0, "max": 0.5
    }
]

# Validate all measurements
all_passed = True
for test in test_configs:
    for slot_key in test['slots']:
        value = cal.get(slot_key, 0)
        if not (test['min'] <= value <= test['max']):
            all_passed = False
            break

# Validate power measurements
ch1_current = cal.get('power_ch1_current_end', 0)
ch2_current = cal.get('power_ch2_current_end', 0)
total_power = cal.get('total_power', 0)

power_passed = True
if not (0.5 <= ch1_current <= 3.0):
    power_passed = False
if not (0.5 <= ch2_current <= 3.0):
    power_passed = False
if not (4.0 <= total_power <= 30.0):
    power_passed = False

# Overall status includes both calibration tests and power check
overall_status = "PASS" if (all_passed and power_passed) else "FAIL"
overall_status_class = "pass" if (all_passed and power_passed) else "fail"

# HTML content with professional styling (Clean & Simple)
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB Calibration Path Control Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #ffffff;
            color: #000000;
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
        }}

        /* Header Section */
        .header {{
            border-bottom: 3px solid #000000;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 24px;
            font-weight: bold;
            color: #000000;
            margin-bottom: 5px;
        }}
        .header .subtitle {{
            font-size: 14px;
            color: #666666;
        }}

        /* Status Badge */
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 16px;
            margin-top: 15px;
            border: 2px solid;
        }}
        .status-badge.pass {{
            color: #166534;
            background-color: #dcfce7;
            border-color: #166534;
        }}
        .status-badge.fail {{
            color: #991b1b;
            background-color: #fee2e2;
            border-color: #991b1b;
        }}

        /* Info Section */
        .info-section {{
            margin: 20px 0;
            padding: 15px;
            background: #f9fafb;
            border-left: 4px solid #000000;
        }}
        .info-row {{
            display: flex;
            margin: 8px 0;
        }}
        .info-label {{
            font-weight: bold;
            width: 150px;
            color: #000000;
        }}
        .info-value {{
            color: #374151;
        }}

        /* Test Section */
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #000000;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            border: 1px solid #000000;
        }}
        th {{
            background-color: #f3f4f6;
            color: #000000;
            font-weight: bold;
            text-align: left;
            padding: 12px;
            border: 1px solid #000000;
        }}
        td {{
            padding: 12px;
            border: 1px solid #d1d5db;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        .status-cell {{
            font-weight: bold;
            text-align: center;
        }}
        .status-pass {{
            color: #166534;
        }}
        .status-fail {{
            color: #991b1b;
        }}
        .error-cell {{
            background: #fee2e2 !important;
            color: #991b1b !important;
            font-weight: bold;
        }}

        /* Test Description Box */
        .test-description {{
            margin: 10px 0;
            padding: 10px;
            background: #fafafa;
            border-left: 3px solid #9ca3af;
            font-size: 14px;
            color: #4b5563;
        }}

        /* Footer */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
        }}

        /* Print Styles */
        @media print {{
            body {{
                padding: 0;
            }}
            .container {{
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>DUNE WIB Quality Control</h1>
            <div class="subtitle">Calibration Path Control Test Report (Test02)</div>
            <div class="status-badge {overall_status_class}">Overall Status: {overall_status}</div>
        </div>

        <!-- Test Information -->
        <div class="info-section">
            <div class="info-row">
                <div class="info-label">Test Date:</div>
                <div class="info-value">{now.strftime("%Y-%m-%d %H:%M:%S UTC")}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Total Test Time:</div>
                <div class="info-value">{cal['Communication_Time_Consumption']} seconds</div>
            </div>
            <div class="info-row">
                <div class="info-label">Test Items:</div>
                <div class="info-value">6 calibration path tests, 24 total measurements</div>
            </div>
        </div>

        <!-- Power Measurements -->
        <div class="section">
            <div class="section-title">Power Supply Measurements</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 20%;">Channel</th>
                        <th style="width: 20%;">Voltage (V)</th>
                        <th style="width: 20%;">Current (A)</th>
                        <th style="width: 20%;">Power (W)</th>
                        <th style="width: 20%;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Channel 1</strong></td>
                        <td>{cal.get('power_ch1_voltage_end', 0):.3f} V</td>
                        <td>{cal.get('power_ch1_current_end', 0):.3f} A</td>
                        <td>{(cal.get('power_ch1_voltage_end', 0) * cal.get('power_ch1_current_end', 0)):.3f} W</td>
                        <td class="status-cell status-{'pass' if 0.5 <= cal.get('power_ch1_current_end', 0) <= 3.0 else 'fail'}">
                            {'PASS' if 0.5 <= cal.get('power_ch1_current_end', 0) <= 3.0 else 'FAIL'}
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Channel 2</strong></td>
                        <td>{cal.get('power_ch2_voltage_end', 0):.3f} V</td>
                        <td>{cal.get('power_ch2_current_end', 0):.3f} A</td>
                        <td>{(cal.get('power_ch2_voltage_end', 0) * cal.get('power_ch2_current_end', 0)):.3f} W</td>
                        <td class="status-cell status-{'pass' if 0.5 <= cal.get('power_ch2_current_end', 0) <= 3.0 else 'fail'}">
                            {'PASS' if 0.5 <= cal.get('power_ch2_current_end', 0) <= 3.0 else 'FAIL'}
                        </td>
                    </tr>
                    <tr style="background-color: #f3f4f6; font-weight: bold;">
                        <td><strong>TOTAL</strong></td>
                        <td colspan="2"></td>
                        <td>{cal.get('total_power', 0):.3f} W</td>
                        <td class="status-cell status-{'pass' if 4.0 <= cal.get('total_power', 0) <= 30.0 else 'fail'}">
                            {'PASS' if 4.0 <= cal.get('total_power', 0) <= 30.0 else 'FAIL'}
                        </td>
                    </tr>
                </tbody>
            </table>
            <div class="test-description">
                <strong>Note:</strong> Power measurements taken at test completion. Expected current range: 0.5-3.0A per channel. Total power range: 4.0-30.0W.
            </div>
        </div>

        <!-- Test Results Summary -->
        <div class="section">
            <div class="section-title">Test Results Summary</div>"""

# Generate table for each test configuration
for idx, test in enumerate(test_configs, 1):
    # Check if this test passed
    test_passed = all(test['min'] <= cal.get(slot_key, 0) <= test['max'] for slot_key in test['slots'])

    html_content += f"""
            <div class="test-description">
                <strong>Test {idx}: {test['name']}</strong> - {test['description']}
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 20%;">SLOT</th>
                        <th style="width: 20%;">Measured (V)</th>
                        <th style="width: 30%;">Expected Range (V)</th>
                        <th style="width: 15%;">Status</th>
                        <th style="width: 15%;">Port</th>
                    </tr>
                </thead>
                <tbody>"""

    slot_names = ['SLOT0', 'SLOT1', 'SLOT2', 'SLOT3']
    port_names = ['P8', 'P7', 'P6', 'P4']

    for slot_idx, slot_key in enumerate(test['slots']):
        value = cal.get(slot_key, 0)
        in_range = test['min'] <= value <= test['max']
        status_text = "PASS" if in_range else "FAIL"
        status_class = "status-pass" if in_range else "status-fail"
        error_class = "" if in_range else ' class="error-cell"'

        html_content += f"""
                    <tr>
                        <td><strong>{slot_names[slot_idx]}</strong></td>
                        <td{error_class}>{value:.4f} V</td>
                        <td>{test['min']:.2f} - {test['max']:.2f} V</td>
                        <td class="status-cell {status_class}">{status_text}</td>
                        <td>{port_names[slot_idx]}</td>
                    </tr>"""

    html_content += """
                </tbody>
            </table>"""

html_content += f"""
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>DUNE WIB Quality Control System - Test02 Calibration Path Control</p>
            <p>Report generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
        </div>
    </div>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved (new file) to {target_file_path}")

