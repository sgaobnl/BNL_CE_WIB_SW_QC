# FragmentHeader v1 (Deprecated)

This document describes the format of the FragmentHeader class, version 1. It should **not** be updated, but rather kept as a historic record of the data format for this version.

# FragmentHeader Description

A FragmentHeader version 1 consists of 17 32-bit words:

0. Marker (0x11112222)
1. Version (0x00000001)
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
13. [GeoID version 0 (unversioned)](GeoIDV0.md) Component Type (upper 16 bits), Region ID (lower 16 bits)
14. [GeoID version 0 (unversioned)](GeoIDV0.md) Element ID
15. Error bits
16. Fragment Type

# C++ code for FragmentHeader

```CPP
using run_number_t = uint32_t; 
using trigger_number_t = uint64_t; 
using fragment_type_t = uint32_t;
using fragment_size_t = uint64_t; 
using timestamp_t = uint64_t;

struct FragmentHeader
{
  static constexpr uint32_t s_fragment_header_magic = 0x11112222;
  static constexpr uint32_t s_fragment_header_version = 1;
  static constexpr uint32_t s_default_error_bits = 0;

  uint32_t fragment_header_marker = s_fragment_header_magic;
  uint32_t version = s_fragment_header_version;
  fragment_size_t size{ TypeDefaults::s_invalid_fragment_size };
  trigger_number_t trigger_number{ TypeDefaults::s_invalid_trigger_number };
  timestamp_t trigger_timestamp{ TypeDefaults::s_invalid_timestamp };
  timestamp_t window_begin{ TypeDefaults::s_invalid_timestamp };
  timestamp_t window_end{ TypeDefaults::s_invalid_timestamp };
  run_number_t run_number{ TypeDefaults::s_invalid_run_number };
  GeoID element_id;
  uint32_t error_bits{ s_default_error_bits }; 
  fragment_type_t fragment_type{ TypeDefaults::s_invalid_fragment_type };
};
```

# Fragment Notes

A Fragment is a flat array consisting of a FragmentHeader and data from Readout. The format of this data should be able to be inferred from the `fragment_type` field._
