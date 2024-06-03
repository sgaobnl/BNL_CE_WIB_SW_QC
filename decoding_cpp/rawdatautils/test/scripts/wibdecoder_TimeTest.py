from hdf5libs import HDF5RawDataFile
import daqdataformats
from rawdatautils.unpack.wib import *
import fddetdataformats
import click
import time
import numpy as np

@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--tr-count', default=-1, help='How many Trigger Records to test')
def main(filename, tr_count):
    """Test the python WIBFrame decoders on an HDF5 file containing WIBFrames,
    for example np02_bde_coldbox_run011918_0001_20211029T122926.hdf5
    """

    h5_file = HDF5RawDataFile(filename)

    records = h5_file.get_all_record_ids()
    records_to_process = records[0:tr_count]
    print(f'Will process {len(records_to_process)} of {len(records)} records.')

    for r in records_to_process:
        print(f'Processing (Record Number,Sequence Number)=({r[0],r[1]})')
        wib_geo_ids = h5_file.get_geo_ids(r,daqdataformats.GeoID.SystemType.kTPC)
        for gid in wib_geo_ids:
            print(f'Processing geoid {gid}')
            frag = h5_file.get_frag(r,gid)
            frag_hdr = frag.get_header()

            n_frames = (frag.get_size()-frag_hdr.sizeof())//fddetdataformats.WIBFrame.sizeof()

            wf = fddetdataformats.WIBFrame(frag.get_data())
            wh = wf.get_wib_header()

            ts = np.zeros(n_frames,dtype='uint64')
            adcs = np.zeros((n_frames,256),dtype='uint16')

            t0 = time.time()
            for iframe in range(n_frames):
                wf = fddetdataformats.WIBFrame(frag.get_data(iframe*fddetdataformats.WIBFrame.sizeof()))
                ts[iframe] = wf.get_timestamp()
                adcs[iframe] = [ wf.get_channel(k) for k in range(256) ]
            print(f'Time to decode with the python for loop       {time.time() - t0:.3f} s')

            t0 = time.time()
            timestamps = np_array_timestamp_data(frag.get_data(), n_frames)
            ary = np_array_adc_data(frag.get_data(), n_frames)
            print(f'Time to decode with the C++ -> numpy function {time.time() - t0:.3f} s')

            t0 = time.time()
            timestamps = np_array_timestamp(frag)
            ary = np_array_adc(frag)
            print(f'Time to decode with the C++ -> numpy function (with a Fragment as input) {time.time() - t0:.3f} s')

            if (adcs == ary).all() and (ts == timestamps).all():
                print(f'The arrays obtained for TR {r} are the same for the python for loop and the C++ -> numpy functions')
            else:
                print('Test failed, the python for loop and the C++ -> numpy functions return different results')

        #end gid loop
    #end record loop

    print(f'Processed all requested records')

if __name__ == '__main__':
    main()
