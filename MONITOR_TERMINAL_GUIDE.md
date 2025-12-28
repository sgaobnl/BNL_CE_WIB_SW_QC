# Monitor Terminal Configuration Guide

## 🖥️ Current Configuration

The monitoring terminal (`CTS_Real_Time_Monitor.py`) is now configured to:
- ✅ Launch automatically when main program starts
- ✅ **Auto-minimize** to taskbar
- ✅ Positioned on right side when restored
- ✅ Named "CTS Monitor" for easy identification

## 🎯 How It Works

### 1. **Terminal Launch**
```python
gnome-terminal --title="CTS Monitor" --geometry=80x40-0+0 \
  --working-directory="{current_dir}" \
  -- bash -c "python3 {script}; exec bash" &
```

- `--title="CTS Monitor"`: Sets window title for identification
- `--geometry=80x40-0+0`: 80 columns × 40 rows, positioned at right-top
- Runs in background (`&`)

### 2. **Auto-Minimize**
```python
time.sleep(0.5)  # Wait for terminal to open
wmctrl -r "CTS Monitor" -b add,hidden
```

- Waits 0.5 seconds for window to appear
- Uses `wmctrl` to minimize window by title
- Falls back to `xdotool` if `wmctrl` fails

## 📋 Usage

### **Restore Monitor Terminal**
Click on "CTS Monitor" in your taskbar, or:
```bash
wmctrl -r "CTS Monitor" -b remove,hidden
```

### **Manually Minimize**
```bash
wmctrl -r "CTS Monitor" -b add,hidden
```

### **Check If Running**
```bash
ps aux | grep CTS_Real_Time_Monitor.py
```

### **Kill Monitor Process**
```bash
pkill -f CTS_Real_Time_Monitor.py
```

## ⚙️ Configuration Options

### **Option 1: Keep Terminal Visible (No Auto-Minimize)**
Comment out the minimize command:
```python
# os.system('wmctrl -r "CTS Monitor" -b add,hidden ...')
```

### **Option 2: Different Position**
Modify geometry parameter:
```python
# Left side
--geometry=80x40+0+0

# Right side (current)
--geometry=80x40-0+0

# Center (approximate)
--geometry=80x40+500+100

# Larger window
--geometry=100x50-0+0
```

### **Option 3: Run Completely Hidden (Background)**
Replace terminal launch with direct script execution:
```python
os.system(f'nohup python3 {script} > /tmp/cts_monitor.log 2>&1 &')
```

### **Option 4: Adjust Minimize Delay**
If window doesn't minimize reliably:
```python
time.sleep(1.0)  # Increase from 0.5 to 1.0 seconds
```

## 🔧 Troubleshooting

### **Monitor Doesn't Minimize**
**Cause**: Terminal window takes longer to appear

**Solution**: Increase sleep time
```python
time.sleep(1.0)  # or even 1.5
```

### **"CTS Monitor" Not Found**
**Check if terminal launched**:
```bash
wmctrl -l | grep "CTS Monitor"
```

**If not found**, window might have different title:
```bash
wmctrl -l  # List all windows
```

### **Tools Not Installed** (shouldn't happen on this system)
```bash
# Install wmctrl
sudo apt-get install wmctrl

# Install xdotool
sudo apt-get install xdotool
```

### **Want to See Monitor Output**
1. Click "CTS Monitor" in taskbar
2. Or use this command:
```bash
wmctrl -r "CTS Monitor" -b remove,hidden
# Then move to front
wmctrl -r "CTS Monitor" -b add,above
```

## 📊 Window States

| Command | Effect |
|---------|--------|
| `add,hidden` | Minimize to taskbar |
| `remove,hidden` | Restore from taskbar |
| `add,above` | Always on top |
| `remove,above` | Normal layer |
| `add,fullscreen` | Fullscreen mode |
| `add,maximized_vert` | Maximize vertically |
| `add,maximized_horz` | Maximize horizontally |

## 💡 Advanced Usage

### **Auto-Restore on Error**
Monitor terminal can be configured to automatically restore when errors occur:
```python
# In CTS_Real_Time_Monitor.py
import os
def notify_error():
    os.system('wmctrl -r "CTS Monitor" -b remove,hidden')
```

### **Custom Title with Timestamp**
```python
import datetime
title = f"CTS Monitor - {datetime.now().strftime('%H:%M:%S')}"
os.system(f'gnome-terminal --title="{title}" ...')
```

### **Multiple Monitors**
Launch different monitoring scripts on different screens:
```python
# Monitor 1 - Left screen
--geometry=80x40+0+0

# Monitor 2 - Right screen (if dual monitor)
--geometry=80x40-0+0
```

## 🎨 Window Decorations

### **Frameless Window** (no title bar)
Not directly supported in gnome-terminal, but can use:
```bash
# After launch, remove decorations
wmctrl -r "CTS Monitor" -b add,undecorated
```

### **Transparent Background**
Configure in gnome-terminal profile settings, or:
```bash
gnome-terminal --window-with-profile=Transparent
```

## 📝 Notes

- ✅ Monitor terminal stays running even when minimized
- ✅ Output is still being logged/processed
- ✅ Can restore anytime from taskbar
- ✅ Automatically killed when main program exits (via pkill)
- ✅ Terminal persists after main script finishes (bash shell stays open)

## 🔄 Alternative: No Terminal at All

If you want monitoring without any terminal window:

```python
# Run monitor script in background, redirect to log file
log_file = os.path.join(current_dir, "monitor.log")
os.system(f'nohup python3 {script} > {log_file} 2>&1 &')
print(f"✓ Monitor running in background (log: {log_file})")

# View live output
# tail -f {log_file}
```
