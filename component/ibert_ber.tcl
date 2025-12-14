
open_hw
connect_hw_server
open_hw_target

# Get IBERT core
set ibert [get_hw_sio_iberts]
if {[llength $ibert] == 0} {
    puts "Error: No IBERT core found!"
    exit
}

# Get all serial links in IBERT
set links [get_hw_sio_links -of_objects $ibert]

# Start BER scan if not already running
foreach link $links {
    create_hw_sio_scan -type BER -hw_sio_link $link
}

# Wait for scan to collect data
after 5000  ;# Wait 5 seconds (adjust as needed)

# Get BER scan results
foreach link $links {
    set ber_scans [get_hw_sio_scans -of_objects $link -filter {TYPE == "ber_scan"}]

    if {[llength $ber_scans] == 0} {
        puts "No BER scans available for $link"
        continue
    }

    # Get BER data
    foreach scan $ber_scans {
        set errors [get_property ERROR_COUNT $scan]
        set bits [get_property BIT_COUNT $scan]

        # Compute BER
        if {$bits > 0} {
            set ber [expr {double($errors) / $bits}]
        } else {
            set ber "N/A (No bits transmitted)"
        }

        puts "Link: $link - Errors: $errors - Total Bits: $bits - BER: $ber"
    }
}

close_hw_target
