import socket # for socket 
import sys 
import time 

class RTS_CFG():
    def __init__(self):
        self.s = None
        self.msg = None
        pass

    def rts_init(self, port=2001, host_ip='192.168.0.2'): # default port for socket 
        try: 
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            print ("Socket successfully created")
        except socket.error as err: 
            print ("socket creation failed with error %s" %(err))
         
        # connecting to the server 
        self.s.connect((host_ip, port))
 
        print("the socket has successfully connected to ",host_ip) 
        self.msg=self.s.recv(1024).decode()
        self.msg = self.msg.strip()
        
        if self.msg != "RTS ready":
        	print("***ERROR! Bad responce from server: [",self.msg,"]")
        	self.s.close()
            exit(-1)
            #return None
        return self.msg

    def MoveChipFromTrayToSocket(self, tray_nr, col_nr, row_nr, DAT_nr, socket_nr):
    	self.msg = "MoveChipFromTrayToSocket"
    	self.s.send(self.msg.encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(tray_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(col_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(row_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(DAT_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(socket_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.msg = self.s.recv(1024).decode()
    	self.msg = self.msg.strip()
    	print("msg: ", self.msg)
    	status = int(msg)
    
    	return status


    def MoveChipFromSocketToTray(self, DAT_nr, socket_nr, tray_nr, col_nr, row_nr):
    	self.msg = "MoveChipFromSocketToTray"
    	self.s.send(self.msg.encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(DAT_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(socket_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(tray_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(col_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.s.send(str(row_nr).encode())
    	self.s.send(b"\r\n")
    
    	self.msg = self.s.recv(1024).decode()
    	self.msg = self.msg.strip()
    	status = int(self.msg)
    
    	return status


    def rts_close(self): 
        self.msg = "PumpOff"
        self.s.send(self.msg.encode())
        self.s.send(b"\r\n")
        self.msg = "Exit"
        self.s.send(self.msg.encode())
        self.s.send(b"\r\n")
        print("Closing socket connection...")
        self.time.sleep(3)
        self.s.close()
        

