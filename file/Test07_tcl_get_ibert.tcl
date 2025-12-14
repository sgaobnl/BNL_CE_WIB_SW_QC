open_hw
connect_hw_server
open_hw_target

# Get the IBERT core
set iberts [get_hw_sio_iberts]
if {[llength $iberts] == 0} {
    puts "No IBERT cores detected. Exiting."
    exit
}

# Select the first IBERT core
set ibert [lindex $iberts 0]
open_hw_target [get_hw_targets *]

# Get all RX channels from IBERT (BER is measured at RX)
set rx_channels [get_hw_sio_rxs -of_objects $ibert]

# Check if RX channels are available
if {[llength $rx_channels] == 0} {
    puts "No RX channels detected. Exiting."
    close_hw
    exit
}

puts "IBERT RX Channel BER Report:"
puts "--------------------------------------"

# Loop through each RX channel and retrieve BER, errors, and bit count
foreach rx $rx_channels {
    # Get Bit Error Rate (BER)
    set ber [get_property RX_BER $rx]

    # Get Total Received Bit Count
    set bit_count [get_property RX_RECEIVED_BIT_COUNT $rx]

    # Get Bit Error Count (LOGIC.ERRBIT_COUNT)
    set error_count [get_property LOGIC.ERRBIT_COUNT $rx]

    # Print results
    puts "RX Channel: $rx"
    puts "  Bit Error Rate (BER): $ber"
    puts "  Bit Errors: $error_count"
    puts "  Total Received Bits: $bit_count"
    puts "--------------------------------------"
}

# Close hardware session
close_hw


# we use list code to get the detail of hw_sio_links and explain the detail of the property we record the detail in a python file in ./file/record_code
