# -*- coding: utf-8 -*-
"""
Test Thresholds Configuration
DUNE WIB Quality Control System

This file contains all threshold values for quality control tests.
You can modify these values according to your requirements.

Last modified: 2025-12-18
"""

# ============================================
# Power Rail Thresholds
# ============================================

# Voltage tolerance (V)
VOLTAGE_TOLERANCE = 0.2  # ±0.2V from set value

# Current reference values and tolerances (A)
CURRENT_THRESHOLDS = {
    # Format: {rail_name: (reference_current, tolerance)}
    "FE": {
        "I_ref": 0.42,      # Reference current for FE (LArASIC)
        "tolerance": 0.1,   # ±0.1A
        "I_ref_alt": 0.63,  # Alternative reference (for different config)
        "tolerance_alt": 0.1
    },
    "ADC": {
        "I_ref": 1.6,       # Reference current for ADC (ColdADC)
        "tolerance": 0.2    # ±0.2A
    },
    "CD": {
        "I_ref": 0.2,       # Reference current for CD (COLDATA)
        "tolerance": 0.1    # ±0.1A
    },
    "BIAS": {
        "I_ref": 0.05,      # Reference current for BIAS
        "tolerance": 0.1    # ±0.1A
    }
}

# Total power consumption limits (W)
POWER_LIMITS = {
    "SEOFF": {
        "min": 4.0,         # Minimum expected power (W)
        "max": 7.0          # Maximum expected power (W)
    },
    "SEON_SDC": {
        "min": 4.5,
        "max": 7.5
    },
    "DIFF": {
        "min": 4.5,
        "max": 7.5
    }
}

# ============================================
# ADC Monitoring Thresholds (mV)
# ============================================

ADC_VOLTAGE_THRESHOLDS = {
    "VCMI": {
        "min": 800,         # Minimum VCMI voltage (mV)
        "max": 1200         # Maximum VCMI voltage (mV)
    },
    "VCMO": {
        "min": 800,
        "max": 1200
    },
    "VREFP": {
        "min": 1600,
        "max": 2400
    },
    "VREFN": {
        "min": 100,
        "max": 400
    }
}

# ============================================
# Channel Response Thresholds
# ============================================

CHANNEL_THRESHOLDS = {
    "rms_noise": {
        "max": 5.0          # Maximum RMS noise (ADC bins)
    },
    "pedestal": {
        "min": 2000,        # Minimum pedestal value
        "max": 14000        # Maximum pedestal value
    },
    "response": {
        "min_amplitude": 500  # Minimum pulse amplitude
    }
}

# ============================================
# Timing Performance Thresholds (seconds)
# ============================================

TIMING_THRESHOLDS = {
    "total_test_time": {
        "max": 180          # Maximum total test time (3 minutes)
    },
    "power_startup": {
        "max": 30
    },
    "network_check": {
        "max": 10
    },
    "wib_init": {
        "max": 15
    },
    "seoff_test": {
        "max": 30
    },
    "seon_test": {
        "max": 30
    },
    "diff_test": {
        "max": 30
    },
    "data_acquisition": {
        "max": 60
    }
}

# ============================================
# Reception Checkout Thresholds
# ============================================

RECEPTION_CURRENT_LIMITS = {
    "channel_1": {
        "min": 0.5,         # Minimum current (A)
        "max": 2.0          # Maximum current (A)
    },
    "channel_2": {
        "min": 0.5,
        "max": 2.0
    }
}

# ============================================
# Helper Functions
# ============================================

def check_voltage_in_range(v_set, v_meas):
    """Check if measured voltage is within tolerance of set voltage"""
    return abs(v_set - v_meas) <= VOLTAGE_TOLERANCE

def check_current_in_range(rail_name, i_meas, i_ref=None):
    """
    Check if measured current is within tolerance

    Args:
        rail_name: "FE", "ADC", "CD", or "BIAS"
        i_meas: Measured current
        i_ref: Optional reference current (if not using default)

    Returns:
        (bool, str): (is_ok, error_message)
    """
    if rail_name not in CURRENT_THRESHOLDS:
        return False, f"Unknown rail: {rail_name}"

    threshold = CURRENT_THRESHOLDS[rail_name]
    ref = i_ref if i_ref is not None else threshold["I_ref"]
    tol = threshold["tolerance"]

    # Check alternative reference for FE
    if rail_name == "FE" and abs(threshold["I_ref_alt"] - i_meas) <= threshold["tolerance_alt"]:
        return True, ""

    if abs(ref - i_meas) <= tol:
        return True, ""
    else:
        return False, f"{rail_name}: I_meas={i_meas:.3f}A, expected {ref:.3f}±{tol:.3f}A"

def check_power_in_range(mode, power):
    """
    Check if total power consumption is within expected range

    Args:
        mode: "SEOFF", "SEON_SDC", or "DIFF"
        power: Total power consumption (W)

    Returns:
        (bool, str): (is_ok, error_message)
    """
    if mode not in POWER_LIMITS:
        return False, f"Unknown mode: {mode}"

    limits = POWER_LIMITS[mode]
    if limits["min"] <= power <= limits["max"]:
        return True, ""
    else:
        return False, f"{mode}: Power={power:.3f}W, expected {limits['min']:.1f}-{limits['max']:.1f}W"

def check_adc_voltage(param_name, value_mv):
    """
    Check if ADC voltage parameter is within range

    Args:
        param_name: "VCMI", "VCMO", "VREFP", or "VREFN"
        value_mv: Measured value in mV

    Returns:
        (bool, str): (is_ok, error_message)
    """
    if param_name not in ADC_VOLTAGE_THRESHOLDS:
        return False, f"Unknown parameter: {param_name}"

    limits = ADC_VOLTAGE_THRESHOLDS[param_name]
    if limits["min"] <= value_mv <= limits["max"]:
        return True, ""
    else:
        return False, f"{param_name}={value_mv}mV, expected {limits['min']}-{limits['max']}mV"

# ============================================
# Export thresholds summary
# ============================================

def get_thresholds_summary():
    """Return a dictionary of all thresholds for CSV export"""
    return {
        "voltage_tolerance": VOLTAGE_TOLERANCE,
        "current_thresholds": CURRENT_THRESHOLDS,
        "power_limits": POWER_LIMITS,
        "adc_voltage_thresholds": ADC_VOLTAGE_THRESHOLDS,
        "channel_thresholds": CHANNEL_THRESHOLDS,
        "timing_thresholds": TIMING_THRESHOLDS,
        "reception_current_limits": RECEPTION_CURRENT_LIMITS
    }
