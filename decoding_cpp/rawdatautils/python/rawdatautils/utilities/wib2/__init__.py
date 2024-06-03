import daqdataformats
import detdataformats

def print_header(wib_frame,prefix="\t"):
    header = wib_frame.get_header()
    print(f'{prefix}Version: {header.version}')
    print(f'{prefix}Detector ID: {header.detector_id}')
    print(f'{prefix}(Crate,Slot,Link): ({header.crate},{header.slot},{header.link})')
    print(f'{prefix}(Timestamp1,Timestamp2): ({header.timestamp_1},{header.timestamp_2})')
    print(f'{prefix}Colddata Timestamp ID: {header.colddata_timestamp_id}')
    print(f'{prefix}FEMB Valid: {header.femb_valid}')
    print(f'{prefix}Link Mask: {header.link_mask}')
    print(f'{prefix}Lock output status: {header.lock_output_status}')
    print(f'{prefix}FEMB Pulser Frame Bits: {header.femb_pulser_frame_bits}')
    print(f'{prefix}FEMB Sync Flags: {header.femb_sync_flags}')
    print(f'{prefix}Colddata Timestamp: {header.colddata_timestamp}')

