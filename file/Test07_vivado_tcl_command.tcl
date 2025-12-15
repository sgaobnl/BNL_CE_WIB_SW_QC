# Open Hardware Manager
open_hw_manager
connect_hw_server

# Open Target FPGA
open_hw_target

# Specify the device (adjust index if multiple devices exist)
set device [lindex [get_hw_devices] 0]

# Program FPGA with .bin file
set_property PROGRAM.FILE "/home/dune/Documents/DUNE_WIB_QC_Script/file/example_ibert_ultrascale_gth_0.bit" $device
program_hw_devices $device

# Load the .ltx file for debugging (optional)
set_property PROBES.FILE "/home/dune/Documents/DUNE_WIB_QC_Script/file/example_ibert_ultrascale_gth_0.ltx" $device
refresh_hw_device $device
detect_hw_sio_links
# we use list code to get the detail of hw_sio_links and explain the detail of the property we record the detail in a python file in ./file/record_code

###############
#open_hw
#open_hw_target
set iberts [get_hw_sio_iberts]
if {[llength $iberts] == 0} {
    puts "No IBERT cores detected. Exiting."
    exit
}
set ibert [lindex $iberts 0]
open_hw_target [get_hw_targets *]

set rx_channels [get_hw_sio_rxs -of_objects $ibert]
###
set rx_channels [get_hw_sio_rxs -of_objects $ibert]
if {[llength $rx_channels] == 0} {
    puts "No RX channels detected. Exiting."
    close_hw
    exit
}

puts "IBERT RX Channel BER Report:"
puts "--------------------------------------"
foreach rx $rx_channels {
    # Get Bit Error Rate (BER)
    set ber [get_property RX_BER $rx]

    # Get Total Received Bit Count
    set bit_count [get_property RX_RECEIVED_BIT_COUNT $rx]

    # Get Bit Error Count (LOGIC.ERRBIT_COUNT)
    set error_count [get_property LOGIC.ERRBIT_COUNT $rx]

    # Print results
    #Bit Error Rate (BER) second BER
    #Bit Errors second BEN
    #Total Received Bits second TCB
    puts "RX Channel First: $rx"
    puts "  BER: $ber"
    puts "  ERROR_count: $error_count"
    puts "  BIT_count: $bit_count"
    puts "--------------------------------------"
}

###


##########



Close the connection
close_hw_manager
exit