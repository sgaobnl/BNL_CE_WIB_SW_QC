#!/usr/bin/env python3
"""
Alternative: Run monitor completely in background without terminal window
"""

import os
import sys
from pathlib import Path

# Get script directory
ROOT_DIR = Path(__file__).parent
MONITOR_SCRIPT = ROOT_DIR / "CTS_Real_Time_Monitor.py"
LOG_FILE = ROOT_DIR / "monitor_output.log"

# Kill old process
os.system(f'pkill -f "{MONITOR_SCRIPT.name}"')
os.system('sleep 1')

# Run in background, redirect output to log file
print(f"Starting monitor in background...")
print(f"Log file: {LOG_FILE}")
os.system(f'nohup python3 {MONITOR_SCRIPT} > {LOG_FILE} 2>&1 &')
print("✓ Monitor running in background")
print(f"  View live: tail -f {LOG_FILE}")
print(f"  Stop:      pkill -f {MONITOR_SCRIPT.name}")
