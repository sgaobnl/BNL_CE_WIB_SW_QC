import subprocess

process1 = subprocess.Popen(["python", "CTS_FEMB_QC_top.py"])
process2 = subprocess.Popen(["python", "Real_Time_Monitor.py"])

process1.wait()
process2.wait()
