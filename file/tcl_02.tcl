open_hw_manager
connect_hw_server
open_hw
open_hw_target
set device [lindex [get_hw_devices] 0]
refresh_hw_device $device
detect_hw_sio_links

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
# after 10000
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
    puts " $rx Total_BER: $ber"
    puts " $rx Total_ERROR_count: $error_count"
    puts " $rx Total_BIT_count: $bit_count"
    puts "--------------------------------------"
}


Close the connection
close_hw_manager
exit