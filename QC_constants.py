SNC = ["900mVBL", "200mVBL"]  # 0,1 
SGS = ["14_0mVfC", "25_0mVfC", "7_8mVfC", "4_7mVfC" ]   # 0,1,2,3
STS = ["1_0us", "0_5us",  "3_0us", "2_0us"]  # 0,1,2,3

# pedestal lower limit
# PED_LN_lo[snc][sgs][sts]
PED_LN_lo = [[[0]*4]*4]*2
PED_LN_lo[0][0][0] = 500   # 900mV, 14mV/fC, 1.0 us
PED_LN_lo[0][0][1] = 500   # 900mV, 14mV/fC, 0.5 us
PED_LN_lo[0][0][2] = 500   # 900mV, 14mV/fC, 3.0 us
PED_LN_lo[0][0][3] = 500   # 900mV, 14mV/fC, 2.0 us
PED_LN_lo[0][1][0] = 500   # 900mV, 25mV/fC, 1.0 us
PED_LN_lo[0][1][1] = 500   # 900mV, 25mV/fC, 0.5 us
PED_LN_lo[0][1][2] = 500   # 900mV, 25mV/fC, 3.0 us
PED_LN_lo[0][1][3] = 500   # 900mV, 25mV/fC, 2.0 us
PED_LN_lo[0][2][0] = 500   # 900mV, 7.8mV/fC, 1.0 us
PED_LN_lo[0][2][1] = 500   # 900mV, 7.8mV/fC, 0.5 us
PED_LN_lo[0][2][2] = 500   # 900mV, 7.8mV/fC, 3.0 us
PED_LN_lo[0][2][3] = 500   # 900mV, 7.8mV/fC, 2.0 us
PED_LN_lo[0][3][0] = 500   # 900mV, 4.7mV/fC, 1.0 us
PED_LN_lo[0][3][1] = 500   # 900mV, 4.7mV/fC, 0.5 us
PED_LN_lo[0][3][2] = 500   # 900mV, 4.7mV/fC, 3.0 us
PED_LN_lo[0][3][3] = 500   # 900mV, 4.7mV/fC, 2.0 us

# pedestal higher limit
PED_LN_hi = [[[0]*4]*4]*2
PED_LN_hi[0][0][0] = 500   # 900mV, 14mV/fC, 1.0 us
PED_LN_hi[0][0][1] = 500   # 900mV, 14mV/fC, 0.5 us
PED_LN_hi[0][0][2] = 500   # 900mV, 14mV/fC, 3.0 us
PED_LN_hi[0][0][3] = 500   # 900mV, 14mV/fC, 2.0 us
PED_LN_hi[0][1][0] = 500   # 900mV, 25mV/fC, 1.0 us
PED_LN_hi[0][1][1] = 500   # 900mV, 25mV/fC, 0.5 us
PED_LN_hi[0][1][2] = 500   # 900mV, 25mV/fC, 3.0 us
PED_LN_hi[0][1][3] = 500   # 900mV, 25mV/fC, 2.0 us
PED_LN_hi[0][2][0] = 500   # 900mV, 7.8mV/fC, 1.0 us
PED_LN_hi[0][2][1] = 500   # 900mV, 7.8mV/fC, 0.5 us
PED_LN_hi[0][2][2] = 500   # 900mV, 7.8mV/fC, 3.0 us
PED_LN_hi[0][2][3] = 500   # 900mV, 7.8mV/fC, 2.0 us
PED_LN_hi[0][3][0] = 500   # 900mV, 4.7mV/fC, 1.0 us
PED_LN_hi[0][3][1] = 500   # 900mV, 4.7mV/fC, 0.5 us
PED_LN_hi[0][3][2] = 500   # 900mV, 4.7mV/fC, 3.0 us
PED_LN_hi[0][3][3] = 500   # 900mV, 4.7mV/fC, 2.0 us

PED_LN_lo = [[[0]*4]*4]*2
PED_LN_lo[1][0][0] = 500   # 200mV, 14mV/fC, 1.0 us
PED_LN_lo[1][0][1] = 500   # 200mV, 14mV/fC, 0.5 us
PED_LN_lo[1][0][2] = 500   # 200mV, 14mV/fC, 3.0 us
PED_LN_lo[1][0][3] = 500   # 200mV, 14mV/fC, 2.0 us
PED_LN_lo[1][1][0] = 500   # 200mV, 25mV/fC, 1.0 us
PED_LN_lo[1][1][1] = 500   # 200mV, 25mV/fC, 0.5 us
PED_LN_lo[1][1][2] = 500   # 200mV, 25mV/fC, 3.0 us
PED_LN_lo[1][1][3] = 500   # 200mV, 25mV/fC, 2.0 us
PED_LN_lo[1][2][0] = 500   # 200mV, 7.8mV/fC, 1.0 us
PED_LN_lo[1][2][1] = 500   # 200mV, 7.8mV/fC, 0.5 us
PED_LN_lo[1][2][2] = 500   # 200mV, 7.8mV/fC, 3.0 us
PED_LN_lo[1][2][3] = 500   # 200mV, 7.8mV/fC, 2.0 us
PED_LN_lo[1][3][0] = 500   # 200mV, 4.7mV/fC, 1.0 us
PED_LN_lo[1][3][1] = 500   # 200mV, 4.7mV/fC, 0.5 us
PED_LN_lo[1][3][2] = 500   # 200mV, 4.7mV/fC, 3.0 us
PED_LN_lo[1][3][3] = 500   # 200mV, 4.7mV/fC, 2.0 us

# pedestal higher limit
PED_LN_hi = [[[0]*4]*4]*2
PED_LN_hi[1][0][0] = 500   # 200mV, 14mV/fC, 1.0 us
PED_LN_hi[1][0][1] = 500   # 200mV, 14mV/fC, 0.5 us
PED_LN_hi[1][0][2] = 500   # 200mV, 14mV/fC, 3.0 us
PED_LN_hi[1][0][3] = 500   # 200mV, 14mV/fC, 2.0 us
PED_LN_hi[1][1][0] = 500   # 200mV, 25mV/fC, 1.0 us
PED_LN_hi[1][1][1] = 500   # 200mV, 25mV/fC, 0.5 us
PED_LN_hi[1][1][2] = 500   # 200mV, 25mV/fC, 3.0 us
PED_LN_hi[1][1][3] = 500   # 200mV, 25mV/fC, 2.0 us
PED_LN_hi[1][2][0] = 500   # 200mV, 7.8mV/fC, 1.0 us
PED_LN_hi[1][2][1] = 500   # 200mV, 7.8mV/fC, 0.5 us
PED_LN_hi[1][2][2] = 500   # 200mV, 7.8mV/fC, 3.0 us
PED_LN_hi[1][2][3] = 500   # 200mV, 7.8mV/fC, 2.0 us
PED_LN_hi[1][3][0] = 500   # 200mV, 4.7mV/fC, 1.0 us
PED_LN_hi[1][3][1] = 500   # 200mV, 4.7mV/fC, 0.5 us
PED_LN_hi[1][3][2] = 500   # 200mV, 4.7mV/fC, 3.0 us
PED_LN_hi[1][3][3] = 500   # 200mV, 4.7mV/fC, 2.0 us


