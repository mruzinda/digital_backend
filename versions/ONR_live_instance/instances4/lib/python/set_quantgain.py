import corr
import time

quant_gain = 10

roachNames = ["flagr2-1", "flagr2-2", "flagr2-3", "flagr2-4", "flagr2-5"]

for name in roachNames:
    print "Setting quant_gain for: %s" % name

    fpga = corr.katcp_wrapper.FpgaClient(name)
    time.sleep(.1)

    fpga.write_int('quant_gain', quant_gain)
    print
