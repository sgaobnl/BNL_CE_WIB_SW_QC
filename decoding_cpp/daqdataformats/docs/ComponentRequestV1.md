# ComponentRequest v1

This document describes the format of the ComponentRequest struct, version 1.

# Description of ComponentRequest

ComponentRequest version 1 consists of 10 32-bit words:

0. Version Number
1. Pad Word
2. [GeoID version 1](GeoIDV1.md) Version Number
3. [GeoID version 1](GeoIDV1.md) Component Type (upper 16 bits), Region ID (lower 16 bits)
4. [GeoID version 1](GeoIDV1.md) Element ID
5. [GeoID version 1](GeoIDV1.md) Pad Word
6. Window Begin (upper 32 bits)
7. Window Begin (lower 32 bits)
8. Window End (upper 32 bits)
9. Window End (lower 32 bits)

# C++ Code for ComponentRequest

```CPP
struct ComponentRequest
{
  uint32_t version{ 1 };
  unit32_t unused {0xFFFFFFFF};
  GeoID component;
  timestamp_t window_begin{ TypeDefaults::s_invalid_timestamp };
  timestamp_t window_end{ TypeDefaults::s_invalid_timestamp };

  ComponentRequest();
  ComponentRequest(GeoID comp, timestamp_t wbegin, timestamp_t wend);
};
```

# Notes
