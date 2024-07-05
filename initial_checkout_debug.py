import socket # for socket 
import sys 
import subprocess
import time 

try: 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    print ("Socket successfully created")
except socket.error as err: 
    print ("socket creation failed with error %s" %(err))
 
# default port for socket 
port = 2001
host_ip='192.168.0.2'
 
 
# connecting to the server 
s.connect((host_ip, port))
 
print("the socket has successfully connected to ",host_ip) 
msg=s.recv(1024).decode()
msg = msg.strip()

if msg != "RTS ready":
	print("***ERROR! Bad responce from server: [",msg,"]")
	s.close()
	exit(-1)

def MoveChipFromTrayToSocket(tray_nr, col_nr, row_nr, DAT_nr, socket_nr):
	msg = "MoveChipFromTrayToSocket"
	s.send(msg.encode())
	s.send(b"\r\n")

	s.send(str(tray_nr).encode())
	s.send(b"\r\n")

	s.send(str(col_nr).encode())
	s.send(b"\r\n")

	s.send(str(row_nr).encode())
	s.send(b"\r\n")

	s.send(str(DAT_nr).encode())
	s.send(b"\r\n")

	s.send(str(socket_nr).encode())
	s.send(b"\r\n")

	msg = s.recv(1024).decode()
	msg = msg.strip()
	print("msg: ", msg)
	status = int(msg)

	return status


def MoveChipFromSocketToTray(DAT_nr, socket_nr, tray_nr, col_nr, row_nr):
	msg = "MoveChipFromSocketToTray"
	s.send(msg.encode())
	s.send(b"\r\n")

	s.send(str(DAT_nr).encode())
	s.send(b"\r\n")

	s.send(str(socket_nr).encode())
	s.send(b"\r\n")

	s.send(str(tray_nr).encode())
	s.send(b"\r\n")

	s.send(str(col_nr).encode())
	s.send(b"\r\n")

	s.send(str(row_nr).encode())
	s.send(b"\r\n")

	msg = s.recv(1024).decode()
	msg = msg.strip()
	status = int(msg)

	return status


def DAT_run_initial_test():

	ret = 0
	result = subprocess.run(["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 DAT_LArASIC_QC_top.py -t 0;"],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False)

	print(result.stdout)

	if b"Pass the interconnection checkout, QC may start now!" in result.stdout:
		print("Success!")
	else:
		print("Failed")
		ret = 1

	return ret


def LoadChipsToSockets():

	status = -1

	#for i in range(1,9):
	for i in [1]:
		print("Moving chip to socket ",i)
		status = MoveChipFromTrayToSocket(2, 7+i, 6, 2, i)
		print("Status: ", status)
		if status < 0:
			print("Error moving chips")
			break

	if status > 0:
		msg = "PumpOff"
		s.send(msg.encode())
		s.send(b"\r\n")

	return status

def MoveChipsToTray():

	status = -1

	#for i in range(1,9):
	for i in [1]:
		print("Moving chip from socket ",i)
		status = MoveChipFromSocketToTray(2, i, 2, 7+i, 6)
		print("Status: ", status)
		if status < 0:
			print("Error moving chips")
			break

	return status
	
ncycles=1
status = 0
for k in range(0,ncycles):

	print("Cycle ",k," / ", ncycles)

	status = 0

	status = LoadChipsToSockets()

	if status < 0:
		break


	print("Running WIB initial testing...")
	#status = DAT_run_initial_test()

	#if status != 0:
	#	"***ERROR! WIB inital test failed"
	#	break

	status = MoveChipsToTray()

	if status < 0:
		break
             



msg = "PumpOff"
s.send(msg.encode())
s.send(b"\r\n")


msg = "Exit"
msg = "Shutdown"
s.send(msg.encode())
s.send(b"\r\n")
print("Closing socket connection...")
time.sleep(3)
s.close()


