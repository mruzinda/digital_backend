######################################################################
#
#  player.py - A ZMQ server that controls the operations of a ROACH2.
#
#  Copyright (C) 2013 Associated Universities, Inc. Washington DC, USA.
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

import zmq
import ConfigParser
import inspect
import subprocess
import signal
import sys
import traceback
import time
import os
import socket
import numpy as np

from corr import katcp_wrapper
from datetime import datetime, timedelta
from ConfigData import ModeData, BankData, AutoVivification, _ip_string_to_int, _hostname_to_ip

# The backends:
#import Backend
#import VegasBackend
import VegasHBWBackend
import VegasL1LBWBackend
import VegasL8LBWBackend
import GuppiBackend
import GuppiCODDBackend
import BeamformerBackend

from ZMQJSONProxy import ZMQJSONProxyServer

import warnings
warnings.filterwarnings('ignore')

def print_doc(obj):
    print obj.__doc__

def datetime_to_tuple(dt):
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)

class Bank(object):
    """
    A roach bank manager class.
    """

    def __init__(self, bank_name = None, simulate = False):

        print "Player::Bank()"

        # Set up a dictionary of BackEnd Types. This will be used to
        # create the correct backend based on the MODENAME key in the
        # MODE sections of the configuration file:
        self.BET = {"h1k"           : VegasHBWBackend.VegasHBWBackend,
                    "h16k"          : VegasHBWBackend.VegasHBWBackend,
                    "l1/lbw1"       : VegasL1LBWBackend.VegasL1LBWBackend,
                    "l8/lbw1"       : VegasL8LBWBackend.VegasL8LBWBackend,
                    "l8/lbw8"       : VegasL8LBWBackend.VegasL8LBWBackend,
                    "guppi-inco"    : GuppiBackend.GuppiBackend,
                    "guppi-codd"    : GuppiCODDBackend.GuppiCODDBackend,
                    "hi_correlator"     : BeamformerBackend.BeamformerBackend,
                    "cal_correlator"    : BeamformerBackend.BeamformerBackend,
                    "frb_correlator"    : BeamformerBackend.BeamformerBackend,
                    "correlator_save"   : BeamformerBackend.BeamformerBackend,
                    "pulsar_beamformer" : BeamformerBackend.BeamformerBackend,
                    "flag_diagnostic"   : BeamformerBackend.BeamformerBackend,
                    "flag_pfb"          : BeamformerBackend.BeamformerBackend,
                    "flag_pfb_corr"     : BeamformerBackend.BeamformerBackend,
                    "flag_bx_mode"      : BeamformerBackend.BeamformerBackend,
                    "flag_xrfi_corr"    : BeamformerBackend.BeamformerBackend}


        self.dibas_dir = os.getenv('DIBAS_DIR')

        if self.dibas_dir == None:
            raise Exception("'DIBAS_DIR' is not set!")
        self.backend = None
        self.roach = None
        self.valon = None
        self.hpc_macs = {}
        self.simulate = simulate
        print "Player::Bank(): self.simulate=", self.simulate

        # Bank name may be provided, or if not will be inferred from the config file.
        self.bank_name = bank_name.upper() if bank_name else None
        self.bank_data = BankData()
        self.mode_data = {}
        self.banks = {}
        self.current_mode = None
        self.check_shared_memory()
        self.read_config_file(self.dibas_dir + '/etc/config/dibas.conf')
        self.scan_number = 1

        # This turns on the automatic reaping of dead child processes (anti-zombification)
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        #print "setting backend:"
        #self.backend = VegasBackend.Backend(self.bank_data, self.mode_data['MODE1'])

        #print "status mem: ", self.backend.get_status()

    def __del__(self):
        """
        Perform cleanup activities for a Bank object.
        """
        pass

    def check_shared_memory(self):
        """
        This method creates the status shared memory segment if necessary.
        If the segment exists, the state of the status memory is not modified.
        """
        if not self.simulate:
            os.system(self.dibas_dir + '/bin/init_status_memory')

    def clear_shared_memory(self):
        """
        This method clears the status shared memory segment if necessary.
        """
        pass
        #if not self.simulate:
            # os.system(self.dibas_dir + '/bin/x86_64-linux/check_vegas_status -C -I %d' % self.instance_id)
            # Command removed by RB 3/17/17 -- doesn't actually clear shared memory and just clutters the console with unnecessary output
        # print 'not cleaning status memory -- fix this'

        # Clear shared memory segments
        # command = "hashpipe_clean_shmem -I %d" % (self.instance_id)
        # ps_clean = subprocess.Popen(command.split())
        # ps_clean.wait()

    def reformat_data_buffers(self, mode):
        """
        Since the vegas and guppi HPC programs require different data buffer
        layouts, remove and re-create the databuffers as appropriate for the
        HPC program in use.
        """
        if self.simulate:
            return
        if self.current_mode is None:
            raise Exception( "No current mode is selected" )

        fmt_path = self.dibas_dir + '/bin/re_create_data_buffers'

        hpc_program = self.mode_data[self.current_mode].hpc_program
        if hpc_program is None:
            raise Exception("Configuration error: no field hpc_program specified in "
                            "MODE section of %s " % (self.current_mode))

        #mem_fmt_process = subprocess.Popen((fmt_path,hpc_program))
        print "reformatting data buffers"
        os.system(fmt_path + ' ' + hpc_program)

    def get_bank_name(self, config):
        """Dive into the config file and fetch the bank name based on the
        current host running this bank.

        """
        banks = [p for p in config.sections() if 'BANK' in p]
        host = socket.gethostname()

        for i in banks:
            hpchost = config.get(i, 'hpchost')
            # either 'host' or 'hpchost' or both should contain the base
            # host name ('hpc1', 'hpc2', etc.) Just in case an alternate
            # name is used by either (such as 'hpc1-1'), compare them
            # both ways.
            if host in hpchost or hpchost in host:
                return i.upper()

    def bank2inst(self, bank):
        """
        Converts either the string or char bank name to an integer
        'instance id' for use with hashpipe and shared memory.
        Ex: 'BANKC' -> 3
        Ex: 'D' -> 4
        """
        if len(bank) > 1:
            # BANKC -> C
            bank = bank[-1]
        return ord(bank) - ord('A')

    def read_config_file(self, filename):
        """
        read_config_file(filename)

        Reads the config file 'filename' and loads the values into data
        structures in memory. 'filename' should be a fully qualified
        filename. The config file contains a 'bank' section of interest to
        this bank; in addition, it contains any number of 'MODEX' sections,
        where 'X' is a mode name/number.
        """

        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open(filename))

            if not self.bank_name:
                self.bank_name = self.get_bank_name(config)

                if not self.bank_name:
                    sys.exit(0)

            bank = self.bank_name
            print "bank =", bank, "filename =", filename

            # Read general stuff:
            telescope = config.get('DEFAULTS', 'telescope').lstrip().rstrip().lstrip('"').rstrip('"')
            self.set_status(TELESCOP=telescope)

            # Read the HPC MAC addresses
            macs = config.items('HPCMACS')
            self.hpc_macs = {}

            for i in macs:
                key = _ip_string_to_int(_hostname_to_ip(i[0])) & 0xFF
                self.hpc_macs[key] = int(i[1], 16)

            # Get all bank data and store it. This is needed by any mode
            # where there is 1 ROACH and N Players & HPC programs
            banks = [s for s in config.sections() if 'BANK' in s]

            for bank in banks:
                b = BankData()
                b.load_config(config, bank)
                self.banks[bank] = b

            # Get config info on this bank's ROACH2. Normally there is 1
            # ROACH per Player/HPC node, so this is it.
            self.bank_data = self.banks[self.bank_name]
            self.instance_id = self.bank2inst(self.bank_name) #self.bank_data.instance_id

            # Get config info on all modes
            modes = [s for s in config.sections() if 'MODE' in s]

            for mode in modes:
                m = ModeData()

                try:
                    m.load_config(config, mode)
                except Exception, e:
                    if self.simulate:
                        pass
                    else:
                        raise e

                self.mode_data[mode] = m

        except ConfigParser.NoSectionError as e:
            print str(e)
            return str(e)

        # Now that all the configuration data is loaded, set up some
        # basic things: KATCP, Valon, etc.  Not all backends will
        # have/need katcp & valon, so it config data says no roach &
        # valon, these steps will not happen.
        self.valon = None
        self.roach = None

        if not self.simulate and self.bank_data.has_roach:
            self.roach = katcp_wrapper.FpgaClient(self.bank_data.katcp_ip,
                                                  self.bank_data.katcp_port,
                                                  timeout = 30.0)
            time.sleep(1) # It takes the KATCP interface a little while to get ready. It's used below
                          # by the Valon interface, so we must wait a little.

            # The Valon can be on this host ('local') or on the ROACH
            # ('katcp'), or None. Create accordingly.
            if self.bank_data.synth == 'local':
                import valon_synth
                self.valon = valon_synth.Synthesizer(self.bank_data.synth_port)
            elif self.bank_data.synth == 'katcp':
                from valon_katcp import ValonKATCP
                self.valon = ValonKATCP(self.roach, self.bank_data.synth_port)

            # Valon is now assumed to be working
            if self.valon:
                self.valon.set_ref_select(self.bank_data.synth_ref)
                self.valon.set_reference(self.bank_data.synth_ref_freq)
                self.valon.set_vco_range(0, *self.bank_data.synth_vco_range)
                self.valon.set_rf_level(0, self.bank_data.synth_rf_level)
                self.valon.set_options(0, *self.bank_data.synth_options)

            print "connecting to %s, port %i" % (self.bank_data.katcp_ip, self.bank_data.katcp_port)
        print self.bank_data
        return "config file loaded."

    def set_scan_number(self, num):
        """
        set_scan_number(scan_number)

        Sets the scan number to the value specified
        """
        self.scan_number = num
        self.set_status(SCANNUM=num)
        self.set_status(SCAN=num)

    def increment_scan_number(self):
        """
        increment_scan_number()

        Increments the current scan number
        """
        self.scan_number = self.scan_number+1
        self.set_scan_number(self.scan_number)

    def set_status(self, **kwargs):
        """
        set_status(self, **kwargs)

        Updates the values for the keys specified in the parameter list
        as keyword value pairs. So:

          set_status(PROJID='JUNK', OBS_MODE='HBW')

        would set those two parameters.
        """
        if self.backend is not None:
            self.backend.write_status(**kwargs)

    def get_status(self, keys = None):
        """
        get_status(keys=None)

        Returns the specified key's value, or the values of several
        keys, or the entire contents of the shared memory status buffer.

        'keys' == None: The entire buffer is returned, as a
        dictionary containing the key/value pairs.

        'keys' is a list of keys, which are strings: returns a dictionary
        containing the requested subset of key/value pairs.

        'keys' is a single string: a single value will be looked up and
        returned using 'keys' as the single key.
        """
        if self.backend is not None:
            return self.backend.get_status(keys)
        else:
            return None

    def list_modes(self):
        modes = self.mode_data.keys()
        modes.sort()
        return modes


    def set_cov_mode(self,n):

      if n == 1:

        string = 'HI'
        cmd = 'hashpipe_check_status -k COVMODE -s %s'% string
        print 'Writing mode into shared memory: %s' % cmd
        os.system(cmd)

      elif n == 2:
        string = 'PAF_CAL'
        cmd = 'hashpipe_check_status -k COVMODE -s %s' % string
        print 'Writing mode into shared memory: %s' % cmd
        os.system(cmd)

      elif n == 3:
        string = 'FRB'
        cmd = 'hashpipe_check_status -k COVMODE -s %s' % string
        print 'Writing mode into shared memory: %s' % cmd
        os.system(cmd)

      else:

        string = 'NONE'
        print 'Correct mode not found'
        cmd = 'hashpipe_check_status -k COVMODE -f %s' % string
        print 'Writing mode into shared memory: %s' % cmd
        os.system(cmd)




    def set_mode(self, mode, bandwidth = None, force = False):
        """set_mode(mode, bandwidth = None, force=False)

        Sets the operating mode for the roach.  Does this by programming
        the roach.

        *mode:*
          A string; A keyword which is one of the '[MODEX]'
          sections of the configuration file, which must have been loaded
          earlier.

        *bandwidth:*
          The valon bandwidth for this new mode. If not
          specified the last value used will be reused. If no value was
          ever provided the config file value will be used.

        *force:*
          A boolean flag; if 'True' and the new mode is the same as
          the current mode, the mode will be reloaded. It is set to
          'False' by default, in which case the new mode will not be
          reloaded if it is already the current mode.

        Returns a tuple consisting of (status, 'msg') where 'status' is
        a boolean, 'True' if the mode was loaded, 'False' otherwise; and
        'msg' explains the error if any.

        Example::

            s, msg = f.set_mode('MODE1') s, msg =
            f.set_mode(mode='MODE1', force=True)

        """
        frequency = bandwidth
        if mode:
            if mode in self.mode_data:
                if force or mode != self.current_mode or frequency != self.mode_data[mode].frequency:
                    self.check_shared_memory()
                    print "New mode specified and/or bandwidth specified!"
                    if self.current_mode:
                        old_hpc_program = self.mode_data[self.current_mode].hpc_program
                    else:
                        old_hpc_program = "none"

                    self.current_mode = mode
                    new_hpc_program = self.mode_data[mode].hpc_program

                    if(mode=='MODE42'):
                       self.set_cov_mode(1)
                    if(mode=='MODE44'):
                       self.set_cov_mode(2)
                    if(mode=='MODE45'):
                       self.set_cov_mode(3)

                    if old_hpc_program != new_hpc_program:
                    #if 0:
                        self.clear_shared_memory()
                        #self.reformat_data_buffers(mode)
                    else:
                        print 'Not reformatting buffers'

                    # The correct Backend type will be chosen from the
                    # dictionary of available Backend types self.BET,
                    # based on the MODENAME key in the MODE
                    # sections. The modes include VEGAS-style spectral
                    # modes, and GUPPI-style pulsar modes. The spectral
                    # modes are further divided into HBW and LBW modes,
                    # and the GUPPI modes into coherent dedispersion
                    # (CDD) and incoherent mode. CDD modes are
                    # characterised by having only 1 ROACH sending data
                    # to 8 different HPC servers. The ROACH has 8
                    # network adapters for the purpose. Because of the
                    # 1->8 arrangement, one of the Players is Master and
                    # programs the ROACH. The others set up everything
                    # except their ROACH; in fact the others deprogram
                    # their ROACH so that the IP addresses may be used
                    # in the one CDD ROACH.
                    #
                    # The other kind of mode has 1 ROACH -> 1 HPC
                    # server, so each Player programs its ROACH.

                    # based upon the mode's backend config setting, create the appropriate
                    # parameter calculator 'backend'
                    if self.backend is not None:
                        self.backend.cleanup()
                        print "set_mode(%s): cleaned up old backend." % mode
                        del(self.backend)
                        self.backend = None

                    # If 'frequency' is provided record in mode data
                    # for use and reuse if not subsequently
                    # provided. Initial value of mode data frequency
                    # is from config file.
                    if frequency:
                        self.mode_data[mode].frequency = frequency

                    # get backend type based on backend name: h1k, h16k, l1/lbw1, etc.
                    Backend = self.BET[self.mode_data[mode].backend_name.lower()]
                    print "set_mode(%s): Creating new %s" % (mode, Backend.__name__)
                    # instantiate our new backend:
                    self.backend = Backend(self.bank_data,
                                           self.mode_data[mode],
                                           self.roach,
                                           self.valon,
                                           self.hpc_macs,
                                           self.simulate)
                    print "set_mode(%s): beginning wait for DAQ program" % mode
                    self.backend._wait_for_status('DAQSTATE', 'stopped', timedelta(seconds=1))
                    print "set_mode(%s): wait for DAQ program ended." % mode

                    if self.simulate:
                        time.sleep(10) # make it realistic

                    return (True, 'New mode %s set!' % mode)
                else:
                    return (False, 'Mode %s is already set! Use \'force=True\' to force.' % mode)
            else:
                return (False, 'Mode %s is not supported.' % mode)
        else:
            return (False, "Mode is 'None', doing nothing.")

    def get_mode(self):
        """
        get_mode()

        Returns the current operating mode for the bank.
        """
        return self.current_mode

    def write_cmd(self,string):

        if self.backend:
           print string
           self.backend.hpc_cmd(string)
           self.backend.fits_writer_cmd(string)

        if string == 'QUIT':
            os.system('clean_ipc')

    def startin(self, inSecs, durSecs):
        "An alternative method for running a scan, only available for Beamformer backend."
        mode = self.get_mode()
        assert self.current_mode == mode
        print "Current mode is",self.current_mode
        if self.backend: # should modify to check equal to beamformerbackend type because other backends donn't have a startin function defined
            self.backend.startin(inSecs, durSecs)

    def start(self, starttime = None):
        """
        start(self, starttimeelf= None)

        starttime: a datetime object representing a start time, in UTC

        --OR--

        starttime: a tuple or list(for ease of JSON serialization) of
        datetime compatible values: (year, month, day, hour, minute,
        second, microsecond), UTC.

        Sets up the system for a measurement and kicks it off at the
        appropriate time, based on 'starttime'.  If 'starttime' is not
        on a PPS boundary it is bumped up to the next PPS boundary.  If
        'starttime' is not given, the earliest possible start time is
        used.

        start() may require a needed arm delay time, which is specified
        in every mode section of the configuration file as
        'needed_arm_delay'. During this delay it tells the HPC program
        to start its net, accum and disk threads, and waits for the HPC
        program to report that it is receiving data. It then calculates
        the time it needs to sleep until just after the penultimate PPS
        signal. At that time it wakes up and arms the ROACH. The ROACH
        should then send the initial packet at that time.

        If a start time is specified that cannot be met an Exception is
        thrown with a message stating the problem.
        """

        if self.backend:
       #     self.increment_scan_number()
            print starttime
            return self.backend.start(starttime)


    def monitor(self):
        """monitor(self)

        monitor() requests that the DAQ program go into monitor
        mode. This is handy for troubleshooting issues like no data. In
        monitor mode the DAQ's net thread starts receiving data but does
        not do anything with that data. However the thread's status may
        be read in the status memory: NETSTAT will say 'receiving' if
        packets are arriving, 'waiting' if not.

        """

        if self.backend:
            return self.backend.monitor()
        else:
            return (False, "No backend selected!")

    def stop(self):
        """
        Stops a running scan, by telling the current backend to stop.
        """

        if self.backend:
            return self.backend.stop()
        else:
            return (False, "No backend selected!")

    def scan_status(self):
        """
        scan_status(self):

        Returns the state of currently running scan. The return type is
        a tuple, backend dependent.
        """

        if self.backend:
            return self.backend.scan_status()
        else:
            return (False, "No backend selected!")


    def earliest_start(self):
        if self.backend:
            return (True, datetime_to_tuple(self.backend.earliest_start()))
        else:
            return (False, "No backend selected!")


    def set_param(self, **kvpairs):
        """
        A pass-thru method which conveys a backend specific parameter to the modes parameter engine.

        Example usage:
        set_param(exposure=x,switch_period=1.0, ...)
        """

        if self.backend is not None:
            for k,v in kvpairs.items():
                return self.backend.set_param(str(k), v)
        else:
            raise Exception("Cannot set parameters until a mode is selected")

    def help_param(self, name = None):
        """
        A pass-thru method which conveys a backend specific parameter to the modes parameter engine.

        Example usage::

          help_param(exposure)
        """

        if self.backend is not None:
            return self.backend.help_param(name)
        else:
            raise Exception("Cannot set parameters until a mode is selected")

    def get_param(self, name = None):
        """A pass-thru method which gets the values of a backend specific parameter.

        Example usage::

          get_param(exposure)

        """

        if self.backend is not None:
            return self.backend.get_param(name)
        else:
            raise Exception("Cannot get parameters until a mode is selected")


    def prepare(self):
        """
        Perform calculations for the current set of parameter settings
        """
        if self.backend is not None:
            self.backend.prepare()
        else:
            raise Exception("Cannot prepare until a mode is selected")

    def reset_roach(self):
        """
        reset_roach(self):

        Sends a sequence of commands to reset the ROACH. This is mode
        dependent and mode should have been specified in advance, as the
        sequence of commands is obtained from the 'MODEX' section of the
        configuration file.
        """

        if self.backend:
            self.backend.reset_roach()


    def arm_roach(self):
        """
        arm_roach(self):

        Sends a sequence of commands to arm the ROACH. This is mode
        dependent and mode should have been specified in advance, as the
        sequence of commands is obtained from the 'MODEX' section of the
        configuration file.
        """
        if self.backend:
            self.backend.arm_roach()

    def disarm_roach(self):
        """
        disarm_roach(self):

        Sends a sequence of commands to disarm the ROACH. This is mode
        dependent and mode should have been specified in advance, as the
        sequence of commands is obtained from the 'MODEX' section of the
        configuration file.
        """
        if self.backend:
            self.backend.disarm_roach()


    def clear_switching_states(self):
        """
        resets/deletes the switching_states (backend dependent)
        """
        if self.backend:
            return self.backend.clear_switching_states()
        else:
            raise Exception("Cannot clear switcvhing states until a mode has been selected")

    def add_switching_state(self, duration, blank = False, cal = False, sig_ref_1 = False):
        """add_switching_state(duration, blank, cal, sig):

        Add a description of one switching phase (backend dependent).

        *duration*
          the length of this phase in seconds,
        *blank*
          the state of the blanking signal (True = blank, False = no blank)
        *cal*
          the state of the cal signal (True = cal, False = no cal)
        *sig*
          the state of the sig_ref signal (True = ref, false = sig)

        Example to set up a 8 phase signal (4-phase if blanking is not
        considered) with blanking, cal, and sig/ref, total of 400 mS::

          be = Backend(None) # no real backend needed for example
          be.clear_switching_states()
          be.add_switching_state(0.01, blank = True, cal = True, sig = True)
          be.add_switching_state(0.09, cal = True, sig = True)
          be.add_switching_state(0.01, blank = True, cal = True)
          be.add_switching_state(0.09, cal = True)
          be.add_switching_state(0.01, blank = True, sig = True)
          be.add_switching_state(0.09, sig = True)
          be.add_switching_state(0.01, blank = True)
          be.add_switching_state(0.09)

        """
        if self.backend:
            return self.backend.add_switching_state(duration, blank, cal, sig_ref_1)
        else:
            raise Exception("Cannot add switching states until a mode has been selected.")

    def set_gbt_ss(self, period, ss_list):
        """set_gbt_ss(period, ss_list):

        adds a complete GBT style switching signal description.

        *period*
          The complete period length of the switching signal.
        *ss_list*
          A list of GBT phase components. Each component is a tuple:
          (phase_start, sig_ref, cal, blanking_time) There is one of
          these tuples per GBT style phase.

        Example::

            b.set_gbt_ss(period = 0.1,
                         ss_list = ((0.0, SWbits.SIG, SWbits.CALON, 0.025),
                                    (0.25, SWbits.SIG, SWbits.CALOFF, 0.025),
                                    (0.5, SWbits.REF, SWbits.CALON, 0.025),
                                    (0.75, SWbits.REF, SWbits.CALOFF, 0.025))
                        )

        """
        if self.backend:
            return self.backend.set_gbt_ss(period, ss_list)
        else:
            raise Exception("Cannot set switching states until a mode has been selected.")

    def _watchdog(self):
        """
        Looks at internal conditions every so often.
        """

        if self.backend:
             # Monitor scan status
            if self.backend.scan_running:
                now = datetime.utcnow()
                start = self.backend.start_time
                scanlength = self.backend.scan_length + 1

                if all((start, scanlength)):
                    sl = timedelta(seconds=scanlength)
                    rem = (start + sl) - now
                    # lets have a little scan countdown in status memory
                    self.set_status(SCANREM=rem.seconds - 1)

                    if now > start + sl:

                       print np.str(scanlength)
                       isDone = False
                       ctr = 0
                       while not isDone:
                           netStatus = self.get_status("NETSTAT")
                           if netStatus == "IDLE":
                               isDone = True
                           else:
                               time.sleep(.25)
                               ctr+=1

                           if ctr >= 20:
                               print "BFBE: Something froze???..."
                               isDone = True

                       self.stop()

                       self.set_status(SCANREM='scan terminated')


