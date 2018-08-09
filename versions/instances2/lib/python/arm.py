#!/opt/local/bin/python2.7

#import corr, time, struct, sys, logging, socket
import corr, time, struct, sys, logging, socket

if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser()
    p.set_usage('arm.py ROACH_NUMBERs -s offset_in_sec [roach_numbers are 1,2,3,4,5]')
    p.set_description(__doc__)
    p.add_option('-s'  , '--sec_offset', dest='offset', type = 'int', default=5, 
         help='Arm after specified offset in sec')

    opts, args = p.parse_args(sys.argv[1:])

    R2s = ['flagr2-1', 'flagr2-2', 'flagr2-3', 'flagr2-4', 'flagr2-5']
    fpgacnt=0;
    fpga=[]
    for scnt in args:
       cnt = int(scnt) - 1;
       roach = R2s[cnt];
       print('Connecting to server %s... \n'%(roach)),
       fpga.append(corr.katcp_wrapper.FpgaClient(roach))
       time.sleep(0.2)

       if fpga[fpgacnt].is_connected():
          print 'ok\n'
       else:
          print 'ERROR connecting to server %s.\n'%(roach)
          try:
              fpga[fpgacnt].stop()
          except: 
              pass
          exit()
       fpgacnt += 1

    for f in fpga: 
      f.write_int('ARM',0)

    now_sec = time.mktime(time.gmtime())
    gmt = time.gmtime()
    start_sec = time.mktime((gmt[0], gmt[1], gmt[2], gmt[3],
                             gmt[4], gmt[5]+opts.offset, gmt[6], gmt[7], 0))
    while start_sec > now_sec :
       now_sec = time.mktime(time.gmtime())
       print 'start_sec:', start_sec,'now_sec:', now_sec
       time.sleep(0.25)

    for f in fpga: 
      print 'Sending sync pulse \n'
      f.write_int('ARM',1)

    for f in fpga: 
      f.write_int('ARM',0)
      print 'done ... \n'
      try:
        f.stop()
      except: 
        pass

    exit()



