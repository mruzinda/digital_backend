#!/bin/env ipython
# script for running FLAG simulator 3 (packetizer simulator)

import corr, struct, time
import numpy as np

#Replace below with your ROACH name
print 'Connecting to ROACH2-R2... '
fpga=corr.katcp_wrapper.FpgaClient('flagr2-7',7147)
time.sleep(0.5)
print 'done. \n'

#Program the ROACH with the simulator firmware
print 'Loading the firmware... '
fpga.progdev('flag_sim3_v2.bof')
time.sleep(5)
print 'done. \n'

fabric_port = 60000    
mac_base    = (2<<32)+(2<<40)

# SOURCE_IP for flagr2-7 gbe0  
print 'Setting source ip addresses... '
source_ip0 = 10*(2**24)+17*(2**16)+0*(2**8)+42
source_ip1 = 10*(2**24)+17*(2**16)+0*(2**8)+43
source_ip2 = 10*(2**24)+17*(2**16)+0*(2**8)+44
source_ip3 = 10*(2**24)+17*(2**16)+0*(2**8)+45
time.sleep(0.5)
print 'done. \n'


#set f_id
print 'Write f engine id... '
fpga.write_int('part2_f_id',0)
time.sleep(0.5)
print 'done. \n'

#set x_id's
print 'Write x engine id... '
fpga.write_int('part2_x_id0',0)
fpga.write_int('part2_x_id1',1)
fpga.write_int('part2_x_id2',2)
fpga.write_int('part2_x_id3',3)
fpga.write_int('part2_x_id4',4)
fpga.write_int('part2_x_id5',5)
fpga.write_int('part2_x_id6',6)
fpga.write_int('part2_x_id7',7)
fpga.write_int('part2_x_id8',8)
fpga.write_int('part2_x_id9',9)
fpga.write_int('part2_x_id10',10)
fpga.write_int('part2_x_id11',11)
fpga.write_int('part2_x_id12',12)
fpga.write_int('part2_x_id13',13)
fpga.write_int('part2_x_id14',14)
fpga.write_int('part2_x_id15',15)
fpga.write_int('part2_x_id16',16)
fpga.write_int('part2_x_id17',17)
fpga.write_int('part2_x_id18',18)
fpga.write_int('part2_x_id19',19)
time.sleep(0.5)
print 'done. \n'


#Write the destination port
print 'Writing destination port...'
fpga.write_int('part2_x_port', 60000)
time.sleep(0.5)
print 'done \n'


#set x_engine ip addresses
print 'Setting x engine ip addresses... '
dest_ip = 10*(2**24)+17*(2**16)+0*(2**8)+33

fpga.write_int('part2_x_ip0',dest_ip)
fpga.write_int('part2_x_ip1',0)
fpga.write_int('part2_x_ip2',0)
fpga.write_int('part2_x_ip3',0)
fpga.write_int('part2_x_ip4',0)
fpga.write_int('part2_x_ip5',0)
fpga.write_int('part2_x_ip6',0)
fpga.write_int('part2_x_ip7',0)
fpga.write_int('part2_x_ip8',0)
fpga.write_int('part2_x_ip9',0)
fpga.write_int('part2_x_ip10',0)
fpga.write_int('part2_x_ip11',0)
fpga.write_int('part2_x_ip12',0)
fpga.write_int('part2_x_ip13',0)
fpga.write_int('part2_x_ip14',0)
fpga.write_int('part2_x_ip15',0)
fpga.write_int('part2_x_ip16',0)
fpga.write_int('part2_x_ip17',0)
fpga.write_int('part2_x_ip18',0)
fpga.write_int('part2_x_ip19',0)
time.sleep(0.5)
print 'done. \n'

print 'Load the GbE cores... '
fpga.tap_start('tap0','part2_gbe0',mac_base,source_ip0,fabric_port)
fpga.tap_start('tap1','part2_gbe1',mac_base,source_ip1,fabric_port)
fpga.tap_start('tap2','part2_gbe2',mac_base,source_ip2,fabric_port)
fpga.tap_start('tap3','part2_gbe3',mac_base,source_ip3,fabric_port)
time.sleep(0.5)
print 'done. \n'

print 'Write data into BRAMs... ' 
data_lsb = np.ones(256)
data_usb = np.ones(256)
for i in np.arange(50):
    if i==0:
       data_lsb[0:5] = 49
       data_usb[0:5] = 50
    else:
       data_lsb[5*i:5*i+5] = 50-(i+1)
       data_usb[5*i:5*i+5] = 50+i

data_lsb[250:256] = -1
data_usb[250:256] = -1


lsb_re_A01 = np.array([data_lsb]*16) 
lsb_im_A01 = np.array([data_lsb]*16)
usb_re_A01 = np.array([data_usb]*16)
usb_im_A01 = np.array([data_usb]*16)

lsb_re_A01_to_pack = np.array(lsb_re_A01.reshape(1,4096)[0,:])
lsb_im_A01_to_pack = np.array(lsb_im_A01.reshape(1,4096)[0,:])
usb_re_A01_to_pack = np.array(usb_re_A01.reshape(1,4096)[0,:])
usb_im_A01_to_pack = np.array(usb_im_A01.reshape(1,4096)[0,:])