def _testCaseVegas1():

    # Not sure why I can't import SWbits from VegasBackend ???
    SIG=1
    REF=0
    CALON=1
    CALOFF=0

    b=Bank('BANKH')
    print "Setting Mode1"
    b.set_mode('MODE1')
    b.backend.set_switching_period(10.0)
    b.backend.add_switching_state(0.0,  SIG, CALON, 0.0)
    b.backend.add_switching_state(0.25, SIG, CALOFF, 0.0)
    b.backend.add_switching_state(0.5,  REF, CALON, 0.0)
    b.backend.add_switching_state(0.75, REF, CALOFF, 0.0)
    b.backend.prepare()


proxy = None

def main_loop(bank_name = None, URL = None, sim = False):
    # The proxy server, can proxy many classes.
    global proxy

    ctx = zmq.Context()

    if not URL:
        dibas_dir = os.getenv('DIBAS_DIR')

        if dibas_dir == None:
            raise Exception("'DIBAS_DIR' is not set!")

        config_file = dibas_dir + '/etc/config/dibas.conf'
        config = ConfigParser.ConfigParser()
        config.readfp(open(config_file))

        if bank_name:
            playerport = config.getint(bank_name.upper(), 'player_port')
        else:
            playerport = config.getint('DEFAULTS', 'player_port')
        URL = "tcp://0.0.0.0:%i" % playerport

    proxy = ZMQJSONProxyServer(ctx, URL)
    # A class to expose
    bank = Bank(bank_name, sim)
    # Expose some interfaces. The classes can be any class, including
    # contained within another exposed class. The name can be anything
    # at all that uniquely identifies the interface.
    proxy.expose("bank", bank)
    proxy.expose("bank.roach", bank.roach)
    proxy.expose("bank.valon", bank.valon)

    # Run the proxy:
    proxy.run_loop(bank._watchdog)


def signal_handler(signal, frame):
    global proxy
    proxy.quit_loop()

if __name__ == '__main__':
    sim = False
    url = None
    bank_name = None

    if len(sys.argv) > 3:
        bank_name = sys.argv[1]
        url = sys.argv[2]
        print "sys.argv[3] =", sys.argv[3]
        sim = True if str(sys.argv[3]) == "simulate" else False
    elif len(sys.argv) > 2:
        bank_name = sys.argv[1]
        url = sys.argv[2]
    elif len(sys.argv) > 1:
        bank_name = sys.argv[1]

    if len(sys.argv) > 0:
        signal.signal(signal.SIGINT, signal_handler)
        print "Player.py:: Main loop..."
        main_loop(bank_name, url, sim)
