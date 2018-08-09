#!/opt/local/bin/python2.7

import corr, time, struct, sys, logging, socket
from numpy import genfromtxt
import numpy as np

#boffile     = 'flag36_2016_Jul_29_1532.bof'
boffile = 'flag39_4_2017_May_09_0946.bof'
paf0        = 10*(2**24)+17*(2**16)+16*(2**8)+39
paf1        = 10*(2**24)+17*(2**16)+16*(2**8)+40
flag3_p0    = 10*(2**24)+17*(2**16)+16*(2**8)+208
flag3_p1    = 10*(2**24)+17*(2**16)+16*(2**8)+209
flag3_p2    = 10*(2**24)+17*(2**16)+16*(2**8)+210
flag3_p3    = 10*(2**24)+17*(2**16)+16*(2**8)+211
#west        = 10*(2**24)+17*(2**16)+0*(2**8)+35 # west ip address , need to direct the unwanted packets somewhere   
#tofu        = 10*(2**24)+17*(2**16)+0*(2**8)+36 # ip address of tofu for the correct mac address
#south       = 10*(2**24)+17*(2**16)+0*(2**8)+33 
blackhole   = 10*(2**24)+17*(2**16)+16*(2**8)+200

source_port = 60000                             #the physical port on the roach board side  which it will be sending from

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
    '10.17.16.39': 0x000F5308458C, # paf0
    '10.17.16.40': 0x000F5308458D, # paf1
    '10.17.16.208': 0x7cfe90b92df0, # flag3_p0
    '10.17.16.209': 0x7cfe90b92bd0, # flag3_p1
    '10.17.16.210': 0x7cfe90b92bd1, # flag3_p2
    '10.17.16.211': 0x7cfe90b92df1, # flag3_p3
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


