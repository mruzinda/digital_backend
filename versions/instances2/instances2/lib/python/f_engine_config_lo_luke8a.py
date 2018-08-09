#!/opt/local/bin/python2.7

import corr, time, struct, sys, logging, socket, math, operator
from numpy import genfromtxt
import numpy as np

boffile     = 'flag39_3_2017_Apr_03_1445.bof'#Luke replace boffile name
paf0        = 10*(2**24)+17*(2**16)+16*(2**8)+39
flag3_0     = 10*(2**24)+17*(2**16)+16*(2**8)+208
flag3_1     = 10*(2**24)+17*(2**16)+16*(2**8)+209
flag3_2     = 10*(2**24)+17*(2**16)+16*(2**8)+210
flag3_3     = 10*(2**24)+17*(2**16)+16*(2**8)+211
#west        = 10*(2**24)+17*(2**16)+0*(2**8)+35 # west ip address , need to direct the unwanted packets somewhere   
#tofu        = 10*(2**24)+17*(2**16)+0*(2**8)+36 # ip address of tofu for the correct mac address
#south       = 10*(2**24)+17*(2**16)+0*(2**8)+33 
blackhole   = 10*(2**24)+17*(2**16)+16*(2**8)+200

source_port = 60000                             #the physical port on the roach board side  which it will be sending from
                    #luke why 60,000???

#From Ray's Dealer Player code
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

macs = {
    '10.17.16.39' : 0x000F5308458C, # paf0
    '10.17.16.208': 0x7CFE90B92DF0, # flag3_0 
    '10.17.16.209': 0x7CFE90B92BD0, # flag3_1 
    '10.17.16.210': 0x7CFE90B92BD1, # flag3_2
    '10.17.16.211': 0x7CFE90B92DF1, # flag3_3
#    '10.17.0.35': 0x000F530C668C, # west
#    '10.17.0.33': 0x0002C952FDCB, # south
#    '10.17.0.36': 0x000F530CFDB8, # tofu
    '10.17.16.200': 0x0202b1ac401e, # blackhole mac address and fake ip; Note the switch is configured to drop packets sent to this mac
}

hpc_macs = {}
hpc_macs_list = [0xffffffffffff] * 256

for hostname, mac in macs.iteritems():
    key = _ip_string_to_int(_hostname_to_ip(hostname)) & 0xFF
    hpc_macs[key] = mac
    hpc_macs_list[key] = mac


def treat_data_sbs(j,k):
    if(j==0):
            fur67 = open("usb_data_re01.txt","r")
            fui67 = open("usb_data_im01.txt","r")
            flr67 = open("lsb_data_re01.txt","r")
            fli67 = open("lsb_data_im01.txt","r")
    elif j==2:
            fur67 = open("usb_data_re23.txt","r")
            fui67 = open("usb_data_im23.txt","r")
            flr67 = open("lsb_data_re23.txt","r")
            fli67 = open("lsb_data_im23.txt","r")
    elif j==4:
            fur67 = open("usb_data_re45.txt","r")
            fui67 = open("usb_data_im45.txt","r")
            flr67 = open("lsb_data_re45.txt","r")
            fli67 = open("lsb_data_im45.txt","r")
    elif j==6:
            fur67 = open("usb_data_re67.txt","r")
            fui67 = open("usb_data_im67.txt","r")
            flr67 = open("lsb_data_re67.txt","r")
            fli67 = open("lsb_data_im67.txt","r")
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

def get_data_sbs(k,j):



    #for k in range(4):
        #lsb_raw_re = fpga.read('lsb_re_'+str(k)+str(k+1)+'_bram',2**12,0)
        #lsb_raw_re = fpga.read('lsb_re_01_1',2**12,0)
        if(k==6):
            lsb_raw_re = lsb_raw_re = fpga.read('lsb_re_'+str(k)+str(k+1)+'_2',2**12,0)
        else:
            lsb_raw_re = fpga.read('lsb_re_'+str(k)+str(k+1)+'_1',2**12,0)
        lsb_re = struct.unpack('>4096b',lsb_raw_re)
        #print(lsb_re)
        
        #lsb_raw_im = fpga.read('lsb_im_'+str(k)+str(k+1)+'_bram',2**12,0)
        #lsb_raw_im = fpga.read('lsb_im_01_1',2**12,0)
        if(k==6):
            lsb_raw_im = fpga.read('lsb_im_'+str(k)+str(k+1)+'_2',2**12,0)
        else:
            lsb_raw_im = fpga.read('lsb_im_'+str(k)+str(k+1)+'_1',2**12,0)
        lsb_im = struct.unpack('>4096b',lsb_raw_im)
        
        #usb_raw_re = fpga.read('usb_re_'+str(k)+str(k+1)+'_bram',2**12,0) 
        #usb_raw_re = fpga.read('usb_re_01_1',2**12,0)
        if(k==6):
            usb_raw_re = fpga.read('usb_re_'+str(k)+str(k+1)+'_2',2**12,0)
        else:
            usb_raw_re = fpga.read('usb_re_'+str(k)+str(k+1)+'_1',2**12,0)
        usb_re = struct.unpack('>4096b',usb_raw_re)
        
        #usb_raw_im = fpga.read('usb_im_'+str(k)+str(k+1)+'_bram',2**12,0)
        #usb_raw_im = fpga.read('usb_im_01_1',2**12,0)
        if(k==6):
            usb_raw_im = fpga.read('usb_im_'+str(k)+str(k+1)+'_2',2**12,0)
        else:
            usb_raw_im = fpga.read('usb_im_'+str(k)+str(k+1)+'_1',2**12,0)
        usb_im = struct.unpack('>4096b',usb_raw_im)
       
        usb_r = np.array(usb_re)#/128.0
        #if (j==0):
            #print usb_re
            #print (len(usb_r))
            #print ('first contents of usb_data_re01.txt\n')
            #print(j)
            #print (usb_re[0:255])
            #print ('check it \n')
        usb_i = np.array(usb_im)#/128.0
        lsb_r = np.array(lsb_re)#/128.0
        lsb_i = np.array(lsb_im)#/128.0
        
        m=0
        with open('lsb_data_re'+str(k)+str(k+1)+'.txt','w') as f:
           for m in range(len(lsb_r)):
               the_str = ""
               the_str += str(lsb_r[m]) + "\n"
               f.write(the_str)
        m=0
        with open('lsb_data_im'+str(k)+str(k+1)+'.txt','w') as f:
           for m in range(len(lsb_i)):
               the_str = ""
               the_str += str(lsb_i[m]) + "\n"
               f.write(the_str)

        m=0
        with open('usb_data_re'+str(k)+str(k+1)+'.txt','w') as f:
           for m in range(len(usb_r)):
               the_str = ""
               the_str += str(usb_r[m]) + "\n"
               f.write(the_str)
        m=0
        with open('usb_data_im'+str(k)+str(k+1)+'.txt','w') as f:
           for m in range(len(usb_i)):
               the_str = ""
               the_str += str(usb_i[m]) + "\n"
               f.write(the_str)
        
        return usb_r, usb_i, lsb_r, lsb_i

def get_data_iq(rcv_nr):
    data = fpga.read('final_data_'+str(rcv_nr),2**16*2,0)         #read data from specific receiver number
    d_0=struct.unpack('>65536H',data) #< for little endian B for (8 bits) now made H for 16 bits
    d_0i = []
    d_0q = []
    for n in range(65536):
        d_0i.append(d_0[n]>>8)   #get the top 8 bits of final_data_rcv_nr 
        d_0q.append(d_0[n]&0xff) #get the bottom 8 bits of final_data_rcv_nr

    m=0
    with open('data_' +str(rcv_nr) +'i.txt','w') as f:
       for m in range(len(d_0i)):
           the_str = ""
           the_str += str(d_0i[m]) + "\n"
           f.write(the_str)
    m=0
    with open('data_' +str(rcv_nr) +'q.txt','w') as f1:
       for m in range(len(d_0q)):
           the_str = ""
           the_str += str(d_0q[m]) + "\n"
           f1.write(the_str)

