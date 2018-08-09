import corr
from time import sleep

delays = [2,0,0,0,0,0,0,0,
          0,0,0,0,0,0,0,0,
          0,0,0,0,0,0,0,0,
          0,0,0,0,0,0,0,0,
          0,0,0,0,0,0,0,0]

fpga1 = corr.katcp_wrapper.FpgaClient('flagr2-1')
fpga2 = corr.katcp_wrapper.FpgaClient('flagr2-2')
fpga3 = corr.katcp_wrapper.FpgaClient('flagr2-3')
fpga4 = corr.katcp_wrapper.FpgaClient('flagr2-4')
fpga5 = corr.katcp_wrapper.FpgaClient('flagr2-5')

sleep(0.1)

fpga1.write_int('0iq_dly_reg', delays[0])
fpga1.write_int('1iq_dly_reg', delays[1])
fpga1.write_int('2iq_dly_reg', delays[2])
fpga1.write_int('3iq_dly_reg', delays[3])
fpga1.write_int('4iq_dly_reg', delays[4])
fpga1.write_int('5iq_dly_reg', delays[5])
fpga1.write_int('6iq_dly_reg', delays[6])
fpga1.write_int('7iq_dly_reg', delays[7])

fpga2.write_int('0iq_dly_reg', delays[8])
fpga2.write_int('1iq_dly_reg', delays[9])
fpga2.write_int('2iq_dly_reg', delays[10])
fpga2.write_int('3iq_dly_reg', delays[11])
fpga2.write_int('4iq_dly_reg', delays[12])
fpga2.write_int('5iq_dly_reg', delays[13])
fpga2.write_int('6iq_dly_reg', delays[14])
fpga2.write_int('7iq_dly_reg', delays[15])

fpga3.write_int('0iq_dly_reg', delays[16])
fpga3.write_int('1iq_dly_reg', delays[17])
fpga3.write_int('2iq_dly_reg', delays[18])
fpga3.write_int('3iq_dly_reg', delays[19])
fpga3.write_int('4iq_dly_reg', delays[20])
fpga3.write_int('5iq_dly_reg', delays[21])
fpga3.write_int('6iq_dly_reg', delays[22])
fpga3.write_int('7iq_dly_reg', delays[23])

fpga4.write_int('0iq_dly_reg', delays[24])
fpga4.write_int('1iq_dly_reg', delays[25])
fpga4.write_int('2iq_dly_reg', delays[26])
fpga4.write_int('3iq_dly_reg', delays[27])
fpga4.write_int('4iq_dly_reg', delays[28])
fpga4.write_int('5iq_dly_reg', delays[29])
fpga4.write_int('6iq_dly_reg', delays[30])
fpga4.write_int('7iq_dly_reg', delays[31])

fpga5.write_int('0iq_dly_reg', delays[32])
fpga5.write_int('1iq_dly_reg', delays[33])
fpga5.write_int('2iq_dly_reg', delays[34])
fpga5.write_int('3iq_dly_reg', delays[35])
fpga5.write_int('4iq_dly_reg', delays[36])
fpga5.write_int('5iq_dly_reg', delays[37])
fpga5.write_int('6iq_dly_reg', delays[38])
fpga5.write_int('7iq_dly_reg', delays[39])
