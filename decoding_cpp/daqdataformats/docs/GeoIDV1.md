# GeoID v1

This document describes the format of the GeoID struct, version 1.

# Description of GeoID

GeoID version 1 consists of four 32-bit words:

0. Version Number
1. System Type (upper 16 bits), Region Number (lower 16 bits)
2. Element Number
3. Pad word (64b alignment)

# C++ Code for GeoID

```CPP
struct GeoID
{
  enum class SystemType : uint16_t
  {
    kTPC = 1,
    kPDS = 2,
    kDataSelection = 3,
  ...
    kInvalid = 0
  };
  uint32_t version{ 1 };
  SystemType system_type{ SystemType::kInvalid };
  uint16_t region_number{ std::numeric_limits<uint16_t>::max() };
  uint32_t element_number{ std::numeric_limits<uint32_t>::max() };
  uint32_t unused {0xFFFFFFFF};

  GeoID();
  GeoID(SystemType type, uint16_t region, uint32_t element);
};
```

# Notes
