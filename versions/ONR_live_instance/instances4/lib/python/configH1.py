import os
from f_engine_config.RoachDoctor import RoachDoctor

from config.DibasParser import DibasParser


config_file = os.getenv("DIBAS_DIR") + '/etc/config/dibas.conf'
dibas_parser = DibasParser(dibas_conf_file=config_file)
dibas_info = dibas_parser.get_dibas_info()

roach_names = dibas_info['roaches']

RD = RoachDoctor(roach_host_list=roach_names, dibas_info=dibas_info)
roaches = RD.get_roaches()

#num = [0, 2, 4, 6, 8, 10, 12, 14]
num = [0, 2, 4, 6, 8, 10]
for roach in roaches:
    i = 7
    #i=5
    for xid in num:
		#print "idx=%d, xid=%d" % (xid, i)
		roach.write_int('part2_x_id' + str(xid), i)
		i = i+1
