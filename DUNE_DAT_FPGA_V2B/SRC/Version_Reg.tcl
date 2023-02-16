
proc update_version_number { input_file output_file} {
    # If the input file can't be opened, return an error.
    if { [catch {open $input_file} input] } {
        return -code error $input
    }

    # If the output file can't be opened, return an error
    if { [catch {open $output_file w} output] } {
        return -code error $output
    }

    # Read through the input file a line at a time
    while {-1 != [ gets $input line ] } {
        # This regular expression is specific to the design
        # file line in near the top of the web page.
        # You must change it as appropriate for your file.     
if { [regexp {^\s+data_out <= X"([[:xdigit:]]+)";} \ $line match version_number] }   { # Convert the hexadecimal version number to base ten and increment it. 
      scan $version_number "%x" decimal_value 
      incr decimal_value 
      set new_version_number [format "%X" $decimal_value]  
      regsub X"${version_number} $line X"${new_version_number} line
      post_message -type info "1 = $match 2 = $version_number  3 = $new_version_number"     
      post_message -type info "NEW version number is -> $new_version_number"
   } 
 if { [regexp {^\s+Date_s <= X"([[:xdigit:]]+)";} \ $line match date] }   { # Convert the hexadecimal version number to base ten and increment it. 
 
      set str [clock format [clock seconds] -format {%Y%m%d}]
      regsub X"${date} $line X"${str} line
      post_message -type info "$line"
   }  
  if { [regexp {^\s+Time_s <= X"([[:xdigit:]]+)";} \ $line match Time] }   { # Convert the hexadecimal version number to base ten and increment it. 
 
      set str2 [clock format [clock seconds] -format {%H%M%S}]
      regsub X"${Time} $line X"${str2} line
      post_message -type info "$line"
   }  
     
# Write out the line to the new file 
puts $output $line 
} 

close $input 
close $output 

}
       
set file_name ".\\src\\Version_Reg.vhd"
set output_file_name ${file_name}.updated_version_number

if { [catch { update_version_number $file_name $output_file_name } res] } {
    post_message -type critical_warning "Could not update version number: $res"
} else {

    if { [catch { file rename -force $output_file_name $file_name } res ] } {
        post_message -type critical_warning \
            "Could not update version number: $res"
    }
}


