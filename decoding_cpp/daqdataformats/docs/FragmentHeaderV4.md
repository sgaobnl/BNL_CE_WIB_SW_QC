# FragmentHeader v4

This document describes the format of the `FragmentHeader` struct, version 4. It should **not** be updated, but rather kept as a historic record of the data format for this version.

# FragmentHeader Description

Version 4 of the `FragmentHeader` consists of 18 32-bit words:

0. Marker (0x11112222)
1. Version (0x00000004)
2. Size in bytes, including header and Fragment payload (upper 32 bits)
3. Size in bytes, including header and Fragment payload (lower 32 bits)
4. Trigger number (upper 32 bits)
5. Trigger number (lower 32 bits)
6. Trigger timestamp (upper 32 bits)
7. Trigger timestamp (lower 32 bits)
8. Data window begin (upper 32 bits)
9. Data window begin (lower 32 bits)
10. Data window end (upper 32 bits)
11. Data window end (lower 32 bits)
12. Run Number
13. Error bits
14. Fragment Type
15. Sequence Number (upper 16 bits) / Padding (lower 16 bits)
16. [SourceID version 2](SourceIDV2.md) Version (upper 16 bits) / Subsystem (lower 16 bits)
17. [SourceID version 2](SourceIDV2.md) Element ID

# C++ code for FragmentHeader

```CPP
using run_number_t = uint32_t; 
using trigger_number_t = uint64_t; 
using fragment_type_t = uint32_t;
using fragment_size_t = uint64_t; 
using timestamp_t = uint64_t;
using sequence_number_t = uint16_t;

struct FragmentHeader
{
  static constexpr uint32_t s_fragment_header_marker = 0x11112222;
  static constexpr uint32_t s_fragment_header_version = 4;
  static constexpr uint32_t s_default_error_bits = 0;

  uint32_t fragment_header_marker = s_fragment_header_marker;
  uint32_t version = s_fragment_header_version;
  fragment_size_t size{ TypeDefaults::s_invalid_fragment_size };
  trigger_number_t trigger_number{ TypeDefaults::s_invalid_trigger_number };
  timestamp_t trigger_timestamp{ TypeDefaults::s_invalid_timestamp };
  timestamp_t window_begin{ TypeDefaults::s_invalid_timestamp };
  timestamp_t window_end{ TypeDefaults::s_invalid_timestamp };
  run_number_t run_number{ TypeDefaults::s_invalid_run_number };
  uint32_t error_bits{ s_default_error_bits }; 
  fragment_type_t fragment_type{ TypeDefaults::s_invalid_fragment_type };
  sequence_number_t sequence_number {TypeDefaults::s_invalid_sequence_number };
  uint16_t unused {0xFFFF};
  SourceID element_id;
};
```

# Fragment Notes

A `Fragment` is a flat array consisting of a `FragmentHeader` and payload data (e.g. data from electronics readout). The format of this data should be able to be inferred from the `fragment_type` field of the `FragmentHeader`.
