######################################################################
#
#  BeamformerBackend.py -- Instance class for the DIBAS Vegas
#  modes. Derives Vegas mode functionality from VegasBackend, adding
#  only HBW specific functionality, and I/O with the roach and with the
#  status shared memory.
#
#  Copyright (C) 2014 Associated Universities, Inc. Washington DC, USA.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Correspondence concerning GBT software should be addressed as follows:
#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
######################################################################

import time
import shlex
import subprocess
import os
from datetime import datetime, timedelta
import calendar

from Backend import Backend

#from f_engine_config.helper_functions import *
from f_engine_config.RoachDoctor import RoachDoctor

import ConfigParser # We have additional parameters that are in the config file
from config.DibasParser import DibasParser
from flag_pole import FlagPole # flag shmem handle

# for bit/byte lock
import nb_util as nb

class BeamformerBackend(Backend):
#class BeamformerBackend(VegasBackend):
    """A class which implements the FLAG Beamformer functionality. 
    and which communicates with the roach and with the HPC programs via
    shared memory.

    BeamformerBackend(theBank, theMode, theRoach = None, theValon = None)

    Where:

    * *theBank:* Instance of specific bank configuration data BankData.
    * *theMode:* Instance of specific mode configuration data ModeData.
    * *theRoach:* Instance of katcp_wrapper
    * *theValon:* instance of ValonKATCP
    * *unit_test:* Set to true to unit test. Will not attempt to talk to
      roach, shared memory, etc.

    """

    def __init__(self, theBank, theMode, theRoach, theValon, hpc_macs, unit_test = False, instance_id = None):
        """
        Creates an instance of BeamformerBackend
        """
        self.name = theMode.backend_name.lower()
        self.current_mode = theMode.name
        self.bank_name = theBank.name.upper()

        # Read in the additional parameters from the configuration file
        #config_file = './dibas.conf'
        config_file = os.getenv("DIBAS_DIR") + '/etc/config/dibas.conf'
        dibas_parser = DibasParser(dibas_conf_file=config_file)
        dibas_info = dibas_parser.get_dibas_info()

        self.roaches = []
        self.configures_roaches = False
        self.RD = None

        roach_names = dibas_info['roaches']
        if theBank.name == dibas_info['isDoctor']:
            self.RD = RoachDoctor(roach_host_list=roach_names, dibas_info=dibas_info)
            self.configures_roaches = True
            self.roaches = self.RD.get_roaches()
            self.RD.configure(fft_shift=0xffffffff, quan_gain=0x0000000a)

        self.read_parameters(theBank, theMode)

        # init the super, clear shmem and init shmem
        Backend.__init__(self, theBank, theMode, theRoach, theValon, hpc_macs, unit_test)
        self.clear_shared_memory()
        self.status = FlagPole(instance_id=self.instance)

        # Set some default parameter values
        self.requested_weight_file = ''
        self.weifile_new = ''
        self.requested_channel = 0
        self.requested_integration_time = 1.0

        self.fits_writer_process = None

        # Add additional dealer-controlled parameters
        self.params["int_length"] = self.setIntegrationTime
        self.params["weight_file"] = self.setNewWeightFilename
        self.params["channel_select"] = self.setChannel

        # TODO: will we need use roach_kvpairs
        if self.mode.roach_kvpairs:
            self.write_registers(**self.mode.roach_kvpairs)

        # TODO: will we need to use reset_roach - this is defined in diabs.conf, a sequence of commands to execute
        #self.reset_roach()

        self.prepare()

        # super class backend says this is backend dependent and I dont think our backend needs this
        #self.clear_switching_states()
        #self.add_switching_state(1.0, blank = False, cal = False, sig_ref_1 = False)
        self.start_hpc()

        self.fits_writer_program = self.fits_writer_program_bf
        self.start_fits_writer()

    def setIntegrationTime(self, int_time):
        """
        Sets the integration time for each integration.
        """
        self.requested_integration_time = int_time

    def setNewWeightFilename(self, weights):
        """
        Sets the file containing the weights
        
        Assumes the file is submited as "weight_file_name.ext", The function will then separate the name and 
        extension in order to append the bank letter at the end of the file and then reapply the extension such
        that the file is now "weight_file_name[LETTER].ext"
        
        """

        flist = weights.split('.')
        name = flist[0]
        ext = flist[1]
        f = name + (self.bank_name[-1]).upper() + "." + ext
        self.requested_weight_file = f

    def setChannel(self, channel):
        """
        This method is available to the user to select a block of 5 contiguous coarse channels for fine filter bank processing.
        @param channel - int - [0,4]
                0 --> channels 0-4
                1 --> channels 5-9
                2 --> channels 10-14
                3 --> channels 15-19
                4 --> channels 20-24

        If the selected channels is outside the range [0,4] prints an error to the user and retains the current channel select value.
        """

        if channel >= 0 and channel <=4:
            self.requested_channel = channel
        else:
            print("ERROR: Invalid channel selection. Valid values are in the range [0,4].")
            print("\tUsing %i as the selected channel." % self.requested_channel)
        return

    def earliest_start(self):
        # Get the current time
        now = datetime.utcnow()

        # Add the needed arming time to get earliest possible start time
        earliest_start = self.round_second_up(now) + self.mode.needed_arm_delay
        return earliest_start

    def read_parameters(self, theBank, theMode):
        # Quick little process to convert IP addresses from raw integer values
        int2ip  = lambda n: '.'.join([str(n >> (i << 3) & 0xFF) for i in range(0,4)[::-1]])

        bank = theBank.name
        mode = theMode.name
        dibas_dir = os.getenv('DIBAS_DIR') # Should always succeed since player started up

        # Create a quick ConfigParser to parse the extra information in dibas.conf
        config = ConfigParser.ConfigParser()
        filename = dibas_dir + '/etc/config/dibas.conf'
        config.readfp(open(filename))
        # Extract the XID
        self.xid = config.getint(bank, 'xid')
        # Extract the Hashpipe instance number
        self.instance = config.getint(bank, 'instance')
        # Extract the GPU device index
        self.gpudev = config.getint(bank, 'gpudev')
        # Extract the list of cpu cores on which to run the threads
        self.cpus = config.get(bank, 'cpus')
        self.core = [int(x) for x in self.cpus.split(',') if x.strip().isdigit()]

        if mode.lower() == "flag_rtbf_mode":
            self.weightdir = config.get(mode, "WEIGHTD") 
        if mode.lower() == "flag_pfb_mode" or mode.lower() == "flag_pfbcorr_mode":
            self.coeffdir = config.get(mode, "COEFFDIR")

        # Get the 10 GbE BINDHOST and BINDPORT for this player
        self.bindhost = int2ip(theBank.dest_ip)
        self.bindport = theBank.dest_port

        # Get the FITS writer process name
        self.fits_writer_program_bf = config.get(mode, 'fits_process')
        # Get sim3 flag
        self.sim3 = config.getint(mode, 'sim3')
  
    def start(self, starttime = None):
        """
        Method that arms the ROACH boards and starts the acquisition process in flag_gpu
        Overloads the start method in VegasBackend.py
        """

        # Check to see if a scan is already running...
        if self.scan_running:
            print "BFBE: Scan already running..."
            return (False, "Scan already started.")


        # Process the starttime argument
        if starttime:
            if type(starttime) == tuple or type(starttime) == list: # Type check
                starttime = datetime(*starttime) # Convert to datetime object

            if type(starttime) != datetime: # If not a datetime object by here, throw exception
                raise Exception("starttime must be a datetime object or datetime compatible tuple or list.")

            # Make the starttime be on the next 1-second boundary
            starttime = self.round_second_up(starttime)

            now = datetime.utcnow()
            earliest_start = self.earliest_start()

            # Check to see if the required arming time puts us past the desired start time
            if starttime < earliest_start: # BAD-- desired time too close to be ready in time
                raise Exception("Not enough time to arm ROACHs. Start: %s, earliest possible start: %s" % (str(starttime), str(earliest_start)))

        else:
            starttime = earliest_start

        # Set the start time in the system
        self.start_time = starttime
        # Convert datetime to seconds from start of epoch
        t = calendar.timegm(starttime.timetuple())
        # Convert seconds to day-month julian date
        startDMJD = self.secs_2_dmjd(t)
        tstamp = starttime.strftime("%Y_%m_%d_%H:%M:%S")
        # Write the start time/scan length to shared memory for the FITS writer
        # Write day-month julian date and scan length to shared memory
        # Note that self.scan_length can be modified, for example, by using
        #     dealer.set_param(scan_length=2.0)
        # If not set prior to running start(), this will default to 30.0
        self.write_status(STRTDMJD=str(startDMJD), SCANLEN=str(self.scan_length))
        self.write_status(TSTAMP=str(tstamp))
        print "BFBE: TSTAMP ", str(tstamp)
        # Write the integration length to shared memory
        self.write_status(REQSTI=str(self.requested_integration_time))

        # MCB -- Modified the write_status function to allow writing int/str/bool need to type cast the value as in input.
        # Set weight flag to default value of 0
        #self.write_status(WFLAG=str(0))
        #self.write_status(WFLAG=0)
        self.write_status(WFLAG=False)


        # Write the beamformer weight filename to shared memory
        self.write_status(BWEIFILE=str(self.requested_weight_file))

        # Write the nchunk to shared memory
        print "BFBE: Writing CHANSEL=%d" %(self.requested_channel)
        self.write_status(CHANSEL=str(self.requested_channel))

        self.weifile_old = self.weifile_new
        self.weifile_new = self.get_status('BWEIFILE')

        if self.weifile_old is self.weifile_new:
            print "BFBE: Weight file name unchanged."
            #self.write_status(WFLAG=str(0))
            #self.write_status(WFLAG=0)
            self.write_status(WFLAG=False)
        else:
            print "BFBE: Weight file name changed."
            #self.write_status(WFLAG=str(1))
            #self.write_status(WFLAG=1)
            self.write_status(WFLAG=True)

        # Print out this information
        print "BFBE: ", now, starttime

        # Check if everything is up and running
        if self.hpc_process is None:
            print "BFBE: HPC process not running... Starting HPC process..."
            self.start_hpc()
        if self.fits_writer_process is None:
            print "BFBE: Fits writer not running... Starting Fits writer process..."
            self.start_fits_writer()

        # Send start commands to HPC and FITS writer processes
        # NOTE: this does not start any timers or set any time stamps
        #       this only forces the processes to move from IDLE states to ACQUIRE states
        self.hpc_cmd('START')
        self.fits_writer_cmd('START')

        # Let arming time occur immediately after penultimate 1 PPS
        arm_time = starttime - timedelta(microseconds = 900000) # starttime - 0.9 seconds

        # Get current time to compare against
        now = datetime.utcnow()

        # Check to see if we are too late to arm
        if now > arm_time:
            self.hpc_cmd('STOP')
            self.fits_writer_cmd('STOP')
            raise Exception("BFBE: start():: deadline missed, arm time is in the past.")

        # Get amount of waiting time
        tdelta = arm_time - now

        # Set the sleep time
        sleep_time = tdelta.seconds + tdelta.microseconds / 1e6

        print "BFBE: Sleeping for %f seconds..." %(sleep_time)
        time.sleep(sleep_time)

        # Wake up and get to work!
        # We should be within a second of the specified start time
        self.arm_roach()
        # Begin watchdog timer countdown
        self.scan_running = True
        # Write... something to shared memory for some reason...
        #self.write_status(ACCBLKOU='-')

        # End function so new commands can be processed if necessary
        return (True, "BFBE: Successfully started ROACH for starttime=%s" %(str(self.start_time)))

    def startin(self, inSecs, durSecs):

        """
        This method retains the 'interactive dealer' ability to issue a start from within
        a specified time and the duration of the scan.
        """

        self.scan_length = durSecs

        dt = datetime.utcnow()
        dt.replace(second=0)
        dt.replace(microsecond=0)
        dt += timedelta(seconds=inSecs)
        self.start(starttime=dt)

    def start_old(self, inSecs, durSecs):

        """
        Start a scan in inSecs for durSecs long
        Now deprecated (Richard Black), use def start(self, starttime) instead
        """

        # our fake GPU simulator needs to know the start time of the scan
        # and it's duration, so we need to write it to status shared mem.
        def secs_2_dmjd(secs):
            dmjd = (secs/86400) + 40587
            return dmjd + ((secs % 86400)/86400.)

        inSecs = inSecs if inSecs is not None else 5
        durSecs = durSecs if durSecs is not None else 5
        print "self.scan_length= %f" % (self.scan_length)
        self.scan_length = durSecs
        print "self.scan_length after = %f" %  (self.scan_length)

        # TBF: we've done our stuff w/ DMJD, but our start is a utc datetime obj
        now = time.time()
        startDMJD = secs_2_dmjd(int(now + inSecs))

        # NOTE: SCANLEN can also be set w/ player.set_param(scan_length=#)
        self.write_status(STRTDMJD=str(startDMJD),SCANLEN=str(durSecs))
        self.write_status(REQSTI=str(self.requested_integration_time))
        self.write_status(BWEIFILE=str(self.requested_weight_file))
        self.write_status(CHANSEL=str(self.requested_channel))

        self.weifile_old = self.weifile_new
        self.weifile_new = self.get_status('BWEIFILE')

        if self.weifile_old is self.weifile_new:

            print "Weight file name unchanged."
            # MCB -- Modified the write_status function to allow writing int/str/bool need to type cast the value as in input.
            #self.write_status(WFLAG=str(0))
            #self.write_status(WFLAG=int(0))
            self.write_status(WFLAG=False)
        else:
            print "Weight file name changed."
            #self.write_status(WFLAG=str(1))
            #self.write_status(WFLAG=int(1))
            self.write_status(WFLAG=True)

        dt = datetime.utcnow()
        dt.replace(second = 0)
        dt.replace(microsecond = 0)
        dt += timedelta(seconds = inSecs)

        BeamformerBackend.start(self, starttime=dt)
        #print "In Vegas Backend!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        #print "Vegas self.scan_length after = %f" %  (self.scan_length)
        #VegasBackend.start(self, starttime = dt)
        #print "Vegas self.scan_length after = %f" %  (self.scan_length)
        #print "Out of Vegas Backend!!!!!!!!!!!!!!!!!!!!!"

    # prepare() for this class calls the base class prepare then does
    # the bare minimum required just for this backend, and then writes
    # to hardware, HPC, shared memory, etc.
    def prepare(self):
        """
        This command writes calculated values to the hardware and status memory.
        This command should be run prior to the first scan to properly setup
        the hardware.

        The sequence of commands to set up a measurement is thus typically::

          be.set_param(...)
          be.set_param(...)
          ...
          be.set_param(...)
          be.prepare()
        """

        # Dont really want to call vegas (Beamformers current super) prepare method should call the Backend parent
        # class at a minimum however I am not sure we use it in flag. So to do this we need to get rid of the
        # vegas dependency
        # super(BeamformerBackend, self).prepare()

        self.write_status(BANKNAM=self.bank_name[-1])

        bblock = False
        # perform bit/byte lock
        if bblock:
            if self.roaches:
                # Connect and turn noise on
                nb.connect()
                nb.send_recv('ps0')
                time.sleep(2)

                self.arm_roach()

                nb.set_rf_switch('NS')
                time.sleep(15)

                # bit lock
                for roach in self.roaches:
                    self.RD.bit_lock(fpga=roach)

                nb.set_rf_switch('TT')
                time.sleep(15)

                # byte lock
                for roach in self.roaches:
                    self.RD.byte_lock(fpga=roach, check=False)

                # # check byte lock
                # for roach in self.roaches:
                #     self.RD.byte_lock(fpga=roach, check=True)
                #
                # turn noise source off
                nb.set_rf_switch('OFF')
                # turn blades off?
                #nb.send_recv('ps1')
                nb.NB.close()

        # Talk to outside things: status memory, HPC programs, roach
        if self.bank is not None:
            self.write_status(**self.status_mem_local)
        else:
            for i in self.status_mem_local.keys():
                print "%s = %s" % (i, self.status_mem_local[i])

        if self.roach:
            self.write_registers(**self.roach_registers_local)

    # _set_state_table_keywords() overrides the parent version, but
    # should call the parent version first thing, as it will build on
    # what the parent function does. Since the parent class prepare()
    # calls this, no need to call this from this Backend's prepare.
    def _set_state_table_keywords(self):
        """
        Gather status sets here
        Not yet sure what to place here...
        """

        super(BeamformerBackend, self)._set_state_table_keywords()
        self.set_status(BW_MODE = "high")
        self.set_status(OBS_MODE = "HBW")

    def set_instance_id(self, instance_id):
        self.instance_id = instance_id

    def start_hpc(self):
        """
        Beamformer mode's are hashpipe plugins that require special handling:
           * are not in the dibas install area
           * need to pass on the instance id
        """

        if self.test_mode:
            return

        self.stop_hpc()

        # Get hashpipe command (specified by configuration file)
        hpc_program = self.mode.hpc_program
        if hpc_program is None:
            raise Exception("Configuration error: no field hpc_program specified in "
                            "MODE section of %s " % (self.current_mode))

        # Create command to start process
        process_list = []
        # process_list = "sudo nice -n -20 sudo -u rablack".split()
        process_list = process_list + hpc_program.split()

        # Add flags specified by configuration file
        if self.mode.hpc_program_flags:
            process_list = process_list + self.mode.hpc_program_flags.split()

        # Add Instance ID
        inst_str = "-I " + str(self.instance)
        process_list = process_list + inst_str.split()

        # Add BINDHOST
        host_str = "-o BINDHOST=" + str(self.bindhost)
        process_list = process_list + host_str.split()

        # Add BINDPORT
        port_str = "-o BINDPORT=" + str(self.bindport)
        process_list = process_list + port_str.split()

        # Add XID
        xid_str = "-o XID=" + str(self.xid)
        process_list = process_list + xid_str.split()

        # Add GPUDEV
        gpu_str = "-o GPUDEV=" + str(self.gpudev)
        process_list = process_list + gpu_str.split()

        # Add DATADIR
        dir_str = "-o DATADIR=" + str(self.datadir)
        process_list = process_list + dir_str.split()

        # Add PROJID
        proj_str = "-o PROJID=TMP"
        #proj_str = "-o PROJID=."
        process_list = process_list + proj_str.split()

        # Add MODENAME
        mode_name = "-o MODENAME=" + str(self.current_mode)
        process_list = process_list + mode_name.split()

        # Mode-specific thread layout
        if self.name == "hi_correlator":
            # Add mode specifier for FITS writers
            mode_str = "-o COVMODE=HI"
            process_list = process_list + mode_str.split()
            # Add threads
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_transpose_thread" % (self.core[1])
            thread3 = "-c %d flag_correlator_thread" % (self.core[2])
          #  thread4 = "-c %d flag_corsave_thread" % (self.core[3])
            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            process_list = process_list + thread3.split()
           # process_list = process_list + thread4.split()
        elif self.name == "cal_correlator":
            # Add mode specifier for FITS writers
            mode_str = "-o COVMODE=PAF_CAL"
            process_list = process_list + mode_str.split()
            # Add threads
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_transpose_thread" % (self.core[1])
            thread3 = "-c %d flag_correlator_thread" % (self.core[2])
            #thread4 = "-c %d flag_corsave_thread" % (self.core[3])
            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            process_list = process_list + thread3.split()
            #process_list = process_list + thread4.split()
        elif self.name == "correlator_save":
            # Add threads
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_transpose_thread" % (self.core[1])
            thread3 = "-c %d flag_correlator_thread" % (self.core[2])
            #thread4 = "-c %d flag_corsave_thread" % (self.core[3])
            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            process_list = process_list + thread3.split()
            #process_list = process_list + thread4.split()
        if self.name == "frb_correlator":
            # Add mode specifier for FITS writers
            mode_str = "-o COVMODE=FRB"
            process_list = process_list + mode_str.split()
            # Add threads
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_frb_transpose_thread" % (self.core[1])
            thread3 = "-c %d flag_frb_correlator_thread" % (self.core[2])
            thread4 = "-c %d flag_frb_corsave_thread" % (self.core[3])
            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            process_list = process_list + thread3.split()
            #process_list = process_list + thread4.split()
        elif self.name == "pulsar_beamformer":

            # Set weight directory
            weightdir_str = "-o WEIGHTD=" + str(self.weightdir)
            process_list = process_list + weightdir_str.split()
            # Add threads

            # GPU Transpose plugin
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_transpose_beamform_thread" % (self.core[2])

            # CPU Transpose plugin w/ trasponse thread assigned across cores.
            # thread1 = "-c %d flag_net_thread" % (self.core[0])
            # thread2 = "-c %d flag_transpose_thread" % (self.core[1])
            # if not (self.instance % 2):
            #     thread2 = "-c %d flag_transpose_thread" % (self.core[1])
            # else:
            #     thread2 = "-c %d flag_transpose_thread" % (self.core[3])

            #thread3 = "-c %d flag_beamform_thread" % (self.core[2])

            # Save thread
            #thread4 = "-c %d flag_beamsave_thread" % (self.core[3])

            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            #process_list = process_list + thread3.split()
            #process_list = process_list + thread4.split()
        elif self.name == "flag_total_power":
            # Add threads
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_transpose_thread" % (self.core[1])
            thread3 = "-c %d flag_power_thread" % (self.core[2])
            thread4 = "-c %d flag_powersave_thread" % (self.core[3])
            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            process_list = process_list + thread3.split()
            process_list = process_list + thread4.split()
        elif self.name == "flag_bx_mode":
            # Add threads
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_bx_transpose_thread" % (self.core[1])
            thread3 = "-c %d flag_bx_thread" % (self.core[2])
            #thread4 = "-c %d flag_bx_save_thread" % (self.core[3])
            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            process_list = process_list + thread3.split()
            #process_list = process_list + thread4.split()
        elif self.name == "flag_pfb":
            # Set COEFFDIR
            coeffdir_str = "-o COEFFDIR=" + str(self.coeffdir)
            process_list = process_list + coeffdir_str.split()
            # Add threads
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_pfb_transpose_thread" % (self.core[1])
            thread3 = "-c %d flag_pfb_thread" % (self.core[2])
            #thread4 = "-c %d flag_pfbsave_thread" % (self.core[3])
            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            process_list = process_list + thread3.split()
            #process_list = process_list + thread4.split()
        elif self.name == "flag_pfb_corr":
            # Set COEFFDIR
            coeffdir_str = "-o COEFFDIR=" + str(self.coeffdir)
            process_list = process_list + coeffdir_str.split()
            # Add threads
            thread1 = "-c %d flag_net_thread" % (self.core[0])
            thread2 = "-c %d flag_pfb_transpose_thread" % (self.core[1])
            thread3 = "-c %d flag_pfb_thread" % (self.core[2])
            thread4 = "-c %d flag_pfb_correlator_thread" % (self.core[3])
            #thread5 = "-c %d flag_pfb_corsave_thread" % (self.core[1])
            process_list = process_list + thread1.split()
            process_list = process_list + thread2.split()
            process_list = process_list + thread3.split()
            process_list = process_list + thread4.split()
            #process_list = process_list + thread5.split()
            

        print ' '.join(process_list)
        self.hpc_process = subprocess.Popen(process_list, stdin=subprocess.PIPE)

        # Logic to ensure that the process is indeed finished starting
        time.sleep(10)

    def stop(self):
        """
        Stops a scan and the FITS writer. Immediately restart FITS writer for the next scan
        """

        if not self.scan_running:
            return (False, "BFBE: No scan running!")

        if self.scan_running:
            self.hpc_cmd('stop')
            self.fits_writer_cmd('stop')
            self.scan_running = False
            self.write_status(DISKSTAT='-')

        # stop data flow from roaches
        if self.configures_roaches:
            for roach in self.roaches:
                print "BFBE: Stop data flow for roach %s" % roach.host
                roach.write_int('pkt_stop', 1)
                time.sleep(.1)
                roach.write_int('pkt_stop', 0)


        self.start_fits_writer()

    def clear_shared_memory(self):
        """
        Clears status shared memory.
        
        This was originally done in player.py in set_mode(). It has been commented out. Looking through 
        the various parent classes, Vegas, Guppi and Backend, the shared memory status and
        setups have been different and there doesn't seem to be one way to deal with shared memory.
        If there is a universal command to be used this could be done in player. Otherwise the backends
        should do this.
        """

        # Clear shared memory segments
        command = "hashpipe_clean_shmem -I %d" % (self.instance)
        ps_clean = subprocess.Popen(command.split())
        ps_clean.wait()

    
    ######################################################
    # FITS writer functions
    ######################################################

    # Create a simple helper function
    def secs_2_dmjd(self, secs):
        dmjd = (secs / 86400) + 40587
        return dmjd + ((secs % 86400) / 86400.)

    def fits_writer_cmd(self, cmd):
        """
        Opens the named pipe to the fits_writer_cmd program, sends 'cmd', and closes
        the pipe. Takes care not to block on an unconnected fifo.
        """
        if self.test_mode:
            return

        if self.fits_writer_process is None:
            raise Exception( "Fits writer program has not been started" )

        fh=self.fits_writer_process.stdin.fileno()
        os.write(fh, cmd + '\n')

        return True

    def start_fits_writer(self):
        """
        start_fits_writer()
        Starts the fits writer program running. Stops any previously running instance.
        For the beamformer, we have to pass on the instance id.
        """

        if self.test_mode:
            return

        self.stop_fits_writer()

        cmd = self.dibas_dir + '/exec/x86_64-linux/' + self.fits_writer_program
        ## added by N. Pingel on 07/23/17 to test FITS writer memory leak issues.
        ## runs memCheck in valgrind in concurrence with FITS writer
        #cmd = "valgrind --leak-check=full --show-reachable=yes --log-file='/users/npingel/FLAG/misc/memStats/memCheck.log' " + self.dibas_dir + '/exec/x86_64-linux/' + self.fits_writer_program
        cmd += " -i %d" % self.instance
        if self.name == 'hi_correlator':
            cmd += " -m s"
        if self.name == 'flag_pfb_corr':
            cmd += " -m s"
        if self.name == 'cal_correlator':
            cmd += " -m c"
        if self.name == 'frb_correlator':
            cmd += " -m f"
        if self.name == 'pulsar_beamformer':
            cmd += " -m p"
            # GPU Transpose -- puts FITS writer on unique cores.
            if not (self.instance % 2):
                cmd += " -c %d" % self.core[1]
            else:
                cmd += " -c %d" % self.core[3]
            
            # CPU Transpose -- puts the FITS writer on the net thread core for the.
            # cmd += " -c %d" % self.core[0]

        print "BFBE: Command to fits writer >> %s" % cmd
        process_list = shlex.split(cmd)
        self.fits_writer_process = subprocess.Popen(process_list, stdin=subprocess.PIPE)

    def stop_fits_writer(self):
        """
        stop_fits_writer()
        Stops the fits writer program and make it exit.
        To stop an observation use 'stop()' instead.
        @author Mark Ruzindana
        """

        if self.test_mode:
            return

        if self.fits_writer_process is None:
            return False # Nothing to do

        try:
            # First ask nicely
            self.fits_writer_process.communicate("quit\n")
            time.sleep(1)
            # Kill if necessary
            if self.fits_writer_process.poll() == None:
                # still running, try once more
                self.fits_writer_process.terminate()
                time.sleep(1)

                if self.fits_writer_process.poll() is not None:
                    killed = True
                else:
                    self.fits_writer_process.kill()
                    killed = True
            else:
                killed = False
            # this was commented out??? if something with fits breaks check here
            self.fits_writer_process = None
        except OSError, e:
            print "While killing child process:", e
            killed = False
        finally:
            del self.fits_writer_process
            self.fits_writer_process = None

        return killed

    def arm_roach(self):

        if self.configures_roaches:
            print "BFBE: Arming Roaches..."
            for roach in self.roaches:
                print "BFPBE: Sending sync pule to %s" % roach.host
                roach.write_int('ARM', 1)

            for roach in self.roaches:
                roach.write_int('ARM', 0)

        # elif self.roach:
            #print "BFBE: Arming this banks roach..."
        #   super(BeamformerBackend, self).arm_roach()

        







