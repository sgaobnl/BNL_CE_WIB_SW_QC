open_hw_manager
connect_hw_server
open_hw
open_hw_target
set device [lindex [get_hw_devices] 0]
refresh_hw_device $device




refresh_hw_device [lindex [get_hw_devices] 0]
# Set Up Link on first GT
set tx0 [lindex [get_hw_sio_txs] 0]
set rx0 [lindex [get_hw_sio_rxs] 0]
set link0 [create_hw_sio_link $tx0 $rx0]
set_property DESCRIPTION {Link 0} [get_hw_sio_links $link0]
# Set link to use None, and write to hardware
set_property LOOPBACK "None" $link0
commit_hw_sio $link0
# Create, run, display and save scan
set scan0 [create_hw_sio_scan -description {Scan 0} 2d_full_eye [get_hw_sio_rxs -of $link0]]
run_hw_sio_scan [get_hw_sio_scans $scan0]
after 10000
write_hw_sio_scan -force "D:/scan00.csv" [get_hw_sio_scans {SCAN_0}]

refresh_hw_device [lindex [get_hw_devices] 1]
# Set Up Link on first GT
set tx1 [lindex [get_hw_sio_txs] 1]
set rx1 [lindex [get_hw_sio_rxs] 1]
set link1 [create_hw_sio_link $tx1 $rx1]
set_property DESCRIPTION {Link 1} [get_hw_sio_links $link1]
# Set link to use PCS Loopback, and write to hardware
set_property LOOPBACK "None" $link1
commit_hw_sio $link1
# Create, run, display and save scan
set scan1 [create_hw_sio_scan -description {Scan 1} 2d_full_eye [get_hw_sio_rxs -of $link1]]
run_hw_sio_scan [get_hw_sio_scans $scan1]
after 10000
write_hw_sio_scan -force "D:/scan01.csv" [get_hw_sio_scans {SCAN_0}]