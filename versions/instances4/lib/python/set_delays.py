import corr
import numpy as np
import time

delay_dir = "/home/groups/flag/scripts/matFlag/word_lock/output/"
delay_src = "offset_2018_02_07_13:01:36.dat"
fname = delay_dir + delay_src
print "sourced data: %s" % fname
delays = np.fromfile(fname, dtype=np.int8)

roachNames = ["flagr2-1", "flagr2-2", "flagr2-3", "flagr2-4", "flagr2-5"]

rid = 0
for name in roachNames:
    print "Setting delays for: %s" % name

    fpga = corr.katcp_wrapper.FpgaClient(name)
    time.sleep(.1)

    for i in range(0,8):
        register = str(i) + 'iq_dly_reg'
        print "writing to %s: %d" % (register, delays[rid*8+i])
        fpga.write_int(register, delays[rid*8+i])

    rid = rid + 1
    print
