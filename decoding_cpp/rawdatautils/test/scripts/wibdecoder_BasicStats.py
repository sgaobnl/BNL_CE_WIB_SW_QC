from hdf5libs import HDF5RawDataFile

import daqdataformats
from rawdatautils.unpack.wib import *
import fddetdataformats
import detchannelmaps

import click
import time
import numpy as np

@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--tr-count', default=-1, help='How many Trigger Records to test')
@click.option('--channel-map', default=None, help="Channel map to load (default: None)")
def main(filename, tr_count, channel_map):

    h5_file = HDF5RawDataFile(filename)

    records = h5_file.get_all_record_ids()
    records_to_process = records[0:tr_count]
    print(f'Will process {len(records_to_process)} of {len(records)} records.')

    #have channel numbers per geoid in here
    ch_map = None
    if channel_map is not None:
        ch_map = detchannelmaps.make_map(channel_map)
    offline_ch_num_dict = {}

    for r in records_to_process:
        print(f'Processing (Record Number,Sequence Number)=({r[0],r[1]})')
        wib_geo_ids = h5_file.get_geo_ids(r,daqdataformats.GeoID.SystemType.kTPC)
        for gid in wib_geo_ids:
            print(f'\tProcessing geoid {gid}')

            frag = h5_file.get_frag(r,gid)
            frag_hdr = frag.get_header()
            frag_ts = frag.get_trigger_timestamp()

            print(f'\tTrigger timestamp for fragment is {frag_ts}')

            n_frames = (frag.get_size()-frag_hdr.sizeof())//fddetdataformats.WIBFrame.sizeof()

            if(offline_ch_num_dict.get(gid) is None):
                if channel_map is None:
                    offline_ch_num_dict[gid] = range(256)
                else:
                    wf = fddetdataformats.WIBFrame(frag.get_data())
                    wh = wf.get_wib_header()
                    offline_ch_num_dict[gid] = [ch_map.get_offline_channel_from_crate_slot_fiber_chan(wh.crate_no, wh.slot_no, wh.fiber_no, c) for c in range(256)]


            #unpack timestamps into numpy array of uin64
            #timestamps = np_array_timestamp(frag)

            #unpack adcs into a n_frames x 256 numpy array of uint16
            adcs = np_array_adc(frag)

            adcs_rms = np.std(adcs,axis=0)

            for ch,rms in enumerate(adcs_rms):
                print(f'\t\tch {offline_ch_num_dict[gid][ch]}: rms = {rms}')

        #end gid loop
    #end record loop

    print(f'Processed all requested records')

if __name__ == '__main__':
    main()
