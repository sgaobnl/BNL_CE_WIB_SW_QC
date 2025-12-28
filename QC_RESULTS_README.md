# QC Results Module - Enhanced Result Checking

## Overview

The enhanced QC results module (`qc_results.py`) provides a comprehensive, user-friendly way to check and report FEMB QC test results with improved clarity and functionality.

## Key Improvements

### 1. **Structured Result Analysis**
- Creates a `QCResult` object containing all test data
- Separates data collection from presentation
- Provides detailed statistics and slot-by-slot breakdown

### 2. **Enhanced Visual Display**
```
======================================================================
  WARM QC TEST - TEST RESULTS
======================================================================

📊 Test Summary:
   Total Fault Files: 2
   Total Pass Files:  18

🔍 FEMB Status by Slot:
   ✓ Bottom Slot0: FEMB IO-1826-1-001 - PASS
   ✗ Top Slot1: FEMB IO-1826-1-002 - FAIL

⚠️  Fault Files Detected:
   • test_result_F_Slot1.txt
   • checkout_F_Slot1_S1.dat

======================================================================
  ✗✗✗ OVERALL RESULT: FAIL ✗✗✗

  Failed FEMBs:
    • Top Slot1: IO-1826-1-002
======================================================================
```

### 3. **Smart User Interaction**
When tests fail, users are presented with clear options:
- **'r'** - Retry the test (automatic retry loop)
- **'c'** - Continue anyway (with warning)
- **'e'** - Exit program (with recommendations)

### 4. **Automatic Email Notifications**
- Success: Notifies with pass status and next steps
- Failure: Alerts with failure details and recommended actions

### 5. **Comprehensive Final Review**
At the end of the complete QC cycle:
- Option to review all test results from all phases
- Verbose mode shows detailed file lists
- Summary of all warm/cold/final tests

## Function Reference

### `analyze_test_results(paths, inform=None)`
Scans directories for test result files and returns structured data.

**Returns:** `QCResult` object with:
- `fault_files` - List of fault file paths
- `pass_files` - List of pass file paths
- `slot_status` - Dictionary of slot results
- `total_faults` - Count of fault files
- `total_passes` - Count of pass files

### `display_qc_results(result, test_phase, verbose=False)`
Displays formatted test results with color coding.

**Parameters:**
- `result` - QCResult object
- `test_phase` - Name of test (e.g., "Warm QC", "Cold QC")
- `verbose` - Show detailed file paths

**Returns:** `(all_passed, failed_slots)`

### `handle_qc_results(paths, inform, test_phase, allow_retry=True, verbose=False)`
Complete workflow: analyze → display → handle user decision

**Parameters:**
- `paths` - List of result directories
- `inform` - FEMB information dictionary
- `test_phase` - Test name
- `allow_retry` - Enable retry option
- `verbose` - Detailed output

**Returns:** `(all_passed, should_retry, failed_slots)`

## Usage Examples

### Basic Usage (Automatic)
```python
# In main QC script - replaces old check_fault_files
all_passed, should_retry, failed_slots = handle_qc_results(
    paths=[wcdata_path, wcreport_path, wqdata_path, wqreport_path],
    inform=inform,
    test_phase="Warm QC Test",
    allow_retry=True,
    verbose=False
)

if all_passed:
    # Continue to next phase
    break
elif should_retry:
    # Retry current test
    continue
else:
    # User chose to exit (handled automatically)
    pass
```

### Manual Display (No Interaction)
```python
# Just display results without user interaction
result = analyze_test_results(paths, inform)
all_passed, failed_slots = display_qc_results(
    result,
    "Final Review",
    verbose=True
)
```

### Backward Compatible
```python
# For code that just needs slot status
from qc_results import get_slot_results

s0, s1 = get_slot_results(paths, inform)
```

## Benefits

1. **Eliminates Code Duplication**
   - Single function replaces repeated result checking code
   - Consistent behavior across all test phases

2. **Better Error Handling**
   - Clear indication of which FEMBs failed
   - Specific recommendations for failed slots

3. **Improved User Experience**
   - Clear visual formatting with emojis and colors
   - Intuitive options for handling failures
   - Comprehensive statistics

4. **Easier Maintenance**
   - Centralized result checking logic
   - Easy to add new features (e.g., result export)
   - Better testing capability

5. **Enhanced Traceability**
   - Detailed file listings available
   - Clear summary of all tests performed
   - Better documentation of failures

## Migration Notes

### Old Code
```python
s0, s1 = check_fault_files(paths, show_p_files=False, inform=inform)
if s0 and s1:
    print('Pass')
    break
else:
    decision = confirm('Do you want to retest again')
    if decision:
        continue
    else:
        # Handle failure...
```

### New Code
```python
all_passed, should_retry, failed_slots = handle_qc_results(
    paths=paths,
    inform=inform,
    test_phase="Test Name",
    allow_retry=True
)

if all_passed:
    break
elif should_retry:
    continue
```

## Future Enhancements

Potential additions to the module:
- [ ] Export results to JSON/CSV
- [ ] Generate PDF reports
- [ ] Compare results across test runs
- [ ] Statistical analysis of failure patterns
- [ ] Integration with database logging
- [ ] Automatic error categorization
- [ ] Email attachments with detailed logs
