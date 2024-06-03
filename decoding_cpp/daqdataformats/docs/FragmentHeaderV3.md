# FragmentHeader v3

This document describes the format of the FragmentHeader class, version 3. It should **not** be updated, but rather kept as a historic record of the data format for this version.

# FragmentHeader Description

A FragmentHeader version 3 consists of 20 32-bit words:

0. Marker (0x11112222)
1. Version (0x00000003)
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
15. Sequence Number (16b) / Padding
16. [GeoID version 1](GeoIDV1.md) Component Type (upper 16 bits), Region ID (lower 16 bits)
17. [GeoID version 1](GeoIDV1.md) Element ID
18. [GeoID version 1](GeoIDV1.md) Version
19. [GeoID version 1](GeoIDV1.md) Pad Word

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
  static constexpr uint32_t s_fragment_header_version = 3;
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
  GeoID link_id;
};
```

# Fragment Notes

A Fragment is a flat array consisting of a FragmentHeader and data from Readout. The format of this data should be able to be inferred from the `fragment_type` field._