#this function should do a byte swap on the channel specified. 
#As a first implementation ch should be represented in hex
def swap_byte(fpga,ch):
    fpga.write_int('rxslide',ch)   
    fpga.write_int('rxslide',0x00)

    #fpga.write_int('rxslide',ch)   
    #time.sleep(0.5)
    #if (hex(fpga.read_int('msb2_loc')) == 0x80):
    #       fpga.write_int('rxslide',0x00)          
    #       return;
    #time.sleep(1)
    #fpga.write_int('rxslide',0x00)
    #time.sleep(1)
    #while(hex(fpga.read_int('msb2_loc')) != 0x80):
    #    fpga.write_int('rxslide',ch) 
    #    time.sleep(0.5)
    #    if (hex(fpga.read_int('msb2_loc')) == 0x80):
    #       fpga.write_int('rxslide',0x00)          
    #       break;
    #    time.sleep(1)
    #    fpga.write_int('rxslide',0x00)
    #    time.sleep(1)    

def exit_fail():
    print 'FAILURE DETECTED. Log entries:\n',lh.printMessages()
    try:
        fpga.stop()
    except: pass
    raise
    exit()



def exit_clean():
    try:
        for f in fpgas: f.stop()
    except: pass
    exit()


if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser()
    p.set_usage('f_engine_config_lo.py <ROACH_HOSTNAME_or_IP> [options]')
    p.set_description(__doc__)
    p.add_option('-n'  , '--noprogram'         , dest='noprogram'       , action='store_true'                      , help='Don\'t reprogram the roach.')  
    p.add_option('-c'  , '--set_coefficients'  , dest='set_coef'        , type = 'int'       , default=0           , help='Set the sideband separating coefficients.')  
    p.add_option('-l'  , '--lo'                , dest='lo'              , type = 'str'       , default='1450'      , help='Set the LO for sbs coefficients, default is 1450 MHz')  
    p.add_option('-r'  , '--reset_transceivers', dest='reset_trans'     , type = 'int'       , default=0           , help='Reset data input transceivers.')  
    p.add_option('-i'  , '--fft_shift'         , dest='fft_shift'       , type = 'long'      , default=0xaaaaaaaa  , help='Set the fft_shift register, default is 0xaaaaaaaa')  
    p.add_option('-b'  , '--bit_lock'          , dest='auto_align_bits' , type = 'int'       , default=0           , help='Automatically bit align the system')  
    p.add_option('-B'  , '--byte_lock'         , dest='auto_align_bytes', type = 'int'       , default=0           , help='1=calc and align bytes, 2=check byte alignment')
    p.add_option('-e'  , '--byte_swap'         , dest='swap_bytes_ch'   , type = 'long'      , default=-1          , help='Swap bytes of specified channel')
    p.add_option('-a'  , '--set_arm'           , dest='arm'             , type = 'int'       , default=0           , help='ARM the subsystem')  
    p.add_option('-t'  , '--get_time_data'     , dest='time_data'       , type = 'int'       , default=0           , help='Get time domain i and q data')  
    p.add_option('-s'  , '--get_sbs_data'      , dest='sbs_data'        , type = 'int'       , default=0           , help='Get sideband separated frequency data')  
    p.add_option('-d'  , '--boffile'           , dest='bof'             , type = 'str'       , default=boffile     , help='Specify the bof file to load')  
    p.add_option('-p'  , '--packetizer'        , dest='pack'            , type = 'int'       , default=0           , help='Reset GbE cores, start GbE cores, Set f_id & x_id registers on firmware. Set destination port')  
    p.add_option('-x'  , '--xid'               , dest='xid'             , type = 'int'       , default=-1          , help='The x id number for the sideband to grab')  
    p.add_option('-f'  , '--fid'               , dest='fid'             , type = 'int'       , default=-1          , help='The f id number for the roach.')  
    p.add_option('-o'  , '--dport'             , dest='dport'           , type = 'int'       , default=-1          , help='The destination port number')  
    p.add_option('-C'  , '--dcomp'             , dest='dcomp'           , type = 'str'       , default='blackhole' , help='The destination computer (paf0, tofu)')  
    #Luke added
    #p.add_option('-q   , '--IQ_stage'          , dest='iq_stage'        , type = 'int'       , default =0          , help='select stage: 1=initial/USB, 2=check/LSB')
    
    opts, args = p.parse_args(sys.argv[1:])

    if args==[]:
       print 'Please specify a ROACH board. \nExiting.'
       exit()
    else:
       roach = args[0]

    if opts.bof != '':
       boffile = opts.bof

    if (opts.fid == -1):
       print 'Specify ROACH f_id.'
       exit()

    blade_roach = ['A', 'B', 'C', 'D', 'E']
    fid_prefix  = blade_roach[opts.fid]

    lsbre01 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbre01_'+opts.lo+'.csv', delimiter = '/n')
    lsbre23 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbre23_'+opts.lo+'.csv', delimiter = '/n')
    lsbre45 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbre45_'+opts.lo+'.csv', delimiter = '/n')
    lsbre67 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbre67_'+opts.lo+'.csv', delimiter = '/n')
                                                  
    lsbim01 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbim01_'+opts.lo+'.csv', delimiter = '/n')
    lsbim23 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbim23_'+opts.lo+'.csv', delimiter = '/n')
    lsbim45 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbim45_'+opts.lo+'.csv', delimiter = '/n')
    lsbim67 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbim67_'+opts.lo+'.csv', delimiter = '/n')
                                                  
    usbre01 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbre01_'+opts.lo+'.csv', delimiter = '/n')
    usbre23 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbre23_'+opts.lo+'.csv', delimiter = '/n')
    usbre45 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbre45_'+opts.lo+'.csv', delimiter = '/n')
    usbre67 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbre67_'+opts.lo+'.csv', delimiter = '/n')
                                                  
    usbim01 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbim01_'+opts.lo+'.csv', delimiter = '/n')
    usbim23 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbim23_'+opts.lo+'.csv', delimiter = '/n')
    usbim45 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbim45_'+opts.lo+'.csv', delimiter = '/n')
    usbim67 = genfromtxt('./coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbim67_'+opts.lo+'.csv', delimiter = '/n')

    mac_base0   = (2<<40) + (2<<32) + (10<<24) + (17<<16) + (16<<8) + (4*opts.fid+230)               #give each physical port a unique id 
    mac_base1   = (2<<40) + (2<<32) + (10<<24) + (17<<16) + (16<<8) + (4*opts.fid+231) 
    mac_base2   = (2<<40) + (2<<32) + (10<<24) + (17<<16) + (16<<8) + (4*opts.fid+232) 
    mac_base3   = (2<<40) + (2<<32) + (10<<24) + (17<<16) + (16<<8) + (4*opts.fid+233) 
    
    source_ip0 = 10*(2**24)+17*(2**16)+16*(2**8)+230+(4*opts.fid) 
    source_ip1 = 10*(2**24)+17*(2**16)+16*(2**8)+231+(4*opts.fid) 
    source_ip2 = 10*(2**24)+17*(2**16)+16*(2**8)+232+(4*opts.fid) 
    source_ip3 = 10*(2**24)+17*(2**16)+16*(2**8)+233+(4*opts.fid) 

