# SourceID v2

This document describes the format of the `SourceID` struct, version 2. 

# Description of SourceID

Version 2 of `SourceID` consists of two 32-bit words:

0. Version (upper 16 bits) / Subsystem (lower 16 bits)
1. Element ID

# Notes
Since `SourceID` is a direct successor of the old `GeoID` struct, its versioning picks up where `GeoID` left off at version 1. Unlike `GeoID` which was intended to represent a specific region of the detector, `SourceID` is a generalized concept of where a chunk of data used in the DAQ comes from (e.g., it could be produced by a DAQ application rather than a part of the detector). 
