import socket
import struct

import numpy as np

def _ip_string_to_int(ip):
    """_ip_string_to_int(ip)

    Takes an IP address in string representation and returns an integer
    representation::

      iip = _ip_string_to_int('10.17.0.51')
      print(hex(iip))
      0x0A110040

    """
    try:
        rval = sum(map(lambda x, y: x << y,
                       [int(p) for p in ip.split('.')], [24, 16, 8, 0]))
    except (TypeError, AttributeError):
        rval = None

    return rval

def _hostname_to_ip(hostname):
    """_hostname_to_ip(hostname)

    Takes a hostname string and returns an IP address string::

      ip = _hostname_to_ip('vegasr2-1')
      print(ip)
      10.17.0.64

    """
    try:
        rval = socket.gethostbyaddr(hostname)[2][0]
    except (TypeError, socket.gaierror, socket.herror):
        rval = None

    return rval

# Magic byte lock helper functions...
def treat_data_sbs(bb_lock_data_dir, j,k):
    if(j==0):
            fur67 = open(bb_lock_data_dir +"usb_data_re01.txt","r")
            fui67 = open(bb_lock_data_dir +"usb_data_im01.txt","r")
            flr67 = open(bb_lock_data_dir +"lsb_data_re01.txt","r")
            fli67 = open(bb_lock_data_dir +"lsb_data_im01.txt","r")
    elif j==2:
            fur67 = open(bb_lock_data_dir +"usb_data_re23.txt","r")
            fui67 = open(bb_lock_data_dir +"usb_data_im23.txt","r")
            flr67 = open(bb_lock_data_dir +"lsb_data_re23.txt","r")
            fli67 = open(bb_lock_data_dir +"lsb_data_im23.txt","r")
    elif j==4:
            fur67 = open(bb_lock_data_dir +"usb_data_re45.txt","r")
            fui67 = open(bb_lock_data_dir +"usb_data_im45.txt","r")
            flr67 = open(bb_lock_data_dir +"lsb_data_re45.txt","r")
            fli67 = open(bb_lock_data_dir +"lsb_data_im45.txt","r")
    elif j==6:
            fur67 = open(bb_lock_data_dir +"usb_data_re67.txt","r")
            fui67 = open(bb_lock_data_dir +"usb_data_im67.txt","r")
            flr67 = open(bb_lock_data_dir +"lsb_data_re67.txt","r")
            fli67 = open(bb_lock_data_dir +"lsb_data_im67.txt","r")
    else:
        print 'wrong j value in treat_data_sbs \n'

    usb_r67 = np.array(fur67.read().split('\n'))
    #if(j==0):
    #    if(k==0):
            #print ('contents of usb_data_re01.txt\n')
            #print (usb_r67[0:255])
            #print ('check it \n')
    usb_i67 = np.array(fui67.read().split('\n'))
    lsb_r67 = np.array(flr67.read().split('\n'))
    lsb_i67 = np.array(fli67.read().split('\n'))

    i=0
    usb67_mag = usb_r67
    lsb67_mag = lsb_r67
    while i<513:
        usb_r67[i] = float(usb_r67[i])
        usb_i67[i] = float(usb_i67[i])
        usb67_mag[i]=float((float(usb_r67[i])*float(usb_r67[i])+float(usb_i67[i])*float(usb_i67[i])))
        lsb67_mag[i]=float((float(lsb_r67[i])*float(lsb_r67[i])+float(lsb_i67[i])*float(lsb_i67[i])))
        #usb67_mag[i]=float(np.sqrt(float(usb_r67[i])*float(usb_r67[i])+float(usb_i67[i])*float(usb_i67[i])))
        #lsb67_mag[i]=float(np.sqrt(float(lsb_r67[i])*float(lsb_r67[i])+float(lsb_i67[i])*float(lsb_i67[i])))
        i=i+1

    #usb6_mag=map(float,(usb67_mag[0:256]))
    #usb7_mag=map(float,(usb67_mag[256:512]))
    #lsb6_mag=map(float,(lsb67_mag[0:256]))
    #lsb7_mag=map(float,(lsb67_mag[256:512]))


    ############luke
    usb6_mag1=map(float,(usb67_mag[0:256]))
    usb7_mag1=map(float,(usb67_mag[256:512]))
    lsb6_mag1=map(float,(lsb67_mag[0:256]))
    lsb7_mag1=map(float,(lsb67_mag[256:512]))

    return usb6_mag1, lsb6_mag1, usb7_mag1, lsb7_mag1

