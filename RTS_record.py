import sys 
import time 
import pickle
import os
import shutil

class RTS_MANIP():
    def __init__(self):
        self.manip_fp = None
        self.qclog_fp = None
        self.rootdir = None
        self.rts_msg_fp = None

    def read_manipfp(self): # default port for socket 
        try:
            with open(self.manip_fp, 'r') as fn:
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
                return qclog['RTS_IDs']
        except BaseException as e:
            print (e)
            return False

    def manip_extract(self,  rts_r, rts_msg_wfp): # default port for socket 
        rts_msg = rts_msg_wfp[1]
        self.rts_msg_fp  = rts_msg_wfp[0]
        print (self.rts_msg_fp)

#        pic_dir = self.rootdir + "images/"
#        if not os.path.exists(pic_dir):
#            print (pic_dir)
#            try:
#                os.makedirs(pic_dir)
#            except OSError:
#                print ("Error to create folder %s"%pic_dir)
#                sys.exit()
#        else:
#            pass
#        
        f=self.rts_msg_fp 
        x = f.find("_log.bin")
        msg0 = f[x-14:x]
        x = rts_r.find(msg0)
        msg_full = rts_r[x:]
        msg_rls = msg_full.splitlines()

        r2s_p = sorted(list(rts_msg['RTS_MSG_R2S_P'].keys()))
        s2r_p = sorted(list(rts_msg['RTS_MSG_S2R_P'].keys()))
        s2r_f = sorted(list(rts_msg['RTS_MSG_S2R_F'].keys()))

        msgs = r2s_p + s2r_p + s2r_f

        if os.path.exists(self.rootdir + "manip.csv"):
            with open(self.rootdir + "manip.csv", "r") as fn:
                manip_exist = fn.read()
        else:
            manip_exist = ""
            pass

        #save related RTS operation information 
        with open(self.rootdir + "manip.csv", "a+") as fn:
            for msg in msgs:
                for x in msg_rls:
                    if (msg in x) and (msg not in manip_exist):
                        fn.write(x + "\n")
                        #self.pic_copy(x, pic_dir) 
                        break

#    def rts_manip(self, msg, dst): 
    def pic_copy(self, msg, dst): 
        tmps = msg.split(",")
        for tmp in tmps:
            if "images" in tmp:
                src_pic = tmp
                #print (tmp)
#                k = src_pic.find("20240701")
#                src_pic = src_pic[k:]
#                src_pic = "D:\\dat_tmp\\0621\\images\\" + src_pic
#                print (src_pic)
                try:
                    shutil.copy2(src_pic, dst)
                    #if "_SN.bmp" in src_pic:
                    #    try:
                    #        #print (src_pic[0:-7] + "_socket.bmp")
                    #        shutil.copy2(src_pic[0:-7] + "_socket.bmp", dst)
                    #    except BaseException as e:
                    #        print (e)
                except BaseException as e:
                    x = src_pic.find("images")
                    src_pic = src_pic[0:x+7] + "UF_" + src_pic[x+7:]
                    try:
                        shutil.copy2(src_pic, dst)
                    except BaseException as e:
                        print (e)

    def read_rtsmsgfp(self): # default port for socket 
        rts_msgs = [] 
        for root, dirs, files in os.walk(self.rootdir):
            break

        for f in files:
            if "_log.bin" in f:
                self.rts_msg_fp =self.rootdir +  f

                try:
                    with open(self.rts_msg_fp, 'rb') as fn:
                        rts_msg = pickle.load(fn)
                        rts_msgs.append((self.rts_msg_fp,rts_msg))
                        #rts_rls = rts_r.splitlines()
                        #return rts_msg
                except BaseException as e:
                    print (e)
                    return False
        return (rts_msgs)
        


if __name__ == "__main__":
    a = RTS_MANIP()
    a.manip_fp = "C:/Users/coldelec/RTS/manip.csv"
    a.rootdir = "S:/RTS_DAT_LArASIC_QC/B009T0006/"
    rts_r = a.read_manipfp()

    rts_msgs = a.read_rtsmsgfp()
   
    for rts_msg_wfp in rts_msgs:
        msg_d = a.manip_extract(rts_r, rts_msg_wfp)

#    a.qclog_fp = "D:/dat_tmp/dat/Time_20240628185432_DUT_0080_1081_2082_3083_4084_5085_6086_7087/RT_FE_002010000_002020000_002030000_002040000_002050000_002060000_002070000_002080000/QC.log"
