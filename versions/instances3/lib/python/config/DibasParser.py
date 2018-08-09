import os
import ConfigParser
from f_engine_config import RoachDoctor
dibas_conf_file = '/users/mburnett/Github/flag_gpu/scripts/player/dibas.conf'

class DibasParser():
    def __init__(self, dibas_conf_file):

        config = ConfigParser.ConfigParser()
        config.readfp(open(dibas_conf_file))

        self.dibas_info = {}

        backend = config.get('DEFAULTS', 'backend')
        self.dibas_info['backend'] = backend

        hpcs = config.get('HOSTS', 'hpc')
        hpcs = hpcs.split(' ')

        for hpc in hpcs:
            interface = config.get('10GBEINTERFACES', hpc)
            interface = interface.split(' ')

            interface_list = {}
            for ip in interface:
                mac = int(config.get('HPCMACS', ip),16)

                interface_list[ip] = mac
                #interface_list.append({ip:mac})

            self.dibas_info[hpc] = {'10GbE_interfaces' : interface_list}

        self.dibas_info['num_hpcs'] = len(hpcs)

        #roach_config = {}

        doctor = config.get('DEFAULTS', 'isDoctor')
        self.dibas_info['isDoctor'] = doctor

        bof = config.get('ROACHCONFIG', 'bof_file')
        self.dibas_info['bof_file'] = bof

        source_port = config.getint('ROACHCONFIG', 'source_port')
        self.dibas_info['source_port'] = source_port

        dest_port = config.getint('ROACHCONFIG', 'dest_port')
        self.dibas_info['dest_port'] = dest_port

        roaches = config.get('ROACHES', 'roachList')
        roaches = roaches.split(' ')
        self.dibas_info['roaches'] = roaches

        dest_comp = {}
        #for roach in roaches:
        #dest = config.get('ROACHDEST', roach)
        dest = config.get('ROACHDEST', 'destinations')
        dest = dest.split(' ')
        #dest_comp[roach] = dest
        dest_comp = dest
        self.dibas_info['dest_comp'] = dest_comp

    def get_dibas_info(self):
        return self.dibas_info

