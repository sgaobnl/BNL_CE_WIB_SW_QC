# rawdatautils

## General Utilities

### `file_quality_checker.py`

Usage:
```
file_quality_checker.py <FILENAME1> [FILENAME2 ...]
```

This script simply takes a list of HDF5 files produced by the DAQ (globs of course would work on the command line), loops over their records (whether trigger records or timeslices) and performs a few sanity checks. The output of the script when run on one file looks something like the following:
```
Processing /data2/np04_hd_run018000_0009_dataflow0_datawriter_0_20221118T091751.hdf5.copied...
Will process 27 trigger records.
Processed 6 of 27 records...
Processed 12 of 27 records...
Processed 18 of 27 records...
Processed 27 of 27 records...

Progression of record ids over records looks ok (expected change of 1 for each new record)
Progression of sequence ids over records looks ok (expected change of 0 for each new record)

 FragType         |min # in rec|max # in rec|smallest (B)|largest (B)|min err in rec|max err in rec|
----------------------------------------------------------------------------------------------------
kWIB              |40          |40          |3866696     |3866696    |0             |0             |
----------------------------------------------------------------------------------------------------
kHardwareSignal   |1           |1           |96          |96         |1             |1             |
----------------------------------------------------------------------------------------------------
kTriggerCandidate |1           |1           |128         |128        |1             |1             |
----------------------------------------------------------------------------------------------------
```
Concerning the progression of record ids and sequence ids: the script will look at the change in record id and sequence id between the first and second records in the file, and extrapolate that as the normal step size. If this step size is violated, then the full list of id values gets printed; otherwise simple one-sentence summaries such as you see above get printed. 

Concerning the table: each row corresponds to a fragment type found in at least one record in the file. The first and second columns tell you the fewest instances of such a fragment found in a single record, and the most. Of course, these are typically the same value. The third and fourth columns tell you what the smallest and largest examples of this fragment were in the entire file. The fifth and sixth columns tell you the fewest instances of a fragment with a nonzero set of error bits, and the most, in a single record. Of course for these last two columns you'd ideally see all 0's. 

## WIB2	Utilities

### `wib2decoder.py`

```
Usage: wib2decoder.py [OPTIONS] FILENAME

Options:
  -n, --nrecords INTEGER  How many Trigger Records to process (default: all)
  --nskip INTEGER         How many Trigger Records to skip (default: 0)
  --channel-map TEXT      Channel map to load (default: None)
  --print-headers         Print WIB2Frame headers
  --print-adc-stats       Print ADC Pedestals/RMS
  --check-timestamps      Check WIB2 Frame Timestamps
  --help                  Show this message and exit.
```

For example, for HD coldbox data from v2.11 onward, you can do:
```
wib2decoder.py -n 1 --print-headers --print-adc-stats --check-timestamps --channel-map HDColdboxChannelMap <file_name>
```
to dump content of the headers, do some timestamp checks for the frames coming from the same WIB and across different WIBs, and to do some basic processing of the data.

## Unpack utilities for Python

There are fast unpackers of data for working in python. These unpackers will
take a Fragment and put the resulting values (ADCs or timestamps) in a numpy
array with shape `(number of frames, number of channels)` at a similar speed
compared to doing that in C++. This is much faster than doing a similar thing
frame by frame in a loop in python.

To use it import the functions first:
```
from rawdatautils.unpack.<format> import *
```
where `<format>` is one of the supported formats: `wib`, `wib2` or `daphne` for
the corresponding `WIBFrame`, `WIB2Frame` and `DAPHNEFrame` frame formats. Then
there are several functions available:
```
# assumming frag is a fragment
adc = np_array_adc(frag)
timestamp = np.array_timestamp(frag)
print(adc.shape)       # (number of frames in frag, 256 if using wib2)
print(timestamp.shape) # (number of frames in frag, 256 if using wib2)
```
`np_array_adc` and `np_array_timestamp` will unpack the whole fragment. It is also possible to unpack only a part of it:
```
# assumming frag is a fragment
adc = np_array_adc_data(frag.get_data(), 100)             # first 100 frames
timestamp = np_array_timestamp_data(frag.get_data(), 100) # first 100 frames
print(adc.shape)       # (100, 256 if using wib2)
print(timestamp.shape) # (100, 256 if using wib2)
```
Warning: `np_array_adc_data` and `np_array_timestamp_data` do not make any
checks on the number of frames so if passed a value larger than the actual
number of frames in the fragment it will try to read out of bounds.
`np_array_adc` and `np_array_timestamp` call `np_array_adc_data` and
`np_array_timestamp_data` under the hood with the correct checks on the number
of frames.

## File conversion
It's possible to transform binary files using the old `WIBFrame` format to the
newer `WIB2Frame` or `WIBEthFrame` format. That means that the ADC values will
be preserved, as well as other values found in the header such as the crate,
slot, fiber number. The timestamps will be overwritten to differ by 32 (by 32 *
64 for `WIBEthFrame`) to avoid warnings and other issues when these files are
being read by readout. In python:

For WIB -> WIB2
```
from rawdatautils import file_conversion
file_conversion.wib_binary_to_wib2_binary('/path/to/input/file', '/path/to/output/file')
```
and for WIB -> WIBEth
```
from rawdatautils import file_conversion
file_conversion.wib_binary_to_wibeth_binary('/path/to/input/file', '/path/to/output/file')
```

When transforming WIB -> WIBEth it will create 4 files lblecause `WIBFrames`
have 256 channels and `WIBEthFrames` have 64, so the first file has the first 64
channels, the second file has the next 64 channels and so on.

