# ComponentRequest v2

This document describes the format of version 2 of the `ComponentRequest` struct.

# Description of ComponentRequest

`ComponentRequest` version 2 consists of 8 32-bit words:

0. Version 
1. Padding word
2. [SourceID version 2](SourceIDV2.md) Version (upper 16 bits) / Subsystem (lower 16 bits)
3. [SourceID version 2](SourceIDV2.md) Element ID
4. Window Begin (upper 32 bits)
5. Window Begin (lower 32 bits)
6. Window End (upper 32 bits)
7. Window End (lower 32 bits)

# C++ Code for ComponentRequest

```CPP
struct ComponentRequest
{
  uint32_t version{ 2 };
  unit32_t unused {0xFFFFFFFF};
  SourceID component;
  timestamp_t window_begin{ TypeDefaults::s_invalid_timestamp };
  timestamp_t window_end{ TypeDefaults::s_invalid_timestamp };

  ComponentRequest(const SourceID& comp, const timestamp_t& wbegin, const timestamp_t& wend);
};
```

# Notes
As can be seen from the layout of the `ComponentRequest` struct, this can be considered a data source + a time window
