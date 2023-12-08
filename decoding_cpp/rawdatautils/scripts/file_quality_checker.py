#!/usr/bin/env python3

from hdf5libs import HDF5RawDataFile

import detchannelmaps
import daqdataformats
import detdataformats
import gc
import glob
import os
from rawdatautils.unpack.wib2 import *
from rawdatautils.utilities.wib2 import *
import sys
import time
import traceback

import click
import time
import numpy as np

@click.command()
@click.argument('filenames', nargs=-1)
def main(filenames):
    """
This script provides a high-level summary of the records in an output HDF5 file and the fragments which they contain.

It simply takes a filename, or list of filenames, as argument(s) and summarizes each one sequentially.

For info on how to interpret the output, look at rawdatautils documentation:
https://dune-daq-sw.readthedocs.io/en/latest/packages/rawdatautils/

"""

    for filename in filenames:

        if not os.path.exists(filename):
            sys.exit(f"ERROR: file \"{filename}\" doesn't appear to exist")

        try:
            h5file = HDF5RawDataFile(filename)
        except:
            print(traceback.format_exc())
            sys.exit(f"ERROR: file \"{filename}\" couldn't be opened; is it an HDF5 file?")

        print(f"Processing {filename}...")

        is_trigger_records = True
        
        try:
            records = h5file.get_all_trigger_record_ids()
        except RuntimeError:
            is_trigger_records = False
        except:
            print(traceback.format_exc())
            sys.exit("ERROR: Something went wrong when calling h5file.get_all_trigger_record_ids(); file may contain junk data or be corrupted. Exiting...\n")

        if not is_trigger_records:
            try:
                records = h5file.get_all_timeslice_ids()
            except RuntimeError:
                sys.exit(f"Neither get_all_trigger_record_ids() nor get_all_timeslice_ids() returned records. Exiting...\n")
            except:
                print(traceback.format_exc())
                sys.exit("ERROR: Something went wrong when calling h5file.get_all_timeslice_ids(); file may contain junk data or be corrupted. Exiting...\n")
        
        if is_trigger_records:
            print(f'Will process {len(records)} trigger records.')
        else:
            print(f'Will process {len(records)} timeslice records.')
            
        sequence_ids = [] 
        record_ids = []
        tr_global_stats = {}

        assumed_sequence_id_step = -1
        assumed_record_id_step = -1
        first_sequence_id = -1
        first_record_id = -1
        
        for i_r, r in enumerate(records):

            for i_quadrant in range(1,4):
                if i_r == i_quadrant * int(len(records)/4):
                    print(f"Processed {i_r} of {len(records)} records...")

            record_ids.append(r[0])
            sequence_ids.append(r[1])
                    
            if i_r == 0:
                first_record_id = r[0]
                first_sequence_id = r[1]
            elif i_r == 1:
                assumed_record_id_step = r[0] - first_record_id
                assumed_sequence_id_step = r[1] - first_sequence_id
                    
            dset_paths = h5file.get_fragment_dataset_paths(r)
            tr_stats = {}

            for dset_path in dset_paths:
                frag = h5file.get_frag(dset_path)
                if frag.get_fragment_type() in tr_stats:
                    tr_stats[ frag.get_fragment_type()]["count" ] += 1
                    if frag.get_size() > tr_stats[ frag.get_fragment_type() ]["max_size" ]:
                        tr_stats[ frag.get_fragment_type() ][ "max_size" ] = frag.get_size()
                    if frag.get_size() < tr_stats[ frag.get_fragment_type()]["min_size" ]:
                        tr_stats[ frag.get_fragment_type()]["min_size" ] = frag.get_size()
                else:
                    tr_stats[ frag.get_fragment_type() ] = { "count": 1, "nonzero_error_bits_count": 0, "max_size": frag.get_size(), "min_size": frag.get_size() }

                if frag.get_header().error_bits != 0:
                        tr_stats[ frag.get_fragment_type() ]["nonzero_error_bits_count"] += 1
                    

            for frag_type in tr_stats:
                if frag_type in tr_global_stats:
                    if tr_stats[frag_type]["count"] > tr_global_stats[frag_type]["max_count"]:
                        tr_global_stats[frag_type]["max_count"] = tr_stats[frag_type]["count"]
                    if tr_stats[frag_type]["count"] < tr_global_stats[frag_type]["min_count"]:
                        tr_global_stats[frag_type]["min_count"] = tr_stats[frag_type]["count"]
                    if tr_stats[frag_type]["nonzero_error_bits_count"] > tr_global_stats[frag_type]["nonzero_error_bits_max_count"]:
                        tr_global_stats[frag_type]["nonzero_error_bits_max_count"] = tr_stats[frag_type]["nonzero_error_bits_count"]
                    if tr_stats[frag_type]["nonzero_error_bits_count"] < tr_global_stats[frag_type]["nonzero_error_bits_min_count"]:
                        tr_global_stats[frag_type]["nonzero_error_bits_min_count"] = tr_stats[frag_type]["nonzero_error_bits_count"]

                    if tr_stats[frag_type]["max_size"] > tr_global_stats[frag_type]["max_size"]:
                        tr_global_stats[frag_type]["max_size"] = tr_stats[frag_type]["max_size"]
                    if tr_stats[frag_type]["min_size"] < tr_global_stats[frag_type]["min_size"]:
                        tr_global_stats[frag_type]["min_size"] = tr_stats[frag_type]["min_size"]

                else:
                    tr_global_stats[frag_type] = { "max_count": tr_stats[frag_type]["count"],
                                                   "min_count": tr_stats[frag_type]["count"],
                                                   "max_size": tr_stats[frag_type]["max_size"],
                                                   "min_size": tr_stats[frag_type]["min_size"],
                                                   "nonzero_error_bits_min_count": tr_stats[frag_type]["nonzero_error_bits_count"],
                                                   "nonzero_error_bits_max_count": tr_stats[frag_type]["nonzero_error_bits_count"]
                                                   }

        print(f"Processed {len(records)} of {len(records)} records...")
        print("")

        sequence_ids_ok = True
        for i_s, seqid in enumerate(sequence_ids):
            if i_s > 0:
                if seqid - sequence_ids[i_s - 1] != assumed_sequence_id_step:
                    sequence_ids_ok = False

        record_ids_ok = True
        for i_r, recid in enumerate(record_ids):
            if i_r > 0:
                if recid - record_ids[i_r - 1] != assumed_record_id_step:
                    record_ids_ok = False

        if record_ids_ok:
            print(f"Progression of record ids over records looks ok (expected change of {assumed_record_id_step} for each new record)")
        else:
            print("Non-constant progression of record ids over records. This may or may not be a problem.")
            print(" ".join([str(recid) for recid in record_ids]))
                    
        if sequence_ids_ok:
            print(f"Progression of sequence ids over records looks ok (expected change of {assumed_sequence_id_step} for each new record)")
        else:
            print("Non-contant progression of sequence ids over records. This may or may not be a problem.")
            print(" ".join([str(seqid) for seqid in sequence_ids]))

        print("")
            

        frag_type_phrase_length = max([len(str(fragname)) - len("FragmentType.") for fragname in tr_global_stats]) + 1
        max_count_phrase = "max # in rec"
        min_count_phrase = "min # in rec"
        max_size_phrase = "largest (B)"
        min_size_phrase = "smallest (B)"
        max_errs_phrase = "max err in rec"
        min_errs_phrase = "min err in rec"

        fmtstring=f"%-{frag_type_phrase_length}s|%s|%s|%s|%s|%s|%s|"
        print(fmtstring % (" FragType ", min_count_phrase, max_count_phrase, min_size_phrase, max_size_phrase, min_errs_phrase, max_errs_phrase))

        divider = "-" * (frag_type_phrase_length + len(min_count_phrase) + len(max_count_phrase) +
                     len(min_size_phrase) + len(max_size_phrase) + len(max_errs_phrase) + len(min_errs_phrase) + 7)
        print(divider)
        
        for frag_type in tr_global_stats:
            fmtstring = f"%-{frag_type_phrase_length}s|%-{len(min_count_phrase)}s|%-{len(max_count_phrase)}s|%-{len(min_size_phrase)}s|%-{len(max_size_phrase)}s|%-{len(min_errs_phrase)}s|%-{len(max_errs_phrase)}s|"
            print(fmtstring % (str(frag_type).replace("FragmentType.",""),
                               tr_global_stats[frag_type]["min_count"],
                               tr_global_stats[frag_type]["max_count"],
                               tr_global_stats[frag_type]["min_size"],
                               tr_global_stats[frag_type]["max_size"],
                               tr_global_stats[frag_type]["nonzero_error_bits_min_count"],
                               tr_global_stats[frag_type]["nonzero_error_bits_max_count"])
                               )

            print(divider)
        print("")

        del h5file
        gc.collect()
            
if __name__ == '__main__':
    main()
