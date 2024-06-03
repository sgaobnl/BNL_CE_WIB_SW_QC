# Some Notes on DAQ Data Formats

## Versioning Data Formats

We currently do not have an explicit versioning scheme in place, however we are planning on having a "version" field as the first member of each struct (after an optional "magic bytes" string), so that the version can always be read from a struct without knowing which version the specific instance is.

## Variable-Size Data in DAQ Data Formats

For data types where the size of the payload is variable (e.g. `Fragment`, `TriggerRecordHeader`), the class is represented internally as a flat array of bytes. The start of this array is a header object (e.g. `FragmentHeader` or `TriggerRecordHeaderData`), which contains the information about the object and a size member which describes the size of the rest of the memory block. This allows us to store these objects as flat HDF5 DataSets directly.

## Padding and Alignment in Struct Definitions

### Problem Statement
According to the C++ Standard (See https://en.cppreference.com/w/cpp/language/object subsection Alignment), members of objects are aligned to addresses based on their size (e.g. an `int` will be aligned to a 4-byte address), and padding will be inserted between members as necessary to satisfy this requirement.

For example:
```C++
struct MyStruct {
  int mem001; // 4 bytes
  char mem002; // 1 byte, with 3 bytes padding added
  int mem003; // 4 bytes
};
static_assert(sizeof(MyStruct) == 12, "MyStruct size different than expected");
```

Objects will also be padded so that their size is a multiple of the size of their largest member, for most DUNE-DAQ structs, this means 64 bits.

### Implications for DUNE-DAQ Code

These considerations have some implications for the data structures that may be persisted to disk from DUNE-DAQ:

1. All padding should be explicitly specified in structs
2. Structs should have members sorted so that there is no internal padding
3. Developers should statically assert the expected size of their structs, and update that assertion when the struct is updated
4. All struct members should have explicit sizes (i.e. `enum class MyEnum : uint16_t {};`)

For sorting members, the following is fine:
```C++
struct MySortedStruct {
  uint16_t version; // These three fields together form a 64-bit block
  uint16_t first_field;
  uint32_t second_field;
  
  uint64_t third_field;

  uint32_t fourth_field;
  uint16_t fifth_field;
  uint8_t sixth_field;
  uint8_t padding;
};
static_assert(sizeof(MySortedStruct) == 24, "MySortedStruct size different than expected");
```

In the general case, sorting members from largest to smallest will guarantee no internal padding is inserted by the compiler. 

In the above struct, if `first_field` and `second_field` are swapped, the compiler will insert 8 bytes of padding: 2 bytes between `version` and `second_field` to align `second_field` to a 32-bit address, then 6 bytes after `first_field` to align `third_field` to a 64-bit address.