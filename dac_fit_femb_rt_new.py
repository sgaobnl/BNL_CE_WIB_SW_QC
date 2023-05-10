# -*- coding: utf-8 -*-
"""
File Name: read_mean.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/9/2016 7:12:33 PM
Last modified: 3/8/2023 11:04:34 AM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

import openpyxl as px
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

def linear_fit(x, y):
    error_fit = False 
    try:
        results = sm.OLS(y,sm.add_constant(x)).fit()
    except ValueError:
        error_fit = True 
    if ( error_fit == False ):
        error_gain = False 
        try:
            slope = results.params[1]
        except IndexError:
            slope = 0
            error_gain = True
        try:
            constant = results.params[0]
        except IndexError:
            constant = 0
    else:
        slope = 0
        constant = 0
        error_gain = True

    y_fit = np.array(x)*slope + constant
    delta_y = abs(y - y_fit)
    inl = delta_y / (max(y)-min(y))
    peakinl = max(inl)
    return slope, constant, peakinl, error_gain


remove_val=0
dac_lin=64
encs = [0] * (dac_lin-remove_val) 
ps = [0] * (dac_lin-remove_val) 
lin_amp_200mv_ch4_rt_si_47=(dac_lin-remove_val)*[0]
lin_amp_200mv_ch4_rt_si_78=(dac_lin-remove_val)*[0]
lin_amp_200mv_ch4_rt_si_14=(dac_lin-remove_val)*[0]
lin_amp_200mv_ch4_rt_si_25=(dac_lin-remove_val)*[0]
lin_amp_200mv_ch4_rt_si_sgp1=(dac_lin-remove_val)*[0]

amp_200mv_ch4=(dac_lin-2)*[0]
plot_dir= "./"

amp = np.array( [ 7.65,26.2,44.65,62.95,81.25,100.4,119.57,138.42,157.17,175.9,194.52,212.9,231.6,250.53,269.52,288.12,306.8,325.13,343.9,362.16,380.5,399.25,417.8,436.57,454.89,473.66,492.27,510.5,529.3,547.7,567,586.2,605.2,623.5,642.4,661,679.5,698.2,717,735.2,753.8,772.6,791.1,809.6,828.5,848,866.9,885.3,904.1,922.6,941.4,959.8,978.5,997.1,1015,1033.6,1052.3,1070.8,1089.3,1108,1126.7,1145.7,1164.4,1183.1  
                  ] )
amp_RT_SGP0_47=np.array( [ 7.65,26.2,44.65,62.95,81.25,100.4,119.57,138.42,157.17,175.9,194.52,212.9,231.6,250.53,269.52,288.12,306.8,325.13,343.9,362.16,380.5,399.25,417.8,436.57,454.89,473.66,492.27,510.5,529.3,547.7,567,586.2,605.2,623.5,642.4,661,679.5,698.2,717,735.2,753.8,772.6,791.1,809.6,828.5,848,866.9,885.3,904.1,922.6,941.4,959.8,978.5,997.1,1015,1033.6,1052.3,1070.8,1089.3,1108,1126.7,1145.7,1164.4,1183.1])
amp_RT_SGP0_78=np.array( [ 280.5,294.8,308.8,322.84,336.9,350.6,366.3,380.8,392.2,409.5,423.9,438,452.5,467,481.4,495.8,510.1,524.2,538.6,552.6,566.7,581.1,595.3,609.8,623.9,638.3,652.5,666.6,681,695.2,710,724.7,739.3,753.3,767.9,782.1,796.3,810.7,825.2,839.1,853.4,867.8,882,896.2,910.7,925.6,940.2,954.3,968.7,982.9,997.4,1011.5,1025.9,1040.2,1053.9,1068.3,1082.6,1096.8,1111.1,1125.4,1139.7,1154.4,1168.8,1183.1])
amp_RT_SGP0_14=np.array( [673.4,681.6,689.5,697.5,705.4,713.7,722,730.1,738.3,746.4,754.5,762.5,770.6,778.9,787,795.2,803.2,811.2,819.3,827.2,835.1,843.2,851.2,859.4,867.3,875.5,883.6,891.5,899.6,907.6,916,924.3,932.5,940.4,948.6,956.6,964.7,972.7,980.9,988.7,996.8,1005,1013,1021,1029.2,1037.6,1045.9,1053.8,1062,1070,1078.2,1086.2,1094.3,1102.4,1110.1,1118.2,1126.3,1134.3,1142.4,1150.5,1158.6,1166.9,1175,1183.1])
amp_RT_SGP0_25=np.array( [892.7,897.7,901.8,906.4,910.9,915.6,920.3,925,929.7,933.3,938.9,943.4,948,952.7,957.4,962,966.6,971.1,975.7,980.2,984.7,989.4,994,998.6,1003.1,1007.8,1012.4,1016.8,1021.5,1026,1030.8,1035.6,1040.2,1044.7,1049.4,1054,1058.5,1063.2,1067.8,1072.3,1076.9,1081.6,1086.1,1090.7,1095.4,1100.2,1104.9,1109.4,1114.1,1118.7,1123.3,1127.9,1132.5,1137.2,1141.5,1146.2,1150.8,1155.3,1160,1164.5,1169.2,1173.9,1178.5,1183.1])
amp_RT_SGP1=np.array( [7.81,26.4,44.9,63.1,81.4,100.5,119.7,138.5,157.4,175.8,194.5,213,231.7,250.6,269.5,288.2,307,325.3,344,362.2,380.5,399.3,417.8,436.6,454.9,473.7,492.3,510.6,529.3,547.8,567.1,586.4,605.3,623.5,642.4,661,679.5,698.3,717.1,735.2,753.8,772.6,791.1,809.6,828.6,848,866.9,885.4,904.1,922.6,941.5,959.8,978.5,997.1,1015,1033.7,1052.3,1070.7,1089.3,1108,1126.7,1145.7,1164.4,1183.1])

amp_LN2_SGP0_47=np.array( [ 1.81,1.81,14.2,32,50.4,70.1,89.7,109.1,128.3,147,166,184.5,203.8,223,242.2,261.2,280.2,298.8,318,336.4,354.7,373.8,392.6,411.9,430.4,449.8,468.6,487.1,506.4,525,545,564.9,584.3,602.8,622.6,641.5,660.2,679.3,698.5,716.5,735.5,754.7,773.1,791.9,810.8,831.2,850.3,868.5,887.4,905.8,924.4,942.5,961.1,980.1,997.8,1016.7,1035.7,1054.5,1073.1,1092,1110.9,1130.3,1148.6,1167.3])
amp_LN2_SGP0_78=np.array( [253.1,267.7,282,296,310.4,325.8,341,356,370.8,385.2,399.8,414.1,428.9,443.6,458.4,473,487.6,502,516.7,530.8,544.8,559.6,574,588.8,603,617.9,632,646.4,661.2,675.4,690.7,705.9,720.7,734.8,749.9,764.1,778.4,792.8,807.5,821.2,835.7,850.4,864.5,878.9,893.3,908.8,923.3,937,951.4,965.5,980.2,994.5,1009.1,1023.8,1037.4,1051.9,1066.4,1080.7,1095,1109.5,1124,1138.9,1152.9,1167.3])
amp_LN2_SGP0_14=np.array( [651.7,660,668.1,676,684.1,692.7,701.1,709.6,717.9,725.9,734.1,742.1,750.4,758.6,766.9,775.1,783.2,791.2,799.5,807.4,815.2,823.5,831.5,839.9,847.8,856.1,864.2,872.1,880.3,888.3,896.8,905.2,913.5,921.3,929.7,937.7,945.6,953.7,961.9,969.7,978,986.5,994.6,1002.9,1011.3,1020.2,1028.6,1036.6,1045,1053.1,1061.4,1069.5,1077.7,1086,1093.6,1101.8,1110,1118.2,1126.2,1134.4,1142.7,1151.2,1159.1,1167.3])
amp_LN2_SGP0_25=np.array( [ 878,882.6,887.1,891.5,896,900.7,905.5,910.1,914.7,919.1,923.6,928,932.6,937.1,941.7,946.2,950.7,955.1,959.8,964.2,968.6,973.3,977.8,982.5,987.1,991.8,996.4,1000.9,1005.6,1010.1,1015,1019.9,1024.6,1029.1,1033.9,1038.5,1043.1,1047.7,1052.4,1056.8,1061.5,1066.2,1070.7,1075.3,1079.9,1084.9,1089.6,1094.1,1098.8,1103.3,1108,1112.5,1117.2,1121.7,1126,1130.6,1135.2,1139.8,1144.3,1148.9,1153.5,1158.3,1162.7,1167.3])
amp_LN2_SGP1=np.array( [1.8,1.8,14.3,32.1,50.5,70.2,89.8,109.2,128.4,147.2,166.2,184.7,203.9,223.1,242.3,261.3,280.3,298.9,318.2,336.5,354.7,373.9,392.6,412,430.5,449.9,468.7,487.1,506.5,525.1,545.1,565,584.4,602.9,622.7,641.6,660.3,679.3,698.5,716.6,735.5,754.7,773.2,791.9,810.9,831.2,850.3,868.5,887.4,905.8,924.5,942.6,961.1,980.1,997.8,1016.8,1035.8,1054.5,1073.1,1092,1110.9,1130.4,1148.6,1167.3])

amp=amp_LN2_SGP1
temp=  "LN2"#"RT"
Gain= ""#"25"  #"14" ## #"7.8"
sgp= "" # "SGP_1"

a = []
for i in range(64, 0, -1):
#for i in range(64):
        a.append(i)
dacbins = np.array(a)

index =0 
 
amp=amp_RT_SGP0_47
for i in range(dac_lin-remove_val):
    ps[i]= i+remove_val
    encs[i]=amp[i+remove_val]
fit_results1 = linear_fit(ps, encs)

for i in range(dac_lin-remove_val):
    lin_amp_200mv_ch4_rt_si_47[i]=  fit_results1[0]*(i+2)+ fit_results1[1]

amp=amp_RT_SGP0_78
for i in range(dac_lin-remove_val):
    ps[i]= i+remove_val
    encs[i]=amp[i+remove_val]
fit_results2 = linear_fit(ps, encs)

for i in range(dac_lin-remove_val):
    lin_amp_200mv_ch4_rt_si_78[i]=  fit_results2[0]*(i+2)+ fit_results2[1]

amp=amp_RT_SGP0_14    
for i in range(dac_lin-remove_val):
    ps[i]= i+remove_val
    encs[i]=amp[i+remove_val]
fit_results3 = linear_fit(ps, encs)

for i in range(dac_lin-remove_val):
    lin_amp_200mv_ch4_rt_si_14[i]=  fit_results3[0]*(i+2)+ fit_results3[1]

amp=amp_RT_SGP0_25
for i in range(dac_lin-remove_val):
    ps[i]= i+remove_val
    encs[i]=amp[i+remove_val]
fit_results4 = linear_fit(ps, encs)

for i in range(dac_lin-remove_val):
    lin_amp_200mv_ch4_rt_si_25[i]=  fit_results4[0]*(i+2)+ fit_results4[1]

amp=amp_RT_SGP1
for i in range(dac_lin-remove_val):
    ps[i]= i+remove_val
    encs[i]=amp[i+remove_val]
fit_results5 = linear_fit(ps, encs)

for i in range(dac_lin-remove_val):
    lin_amp_200mv_ch4_rt_si_sgp1[i]=  fit_results5[0]*(i+2)+ fit_results5[1]

    
amp_900mv_ch4=[0] * 64  
residu  =(dac_lin-remove_val)*[0]    
   
x = np.array([63,62,61,60,59,58,57,56,55,54,53,52,51,50,49,48,47,46,45,44,43,42,41,40,39,38,37,36,35,34,33,32,31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0])
x1 = x[remove_val:]

plt.plot(dacbins, amp_LN2_SGP0_47, marker='.', linewidth=1.5, label= "SGP = 0, 4.7 mV/fC")
plt.plot(dacbins, amp_LN2_SGP0_78, marker='.', linewidth=1.5, label= "SGP = 0, 7.8 mV/fC")
plt.plot(dacbins, amp_LN2_SGP0_14, marker='.', linewidth=1.5, label= "SGP = 0, 14 mV/fC")
plt.plot(dacbins, amp_LN2_SGP0_25, marker='.', linewidth=1.5, label= "SGP = 0, 25 mV/fC")
plt.plot(dacbins, amp_LN2_SGP1, marker='.', linewidth=1.5, label= "SGP = 1")
plt.legend()

#x = np.arange(2, dac_lin, 1)
#plt.plot(x1, lin_amp_200mv_ch4_rt_si, c='b', linewidth=1.5)
plt.ylabel("Amplitude / mV")
plt.xlabel("DAC bins")
#plt.text(64,1100.0,"Y = (%f) * X + (%f)"%(fit_results[1],fit_results[0]) )
#plt.title("Linear fit, " +  temp + ", " + sgp + " ," + Gain + "mV/fC" )
plt.title("DAC, " +  temp   )
#plt.xlim(max(dacbins)+1, min(dacbins)-1)
plt.tight_layout()
plt.grid()
#plt.ylim(max(y), min(y))
plt.savefig(plot_dir+ "DAC_"+ temp + "_" + sgp+ "_" + Gain + "mV-fc.jpg")
plt.close()


#dnl1 = []
#for i in range(len(amp) - remove_val -1 ):
#    dnl1.append( amp[i+1+remove_val] -amp[i+remove_val] )
##print cslope
#print (dnl1)
#lsb = (amp[63-remove_val]-amp[0] )/ (64-remove_val)
#dnl1 = ( ( dnl1 - lsb) /lsb ) 
remove_val=2
amp=amp_LN2_SGP0_47
dnl1 = []
for i in range(len(amp) - remove_val -1 ):
    dnl1.append( amp[i+1+remove_val] -amp[i+remove_val] )
#print cslope
print (dnl1)
lsb = ((amp[63-remove_val]-amp[0] )/ (63-remove_val))
dnl1 = ( ( dnl1 - lsb) /lsb ) 
print(np.mean(dnl1))
#dnl1=dnl1-np.mean(dnl1)

remove_val=0
amp=amp_LN2_SGP0_78
dnl2 = []
for i in range(len(amp) - remove_val -1 ):
    dnl2.append( amp[i+1+remove_val] -amp[i+remove_val] )
#print cslope
print (dnl2)
lsb =  ((amp[63-remove_val]-amp[0] )/ (63-remove_val))
dnl2 = ( ( dnl2 - lsb) /lsb )
print(np.mean(dnl2))
#dnl2=dnl2-np.mean(dnl2)

remove_val=0
amp=amp_LN2_SGP0_14
dnl3 = []
for i in range(len(amp) - remove_val -1 ):
    dnl3.append( amp[i+1+remove_val] -amp[i+remove_val] )
#print cslope
print (dnl3)
lsb =  ((amp[63-remove_val]-amp[0] )/ (63-remove_val))
dnl3 = ( ( dnl3 - lsb) /lsb )
print(np.mean(dnl3))
#dnl3=dnl3-np.mean(dnl3)

remove_val=0
amp=amp_LN2_SGP0_25
dnl4 = []
for i in range(len(amp) - remove_val -1 ):
    dnl4.append( amp[i+1+remove_val] -amp[i+remove_val] )
#print cslope
print (dnl4)
lsb =  ((amp[63-remove_val]-amp[0] )/ (63-remove_val))
dnl4 = ( ( dnl4 - lsb) /lsb )
print(np.mean(dnl4))
#dnl4=dnl4-np.mean(dnl4)

remove_val=2
amp=amp_LN2_SGP1
dnl5 = []
for i in range(len(amp) - remove_val -1 ):
    dnl5.append( amp[i+1+remove_val] -amp[i+remove_val] )
#print cslope
print (dnl5)
lsb =  ((amp[63-remove_val]-amp[0] )/ (63-remove_val))
dnl5 = ( ( dnl5 - lsb) /lsb )
print(np.mean(dnl5))
#dnl5=dnl5-np.mean(dnl5)

#plt.scatter(dacbins[(1+remove_val):], dnl, c='r',marker='.', linewidth=1.5)
#plt.plot(dacbins[(1+remove_val):], dnl, c='b', linewidth=1.5)
plt.plot(dacbins[(1+2):], dnl1[:],  marker='.', linewidth=1.5, label= "SGP = 0, 4.7 mV/fC")
plt.plot(dacbins[(1+0):], dnl2,  marker='.', linewidth=1.5, label= "SGP = 0, 7.8 mV/fC")
plt.plot(dacbins[(1+0):], dnl3,  marker='.', linewidth=1.5, label= "SGP = 0, 14 mV/fC")
plt.plot(dacbins[(1+0):], dnl4,  marker='.', linewidth=1.5, label= "SGP = 0, 25 mV/fC")
plt.plot(dacbins[(1+2):], dnl5[:],  marker='.', linewidth=1.5, label= "SGP = 1")
plt.legend()
plt.ylabel("DNL / LSB")
plt.xlabel("DAC bins")
plt.ylim([-1,1])
#plt.xlim([0,63-remove_val])
#plt.text(max(x)-remove_val, 0.8, "LSB = %3f"%(lsb) )
plt.text(min(x)+remove_val, 0.6, "DNL(i) = (V(i) - V(i-1) - LSB) / LSB" )
plt.title("DAC DNL, " +  temp + " " + sgp + " " + Gain + "" )
plt.grid(True)
#plt.xlim(max(x)+1 - remove_val, min(x)-1)
plt.savefig(plot_dir+ "DNL_"+ temp + "_" + sgp+ "_" + Gain + "mV-fc.jpg")
plt.close()


inl1 = []
for i in range(len(dnl1)):
    if (i == 0):
        inl1.append(0)
    else:
        inl1.append(np.sum(dnl1[0:i]))
print (inl1)

inl2 = []
for i in range(len(dnl2)):
    if (i == 0):
        inl2.append(0)
    else:
        inl2.append(np.sum(dnl2[0:i]))
print (inl2)

inl3 = []
for i in range(len(dnl3)):
    if (i == 0):
        inl3.append(0)
    else:
        inl3.append(np.sum(dnl3[0:i]))
print (inl3)

inl4 = []
for i in range(len(dnl4)):
    if (i == 0):
        inl4.append(0)
    else:
        inl4.append(np.sum(dnl4[0:i]))
print (inl4)

inl5 = []
for i in range(len(dnl5)):
    if (i == 0):
        inl5.append(0)
    else:
        inl5.append(np.sum(dnl5[0:i]))
print (inl5)
#plt.scatter(dacbins[(1+remove_val):], inl, c='r',marker='.', linewidth=1.5)
#plt.plot(dacbins[(1+remove_val):], inl, c='b')

plt.plot(dacbins[(1+2):], inl1[:], marker='.', linewidth=1.5, label= "SGP = 0, 4.7 mV/fC")
plt.plot(dacbins[(1+0):], inl2,  marker='.', linewidth=1.5, label= "SGP = 0, 7.8 mV/fC")
plt.plot(dacbins[(1+0):], inl3,  marker='.', linewidth=1.5, label= "SGP = 0, 14 mV/fC")
plt.plot(dacbins[(1+0):], inl4,  marker='.', linewidth=1.5, label= "SGP = 0, 25 mV/fC")
plt.plot(dacbins[(1+2):], inl5[:],  marker='.', linewidth=1.5, label= "SGP = 1")
plt.legend()

plt.ylabel("INL / LSB")
plt.xlabel("DAC bins")
plt.ylim([-3,3])
#plt.xlim([0,63])
#plt.text(max(x) - remove_val, 2.5, "LSB = %3f"%(lsb) )
plt.text(min(x)+ remove_val, 2.1, "INL(i) = DNL(0) + DNL(1) + ... + DNL(i-1)" )
plt.title("DAC INL, " +  temp + " " + sgp + " " + Gain + "" )
plt.grid(True)
#plt.xlim(max(x)+1 - remove_val, min(x)-1)
plt.savefig(plot_dir+ "INL_"+ temp + "_" + sgp+ "_" + Gain + "mV-fc.jpg")
plt.close()


#def adc_fit():
#    
#    a = []
#    for i in range(64):
#        a.append(i)
#
#    dacbins = np.array(a)
#    #amp = np.array( [0.005, 0.025,0.025,0.025,0.041,0.059,0.078,0.096,0.115,
##    amp = np.array( [ 0.025,0.025,0.025,0.041,0.059,0.078,0.096,0.115,
##                     0.133,0.152,0.171,0.189,0.208,0.227,0.245,0.264,
##                     0.282,0.301,0.319,0.338,0.356,0.375,0.394,0.412,
##                     0.431,0.450,0.468,0.487,0.505,0.524,0.542,0.561,
##                     0.579,0.598,0.616,0.635,0.653,0.672,0.691,0.709,
##                     0.728,0.746,0.765,0.784,0.802,0.821,0.840,0.858,
##                     0.877,0.896,0.914,0.933,0.951,0.970,0.988,1.007,
##                     1.026,1.044,1.062,1.081,1.100,1.118,1.137,1.155
##                    ] )
#
##    amp = np.array( [ 0.001,0.015 ,0.019 ,0.029 ,0.047 ,0.063 ,0.081 ,0.099 ,0.116 ,
#    amp = np.array( [ 7.65,26.2,44.65,62.95,81.25,100.4,119.57,138.42,157.17,175.9,194.52,212.9,231.6,250.53,269.52,288.12,306.8,325.13,343.9,362.16,380.5,399.25,417.8,436.57,454.89,473.66,492.27,510.5,529.3,547.7,567,586.2,605.2,623.5,642.4,661,679.5,698.2,717,735.2,753.8,772.6,791.1,809.6,828.5,848,866.9,885.3,904.1,922.6,941.4,959.8,978.5,997.1,1015,1033.6,1052.3,1070.8,1089.3,1108,1126.7,1145.7,1164.4,1183.1
#                    ] )
#
#
#    cresults = sm.OLS(amp[1:64],sm.add_constant(dacbins[1:64])).fit()
#    cslope = cresults.params[1]
#    cconstant = cresults.params[0]
#    with open ("adc_fit.txt","w") as f:
#        a = str(cresults.summary())
#        f.write(a)        
#
#    plt.scatter(dacbins[:], amp[:], c='r',marker='o')
#    cx_plot = np.linspace(0,max(dacbins))
#    cx_plot1 =np.arange(63, 0, -1)
#    plt.ylabel("Amplitude / V")
#    plt.xlabel("DAC bins")
#    plt.text(1,1.0,"Y = (%f) * X + (%f)"%(cslope,cconstant) )
#    plt.title("Linear fit (RT)" )
#    plt.plot(cx_plot1, cx_plot*cslope + cconstant, 'r')
#    plt.savefig(".\\dac_fit_femb.jpg")
#    plt.close()
#
#
#    dnl = []
#    for i in range(len(amp) - 4):
#        dnl.append( amp[i+4] -amp[i+3] )
#    #print cslope
#    print (dnl)
#    lsb = (amp[63]-amp[0] )/ 64
#    dnl = ( ( dnl - lsb) /lsb ) 
#
#    plt.scatter(dacbins[4:], dnl, c='r',marker='o')
#    plt.plot(dacbins[4:], dnl, c='b')
#    
#    plt.ylabel("DNL / LSB")
#    plt.xlabel("DAC bins")
#    plt.ylim([-1,1])
#    plt.xlim([0,63])
#    plt.text(1, 0.8, "LSB = %3f"%(lsb) )
#    plt.text(1, 0.6, "DNL(i) = (V(i) - V(i-1) - LSB) / LSB" )
#    plt.title("DNL (RT)" )
#    plt.grid(True)
#    plt.savefig(".\\dac_fit_femb_dnl.jpg")
#    plt.close()
#
#    inl = []
#    for i in range(len(dnl)):
#        if (i == 0):
#            inl.append(0)
#        else:
#            inl.append(np.sum(dnl[0:i]))
#    
#    print (inl)
#
#    plt.scatter(dacbins[4:], inl, c='r',marker='o')
#    plt.plot(dacbins[4:], inl, c='b')
#
#    plt.ylabel("INL / LSB")
#    plt.xlabel("DAC bins")
#    plt.ylim([-3,3])
#    plt.xlim([0,63])
#    plt.text(1, 0.8, "LSB = %3f"%(lsb) )
#    plt.text(1, 0.6, "INL(i) = DNL(0) + DNL(1) + ... + DNL(i-1)" )
#    plt.title("INL (RT)" )
#    plt.grid(True)
#    plt.savefig(".\\dac_fit_femb_inl.jpg")
#    plt.close()
#
#
#adc_fit()




