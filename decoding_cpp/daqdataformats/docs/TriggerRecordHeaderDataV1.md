# TriggerRecordHeaderData v1 (Deprecated)

This document describes the format of the TriggerRecordHeaderData class, version 1. It should **not** be updated, but rather kept as a historic record of the data format for this version.

# TriggerRecordHeaderData Description

A TriggerRecordHeaderData version 1 consists of 12 32-bit words:

0. Marker (0x33334444)
1. Version (0x00000001)
2. Trigger Number (upper 32 bits)
3. Trigger Number (lower 32 bits)
4. Trigger timestamp (upper 32 bits)
5. Trigger timestamp (lower 32 bits)
6. Number of Requested Components (upper 32 bits)
7. Number of Requested Components (lower 32 bits)
8. Run number
9. Error bits
10. Upper 16 bits: Trigger type, Lower 16 bits: Unused
11. Unused


# C++ code for TriggerRecordHeaderData

```CPP
using run_number_t = uint32_t; 
using trigger_number_t = uint64_t; 
using timestamp_t = uint64_t;
using trigger_type_t = uint16_t; 

struct TriggerRecordHeaderData
{
  
  static constexpr uint32_t s_trigger_record_header_magic = 0x33334444;
  static constexpr uint32_t s_trigger_record_header_version = 1;
  static constexpr uint64_t s_invalid_number_components = std::numeric_limits<uint64_t>::max();
  static constexpr uint32_t s_default_error_bits = 0;

  uint32_t trigger_record_header_marker = s_trigger_record_header_magic;
  uint32_t version = s_trigger_record_header_version;
  trigger_number_t trigger_number{ TypeDefaults::s_invalid_trigger_number };
  timestamp_t trigger_timestamp{ TypeDefaults::s_invalid_timestamp };
  uint64_t num_requested_components{ s_invalid_number_components };
  run_number_t run_number{ TypeDefaults::s_invalid_run_number };
  uint32_t error_bits{ s_default_error_bits };
  trigger_type_t trigger_type{ TypeDefaults::s_invalid_trigger_type };
  uint16_t unusedA { 0xFFFF};
  uint32_t unusedB { 0xFFFFFFFF};
};
```

# Notes

A TriggerRecordHeader instance is a flat array consisting of a TriggerRecordHeaderData instance followed immediately by zero or more ComponentRequest instances. For TriggerRecordHeaderData version 1, these are assumed to be [ComponentRequest version 0 (unversioned)](ComponentRequestV0.md).
