import socket # for socket 
import sys 
import time 

class RTS_CFG():
    def __init__(self):
        self.s = None
        self.msg = None

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
            exit()
            #return None

        self.MotorOn() #
        self.JumpToCamera() #
        return self.msg

    def MotorOn(self): #
        while True:
            try:
                msg = "MotorOn"
                self.s.send(msg.encode())
                self.s.send(b"\r\n") 
                self.msg = self.s.recv(1024).decode() 
                self.msg = self.msg.strip()
                print (self.msg)
                break
            except ConnectionAbortedError:
                print ("ConnectionAbortedError")
                self.rts_init(port=2001, host_ip='192.168.0.2')

    def JumpToCamera(self): #
        while True:
            try:
                msg = "JumpToCamera"
                self.s.send(msg.encode())
                self.s.send(b"\r\n") 
                self.msg = self.s.recv(1024).decode() 
                self.msg = self.msg.strip()
                print (self.msg)
                break
            except ConnectionAbortedError:
                print ("ConnectionAbortedError")
                self.rts_init(port=2001, host_ip='192.168.0.2')

    def PumpOff(self): #
        while True:
            try:
                msg = "PumpOff"
                self.s.send(msg.encode())
                self.s.send(b"\r\n")
                self.msg = self.s.recv(1024).decode()
                self.msg = self.msg.strip()
                print (self.msg)
                break
            except ConnectionAbortedError:
                print ("ConnectionAbortedError")
                self.rts_init(port=2001, host_ip='192.168.0.2')

    def MoveChipFromTrayToSocket(self, tray_nr, col_nr, row_nr, DAT_nr, socket_nr):
        while True:
            try:
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
                status = int(self.msg)
                break
            except ConnectionAbortedError:
                print ("ConnectionAbortedError")
                self.rts_init(port=2001, host_ip='192.168.0.2')
        return status


    def MoveChipFromSocketToTray(self, DAT_nr, socket_nr, tray_nr, col_nr, row_nr):
        while True:
            try:
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
                print("msg: ", self.msg)
                status = int(self.msg)
                break
            except ConnectionAbortedError:
                print ("ConnectionAbortedError")
                self.rts_init(port=2001, host_ip='192.168.0.2')
        return status

    def MoveChipFromTrayToTray(self, stray_nr, scol_nr, srow_nr, dtray_nr, dcol_nr, drow_nr,):
        i = 0
        origpos = False
        while True:
            i = i + 1
            self.msg = "MoveChipFromTrayToTray"
            self.s.send(self.msg.encode())
            self.s.send(b"\r\n")
    
            self.s.send(str(stray_nr).encode())
            self.s.send(b"\r\n")
    
            self.s.send(str(scol_nr).encode())
            self.s.send(b"\r\n")
    
            self.s.send(str(srow_nr).encode())
            self.s.send(b"\r\n")

            self.s.send(str(dtray_nr).encode())
            self.s.send(b"\r\n")
    
            self.s.send(str(dcol_nr).encode())
            self.s.send(b"\r\n")
    
            self.s.send(str(drow_nr).encode())
            self.s.send(b"\r\n")

            self.msg = self.s.recv(1024).decode()
            self.msg = self.msg.strip()
            print("msg: ", self.msg)
            status = int(self.msg)
            if status >=0 :
                break
            else:
                if origpos:
                    print ("Error")
                    break
                cn = (drow_nr-1)*15+dcol_nr-1 + 1
                dcol_nr = cn%15 + 1
                drow_nr = cn//15 + 1
                print (cn , dcol_nr, drow_nr, i)
                if (cn >= 20) :
                    input ("please check..., any key to put the chip back to orignal position")
                    dtray_nr = stray_nr
                    dcol_nr = scol_nr
                    drow_nr = srow_nr
                    origpos = True
        return status

    def rts_idle(self): 
        while True:
            try:
                print ("Quiet")
                self.msg = "Quiet"
                self.s.send(self.msg.encode())
                self.s.send(b"\r\n")
                self.msg = self.s.recv(1024).decode()
                self.msg = self.msg.strip()
                print (self.msg)
                break
            except ConnectionAbortedError:
                print ("ConnectionAbortedError")
                self.rts_init(port=2001, host_ip='192.168.0.2')

    def rts_shutdown(self): 
        while True:
            try:
                self.PumpOff()

                self.msg = "Shutdown"
                self.s.send(self.msg.encode())
                self.s.send(b"\r\n")
                self.msg = self.s.recv(1024).decode()
                self.msg = self.msg.strip()
                print (self.msg)
                break
            except ConnectionAbortedError:
                print ("ConnectionAbortedError")
                self.rts_init(port=2001, host_ip='192.168.0.2')

        print("Closing socket connection...")
        time.sleep(3)
        self.s.close()
        

