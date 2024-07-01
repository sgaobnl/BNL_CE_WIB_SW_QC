import sys 
import time 
import pickle

class RTS_CFG():
    def __init__(self):
        self.mainp_fp = None
        self.qclog_fp = None

    def read_mainpfp(self): # default port for socket 
        try:
            with open(self.mainp_fp, 'r') as fn:
                rts_r = fn.read()
                #rts_rls = rts_r.splitlines()
                return rts_r
        except BaseException as e:
            print (e)
            return False
        
    def read_qclog(self): # default port for socket 
        try:
            with open(self.qclog_fp, 'rb') as fn:
                qclog = pickle.load(fn)
                a = list(qclog.keys())
                #print (a)
                #print (qclog['RTS_IDs'])
                return qclog['RTS_IDs']
        except BaseException as e:
            print (e)
            return False

    def read_mainpfp(rts_r, msg): # default port for socket 
        if msg in rts_r:
            x = rts_r.find(msg)
            msg_full = rts_r[x:100000]
            msg_rls = msg_full.splitlines()



if __name__ == "__main__":
    a = RTS_CFG()
    a.mainp_fp = "D:/dat_tmp/dat/manip.csv"
    a.qclog_fp = "D:/dat_tmp/dat/Time_20240628185432_DUT_0080_1081_2082_3083_4084_5085_6086_7087/RT_FE_002010000_002020000_002030000_002040000_002050000_002060000_002070000_002080000/QC.log"
    #a.read_mainpfp()
    a.read_qclog()
   