def get_data_sbs(fpga, bb_lock_data_dir, k, j):
    # for k in range(4):
    # lsb_raw_re = fpga.read('lsb_re_'+str(k)+str(k+1)+'_bram',2**12,0)
    # lsb_raw_re = fpga.read('lsb_re_01_1',2**12,0)
    if (k == 6):
        lsb_raw_re = lsb_raw_re = fpga.read('lsb_re_' + str(k) + str(k + 1) + '_2', 2 ** 12, 0)
    else:
        lsb_raw_re = fpga.read('lsb_re_' + str(k) + str(k + 1) + '_1', 2 ** 12, 0)
    lsb_re = struct.unpack('>4096b', lsb_raw_re)
    # print(lsb_re)

    # lsb_raw_im = fpga.read('lsb_im_'+str(k)+str(k+1)+'_bram',2**12,0)
    # lsb_raw_im = fpga.read('lsb_im_01_1',2**12,0)
    if (k == 6):
        lsb_raw_im = fpga.read('lsb_im_' + str(k) + str(k + 1) + '_2', 2 ** 12, 0)
    else:
        lsb_raw_im = fpga.read('lsb_im_' + str(k) + str(k + 1) + '_1', 2 ** 12, 0)
    lsb_im = struct.unpack('>4096b', lsb_raw_im)

    # usb_raw_re = fpga.read('usb_re_'+str(k)+str(k+1)+'_bram',2**12,0)
    # usb_raw_re = fpga.read('usb_re_01_1',2**12,0)
    if (k == 6):
        usb_raw_re = fpga.read('usb_re_' + str(k) + str(k + 1) + '_2', 2 ** 12, 0)
    else:
        usb_raw_re = fpga.read('usb_re_' + str(k) + str(k + 1) + '_1', 2 ** 12, 0)
    usb_re = struct.unpack('>4096b', usb_raw_re)

    # usb_raw_im = fpga.read('usb_im_'+str(k)+str(k+1)+'_bram',2**12,0)
    # usb_raw_im = fpga.read('usb_im_01_1',2**12,0)
    if (k == 6):
        usb_raw_im = fpga.read('usb_im_' + str(k) + str(k + 1) + '_2', 2 ** 12, 0)
    else:
        usb_raw_im = fpga.read('usb_im_' + str(k) + str(k + 1) + '_1', 2 ** 12, 0)
    usb_im = struct.unpack('>4096b', usb_raw_im)

    usb_r = np.array(usb_re)  # /128.0
    # if (j==0):
    # print usb_re
    # print (len(usb_r))
    # print ('first contents of usb_data_re01.txt\n')
    # print(j)
    # print (usb_re[0:255])
    # print ('check it \n')
    usb_i = np.array(usb_im)  # /128.0
    lsb_r = np.array(lsb_re)  # /128.0
    lsb_i = np.array(lsb_im)  # /128.0

    m = 0
    with open(bb_lock_data_dir +bb_lock_data_dir +'lsb_data_re' + str(k) + str(k + 1) + '.txt', 'w') as f:
        for m in range(len(lsb_r)):
            the_str = ""
            the_str += str(lsb_r[m]) + "\n"
            f.write(the_str)
    m = 0
    with open(bb_lock_data_dir +bb_lock_data_dir +'lsb_data_im' + str(k) + str(k + 1) + '.txt', 'w') as f:
        for m in range(len(lsb_i)):
            the_str = ""
            the_str += str(lsb_i[m]) + "\n"
            f.write(the_str)

    m = 0
    with open(bb_lock_data_dir +bb_lock_data_dir +'usb_data_re' + str(k) + str(k + 1) + '.txt', 'w') as f:
        for m in range(len(usb_r)):
            the_str = ""
            the_str += str(usb_r[m]) + "\n"
            f.write(the_str)
    m = 0
    with open(bb_lock_data_dir +bb_lock_data_dir +'usb_data_im' + str(k) + str(k + 1) + '.txt', 'w') as f:
        for m in range(len(usb_i)):
            the_str = ""
            the_str += str(usb_i[m]) + "\n"
            f.write(the_str)

    return usb_r, usb_i, lsb_r, lsb_i