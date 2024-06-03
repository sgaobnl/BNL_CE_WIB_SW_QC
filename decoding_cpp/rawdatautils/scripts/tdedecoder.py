#!/usr/bin/env python3

from hdf5libs import HDF5RawDataFile

import daqdataformats
import detdataformats
from rawdatautils.unpack.tde import *
import detchannelmaps

import click
import time
import numpy as np


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--nrecords', '-n', default=-1, help='How many Trigger Records to process (default: all)')
@click.option('--nskip', default=0, help='How many Trigger Records to skip (default: 0)')
@click.option('--print-headers', is_flag=True, help="Print TDE16Frame headers")
@click.option('--det', default='VD_Top_TPC', help='Subdetector string (default: VD_TopTPC)')

def main(filename, nrecords, nskip, print_headers, det):

    h5_file = HDF5RawDataFile(filename)

    records = h5_file.get_all_record_ids()

    if nskip > len(records):
        print(f'Requested records to skip {nskip} is greater than number of records {len(records)}. Exiting...')
        return
    if nrecords>0:
        if (nskip+nrecords)>len(records):
            nrecords=-1
        else:
            nrecords=nskip+nrecords

    records_to_process = []
    if nrecords==-1:
        records_to_process = records[nskip:]
    else:
        records_to_process = records[nskip:nrecords]
    print(f'Will process {len(records_to_process)} of {len(records)} records.')

    for r in records_to_process:

        print(f'Processing (Record Number,Sequence Number)=({r[0],r[1]})')
        wib_geo_ids = h5_file.get_geo_ids_for_subdetector(r,detdataformats.DetID.string_to_subdetector(det))

        for gid in wib_geo_ids:
            geo_info = detchannelmaps.HardwareMapService.parse_geo_id(gid)
            subdet = detdataformats.DetID.Subdetector(geo_info.det_id)
            det_name = detdataformats.DetID.subdetector_to_string(subdet)
            print(f'\tProcessing subdetector {det_name}, crate {geo_info.det_crate}, slot {geo_info.det_slot}, link {geo_info.det_link}')

            frag = h5_file.get_frag(r,gid)
            frag_hdr = frag.get_header()
            frag_ts = frag.get_trigger_timestamp()

            print(f'\tTrigger timestamp for fragment is {frag_ts}')
            times = np_array_timestamp_data(frag);
            channels = np_array_channel_data(frag);
            n_frames = get_n_frames(frag);
            print(f'\tFound {n_frames} TDE Frames.')

            
            #n_frames = 5
            #print header info
            if print_headers :
                for i in range (0,n_frames):
                    print(f'{times[i]=} {channels[i]=}')

            print("\n")
        
    #end record loop

    print(f'Processed all requested records')

if __name__ == '__main__':
    main()