try:
    lh = corr.log_handlers.DebugLogHandler()
    logger = logging.getLogger(roach)
    logger.addHandler(lh)
    logger.setLevel(10)

    print('Connecting to server %s... '%(roach)),
    fpga = corr.katcp_wrapper.FpgaClient(roach, logger=logger)
    time.sleep(1)

    if fpga.is_connected():
       print 'ok\n'
    else:
       print 'ERROR connecting to server %s.\n'%(roach)
       exit_fail()
    
    if not opts.noprogram:
       print '------------------------'
       print 'Programming ROACH: %s'%(roach) 
       sys.stdout.flush()
       fpga.progdev(boffile)
       time.sleep(1)
       print 'done. \n'
       
    if (opts.reset_trans):
       print 'Resetting the transceivers on: %s.\n'%(roach)
       fpga.write_int('gtxrxreset_in', 0xff)
       fpga.write_int('gtxrxreset_in', 0x00)
       print 'done \n'

    if (opts.set_coef):
       print 'Setting coefficients on: %s.\n'%(roach)
       # 000000 111111 #      
       lsbre01_to_pack = np.round(lsbre01*2**29)
       lsbre01_packed  = struct.pack('>512l', *lsbre01_to_pack)   #the star is there so that it actually reads lsbre01_topack[0] lsbre01_topack[1] lsbre01_topack[2] .... lsbre01_topack[512]
       fpga.write('lsbre01', lsbre01_packed, 0)          
       
       lsbim01_to_pack = np.round(lsbim01*2**29)
       lsbim01_packed  = struct.pack('>512l', *lsbim01_to_pack)   
       fpga.write('lsbim01', lsbim01_packed, 0) 
  
       usbre01_to_pack = np.round(usbre01*2**29)    
       usbre01_packed  = struct.pack('>512l', *usbre01_to_pack)
       fpga.write('usbre01', usbre01_packed, 0)

       usbim01_to_pack = np.round(usbim01*2**29)
       usbim01_packed  = struct.pack('>512l', *usbim01_to_pack)
       fpga.write('usbim01', usbim01_packed, 0)

       # 222222 333333 #
       lsbre23_to_pack = np.round(lsbre23*2**29)
       lsbre23_packed  = struct.pack('>512l', *lsbre23_to_pack)
       fpga.write('lsbre23', lsbre23_packed, 0)

       lsbim23_to_pack = np.round(lsbim23*2**29)
       lsbim23_packed  = struct.pack('>512l', *lsbim23_to_pack)
       fpga.write('lsbim23', lsbim23_packed, 0)

       usbre23_to_pack = np.round(usbre23*2**29)
       usbre23_packed  = struct.pack('>512l', *usbre23_to_pack)
       fpga.write('usbre23', usbre23_packed, 0)

       usbim23_to_pack = np.round(usbim23*2**29)
       usbim23_packed  = struct.pack('>512l', *usbim23_to_pack)
       fpga.write('usbim23', usbim23_packed, 0)

       # 444444 555555 #
       lsbre45_to_pack = np.round(lsbre45*2**29)
       lsbre45_packed  = struct.pack('>512l', *lsbre45_to_pack)
       fpga.write('lsbre45', lsbre45_packed, 0)

       lsbim45_to_pack = np.round(lsbim45*2**29)
       lsbim45_packed  = struct.pack('>512l',*lsbim45_to_pack)
       fpga.write('lsbim45', lsbim45_packed, 0)

       usbre45_to_pack = np.round(usbre45*2**29)
       usbre45_packed  = struct.pack('>512l',*usbre45_to_pack)
       fpga.write('usbre45', usbre45_packed, 0)

       usbim45_to_pack = np.round(usbim45*2**29)
       usbim45_packed  = struct.pack('>512l',*usbim45_to_pack)
       fpga.write('usbim45', usbim45_packed, 0)

       # 666666 777777 #
       lsbre67_to_pack = np.round(lsbre67*2**29)
       lsbre67_packed  = struct.pack('>512l',*lsbre67_to_pack)
       fpga.write('lsbre67', lsbre67_packed, 0)
 
       lsbim67_to_pack = np.round(lsbim67*2**29)
       lsbim67_packed  = struct.pack('>512l',*lsbim67_to_pack)
       fpga.write('lsbim67', lsbim67_packed, 0)

       usbre67_to_pack = np.round(usbre67*2**29)
       usbre67_packed  = struct.pack('>512l',*usbre67_to_pack)
       fpga.write('usbre67', usbre67_packed, 0)

       usbim67_to_pack = np.round(usbim67*2**29)
       usbim67_packed  = struct.pack('>512l',*usbim67_to_pack)
       fpga.write('usbim67', usbim67_packed, 0)
       print 'done. \n'

    if (opts.auto_align_bits):
       print 'Aligning bits... \n'
       fpga.write_int('msb_realign',1)
       time.sleep(0.5)
       fpga.write_int('msb_realign',0)
       time.sleep(0.5)             #luke
       if(fpga.read_int('bit_locked') !=255):#luke
            print 'bit locked failed. \n'   #luke
       print 'done. \n'

    if (opts.auto_align_bytes==1):
       print 'Aligning IQ... \n'
       
       ###############
       #Luke debug
       ###############

    
       time.sleep(0.3)
       ####################################
       ####################################
       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,0)
       usb0_mag1, lsb0_mag1, usb1_mag1, lsb1_mag1 = treat_data_sbs(0,0)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag1, lsb2_mag1, usb3_mag1, lsb3_mag1 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag1, lsb4_mag1, usb5_mag1, lsb5_mag1 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag1, lsb6_mag1, usb7_mag1, lsb7_mag1 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag2, lsb0_mag2, usb1_mag2, lsb1_mag2 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag2, lsb2_mag2, usb3_mag2, lsb3_mag2 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag2, lsb4_mag2, usb5_mag2, lsb5_mag2 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag2, lsb6_mag2, usb7_mag2, lsb7_mag2 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag3, lsb0_mag3, usb1_mag3, lsb1_mag3 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag3, lsb2_mag3, usb3_mag3, lsb3_mag3 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag3, lsb4_mag3, usb5_mag3, lsb5_mag3 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag3, lsb6_mag3, usb7_mag3, lsb7_mag3 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag4, lsb0_mag4, usb1_mag4, lsb1_mag4 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag4, lsb2_mag4, usb3_mag4, lsb3_mag4 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag4, lsb4_mag4, usb5_mag4, lsb5_mag4 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag4, lsb6_mag4, usb7_mag4, lsb7_mag4 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag5, lsb0_mag5, usb1_mag5, lsb1_mag5 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag5, lsb2_mag5, usb3_mag5, lsb3_mag5 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag5, lsb4_mag5, usb5_mag5, lsb5_mag5 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag5, lsb6_mag5, usb7_mag5, lsb7_mag5 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag6, lsb0_mag6, usb1_mag6, lsb1_mag6 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag6, lsb2_mag6, usb3_mag6, lsb3_mag6 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag6, lsb4_mag6, usb5_mag6, lsb5_mag6 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag6, lsb6_mag6, usb7_mag6, lsb7_mag6 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag7, lsb0_mag7, usb1_mag7, lsb1_mag7 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag7, lsb2_mag7, usb3_mag7, lsb3_mag7 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag7, lsb4_mag7, usb5_mag7, lsb5_mag7 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag7, lsb6_mag7, usb7_mag7, lsb7_mag7 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag8, lsb0_mag8, usb1_mag8, lsb1_mag8 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag8, lsb2_mag8, usb3_mag8, lsb3_mag8 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag8, lsb4_mag8, usb5_mag8, lsb5_mag8 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag8, lsb6_mag8, usb7_mag8, lsb7_mag8 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag9, lsb0_mag9, usb1_mag9, lsb1_mag9 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag9, lsb2_mag9, usb3_mag9, lsb3_mag9 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag9, lsb4_mag9, usb5_mag9, lsb5_mag9 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag9, lsb6_mag9, usb7_mag9, lsb7_mag9 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag10, lsb0_mag10, usb1_mag10, lsb1_mag10 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag10, lsb2_mag10, usb3_mag10, lsb3_mag10 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag10, lsb4_mag10, usb5_mag10, lsb5_mag10 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag10, lsb6_mag10, usb7_mag10, lsb7_mag10 = treat_data_sbs(6,1)

       time.sleep(0.1)
       
       usb0_mag=usb0_mag1
       lsb0_mag=lsb0_mag1
       usb1_mag=usb1_mag1
       lsb1_mag=lsb1_mag1
       usb2_mag=usb2_mag1
       lsb2_mag=lsb2_mag1
       usb3_mag=usb3_mag1
       lsb3_mag=lsb3_mag1
       usb4_mag=usb4_mag1
       lsb4_mag=lsb4_mag1
       usb5_mag=usb5_mag1
       lsb5_mag=lsb5_mag1
       usb6_mag=usb6_mag1
       lsb6_mag=lsb6_mag1
       usb7_mag=usb7_mag1
       lsb7_mag=lsb7_mag1

       ii=1
       #while ii<257:
       ########luke
       while ii<256:
            usb0_mag[ii] = usb0_mag1[ii]+usb0_mag2[ii]+usb0_mag3[ii]+usb0_mag4[ii]+usb0_mag5[ii]+usb0_mag6[ii]+usb0_mag7[ii]+usb0_mag8[ii]+usb0_mag9[ii]+usb0_mag10[ii]
            lsb0_mag[ii] = lsb0_mag1[ii]+lsb0_mag2[ii]+lsb0_mag3[ii]+lsb0_mag5[ii]+lsb0_mag5[ii]+lsb0_mag6[ii]+lsb0_mag7[ii]+lsb0_mag8[ii]+lsb0_mag9[ii]+lsb0_mag10[ii]
            usb1_mag[ii] = usb1_mag1[ii]+usb1_mag2[ii]+usb1_mag3[ii]+usb1_mag4[ii]+usb1_mag5[ii]+usb1_mag6[ii]+usb1_mag7[ii]+usb1_mag8[ii]+usb1_mag9[ii]+usb1_mag10[ii]
            lsb1_mag[ii] = lsb1_mag1[ii]+lsb1_mag2[ii]+lsb1_mag3[ii]+lsb1_mag5[ii]+lsb1_mag5[ii]+lsb1_mag6[ii]+lsb1_mag7[ii]+lsb1_mag8[ii]+lsb1_mag9[ii]+lsb1_mag10[ii]
            usb2_mag[ii] = usb2_mag1[ii]+usb2_mag2[ii]+usb2_mag3[ii]+usb2_mag4[ii]+usb2_mag5[ii]+usb2_mag6[ii]+usb2_mag7[ii]+usb2_mag8[ii]+usb2_mag9[ii]+usb2_mag10[ii]
            lsb2_mag[ii] = lsb2_mag1[ii]+lsb2_mag2[ii]+lsb2_mag3[ii]+lsb2_mag5[ii]+lsb2_mag5[ii]+lsb2_mag6[ii]+lsb2_mag7[ii]+lsb2_mag8[ii]+lsb2_mag9[ii]+lsb2_mag10[ii]
            usb3_mag[ii] = usb3_mag1[ii]+usb3_mag2[ii]+usb3_mag3[ii]+usb3_mag4[ii]+usb3_mag5[ii]+usb3_mag6[ii]+usb3_mag7[ii]+usb3_mag8[ii]+usb3_mag9[ii]+usb3_mag10[ii]
            lsb3_mag[ii] = lsb3_mag1[ii]+lsb3_mag2[ii]+lsb3_mag3[ii]+lsb3_mag5[ii]+lsb3_mag5[ii]+lsb3_mag6[ii]+lsb3_mag7[ii]+lsb3_mag8[ii]+lsb3_mag9[ii]+lsb3_mag10[ii]
            usb4_mag[ii] = usb4_mag1[ii]+usb4_mag2[ii]+usb4_mag3[ii]+usb4_mag4[ii]+usb4_mag5[ii]+usb4_mag6[ii]+usb4_mag7[ii]+usb4_mag8[ii]+usb4_mag9[ii]+usb4_mag10[ii]
            lsb4_mag[ii] = lsb4_mag1[ii]+lsb4_mag2[ii]+lsb4_mag3[ii]+lsb4_mag5[ii]+lsb4_mag5[ii]+lsb4_mag6[ii]+lsb4_mag7[ii]+lsb4_mag8[ii]+lsb4_mag9[ii]+lsb4_mag10[ii]
            usb5_mag[ii] = usb5_mag1[ii]+usb5_mag2[ii]+usb5_mag3[ii]+usb5_mag4[ii]+usb5_mag5[ii]+usb5_mag6[ii]+usb5_mag7[ii]+usb5_mag8[ii]+usb5_mag9[ii]+usb5_mag10[ii]
            lsb5_mag[ii] = lsb5_mag1[ii]+lsb5_mag2[ii]+lsb5_mag3[ii]+lsb5_mag5[ii]+lsb5_mag5[ii]+lsb5_mag6[ii]+lsb5_mag7[ii]+lsb5_mag8[ii]+lsb5_mag9[ii]+lsb5_mag10[ii]
            usb6_mag[ii] = usb6_mag1[ii]+usb6_mag2[ii]+usb6_mag3[ii]+usb6_mag4[ii]+usb6_mag5[ii]+usb6_mag6[ii]+usb6_mag7[ii]+usb6_mag8[ii]+usb6_mag9[ii]+usb6_mag10[ii]
            lsb6_mag[ii] = lsb6_mag1[ii]+lsb6_mag2[ii]+lsb6_mag3[ii]+lsb6_mag5[ii]+lsb6_mag5[ii]+lsb6_mag6[ii]+lsb6_mag7[ii]+lsb6_mag8[ii]+lsb6_mag9[ii]+lsb6_mag10[ii]
            usb7_mag[ii] = usb7_mag1[ii]+usb7_mag2[ii]+usb7_mag3[ii]+usb7_mag4[ii]+usb7_mag5[ii]+usb7_mag6[ii]+usb7_mag7[ii]+usb7_mag8[ii]+usb7_mag9[ii]+usb7_mag10[ii]
            lsb7_mag[ii] = lsb7_mag1[ii]+lsb7_mag2[ii]+lsb7_mag3[ii]+lsb7_mag5[ii]+lsb7_mag5[ii]+lsb7_mag6[ii]+lsb7_mag7[ii]+lsb7_mag8[ii]+lsb7_mag9[ii]+lsb7_mag10[ii]
            ii=ii+1

       mag0_rat_a=usb0_mag[166]/lsb0_mag[166]
       mag1_rat_a=usb1_mag[166]/lsb1_mag[166]
       mag2_rat_a=usb2_mag[166]/lsb2_mag[166]
       mag3_rat_a=usb3_mag[166]/lsb3_mag[166]
       mag4_rat_a=usb4_mag[166]/lsb4_mag[166]
       mag5_rat_a=usb5_mag[166]/lsb5_mag[166]
       mag6_rat_a=usb6_mag[166]/lsb6_mag[166]
       mag7_rat_a=usb7_mag[166]/lsb7_mag[166]
       fpga.write_int('rxslide',255)
       time.sleep(0.1)
       fpga.write_int('rxslide',0)
       time.sleep(0.1)
       fpga.write_int('rxslide',255)
       time.sleep(0.1)
       fpga.write_int('rxslide',0)
       time.sleep(0.1)
       fpga.write_int('rxslide',255)
       time.sleep(0.1)
       fpga.write_int('rxslide',0)
       time.sleep(0.1)
       fpga.write_int('rxslide',255)
       time.sleep(0.1)
       fpga.write_int('rxslide',0)
       time.sleep(0.1)
       fpga.write_int('rxslide',255)
       time.sleep(0.1)
       fpga.write_int('rxslide',0)
       time.sleep(0.1)
       fpga.write_int('rxslide',255)
       time.sleep(0.1)
       fpga.write_int('rxslide',0)
       time.sleep(0.1)
       fpga.write_int('rxslide',255)
       time.sleep(0.1)
       fpga.write_int('rxslide',0)
       time.sleep(0.1)
       fpga.write_int('rxslide',255)
       time.sleep(0.1)
       fpga.write_int('rxslide',0)



       time.sleep(1)
       ####################################
       ####################################
       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,0)
       usb0_mag1, lsb0_mag1, usb1_mag1, lsb1_mag1 = treat_data_sbs(0,0)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag1, lsb2_mag1, usb3_mag1, lsb3_mag1 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag1, lsb4_mag1, usb5_mag1, lsb5_mag1 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag1, lsb6_mag1, usb7_mag1, lsb7_mag1 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag2, lsb0_mag2, usb1_mag2, lsb1_mag2 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag2, lsb2_mag2, usb3_mag2, lsb3_mag2 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag2, lsb4_mag2, usb5_mag2, lsb5_mag2 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag2, lsb6_mag2, usb7_mag2, lsb7_mag2 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag3, lsb0_mag3, usb1_mag3, lsb1_mag3 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag3, lsb2_mag3, usb3_mag3, lsb3_mag3 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag3, lsb4_mag3, usb5_mag3, lsb5_mag3 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag3, lsb6_mag3, usb7_mag3, lsb7_mag3 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag4, lsb0_mag4, usb1_mag4, lsb1_mag4 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag4, lsb2_mag4, usb3_mag4, lsb3_mag4 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag4, lsb4_mag4, usb5_mag4, lsb5_mag4 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag4, lsb6_mag4, usb7_mag4, lsb7_mag4 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag5, lsb0_mag5, usb1_mag5, lsb1_mag5 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag5, lsb2_mag5, usb3_mag5, lsb3_mag5 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag5, lsb4_mag5, usb5_mag5, lsb5_mag5 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag5, lsb6_mag5, usb7_mag5, lsb7_mag5 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag6, lsb0_mag6, usb1_mag6, lsb1_mag6 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag6, lsb2_mag6, usb3_mag6, lsb3_mag6 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag6, lsb4_mag6, usb5_mag6, lsb5_mag6 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag6, lsb6_mag6, usb7_mag6, lsb7_mag6 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag7, lsb0_mag7, usb1_mag7, lsb1_mag7 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag7, lsb2_mag7, usb3_mag7, lsb3_mag7 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag7, lsb4_mag7, usb5_mag7, lsb5_mag7 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag7, lsb6_mag7, usb7_mag7, lsb7_mag7 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag8, lsb0_mag8, usb1_mag8, lsb1_mag8 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag8, lsb2_mag8, usb3_mag8, lsb3_mag8 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag8, lsb4_mag8, usb5_mag8, lsb5_mag8 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag8, lsb6_mag8, usb7_mag8, lsb7_mag8 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag9, lsb0_mag9, usb1_mag9, lsb1_mag9 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag9, lsb2_mag9, usb3_mag9, lsb3_mag9 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag9, lsb4_mag9, usb5_mag9, lsb5_mag9 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag9, lsb6_mag9, usb7_mag9, lsb7_mag9 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag10, lsb0_mag10, usb1_mag10, lsb1_mag10 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag10, lsb2_mag10, usb3_mag10, lsb3_mag10 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag10, lsb4_mag10, usb5_mag10, lsb5_mag10 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag10, lsb6_mag10, usb7_mag10, lsb7_mag10 = treat_data_sbs(6,1)

       time.sleep(0.1)
       
       usb0_mag=usb0_mag1
       lsb0_mag=lsb0_mag1
       usb1_mag=usb1_mag1
       lsb1_mag=lsb1_mag1
       usb2_mag=usb2_mag1
       lsb2_mag=lsb2_mag1
       usb3_mag=usb3_mag1
       lsb3_mag=lsb3_mag1
       usb4_mag=usb4_mag1
       lsb4_mag=lsb4_mag1
       usb5_mag=usb5_mag1
       lsb5_mag=lsb5_mag1
       usb6_mag=usb6_mag1
       lsb6_mag=lsb6_mag1
       usb7_mag=usb7_mag1
       lsb7_mag=lsb7_mag1

       ii=1
       #while ii<257:
       ########luke
       while ii<256:
            usb0_mag[ii] = usb0_mag1[ii]+usb0_mag2[ii]+usb0_mag3[ii]+usb0_mag4[ii]+usb0_mag5[ii]+usb0_mag6[ii]+usb0_mag7[ii]+usb0_mag8[ii]+usb0_mag9[ii]+usb0_mag10[ii]
            lsb0_mag[ii] = lsb0_mag1[ii]+lsb0_mag2[ii]+lsb0_mag3[ii]+lsb0_mag5[ii]+lsb0_mag5[ii]+lsb0_mag6[ii]+lsb0_mag7[ii]+lsb0_mag8[ii]+lsb0_mag9[ii]+lsb0_mag10[ii]
            usb1_mag[ii] = usb1_mag1[ii]+usb1_mag2[ii]+usb1_mag3[ii]+usb1_mag4[ii]+usb1_mag5[ii]+usb1_mag6[ii]+usb1_mag7[ii]+usb1_mag8[ii]+usb1_mag9[ii]+usb1_mag10[ii]
            lsb1_mag[ii] = lsb1_mag1[ii]+lsb1_mag2[ii]+lsb1_mag3[ii]+lsb1_mag5[ii]+lsb1_mag5[ii]+lsb1_mag6[ii]+lsb1_mag7[ii]+lsb1_mag8[ii]+lsb1_mag9[ii]+lsb1_mag10[ii]
            usb2_mag[ii] = usb2_mag1[ii]+usb2_mag2[ii]+usb2_mag3[ii]+usb2_mag4[ii]+usb2_mag5[ii]+usb2_mag6[ii]+usb2_mag7[ii]+usb2_mag8[ii]+usb2_mag9[ii]+usb2_mag10[ii]
            lsb2_mag[ii] = lsb2_mag1[ii]+lsb2_mag2[ii]+lsb2_mag3[ii]+lsb2_mag5[ii]+lsb2_mag5[ii]+lsb2_mag6[ii]+lsb2_mag7[ii]+lsb2_mag8[ii]+lsb2_mag9[ii]+lsb2_mag10[ii]
            usb3_mag[ii] = usb3_mag1[ii]+usb3_mag2[ii]+usb3_mag3[ii]+usb3_mag4[ii]+usb3_mag5[ii]+usb3_mag6[ii]+usb3_mag7[ii]+usb3_mag8[ii]+usb3_mag9[ii]+usb3_mag10[ii]
            lsb3_mag[ii] = lsb3_mag1[ii]+lsb3_mag2[ii]+lsb3_mag3[ii]+lsb3_mag5[ii]+lsb3_mag5[ii]+lsb3_mag6[ii]+lsb3_mag7[ii]+lsb3_mag8[ii]+lsb3_mag9[ii]+lsb3_mag10[ii]
            usb4_mag[ii] = usb4_mag1[ii]+usb4_mag2[ii]+usb4_mag3[ii]+usb4_mag4[ii]+usb4_mag5[ii]+usb4_mag6[ii]+usb4_mag7[ii]+usb4_mag8[ii]+usb4_mag9[ii]+usb4_mag10[ii]
            lsb4_mag[ii] = lsb4_mag1[ii]+lsb4_mag2[ii]+lsb4_mag3[ii]+lsb4_mag5[ii]+lsb4_mag5[ii]+lsb4_mag6[ii]+lsb4_mag7[ii]+lsb4_mag8[ii]+lsb4_mag9[ii]+lsb4_mag10[ii]
            usb5_mag[ii] = usb5_mag1[ii]+usb5_mag2[ii]+usb5_mag3[ii]+usb5_mag4[ii]+usb5_mag5[ii]+usb5_mag6[ii]+usb5_mag7[ii]+usb5_mag8[ii]+usb5_mag9[ii]+usb5_mag10[ii]
            lsb5_mag[ii] = lsb5_mag1[ii]+lsb5_mag2[ii]+lsb5_mag3[ii]+lsb5_mag5[ii]+lsb5_mag5[ii]+lsb5_mag6[ii]+lsb5_mag7[ii]+lsb5_mag8[ii]+lsb5_mag9[ii]+lsb5_mag10[ii]
            usb6_mag[ii] = usb6_mag1[ii]+usb6_mag2[ii]+usb6_mag3[ii]+usb6_mag4[ii]+usb6_mag5[ii]+usb6_mag6[ii]+usb6_mag7[ii]+usb6_mag8[ii]+usb6_mag9[ii]+usb6_mag10[ii]
            lsb6_mag[ii] = lsb6_mag1[ii]+lsb6_mag2[ii]+lsb6_mag3[ii]+lsb6_mag5[ii]+lsb6_mag5[ii]+lsb6_mag6[ii]+lsb6_mag7[ii]+lsb6_mag8[ii]+lsb6_mag9[ii]+lsb6_mag10[ii]
            usb7_mag[ii] = usb7_mag1[ii]+usb7_mag2[ii]+usb7_mag3[ii]+usb7_mag4[ii]+usb7_mag5[ii]+usb7_mag6[ii]+usb7_mag7[ii]+usb7_mag8[ii]+usb7_mag9[ii]+usb7_mag10[ii]
            lsb7_mag[ii] = lsb7_mag1[ii]+lsb7_mag2[ii]+lsb7_mag3[ii]+lsb7_mag5[ii]+lsb7_mag5[ii]+lsb7_mag6[ii]+lsb7_mag7[ii]+lsb7_mag8[ii]+lsb7_mag9[ii]+lsb7_mag10[ii]
            ii=ii+1

       mag0_rat_b=usb0_mag[166]/lsb0_mag[166]
       mag1_rat_b=usb1_mag[166]/lsb1_mag[166]
       mag2_rat_b=usb2_mag[166]/lsb2_mag[166]
       mag3_rat_b=usb3_mag[166]/lsb3_mag[166]
       mag4_rat_b=usb4_mag[166]/lsb4_mag[166]
       mag5_rat_b=usb5_mag[166]/lsb5_mag[166]
       mag6_rat_b=usb6_mag[166]/lsb6_mag[166]
       mag7_rat_b=usb7_mag[166]/lsb7_mag[166]

       print ('mag0_rat_a')
       print mag0_rat_a
       print ('mag0_rat_b')
       print mag0_rat_b

       print ('mag1_rat_a')
       print mag1_rat_a
       print ('mag1_rat_b')
       print mag1_rat_b

       print ('mag2_rat_a')
       print mag2_rat_a
       print ('mag2_rat_b')
       print mag2_rat_b

       print ('mag3_rat_a')
       print mag3_rat_a
       print ('mag3_rat_b')
       print mag3_rat_b

       print ('mag4_rat_a')
       print mag4_rat_a
       print ('mag4_rat_b')
       print mag4_rat_b

       print ('mag5_rat_a')
       print mag5_rat_a
       print ('mag5_rat_b')
       print mag5_rat_b

       print ('mag6_rat_a')
       print mag6_rat_a
       print ('mag6_rat_b')
       print mag6_rat_b

       print ('mag7_rat_a')
       print mag7_rat_a
       print ('mag7_rat_b')
       print mag7_rat_b

       if(mag0_rat_a>mag0_rat_b):
            ##flyp dem bites on A0!!!
            print 're-aligning 0 \n'
            fpga.write_int('rxslide',1)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',1)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',1)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',1)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',1)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',1)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',1)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',1)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)


       if(mag1_rat_a>mag1_rat_b):
            ##flyp dem bites on A1!!!
            print 're-aligning 1 \n'
            fpga.write_int('rxslide',2)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',2)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',2)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',2)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',2)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',2)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',2)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',2)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)


       if(mag2_rat_a>mag2_rat_b):
            ##flyp dem bites on A2!!!
            print 're-aligning 2 \n'
            fpga.write_int('rxslide',4)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',4)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',4)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',4)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',4)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',4)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',4)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',4)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)


       if(mag3_rat_a>mag3_rat_b):
            ##flyp dem bites on A3!!!
            print 're-aligning 3 \n'
            fpga.write_int('rxslide',8)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',8)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',8)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',8)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',8)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',8)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',8)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',8)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)


       if(mag4_rat_a>mag4_rat_b):
            ##flyp dem bites on A4!!!
            print 're-aligning 4 \n'
            fpga.write_int('rxslide',16)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',16)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',16)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',16)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',16)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',16)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',16)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',16)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)


       if(mag5_rat_a>mag5_rat_b):
            ##flyp dem bites on A5!!!
            print 're-aligning 5 \n'
            fpga.write_int('rxslide',32)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',32)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',32)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',32)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',32)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',32)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',32)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',32)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)


       if(mag6_rat_a>mag6_rat_b):
            ##flyp dem bites on A6!!!
            print 're-aligning 6 \n'
            fpga.write_int('rxslide',64)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',64)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',64)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',64)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',64)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',64)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',64)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',64)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)


       if(mag7_rat_a>mag7_rat_b):
            ##flyp dem bites on A7!!!
            print 're-aligning 7 \n'
            fpga.write_int('rxslide',128)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',128)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',128)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',128)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',128)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',128)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',128)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)
            time.sleep(0.1)
            fpga.write_int('rxslide',128)
            time.sleep(0.1)
            fpga.write_int('rxslide',0)

       print 'done aligning bytes \n'









    elif (opts.auto_align_bytes == 2):
       print 'Checking IQ Alignment... \n'
       ####################################

       time.sleep(0.3)
       ####################################
       ####################################
       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,0)
       usb0_mag1, lsb0_mag1, usb1_mag1, lsb1_mag1 = treat_data_sbs(0,0)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag1, lsb2_mag1, usb3_mag1, lsb3_mag1 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag1, lsb4_mag1, usb5_mag1, lsb5_mag1 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag1, lsb6_mag1, usb7_mag1, lsb7_mag1 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag2, lsb0_mag2, usb1_mag2, lsb1_mag2 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag2, lsb2_mag2, usb3_mag2, lsb3_mag2 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag2, lsb4_mag2, usb5_mag2, lsb5_mag2 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag2, lsb6_mag2, usb7_mag2, lsb7_mag2 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag3, lsb0_mag3, usb1_mag3, lsb1_mag3 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag3, lsb2_mag3, usb3_mag3, lsb3_mag3 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag3, lsb4_mag3, usb5_mag3, lsb5_mag3 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag3, lsb6_mag3, usb7_mag3, lsb7_mag3 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag4, lsb0_mag4, usb1_mag4, lsb1_mag4 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag4, lsb2_mag4, usb3_mag4, lsb3_mag4 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag4, lsb4_mag4, usb5_mag4, lsb5_mag4 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag4, lsb6_mag4, usb7_mag4, lsb7_mag4 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag5, lsb0_mag5, usb1_mag5, lsb1_mag5 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag5, lsb2_mag5, usb3_mag5, lsb3_mag5 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag5, lsb4_mag5, usb5_mag5, lsb5_mag5 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag5, lsb6_mag5, usb7_mag5, lsb7_mag5 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag6, lsb0_mag6, usb1_mag6, lsb1_mag6 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag6, lsb2_mag6, usb3_mag6, lsb3_mag6 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag6, lsb4_mag6, usb5_mag6, lsb5_mag6 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag6, lsb6_mag6, usb7_mag6, lsb7_mag6 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag7, lsb0_mag7, usb1_mag7, lsb1_mag7 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag7, lsb2_mag7, usb3_mag7, lsb3_mag7 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag7, lsb4_mag7, usb5_mag7, lsb5_mag7 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag7, lsb6_mag7, usb7_mag7, lsb7_mag7 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag8, lsb0_mag8, usb1_mag8, lsb1_mag8 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag8, lsb2_mag8, usb3_mag8, lsb3_mag8 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag8, lsb4_mag8, usb5_mag8, lsb5_mag8 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag8, lsb6_mag8, usb7_mag8, lsb7_mag8 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag9, lsb0_mag9, usb1_mag9, lsb1_mag9 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag9, lsb2_mag9, usb3_mag9, lsb3_mag9 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag9, lsb4_mag9, usb5_mag9, lsb5_mag9 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag9, lsb6_mag9, usb7_mag9, lsb7_mag9 = treat_data_sbs(6,1)

       time.sleep(0.1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(0,1)
       usb0_mag10, lsb0_mag10, usb1_mag10, lsb1_mag10 = treat_data_sbs(0,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(2,1)
       usb2_mag10, lsb2_mag10, usb3_mag10, lsb3_mag10 = treat_data_sbs(2,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(4,1)
       usb4_mag10, lsb4_mag10, usb5_mag10, lsb5_mag10 = treat_data_sbs(4,1)

       usb_r,usb_i,lsb_r,lsb_i=get_data_sbs(6,1)
       usb6_mag10, lsb6_mag10, usb7_mag10, lsb7_mag10 = treat_data_sbs(6,1)

       time.sleep(0.1)
       
       usb0_mag=usb0_mag1
       lsb0_mag=lsb0_mag1
       usb1_mag=usb1_mag1
       lsb1_mag=lsb1_mag1
       usb2_mag=usb2_mag1
       lsb2_mag=lsb2_mag1
       usb3_mag=usb3_mag1
       lsb3_mag=lsb3_mag1
       usb4_mag=usb4_mag1
       lsb4_mag=lsb4_mag1
       usb5_mag=usb5_mag1
       lsb5_mag=lsb5_mag1
       usb6_mag=usb6_mag1
       lsb6_mag=lsb6_mag1
       usb7_mag=usb7_mag1
       lsb7_mag=lsb7_mag1

       ii=1
       #while ii<257:
       ########luke
       while ii<256:
            usb0_mag[ii] = usb0_mag1[ii]+usb0_mag2[ii]+usb0_mag3[ii]+usb0_mag4[ii]+usb0_mag5[ii]+usb0_mag6[ii]+usb0_mag7[ii]+usb0_mag8[ii]+usb0_mag9[ii]+usb0_mag10[ii]
            lsb0_mag[ii] = lsb0_mag1[ii]+lsb0_mag2[ii]+lsb0_mag3[ii]+lsb0_mag5[ii]+lsb0_mag5[ii]+lsb0_mag6[ii]+lsb0_mag7[ii]+lsb0_mag8[ii]+lsb0_mag9[ii]+lsb0_mag10[ii]
            usb1_mag[ii] = usb1_mag1[ii]+usb1_mag2[ii]+usb1_mag3[ii]+usb1_mag4[ii]+usb1_mag5[ii]+usb1_mag6[ii]+usb1_mag7[ii]+usb1_mag8[ii]+usb1_mag9[ii]+usb1_mag10[ii]
            lsb1_mag[ii] = lsb1_mag1[ii]+lsb1_mag2[ii]+lsb1_mag3[ii]+lsb1_mag5[ii]+lsb1_mag5[ii]+lsb1_mag6[ii]+lsb1_mag7[ii]+lsb1_mag8[ii]+lsb1_mag9[ii]+lsb1_mag10[ii]
            usb2_mag[ii] = usb2_mag1[ii]+usb2_mag2[ii]+usb2_mag3[ii]+usb2_mag4[ii]+usb2_mag5[ii]+usb2_mag6[ii]+usb2_mag7[ii]+usb2_mag8[ii]+usb2_mag9[ii]+usb2_mag10[ii]
            lsb2_mag[ii] = lsb2_mag1[ii]+lsb2_mag2[ii]+lsb2_mag3[ii]+lsb2_mag5[ii]+lsb2_mag5[ii]+lsb2_mag6[ii]+lsb2_mag7[ii]+lsb2_mag8[ii]+lsb2_mag9[ii]+lsb2_mag10[ii]
            usb3_mag[ii] = usb3_mag1[ii]+usb3_mag2[ii]+usb3_mag3[ii]+usb3_mag4[ii]+usb3_mag5[ii]+usb3_mag6[ii]+usb3_mag7[ii]+usb3_mag8[ii]+usb3_mag9[ii]+usb3_mag10[ii]
            lsb3_mag[ii] = lsb3_mag1[ii]+lsb3_mag2[ii]+lsb3_mag3[ii]+lsb3_mag5[ii]+lsb3_mag5[ii]+lsb3_mag6[ii]+lsb3_mag7[ii]+lsb3_mag8[ii]+lsb3_mag9[ii]+lsb3_mag10[ii]
            usb4_mag[ii] = usb4_mag1[ii]+usb4_mag2[ii]+usb4_mag3[ii]+usb4_mag4[ii]+usb4_mag5[ii]+usb4_mag6[ii]+usb4_mag7[ii]+usb4_mag8[ii]+usb4_mag9[ii]+usb4_mag10[ii]
            lsb4_mag[ii] = lsb4_mag1[ii]+lsb4_mag2[ii]+lsb4_mag3[ii]+lsb4_mag5[ii]+lsb4_mag5[ii]+lsb4_mag6[ii]+lsb4_mag7[ii]+lsb4_mag8[ii]+lsb4_mag9[ii]+lsb4_mag10[ii]
            usb5_mag[ii] = usb5_mag1[ii]+usb5_mag2[ii]+usb5_mag3[ii]+usb5_mag4[ii]+usb5_mag5[ii]+usb5_mag6[ii]+usb5_mag7[ii]+usb5_mag8[ii]+usb5_mag9[ii]+usb5_mag10[ii]
            lsb5_mag[ii] = lsb5_mag1[ii]+lsb5_mag2[ii]+lsb5_mag3[ii]+lsb5_mag5[ii]+lsb5_mag5[ii]+lsb5_mag6[ii]+lsb5_mag7[ii]+lsb5_mag8[ii]+lsb5_mag9[ii]+lsb5_mag10[ii]
            usb6_mag[ii] = usb6_mag1[ii]+usb6_mag2[ii]+usb6_mag3[ii]+usb6_mag4[ii]+usb6_mag5[ii]+usb6_mag6[ii]+usb6_mag7[ii]+usb6_mag8[ii]+usb6_mag9[ii]+usb6_mag10[ii]
            lsb6_mag[ii] = lsb6_mag1[ii]+lsb6_mag2[ii]+lsb6_mag3[ii]+lsb6_mag5[ii]+lsb6_mag5[ii]+lsb6_mag6[ii]+lsb6_mag7[ii]+lsb6_mag8[ii]+lsb6_mag9[ii]+lsb6_mag10[ii]
            usb7_mag[ii] = usb7_mag1[ii]+usb7_mag2[ii]+usb7_mag3[ii]+usb7_mag4[ii]+usb7_mag5[ii]+usb7_mag6[ii]+usb7_mag7[ii]+usb7_mag8[ii]+usb7_mag9[ii]+usb7_mag10[ii]
            lsb7_mag[ii] = lsb7_mag1[ii]+lsb7_mag2[ii]+lsb7_mag3[ii]+lsb7_mag5[ii]+lsb7_mag5[ii]+lsb7_mag6[ii]+lsb7_mag7[ii]+lsb7_mag8[ii]+lsb7_mag9[ii]+lsb7_mag10[ii]
            ii=ii+1


       print ('usb0_mag_sum')
       print usb0_mag[166]
       print ('lsb0_mag_sum')
       print lsb0_mag[166]

       print ('usb1_mag_sum')
       print usb1_mag[166]
       print ('lsb1_mag_sum')
       print lsb1_mag[166]

       print ('usb2_mag_sum')
       print usb2_mag[166]
       print ('lsb2_mag_sum')
       print lsb2_mag[166]

       print ('usb3_mag_sum')
       print usb3_mag[166]
       print ('lsb3_mag_sum')
       print lsb3_mag[166]

       print ('usb4_mag_sum')
       print usb4_mag[166]
       print ('lsb4_mag_sum')
       print lsb4_mag[166]

       print ('usb5_mag_sum')
       print usb5_mag[166]
       print ('lsb5_mag_sum')
       print lsb5_mag[166]

       print ('usb6_mag_sum')
       print usb6_mag[166]
       print ('lsb6_mag_sum')
       print lsb6_mag[166]

       print ('usb7_mag_sum')
       print usb7_mag[166]
       print ('lsb7_mag_sum')
       print lsb7_mag[166]

       if(usb0_mag[166]<(lsb0_mag[166]*10)):
            ##flyp dem bites on A0!!!
            print 'Channel 0 not aligned\n'
            if(usb0_mag[166]<(lsb0_mag[166]*3)):
                print 'setting threshold lower \n'
                fpga.write_int('rxslide',1)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',1)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',1)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',1)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',1)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',1)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',1)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',1)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)

       if(usb1_mag[166]<(lsb1_mag[166]*10)):
            ##flyp dem bites on A1!!!
            print 'Channel 1 not aligned\n'
            if(usb1_mag[166]<(lsb1_mag[166]*3)):
                print 'setting threshold lower \n'
                fpga.write_int('rxslide',2)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',2)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',2)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',2)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',2)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',2)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',2)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',2)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)

       if(usb2_mag[166]<(lsb2_mag[166]*10)):
            ##flyp dem bites on A2!!!
            print 'Channel 2 not aligned\n'
            if(usb2_mag[166]<(lsb2_mag[166]*3)):
                print 'setting threshold lower \n'
                fpga.write_int('rxslide',4)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',4)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',4)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',4)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',4)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',4)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',4)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',4)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)

       if(usb3_mag[166]<(lsb3_mag[166]*10)):
            ##flyp dem bites on A3!!!
            print 'Channel 3 not aligned\n'
            if(usb3_mag[166]<(lsb3_mag[166]*3)):
                print 'setting threshold lower \n'
                fpga.write_int('rxslide',8)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',8)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',8)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',8)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',8)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',8)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',8)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',8)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)

       if(usb4_mag[166]<(lsb4_mag[166]*10)):
            ##flyp dem bites on A4!!!
            print 'Channel 4 not aligned\n'
            if(usb4_mag[166]<(lsb4_mag[166]*3)):
                print 'setting threshold lower \n'
                fpga.write_int('rxslide',16)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',16)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',16)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',16)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',16)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',16)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',16)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',16)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)

       if(usb5_mag[166]<(lsb5_mag[166]*10)):
            ##flyp dem bites on A5!!!
            print 'Channel 5 not aligned\n'
            if(usb5_mag[166]<(lsb5_mag[166]*3)):
                print 'setting threshold lower \n'
                fpga.write_int('rxslide',32)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',32)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',32)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',32)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',32)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',32)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',32)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',32)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)

       if(usb6_mag[166]<(lsb6_mag[166]*10)):
            ##flyp dem bites on A6!!!
            print 'Channel 6 not aligned\n'
            if(usb6_mag[166]<(lsb6_mag[166]*3)):
                print 'setting threshold lower \n'
                fpga.write_int('rxslide',64)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',64)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',64)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',64)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',64)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',64)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',64)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',64)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)

       if(usb7_mag[166]<(lsb7_mag[166]*10)):
            ##flyp dem bites on A7!!!
            print 'Channel 7 not aligned\n'
            if(usb7_mag[166]<(lsb7_mag[166]*3)):
                print 'setting threshold lower \n'
                fpga.write_int('rxslide',164)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',164)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',164)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',164)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',164)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',164)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',164)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)
                time.sleep(0.1)
                fpga.write_int('rxslide',164)
                time.sleep(0.1)
                fpga.write_int('rxslide',0)

       print 'done checking byte alignment \n'
    #
    if (opts.swap_bytes_ch != -1):
       print 'Swapping bytes on specified channel/s'
      
       #while(hex(fpga.read_int('msb2_loc')) != 0x80):
       #   print 'in while'
       #   swap_byte(fpga,opts.swap_bytes_ch)      
       #print 'done'
 
    print 'Writing fft_shift ..... \n'
    fpga.write_int('fft_shift',opts.fft_shift)    #Don't know where this number comes from but its like this in the tut3 example as well 
    print 'done \n'
    
    print 'Writing quantization gain .... \n'
    fpga.write_int('quant_gain',0x0000000a)
    print 'done \n'

