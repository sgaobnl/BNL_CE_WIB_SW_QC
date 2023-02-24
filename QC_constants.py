SNC = ["900mVBL", "200mVBL"]  # 0,1 
SGS = ["14_0mVfC", "25_0mVfC", "7_8mVfC", "4_7mVfC" ]   # 0,1,2,3
STS = ["1_0us", "0_5us",  "3_0us", "2_0us"]  # 0,1,2,3

# In root temperature pedestal mean value
# PED_RT_mean[snc][sgs][sts]
PED_RT_mean = [[[0]*4]*4]*2
PED_RT_mean[0][0][0] = 8510   # 900mV, 14mV/fC, 1.0 us
PED_RT_mean[0][0][1] = 8434   # 900mV, 14mV/fC, 0.5 us
PED_RT_mean[0][0][2] = 8815   # 900mV, 14mV/fC, 3.0 us
PED_RT_mean[0][0][3] = 8663   # 900mV, 14mV/fC, 2.0 us
PED_RT_mean[0][1][0] = 8629   # 900mV, 25mV/fC, 1.0 us
PED_RT_mean[0][1][1] = 8493   # 900mV, 25mV/fC, 0.5 us
PED_RT_mean[0][1][2] = 9171   # 900mV, 25mV/fC, 3.0 us
PED_RT_mean[0][1][3] = 8901   # 900mV, 25mV/fC, 2.0 us
PED_RT_mean[0][2][0] = 8445   # 900mV, 7.8mV/fC, 1.0 us
PED_RT_mean[0][2][1] = 8401   # 900mV, 7.8mV/fC, 0.5 us
PED_RT_mean[0][2][2] = 8617   # 900mV, 7.8mV/fC, 3.0 us
PED_RT_mean[0][2][3] = 8531   # 900mV, 7.8mV/fC, 2.0 us
PED_RT_mean[0][3][0] = 8411   # 900mV, 4.7mV/fC, 1.0 us
PED_RT_mean[0][3][1] = 8385   # 900mV, 4.7mV/fC, 0.5 us
PED_RT_mean[0][3][2] = 8517   # 900mV, 4.7mV/fC, 3.0 us
PED_RT_mean[0][3][3] = 8464   # 900mV, 4.7mV/fC, 2.0 us

PED_RT_mean[1][0][0] = 762   # 200mV, 14mV/fC, 1.0 us
PED_RT_mean[1][0][1] = 688   # 200mV, 14mV/fC, 0.5 us
PED_RT_mean[1][0][2] = 1057  # 200mV, 14mV/fC, 3.0 us
PED_RT_mean[1][0][3] = 908   # 200mV, 14mV/fC, 2.0 us
PED_RT_mean[1][1][0] = 875   # 200mV, 25mV/fC, 1.0 us
PED_RT_mean[1][1][1] = 745   # 200mV, 25mV/fC, 0.5 us
PED_RT_mean[1][1][2] = 1407   # 200mV, 25mV/fC, 3.0 us
PED_RT_mean[1][1][3] = 1140   # 200mV, 25mV/fC, 2.0 us
PED_RT_mean[1][2][0] = 697   # 200mV, 7.8mV/fC, 1.0 us
PED_RT_mean[1][2][1] = 656   # 200mV, 7.8mV/fC, 0.5 us
PED_RT_mean[1][2][2] = 861   # 200mV, 7.8mV/fC, 3.0 us
PED_RT_mean[1][2][3] = 779   # 200mV, 7.8mV/fC, 2.0 us
PED_RT_mean[1][3][0] = 664    # 200mV, 4.7mV/fC, 1.0 us
PED_RT_mean[1][3][1] = 639    # 200mV, 4.7mV/fC, 0.5 us
PED_RT_mean[1][3][2] = 764    # 200mV, 4.7mV/fC, 3.0 us
PED_RT_mean[1][3][3] = 714    # 200mV, 4.7mV/fC, 2.0 us

# In root temperature rms mean value
# RMS_RT_mean[snc][sgs][sts]
RMS_RT_mean = [[[0]*4]*4]*2
RMS_RT_mean[0][0][0] = 22.4   # 900mV, 14mV/fC, 1.0 us
RMS_RT_mean[0][0][1] = 27.3   # 900mV, 14mV/fC, 0.5 us
RMS_RT_mean[0][0][2] = 18.1   # 900mV, 14mV/fC, 3.0 us
RMS_RT_mean[0][0][3] = 19.1   # 900mV, 14mV/fC, 2.0 us
RMS_RT_mean[0][1][0] = 39.6   # 900mV, 25mV/fC, 1.0 us
RMS_RT_mean[0][1][1] = 47.3   # 900mV, 25mV/fC, 0.5 us
RMS_RT_mean[0][1][2] = 32.1   # 900mV, 25mV/fC, 3.0 us
RMS_RT_mean[0][1][3] = 33.7   # 900mV, 25mV/fC, 2.0 us
RMS_RT_mean[0][2][0] = 12.6   # 900mV, 7.8mV/fC, 1.0 us
RMS_RT_mean[0][2][1] = 15.4   # 900mV, 7.8mV/fC, 0.5 us
RMS_RT_mean[0][2][2] = 10.2   # 900mV, 7.8mV/fC, 3.0 us
RMS_RT_mean[0][2][3] = 10.8   # 900mV, 7.8mV/fC, 2.0 us
RMS_RT_mean[0][3][0] = 7.8   # 900mV, 4.7mV/fC, 1.0 us
RMS_RT_mean[0][3][1] = 9.5   # 900mV, 4.7mV/fC, 0.5 us
RMS_RT_mean[0][3][2] = 6.4   # 900mV, 4.7mV/fC, 3.0 us
RMS_RT_mean[0][3][3] = 6.7   # 900mV, 4.7mV/fC, 2.0 us

RMS_RT_mean[1][0][0] = 21.6   # 200mV, 14mV/fC, 1.0 us
RMS_RT_mean[1][0][1] = 26.2   # 200mV, 14mV/fC, 0.5 us
RMS_RT_mean[1][0][2] = 17.8   # 200mV, 14mV/fC, 3.0 us
RMS_RT_mean[1][0][3] = 18.6   # 200mV, 14mV/fC, 2.0 us
RMS_RT_mean[1][1][0] = 38.5   # 200mV, 25mV/fC, 1.0 us
RMS_RT_mean[1][1][1] = 45.9   # 200mV, 25mV/fC, 0.5 us
RMS_RT_mean[1][1][2] = 31.9   # 200mV, 25mV/fC, 3.0 us
RMS_RT_mean[1][1][3] = 33.2   # 200mV, 25mV/fC, 2.0 us
RMS_RT_mean[1][2][0] = 12.1   # 200mV, 7.8mV/fC, 1.0 us
RMS_RT_mean[1][2][1] = 14.7   # 200mV, 7.8mV/fC, 0.5 us
RMS_RT_mean[1][2][2] = 10.0   # 200mV, 7.8mV/fC, 3.0 us
RMS_RT_mean[1][2][3] = 10.5   # 200mV, 7.8mV/fC, 2.0 us
RMS_RT_mean[1][3][0] = 7.5    # 200mV, 4.7mV/fC, 1.0 us
RMS_RT_mean[1][3][1] = 9.1    # 200mV, 4.7mV/fC, 0.5 us
RMS_RT_mean[1][3][2] = 6.3    # 200mV, 4.7mV/fC, 3.0 us
RMS_RT_mean[1][3][3] = 6.5    # 200mV, 4.7mV/fC, 2.0 us