def get_data_sbs():

    for k in range(4):
        lsb_raw_re = fpga.read('lsb_re_'+str(k*2)+str(k*2+1)+'_bram',2**12,0) 
        lsb_re = struct.unpack('>4096b',lsb_raw_re)
        
        lsb_raw_im = fpga.read('lsb_im_'+str(k*2)+str(k*2+1)+'_bram',2**12,0)
        lsb_im = struct.unpack('>4096b',lsb_raw_im)
        
        usb_raw_re = fpga.read('usb_re_'+str(k*2)+str(k*2+1)+'_bram',2**12,0) 
        usb_re = struct.unpack('>4096b',usb_raw_re)
        
        usb_raw_im = fpga.read('usb_im_'+str(k*2)+str(k*2+1)+'_bram',2**12,0)
        usb_im = struct.unpack('>4096b',usb_raw_im)
       
        usb_r = np.array(usb_re)/128.0
        usb_i = np.array(usb_im)/128.0
        lsb_r = np.array(lsb_re)/128.0
        lsb_i = np.array(lsb_im)/128.0
        
        m=0
        with open('lsb_data_re'+str(k*2)+str(k*2+1)+'.txt','w') as f:
           for m in range(len(lsb_r)):
               the_str = ""
               the_str += str(lsb_r[m]) + "\n"
               f.write(the_str)
        m=0
        with open('lsb_data_im'+str(k*2)+str(k*2+1)+'.txt','w') as f:
           for m in range(len(lsb_i)):
               the_str = ""
               the_str += str(lsb_i[m]) + "\n"
               f.write(the_str)

        m=0
        with open('usb_data_re'+str(k*2)+str(k*2+1)+'.txt','w') as f:
           for m in range(len(usb_r)):
               the_str = ""
               the_str += str(usb_r[m]) + "\n"
               f.write(the_str)
        m=0
        with open('usb_data_im'+str(k*2)+str(k*2+1)+'.txt','w') as f:
           for m in range(len(usb_i)):
               the_str = ""
               the_str += str(usb_i[m]) + "\n"
               f.write(the_str)

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
    p.add_option('-B'  , '--byte_lock'         , dest='auto_align_bytes', type = 'int'       , default=0           , help='Automatically byte align the system')
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
    p.add_option('-S'  , '--safety'            , dest='safety'          , type = 'int'       , default=1           , help='This is the safety to allow packets to be stopped')

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

    lsbre01 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbre01_'+opts.lo+'.csv', delimiter = '/n')
    lsbre23 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbre23_'+opts.lo+'.csv', delimiter = '/n')
    lsbre45 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbre45_'+opts.lo+'.csv', delimiter = '/n')
    lsbre67 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbre67_'+opts.lo+'.csv', delimiter = '/n')
                                                  
    lsbim01 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbim01_'+opts.lo+'.csv', delimiter = '/n')
    lsbim23 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbim23_'+opts.lo+'.csv', delimiter = '/n')
    lsbim45 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbim45_'+opts.lo+'.csv', delimiter = '/n')
    lsbim67 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_lsbim67_'+opts.lo+'.csv', delimiter = '/n')
                                                  
    usbre01 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbre01_'+opts.lo+'.csv', delimiter = '/n')
    usbre23 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbre23_'+opts.lo+'.csv', delimiter = '/n')
    usbre45 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbre45_'+opts.lo+'.csv', delimiter = '/n')
    usbre67 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbre67_'+opts.lo+'.csv', delimiter = '/n')
                                                  
    usbim01 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbim01_'+opts.lo+'.csv', delimiter = '/n')
    usbim23 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbim23_'+opts.lo+'.csv', delimiter = '/n')
    usbim45 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbim45_'+opts.lo+'.csv', delimiter = '/n')
    usbim67 = genfromtxt('/home/groups/flag/dibas/lib/python/coefficients/'+opts.lo+'/'+fid_prefix+'_512_usbim67_'+opts.lo+'.csv', delimiter = '/n')

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
    time.sleep(0.5)

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
       print 'done. \n'

    if (opts.auto_align_bytes):
       print 'IQ Alignment \n'
       fpga.write_int('iq_realign',1)
       time.sleep(0.5)
       fpga.write_int('iq_realign',0)
       print 'done \n'

    #
    if (opts.swap_bytes_ch != -1):
       print 'Swapping bytes on specified channel/s'
      
       while(hex(fpga.read_int('msb2_loc')) != 0x80):
          print 'in while'
          swap_byte(fpga,opts.swap_bytes_ch)      
       print 'done'
 
    print 'Writing fft_shift ..... \n'
    fpga.write_int('fft_shift',opts.fft_shift)    #Don't know where this number comes from but its like this in the tut3 example as well 
    print 'done \n'
    
    print 'Writing quantization gain .... \n'
    fpga.write_int('quant_gain',0x0000000a)
    print 'done \n'

    if (opts.pack):
       #resets the GbE cores
       print 'Resetting the GbE cores on: %s' %(roach) 
       fpga.write_int('part2_gbe_rst_core',0)
       time.sleep(0.5)
       fpga.write_int('part2_gbe_rst_core',1)
       time.sleep(0.5)
       fpga.write_int('part2_gbe_rst_core',0)
       time.sleep(0.5)
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
          print 'Send subbands %d to paf0' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),paf0 )
       elif  (opts.dcomp=='paf1' ):
          print 'Send subbands %d to paf1' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),paf1 )
       elif(opts.dcomp=='south'):
          print 'Send subbands %d to south' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),south)
       elif(opts.dcomp=='west' ):
          print 'Send subbands %d to west' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),west )
       elif(opts.dcomp=='tofu' ):
          print 'Send subbands %d to tofu' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),tofu )
       elif(opts.dcomp=='flag3_p0' ):
          print 'Send subbands %d to flag3-p0' %opts.xid    
          fpga.write_int('part2_x_ip'+str(opts.xid),flag3_p0 )
       elif(opts.dcomp=='flag3'):
          print 'Send subbands %d to flag3-p0' %opts.xid
          fpga.write_int('part2_x_ip'+str(opts.xid),flag3_p0)
          print 'Send subbands %d to flag3-p1' %(opts.xid+1)
          fpga.write_int('part2_x_ip'+str(opts.xid+1),flag3_p1)
          print 'Send subbands %d to flag3-p2' %(opts.xid+2)
          fpga.write_int('part2_x_ip'+str(opts.xid+2),flag3_p2)
          print 'Send subbands %d to flag3-p3' %(opts.xid+3)
          fpga.write_int('part2_x_ip'+str(opts.xid+3),flag3_p3)
       elif(opts.dcomp=='paf0+flag3'):
          print 'Send subbands %d to paf0'     % ((opts.xid + 0) % 20)
          print 'Send subbands %d to flag3-p0' % ((opts.xid + 1) % 20)
          print 'Send subbands %d to flag3-p1' % ((opts.xid + 2) % 20)
          print 'Send subbands %d to flag3-p2' % ((opts.xid + 3) % 20)
          print 'Send subbands %d to flag3-p3' % ((opts.xid + 4) % 20)
          fpga.write_int('part2_x_ip' + str((opts.xid + 0) % 20), paf0)
          fpga.write_int('part2_x_ip' + str((opts.xid + 1) % 20), flag3_p0)
          fpga.write_int('part2_x_ip' + str((opts.xid + 2) % 20), flag3_p1)
          fpga.write_int('part2_x_ip' + str((opts.xid + 3) % 20), flag3_p2)
          fpga.write_int('part2_x_ip' + str((opts.xid + 4) % 20), flag3_p3)
       else :
          print("Unknown destination computer therefore sending packets to the BlAcKhOlE\n");
          fpga.write_int('part2_x_ip'+str(opts.xid),blackhole)

       print '\n done'


    if (opts.arm):
       print 'Sending sync pulse \n'
       fpga.write_int('ARM',1)
       fpga.write_int('ARM',0)
       print 'done ... \n'

    if (opts.sbs_data):
       print 'Enabling output snapshots blocks \n'
       for k in range(4):
          fpga.write_int('lsb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
          fpga.write_int('lsb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,0)
          fpga.write_int('usb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
          fpga.write_int('usb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
 
       for k in range(4):
          fpga.write_int('lsb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,1) 
          fpga.write_int('lsb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,1)
          fpga.write_int('usb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,1) 
          fpga.write_int('usb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,1) 

       for k in range(4):
          fpga.write_int('lsb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
          fpga.write_int('lsb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,0)
          fpga.write_int('usb_re_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
          fpga.write_int('usb_im_'+str(k*2)+str(k*2+1)+'_ctrl',0,0) 
       
       time.sleep(0.5)
       get_data_sbs()
       print 'done \n'

    if (opts.time_data):
       print 'Reseting time domain brams'
       fpga.write_int('bram_we' ,0)
       fpga.write_int('bram_rst',1)
       fpga.write_int('bram_rst',0)
       fpga.write_int('bram_we' ,1)
       time.sleep(2)
       for i in range(8):
         get_data_iq(i)


    # Set ROACH "safety" switch to allow packets to be started and stopped
    if (opts.safety):
        print("FENGINE: Safety enabled for! %s" % roach)
        fpga.write_int('pkt_stop_en', 1)

    print 'done \n'

except KeyboardInterrupt:
  exit_clean()
except:
  exit_fail()

exit_clean()