lsb_re_A23 = np.array([data_lsb]*16) 
lsb_im_A23 = np.array([data_lsb]*16) 
usb_re_A23 = np.array([data_usb]*16) 
usb_im_A23 = np.array([data_usb]*16) 

lsb_re_A23_to_pack = np.array(lsb_re_A23.reshape(1,4096)[0,:])
lsb_im_A23_to_pack = np.array(lsb_im_A23.reshape(1,4096)[0,:])
usb_re_A23_to_pack = np.array(usb_re_A23.reshape(1,4096)[0,:])
usb_im_A23_to_pack = np.array(usb_im_A23.reshape(1,4096)[0,:])

lsb_re_A45 = np.array([data_lsb]*16) 
lsb_im_A45 = np.array([data_lsb]*16) 
usb_re_A45 = np.array([data_usb]*16) 
usb_im_A45 = np.array([data_usb]*16) 

lsb_re_A45_to_pack = np.array(lsb_re_A45.reshape(1,4096)[0,:])
lsb_im_A45_to_pack = np.array(lsb_im_A45.reshape(1,4096)[0,:])
usb_re_A45_to_pack = np.array(usb_re_A45.reshape(1,4096)[0,:])
usb_im_A45_to_pack = np.array(usb_im_A45.reshape(1,4096)[0,:])
                    
lsb_re_A67 = np.array([data_lsb]*16) 
lsb_im_A67 = np.array([data_lsb]*16) 
usb_re_A67 = np.array([data_usb]*16) 
usb_im_A67 = np.array([data_usb]*16) 

lsb_re_A67_to_pack = np.array(lsb_re_A45.reshape(1,4096)[0,:])
lsb_im_A67_to_pack = np.array(lsb_im_A45.reshape(1,4096)[0,:])
usb_re_A67_to_pack = np.array(usb_re_A45.reshape(1,4096)[0,:])
usb_im_A67_to_pack = np.array(usb_im_A45.reshape(1,4096)[0,:])



lsb_re_A01_packed = struct.pack('>4096b', *lsb_re_A01_to_pack)   #the star is there so that it actually reads lsb_re_A01_to_pack[0] lsb_re_A01_to_pack[1] lsb_re_A01_to_pack[2] .... lsb_re_A01_to_pack[4095]
lsb_im_A01_packed = struct.pack('>4096b', *lsb_im_A01_to_pack)
usb_re_A01_packed = struct.pack('>4096b', *usb_re_A01_to_pack)
usb_im_A01_packed = struct.pack('>4096b', *usb_im_A01_to_pack)

lsb_re_A23_packed = struct.pack('>4096b', *lsb_re_A23_to_pack)
lsb_im_A23_packed = struct.pack('>4096b', *lsb_im_A23_to_pack)
usb_re_A23_packed = struct.pack('>4096b', *usb_re_A23_to_pack)
usb_im_A23_packed = struct.pack('>4096b', *usb_im_A23_to_pack)

lsb_re_A45_packed = struct.pack('>4096b', *lsb_re_A45_to_pack)
lsb_im_A45_packed = struct.pack('>4096b', *lsb_im_A45_to_pack)
usb_re_A45_packed = struct.pack('>4096b', *usb_re_A45_to_pack)
usb_im_A45_packed = struct.pack('>4096b', *usb_im_A45_to_pack)

lsb_re_A67_packed = struct.pack('>4096b', *lsb_re_A67_to_pack)
lsb_im_A67_packed = struct.pack('>4096b', *lsb_im_A67_to_pack)
usb_re_A67_packed = struct.pack('>4096b', *usb_re_A67_to_pack)
usb_im_A67_packed = struct.pack('>4096b', *usb_im_A67_to_pack)

fpga.write('LSB_re_A01', lsb_re_A01_packed, 0)          
fpga.write('LSB_im_A01', lsb_im_A01_packed, 0)          
fpga.write('USB_re_A01', usb_re_A01_packed, 0)          
fpga.write('USB_im_A01', usb_im_A01_packed, 0)          

time.sleep(0.5)

fpga.write('LSB_re_A23', lsb_re_A23_packed, 0)          
fpga.write('LSB_im_A23', lsb_im_A23_packed, 0)          
fpga.write('USB_re_A23', usb_re_A23_packed, 0)          
fpga.write('USB_im_A23', usb_im_A23_packed, 0)          

time.sleep(0.5)

fpga.write('LSB_re_A45', lsb_re_A45_packed, 0)          
fpga.write('LSB_im_A45', lsb_im_A45_packed, 0)          
fpga.write('USB_re_A45', usb_re_A45_packed, 0)          
fpga.write('USB_im_A45', usb_im_A45_packed, 0)          

time.sleep(0.5)

fpga.write('LSB_re_A67', lsb_re_A67_packed, 0)          
fpga.write('LSB_im_A67', lsb_im_A67_packed, 0)          
fpga.write('USB_re_A67', usb_re_A67_packed, 0)          
fpga.write('USB_im_A67', usb_im_A67_packed, 0)          

time.sleep(0.5)

print 'done. \n'

print 'Send msync pulse to start process... '
fpga.write_int('ARM', 0)
time.sleep(0.1)
fpga.write_int('ARM', 1)
time.sleep(2)
fpga.write_int('ARM', 0)
print 'done. \n'

