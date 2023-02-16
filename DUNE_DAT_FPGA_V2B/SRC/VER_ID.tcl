# If the input file can't be opened, return an error.
    if { [catch {open $input_file} input] } {
        return -code error $input
    }

    # If the output file can't be opened, return an error
    if { [catch {open $output_file w} output] } {
        return -code error $output
    }

    # Read through the input file a line at a time
    while {-1 != [gets $input line] } {

        # This regular expression is specific to the design
        # file line in near the top of the web page.
        # You must change it as appropriate for your file.
        if { [regexp {^\s+data_out <= \d+'h([[:xdigit:]]+); // Design Version Number$} \ $line match version_number] } { # Convert the hexadecimal version number to base ten and increment it. scan $version_number "%x" decimal_value incr decimal_value set new_version_number [format "%X" $decimal_value] # Substitute the new version number in for the old one regsub h${version_number} $line h${new_version_number} line } # Write out the line to the new file puts $output $line } close $input close $output }   </pre>
 