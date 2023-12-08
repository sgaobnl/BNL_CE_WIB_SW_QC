#!/usr/bin/env python3

from hdf5libs import HDF5RawDataFile

import daqdataformats
import detdataformats
import fddetdataformats
from rawdatautils.unpack.wib2 import *
from rawdatautils.utilities.wib2 import *
import detchannelmaps

import click
import time
import numpy as np


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--nrecords', '-n', default=-1, help='How many Trigger Records to process (default: all)')
@click.option('--nskip', default=0, help='How many Trigger Records to skip (default: 0)')
@click.option('--channel-map', default=None, help="Channel map to load (default: None)")
@click.option('--print-headers', is_flag=True, help="Print WIB2Frame headers")
@click.option('--print-adc-stats', is_flag=True, help="Print ADC Pedestals/RMS")
@click.option('--check-timestamps', is_flag=True, help="Check WIB2 Frame Timestamps")
@click.option('--det', default='HD_TPC', help='Subdetector string (default: HD_TPC)')

def main(filename, nrecords, nskip, channel_map, print_headers, print_adc_stats, check_timestamps, det):

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

    #have channel numbers per geoid in here
    ch_map = None
    if channel_map is not None:
        ch_map = detchannelmaps.make_map(channel_map)
    offline_ch_num_dict = {}
    offline_ch_plane_dict = {}

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

            n_frames = get_n_frames(frag);
            print(f'\tFound {n_frames} WIB2 Frames.')

            wf = fddetdataformats.WIB2Frame(frag.get_data())

            #print header info
            if print_headers:
                print('\n\t==== WIB HEADER (First Frame) ====')
                print_header(wf,prefix='\t\t')

            #fill channel map info if needed
            if(offline_ch_num_dict.get(gid) is None):
                if channel_map is None:
                    offline_ch_num_dict[gid] = np.arange(256)
                    offline_ch_plane_dict[gid] = np.full(256,9999)
                else:
                    wh = wf.get_header()
                    offline_ch_num_dict[gid] = np.array([ch_map.get_offline_channel_from_crate_slot_fiber_chan(wh.crate, wh.slot, wh.link, c) for c in range(256)])
                    offline_ch_plane_dict[gid] = np.array([ ch_map.get_plane_from_offline_channel(uc) for uc in offline_ch_num_dict[gid] ])


            #unpack timestamps into numpy array of uin64
            if check_timestamps:
                timestamps = np_array_timestamp(frag)
                timestamps_diff = np.diff(timestamps)
                timestamps_diff_vals, timestamps_diff_counts = np.unique(timestamps_diff, return_counts=True)

                if(n_frames>0):
                    print('\n\t==== TIMESTAMP CHECK ====')
                    print(f'\t\tTimestamps (First, Last, Min, Max): ({timestamps[0]},{timestamps[-1]},{np.min(timestamps)},{np.max(timestamps)})')
                    print(f'\t\tTimestamp diffs: {timestamps_diff_vals}')
                    print(f'\t\tTimestamp diff counts: {timestamps_diff_counts}')
                    print(f'\t\tAverage diff: {np.mean(timestamps_diff)}')

            if print_adc_stats:

                #unpack adcs into a n_frames x 256 numpy array of uint16
                adcs = np_array_adc(frag)
                adcs_rms = np.std(adcs,axis=0)
                adcs_ped = np.mean(adcs,axis=0)
                
                print('\n\t====WIB DATA====')

                for ch,rms in enumerate(adcs_rms):
                    print(f'\t\tch {offline_ch_num_dict[gid][ch]} (plane {offline_ch_plane_dict[gid][ch]}): ped = {adcs_ped[ch]:.2f}, rms = {adcs_rms[ch]:.4f}')

            print("\n")
        #end gid loop

        if check_timestamps:
            timestamps_frame0 = np.array([ fddetdataformats.WIB2Frame(h5_file.get_frag(r,gid).get_data()).get_timestamp() for gid in wib_geo_ids ])
            timestamps_frame0_diff = timestamps_frame0 - timestamps_frame0[0]
            
            print('\n\t==== TIMESTAMP ACROSS WIBS CHECK ====')
            print(f'\t\tTimestamp diff relative to first WIB',timestamps_frame0_diff)
        
    #end record loop

    print(f'Processed all requested records')

if __name__ == '__main__':
    main()
