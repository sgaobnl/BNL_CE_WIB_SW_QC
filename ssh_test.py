import time
import subprocess
from threading import Thread
from queue import Queue, Empty

t0 =  time.time_ns()
#p = subprocess.Popen(["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 testaa.py"],
p = subprocess.Popen(["python", "testaa.py"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                        )

# Read and print output line by line in real-time

while p.poll() is None:  # Continue loop until the subprocess terminates
    print ( time.time_ns() - t0)
    # Read a line from stdout
    output_line = p.stdout.readline()
    if output_line == '' :
        print ("sleep")
        time.sleep(0.2)
    if output_line:
        print("STDOUT:", output_line.strip())

    # Read a line from stderr
    #error_line = p.stderr.readline()
    #if error_line == '' :
    #    pass
    #if error_line:
    #    print("STDERR:", error_line.strip())

## Function to read and print output and errors
#def read_output(stream, queue):
#    for line in iter(stream.readline, ''):
#        queue.put(line.strip())
#    stream.close()
#
## Create queues for stdout and stderr
#stdout_queue = Queue()
#stderr_queue = Queue()
#
## Start threads to handle stdout and stderr
#stdout_thread = Thread(target=read_output, args=(p.stdout, stdout_queue))
#stdout_thread.daemon = True
#stdout_thread.start()
#
#stderr_thread = Thread(target=read_output, args=(p.stderr, stderr_queue))
#stderr_thread.daemon = True
#stderr_thread.start()
#print ( time.time_ns() - t0)
#
## Main loop to write input and check output
#while p.poll() is None:  # Continue loop until the subprocess terminates
#    time.sleep(10)
#    print ( time.time_ns() - t0)
#    if stdout_queue.empty():
#        pass
#    else:
#        print(stdout_queue.get_nowait())
## Wait for the subprocess to finish
#p.wait()
#
## Join the threads
#stdout_thread.join()
#stderr_thread.join()
#exit()
#
#
##    print ( time.time_ns() - t0)
##    try:
##        # Print stdout
##        while True:
##            xxx = stdout_queue.get_nowait()
##            if "AA" in xxx:
##                print ("AAA")
##            else:
##                print ("xxx")
##            #print(stdout_queue.get_nowait())
##    except Empty:
##        print ("empty")
##        pass
##    
##    try:
##        # Print stderr
##        while True:
##            print(stderr_queue.get_nowait())
##    except Empty:
##        print ("err_empty")
##        pass
##
#
#
##print ( time.time_ns() - t0)
##
### Function to read and print output and errors
##def read_output(stream):
##    for line in iter(stream.readline, ''):
##        print(line.strip())
##    stream.close()
##
### Start the subprocess
##p = subprocess.Popen(["python", "testaa.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
##
### Start threads to read stdout and stderr in real-time
##stdout_thread = Thread(target=read_output, args=(p.stdout,))
##stdout_thread.start()
##
##stderr_thread = Thread(target=read_output, args=(p.stderr,))
##stderr_thread.start()
##
### Wait for the subprocess to finish
##print ( time.time_ns() - t0)
##p.wait()
##print ( time.time_ns() - t0)
##
### Join the threads
##stdout_thread.join()
##stderr_thread.join()
##exit()
#
## Read and print output line by line in real-time
##
##for i in range(15):
##    time.sleep(1)
##    print (i)
##    # Read a line from stdout
##    output_line = p.stdout.readline()
##    if output_line == '' and p.poll() is not None:
##        print ("sleep(1)")
##    if output_line:
##        print("STDOUT:", output_line.strip())
##
##    # Read a line from stderr
##    error_line = p.stderr.readline()
##    if error_line == '' and p.poll() is not None:
##        print ("sleep(2)")
##    if error_line:
##        print("STDERR:", error_line.strip())
##
##exit()
#
## Function to read and print output and errors
#def read_output(stream, queue):
#    for line in iter(stream.readline, ''):
#        queue.put(line.strip())
#        print(line.decode().strip())
#    stream.close()
#
## Create queues for stdout and stderr
#stdout_queue = Queue()
#stderr_queue = Queue()
#
## Start threads to handle stdout and stderr
#stdout_thread = Thread(target=read_output, args=(p.stdout, stdout_queue))
#stdout_thread.daemon = True
#stdout_thread.start()
#
#stderr_thread = Thread(target=read_output, args=(p.stderr, stderr_queue))
#stderr_thread.daemon = True
#stderr_thread.start()
#print ( time.time_ns() - t0)
#
## Main loop to write input and check output
#while p.poll() is None:  # Continue loop until the subprocess terminates
#    time.sleep(1)
#    if stdout_queue.empty():
#        pass
#    else:
#        print(stdout_queue.get_nowait())
##    print ( time.time_ns() - t0)
##    try:
##        # Print stdout
##        while True:
##            print(stdout_queue.get_nowait())
##    except Empty:
##        print ("empty")
##        pass
##    
##    try:
##        # Print stderr
##        while True:
##            print(stderr_queue.get_nowait())
##    except Empty:
##        print ("err_empty")
##        pass
##
### Main loop to check output
##while True:
##    print ("KKKK")
##    p.communicate(timeout=1)
##    #print (output)
##    try:
##        # Print stdout
##        while True:
##            print(stdout_queue.get_nowait())
##    except Empty:
##        pass
##    
##    try:
##        # Print stderr
##        while True:
##            print(stderr_queue.get_nowait())
##    except Empty:
##        pass
##
##    
##    # Check if the subprocess has terminated
##    if p.poll() is not None:
##        break
##
##    # Add some delay to reduce CPU usage
##    time.sleep(0.1)
#
#
#
##    # Write input to the subprocess
##    user_input = input("Enter your input: ")  # Get user input
##    p.stdin.write(user_input + '\n')  # Write input to stdin of subprocess
##    p.stdin.flush()  # Flush the stdin buffer
#
## Close the stdin stream to indicate the end of input
#
## Wait for the subprocess to finish
#p.wait()
#
## Join the threads
#stdout_thread.join()
#stderr_thread.join()
#
### Get and print the final output and errors
##final_output, final_errors = p.communicate()
##print("Final Output:", final_output.strip())
##print("Final Errors:", final_errors.strip())
##
### Read and print output line by line in real-time
##while True:
##    # Read a line from stdout
##    output_line = p.stdout.readline()
##    if output_line == '' and p.poll() is not None:
##        print ("sleep(1)")
##        #time.sleep(1)
##        #break
##    if output_line:
##        print("STDOUT:", output_line.strip())
##
##    # Read a line from stderr
##    error_line = p.stderr.readline()
##    if error_line == '' and p.poll() is not None:
##        print ("sleep(2)")
##        time.sleep(1)
##        #print("STDERR:", error_line.strip())
##        #break
##    if error_line:
##        print("STDERR:", error_line.strip())
##
### Read and print output and errors in real-time with a timeout
##while True:
##    # Create lists of file descriptors to monitor for reading
##    ready_to_read, _, _ = select.select([p.stdout, p.stderr], [], [])
##
##    # Iterate over ready descriptors
##    for file_descriptor in ready_to_read:
##        # Read a line from stdout
##        if file_descriptor == p.stdout:
##            output_line = p.stdout.readline()
##            if output_line:
##                print("STDOUT:", output_line.strip())
##        # Read a line from stderr
##        elif file_descriptor == p.stderr:
##            error_line = p.stderr.readline()
##            if error_line:
##                print("STDERR:", error_line.strip())
##
##    # Check if the process has terminated
##    if p.poll() is not None:
##        break
##
##
#### Wait for the process to terminate
###p.communicate()
##
###import subprocess
###
#### Command to run
###command = ['ping', '192.168.121.123']
###
#### Start the subprocess with stdout and stderr as pipes
###p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
###
#### Read and print output line by line in real-time
###while True:
###    # Read a line from stdout
###    output_line = p.stdout.readline()
###    if output_line == '' and p.poll() is not None:
###        break
###    if output_line:
###        print("STDOUT:", output_line.strip())
###
###    # Read a line from stderr
###    error_line = p.stderr.readline()
###    if error_line == '' and p.poll() is not None:
###        break
###    if error_line:
###        print("STDERR:", error_line.strip())
###
#### Wait for the process to terminate
###p.communicate()
##
###
###import subprocess
###import datetime
###
#### Command to run the input_script.py
####command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC", "testaa.py"]
###command = ["python", "'D:/Github/BNL_CE_WIB_SW_QC_main/testaa.py'"]
###
#### Start the subprocess
###p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
###
####output, errors = p.communicate()
####$#print("Output:", output)
####exit()
#### Provide input to the subprocess
###input_data = 'Hello, World!\n'
###try:
###    output, errors = p.communicate(input=input_data, timeout=15)
###except subprocess.TimeoutExpired:
###    p.kill()
###    output, errors = p.communicate()
###print("Output:", type(output))
###
##### Run your command
####p = subprocess.Popen(["python", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
####
##### Communicate with the process
####output, errors = p.communicate()
####
####print("Output:", output)
####print("Errors:", errors)
###
##### Get the current date and time
####now = datetime.datetime.utcnow()
##### Format it to match the output of the `date` command
####formatted_now = now.strftime('%a %b %d %H:%M:%S UTC %Y')
####result = subprocess.run(["ssh", "root@192.168.121.123", "date -s \'{}\'".format(formatted_now)],
####                        shell=False,
####                        capture_output=True,
####                        text=True,
####                        #stdout=subprocess.PIPE,
####                        #stderr=subprocess.PIPE,
####                        #check=False)
####                        )
####print (result.stdout)
####result = subprocess.run(["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 testaa.py"],
####                        shell=False,
####                        capture_output=True,
####                        text=True,
#####                        stdout=subprocess.PIPE,
#####                        stderr=subprocess.PIPE,
####                        check=False)
#####print (result)
####print (result.stdout)
####
####
#####result = subprocess.run(["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 DAT_LArASIC_QC_top.py -t 0;"],
#####result = subprocess.run(["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"],
#####                        shell=False,
#####                        stdout=subprocess.PIPE,
#####                        stderr=subprocess.PIPE,
#####                        check=False)
#####
####
#####if b"Pass the interconnection checkout, QC may start now!" in result.stdout:
#####	print("Success!")
#####else:
#####	print("Failed")
###