##########################
#######################
#########luke

    if (opts.pack):
       #resets the GbE cores
       print 'Resetting the GbE cores on: %s' %(roach) 
       fpga.write_int('part2_gbe_rst_core',0)
       time.sleep(1)
       fpga.write_int('part2_gbe_rst_core',1)
       time.sleep(1)
       fpga.write_int('part2_gbe_rst_core',0)
       time.sleep(1)
       print 'done. \n'
       
      # Configure 10 GbE cores
       print 'Configuring 10 GbE interfaces on: %s.\n'%(roach) 
       fpga.config_10gbe_core('part2_gbe0', mac_base0, source_ip0, source_port, hpc_macs_list)
       fpga.config_10gbe_core('part2_gbe1', mac_base1, source_ip1, source_port, hpc_macs_list)
       fpga.config_10gbe_core('part2_gbe2', mac_base2, source_ip2, source_port, hpc_macs_list)
       fpga.config_10gbe_core('part2_gbe3', mac_base3, source_ip3, source_port, hpc_macs_list)
       print 'done. \n'
       print '------------------------'

       #set f_id
       print 'Write f engine fid... '  
       fpga.write_int('part2_f_id', opts.fid)
       time.sleep(0.5)
       print 'done. \n'
       
       #set x_id's
       print 'Write x engine id... '
       for i in range(20):
          fpga.write_int('part2_x_id'+str(i),i)
       time.sleep(0.5)
       print 'done. \n'
      
       #set destination port 
       print 'Writing destination port number: %d' %opts.dport
       fpga.write_int('part2_x_port', opts.dport)
       time.sleep(0.5)
       print 'done \n'
      
    #Set the destination IP addresses 
    if (opts.xid != -1):
       for i in range(20): 
          fpga.write_int('part2_x_ip'+str(i), blackhole)

       # The following 11 lines of code can be upgraded to case statements
       if  (opts.dcomp=='paf0' ):
          print 'Send subbands %d to paf0 and subsequent 4 xids to flag3' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid)  ,paf0   )
          fpga.write_int('part2_x_ip'+str(opts.xid+1),flag3_0)
          fpga.write_int('part2_x_ip'+str(opts.xid+2),flag3_1)
          fpga.write_int('part2_x_ip'+str(opts.xid+3),flag3_2)
          fpga.write_int('part2_x_ip'+str(opts.xid+4),flag3_3)
       elif(opts.dcomp=='south'):
          print 'Send subbands %d to south' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),south)
       elif(opts.dcomp=='west' ):
          print 'Send subbands %d to west' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),west )
       elif(opts.dcomp=='tofu' ):
          print 'Send subbands %d to tofu' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),tofu )
       else :
          print("Unknown destination computer therefore sending packets to the BlAcKhOlE\n");
          fpga.write_int('part2_x_ip'+str(opts.xid),blackhole)

       print '\n done'


    if (opts.arm):
       print 'Sending sync pulse \n'
       fpga.write_int('ARM',1)
       fpga.write_int('ARM',0)
       print 'done ... \n'

    #if (opts.sbs_data):
    #   print 'Enabling output snapshots blocks \n'
    #   for k in range(4):
    #      fpga.write_int('lsb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
    #      fpga.write_int('lsb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,0)
    #      fpga.write_int('usb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
    #      fpga.write_int('usb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
# 
#       for k in range(4):
#          fpga.write_int('lsb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,1) 
#          fpga.write_int('lsb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,1)
#          fpga.write_int('usb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,1) 
#          fpga.write_int('usb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,1) ##

       #for k in range(4):
       #   fpga.write_int('lsb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
       #   fpga.write_int('lsb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,0)
       #   fpga.write_int('usb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
       #   fpga.write_int('usb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
       
       #time.sleep(0.5)
       #get_data_sbs(0)
       #get_data_sbs(2)
       #get_data_sbs(4)
       #get_data_sbs(6)
       #print 'done \n'
    #luke added

#Luke commented out
    if (opts.time_data):
       print 'Reseting time domain brams'
       fpga.write_int('bram_we' ,0)
       fpga.write_int('bram_rst',1)
       fpga.write_int('bram_rst',0)
       fpga.write_int('bram_we' ,1)
       time.sleep(2)
       for i in range(8):
         get_data_iq(i)
       print 'done \n'

except KeyboardInterrupt:
  exit_clean()
except:
  exit_fail()

exit_clean()
