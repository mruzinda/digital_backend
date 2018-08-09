#!/opt/local/bin/python2.7

import corr, time, struct, sys, logging, socket, os
from numpy import genfromtxt
import numpy as np

import nb_util as nb
nb.connect()

os.system("flag_turnon.py")
os.system("arm.py")

nb.set_rf_switch('NS')
time.sleep(15)
os.system("f_engine_config_lo_luke8a.py flagr2-1  -n -f 0  -b 1 -i 0xffffffff")
os.system("f_engine_config_lo_luke8a.py flagr2-2  -n -f 1  -b 1 -i 0xffffffff")
os.system("f_engine_config_lo_luke8a.py flagr2-3  -n -f 2  -b 1 -i 0xffffffff")
os.system("f_engine_config_lo_luke8a.py flagr2-4  -n -f 3  -b 1 -i 0xffffffff")
os.system("f_engine_config_lo_luke8a.py flagr2-5  -n -f 4  -b 1 -i 0xffffffff")


nb.set_rf_switch('TT')
time.sleep(15)

###Step Three
print 'Starting flagr2-1 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-1 -n -f 0 -B 1 -i 0xffffffff")
print 'finished flagr2-1 \n'

print 'starting flagr2-2 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-2 -n -f 1 -B 1 -i 0xffffffff")
print 'finished flagr2-2 \n'

print 'starting flagr2-3 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-3 -n -f 2 -B 1 -i 0xffffffff")
print 'finished flagr2-3 \n'

print 'starting flagr2-4 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-4 -n -f 3 -B 1 -i 0xffffffff")
print 'finished flagr2-4 \n'

print 'starting flagr2-5 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-5 -n -f 4 -B 1 -i 0xffffffff")
print 'finished flagr2-5 \n'


###Step Four
print 'Starting flagr2-1 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-1 -n -f 0 -B 2 -i 0xffffffff")
print 'finished flagr2-1 \n'

print 'starting flagr2-2 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-2 -n -f 1 -B 2 -i 0xffffffff")
print 'finished flagr2-2 \n'

print 'starting flagr2-3 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-3 -n -f 2 -B 2 -i 0xffffffff")
print 'finished flagr2-3 \n'

print 'starting flagr2-4 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-4 -n -f 3 -B 2 -i 0xffffffff")
print 'finished flagr2-4 \n'

print 'starting flagr2-5 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-5 -n -f 4 -B 2 -i 0xffffffff")
print 'finished flagr2-5 \n'



###Step Four
print 'Starting flagr2-1 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-1 -n -f 0 -B 2 -i 0xffffffff")
print 'finished flagr2-1 \n'

print 'starting flagr2-2 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-2 -n -f 1 -B 2 -i 0xffffffff")
print 'finished flagr2-2 \n'

print 'starting flagr2-3 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-3 -n -f 2 -B 2 -i 0xffffffff")
print 'finished flagr2-3 \n'

print 'starting flagr2-4 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-4 -n -f 3 -B 2 -i 0xffffffff")
print 'finished flagr2-4 \n'

print 'starting flagr2-5 \n'
os.system(" f_engine_config_lo_luke8a.py flagr2-5 -n -f 4 -B 2 -i 0xffffffff")
print 'finished flagr2-5 \n'

#nb.set_rf_switch('OFF')
nb.NB.close()



