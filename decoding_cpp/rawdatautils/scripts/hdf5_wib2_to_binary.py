#!/usr/bin/env python3
"""
Created on: 21/02/2023 15:28

Author: Shyam Bhuller

Description: Python script to write WIB2 frames from DUNE-DAQ HDF5 files to binary files.
"""

import argparse

from hdf5libs import HDF5RawDataFile
import daqdataformats
import fddetdataformats

from rich import print


def Debug(x):  
    """ print if we are in debug mode

    Args:
        x (any): thing to prints
    """      
    if debug:
        print(x)


def main(args):
    h5file = HDF5RawDataFile(args.file_name)

    total_records = len(h5file.get_all_record_ids())
    if args.n_records == -1:
        args.n_records = total_records
    if args.n_records > total_records:
        raise Exception(f"Number of specified records is greater than the total {total}")

    n_links = len([f for f in h5file.get_fragment_dataset_paths(1) if f.split("_")[-1] == "WIB"]) # exclude other fragments in the record that are not WIB frames
    if args.link >= n_links:
        raise Exception(f"Link number out of range.")

    out_name = f"wib_link_{args.link}.bin"
    with open(out_name, "wb") as bf:
        total_frames = 0
        # loop over all triggers
        for i in range(args.n_records):
            header = h5file.get_record_header_dataset_path(i+1) # trigger number starts at 1
            Debug(header)

            fragments = h5file.get_fragment_dataset_paths(i+1)
            fragments = [f for f in fragments if f.split("_")[-1] == "WIB"] # exclude other fragments in the record that are not WIB frames

            Debug(f"loading fragment: {fragments[args.link]}")
            f = h5file.get_frag(fragments[args.link])
            
            WIB2Frame_size = fddetdataformats.WIB2Frame.sizeof()

            n_frames = (f.get_size() - f.get_header().sizeof()) // WIB2Frame_size # calculate the number of wib frames per fragment
            for j in range(n_frames):
                Debug(f.get_fragment_type())
                Debug(f.get_element_id())

                data = fddetdataformats.WIB2Frame(f.get_data(j * WIB2Frame_size)) # unpack fragment to WIB2Frame
                
                Debug(f"{data.sizeof()=}")
                
                bf.write(bytearray(data.get_bytes())) # write binary data to the file
            total_frames += j
            print(f"writing {total_frames} WIB2 frames to binary file.", "\r")
    print(f"wrote {args.n_records} fragments from wib link {args.link} to file {out_name}.")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Python script to write WIB2 frames from DUNE-DAQ HDF5 files to binary files.')
    parser.add_argument(dest = "file_name", help = 'path to HDF5 file')
    parser.add_argument("-l", "--link", dest = "link", type = int, help = "link number to conver to binary", required = True)
    parser.add_argument('-n', '--num-of-records', dest = "n_records", type = int, help = 'specify number of records to be parsed, -1 will parse all records', default = 0, required = True)
    parser.add_argument("--debug", dest = "debug", action = "store_true", help = "Debugging information")
    args = parser.parse_args()
    debug = args.debug
    Debug(vars(args))
    main(args)
