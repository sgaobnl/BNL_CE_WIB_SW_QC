# Monitor Terminal Size Options

## 🎯 Current Setting: Minimal Window (15x5)

The monitor terminal now uses the **smallest practical size** at the bottom-right corner.

## 📏 Size Comparison

| Configuration | Size | Position | Visibility |
|--------------|------|----------|------------|
| **Current** | `15x5-0-0` | Bottom-right | Tiny, visible ✅ |
| Smaller | `10x3-0-0` | Bottom-right | Minimal |
| Invisible | Background only | N/A | Hidden |
| Large | `80x40-0+0` | Right side | Full monitor |

## 🔧 Quick Configuration Changes

### Option 1: Even Smaller (10x3)
```python
--geometry=10x3-0-0
```

### Option 2: Icon-like (8x2)
```python
--geometry=8x2-0-0
```

### Option 3: Completely Hidden (No Window)
Replace the terminal launch section with:
```python
### Launch monitoring script in background (no window)
current_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(current_dir, "monitor_output.log")
os.system(f'nohup python3 {script} > {log_file} 2>&1 &')
print(f"✓ Monitor running in background (log: {log_file})")
print(f"  View live output: tail -f {log_file}")
```

### Option 4: Different Positions

```python
# Top-right corner
--geometry=15x5-0+0

# Top-left corner
--geometry=15x5+0+0

# Bottom-left corner
--geometry=15x5+0-0

# Bottom-right (current)
--geometry=15x5-0-0
```

## 📊 What Can You See in 15x5 Window?

The tiny window can display:
- ✅ "Running..." status
- ✅ Error messages (truncated)
- ✅ Basic activity indicator
- ❌ Full log details (use `tail -f` for that)

## 💡 Recommended Workflow

### For Normal Operation
**Use current setting (15x5)** - Minimal footprint, visible indicator

### When Debugging Monitor
**Temporarily use larger size**:
```bash
# Edit line 114 in CTS_FEMB_QC_top.py
--geometry=80x30-0+0  # Larger for debugging
```

### For Unattended Operation
**Use background mode** (no window at all)

## 🛠️ How to Change

Edit `CTS_FEMB_QC_top.py` line ~114:

```python
# Current (minimal)
os.system(f'gnome-terminal ... --geometry=15x5-0-0 ...')

# Option: Smaller
os.system(f'gnome-terminal ... --geometry=10x3-0-0 ...')

# Option: Background only (no window)
os.system(f'nohup python3 {script} > monitor.log 2>&1 &')
```

## 🔍 Viewing Monitor Output

Even with a tiny window, you can always see full output:

```bash
# If using terminal (current setup)
# Click on the tiny window to see it

# View full output in real-time
tail -f /tmp/monitor_output.log  # if logging to file

# View monitor process
ps aux | grep CTS_Real_Time_Monitor
```

## ⚙️ Additional Window Options

```python
# Remove window decorations (title bar)
--window-with-profile=Transparent

# Always on top (even though small)
# Then run: wmctrl -r "CTS Monitor" -b add,above

# Transparent background
--window-with-profile=Transparent
```

## 📝 Quick Reference

| What You Want | Geometry Setting |
|---------------|------------------|
| Tiny (current) | `15x5-0-0` |
| Smaller | `10x3-0-0` |
| Minimal | `8x2-0-0` |
| Invisible | Use `nohup` instead |
| Larger | `80x40-0+0` |
| Full size | `120x60-0+0` |

## 🎨 Visual Example

```
Current (15x5):          Smaller (10x3):      Invisible:
┌──────────────┐        ┌─────────┐          [No window]
│CTS Monitor   │        │CTS Mon  │          → Running in
│Running...    │        │Run...   │             background
│...           │        └─────────┘          → Check: ps aux
│              │
└──────────────┘
```

## ✅ Recommendation

**For most users**: Current setting (15x5) is optimal
- Small enough not to be distracting
- Large enough to see it's running
- Easy to find and click if needed

**For advanced users**: Background mode
- No visual clutter
- Use `tail -f` to monitor
- Still automatically managed
