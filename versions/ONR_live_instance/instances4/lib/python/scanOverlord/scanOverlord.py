#! /usr/bin/env python
######################################################################
#
#  auto_dealer.py - A ZMQ pub client that listens to the M&C system of
#  the GBT and responds to incoming values.
#
#  Copyright (C) 2015 Associated Universities, Inc. Washington DC, USA.
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

#import /users/rblack/bf/dibas/lib/python/dealer
import dealer
#from dealer_proxy import DealerProxy
from ZMQJSONProxy import ZMQJSONProxyException
#from /users/rblack/bf/dibas/lib/python/ZMQJSONProxy import ZMQJSONProxyException
import zmq
import sys

from overlord_utils.PBDataDescriptor_pb2 import PBDataField
from overlord_utils.DataStreamUtils import get_service_endpoints, get_every_parameter
from datetime import datetime, tzinfo, date, time, timedelta
import pytz
import FlagCommander
from time import sleep

class scanOverlord:

    def __init__(self, D=None, sim=True):
        self.D = D
        self.sim = sim

        # Initialize starttime
        startdate = datetime.utcnow().date()
        self.starttime = datetime(startdate.year, startdate.month, startdate.day)

    def goLive(self):
        """
        Configures the scanOverlord for live mode.
        This function must be called before startOverlord.
        """
        if not self.sim:
            print "OVERLORD: Already in live mode"
        else:
            self.sim = False
            print "OVERLORD: Entering live mode"

    def goSim(self):
        """
        Configures the scanOverlord for simulation mode.
        This function must be called before startOverlord.
        """
        if self.sim:
            print "OVERLORD: Already in simulation mode"
        else:
            self.sim = True
            print "OVERLORD: Entering simulation mode"

    def addDealer(self, D):
        """
        Connects a dealer instance to the scanOverlord
        """
        if D is None:
            print "OVERLORD: ERROR - dealer instance cannot be NoneType"
        self.D = D
        print "OVERLORD: Connected to new Dealer"
        self.D.list_active_players()

    def removeDealer(self):
        """
        Disconnects the dealer
        """
        self.D = None
    

    def starttime_callback(self,p):
        seconds = p.val_struct[0].val_struct[0].val_double[0]
        startdate = datetime.utcnow().date()
        self.starttime = datetime(startdate.year, startdate.month, startdate.day, tzinfo=pytz.utc) + timedelta(seconds=seconds)
    

    def state_callback(self,p):
        """This is called whenever scans are run on the GBT telescope. The GBT
        M&C system states transition to "Running" via "Comitted." This is
        thus a good state to look for to catch the system about to start a
        scan. Likewise, 'Stopping' or 'Aborting' is a a good indicator
        that a scan is coming to an end.
        """
        val = p.val_struct[0].val_string[0]



        if val == 'Activating':
            print "Activating..."

            fc = FlagCommander.FlagCommander(sim=self.sim)
            sleep(0.3)
            fc.executeQuery()

            if self.starttime.hour != 0 or self.starttime.minute != 0 or self.starttime.second != 0:
                tstamp = self.starttime.strftime("%Y_%m_%d_%H:%M:%S")
                print "   We're doing this at ", tstamp
                project_id = fc.query_result['data_dir']
                scan_length = fc.query_result['scan_length']
                print "   Setting PROJID to %s" %(project_id)
                if self.D:
                    self.D.set_status(PROJID = project_id)
                print "   Setting scan_length to %f" %(float(scan_length))
                if self.D:
                    self.D.set_param(scan_length = float(scan_length))
                print "   Issuing START to players"
                if self.D:
                    self.D.start(self.starttime)
        if val == 'Running':
            pass
        if val == 'Committed':
            pass
        elif val == "Stopping":
            print "Stopping"
        elif val == "Aborting":
            if self.D:
                self.D.stop()
            print "Aborting"

    def start_overlord(self):
        """
        Connects to the ScanCoordinator and begins listening for state changes.
        TBD: Make this a threaded process so this doesn't block.
        """
        keys = {"ScanCoordinator.ScanCoordinator:P:state": self.state_callback,
                "ScanCoordinator.ScanCoordinator:P:startTime": self.starttime_callback}
        ctx = zmq.Context()

        if not self.sim:
            # Real ScanCoordinator
            req_url = "tcp://gbtdata.gbt.nrao.edu:5559"
        else:
            # Simulator ScanCoordinator
            req_url = "tcp://vegas-hpc10.gb.nrao.edu:5559"

        subscriber = ctx.socket(zmq.SUB)

        for key in keys:
            print key

            major, minor = key.split(':')[0].split('.')
            print major, minor

            sub_url, _, _ = get_service_endpoints(ctx, req_url, major, minor, 0)
            print sub_url

            subscriber.connect(sub_url)
            subscriber.setsockopt(zmq.SUBSCRIBE, key)

    
        while True:
            key, payload = subscriber.recv_multipart()
            df = PBDataField()
            df.ParseFromString(payload)
            f = keys[key]

            try:
                f(df)
            except ZMQJSONProxyException, e:
                print "Caught exception from Dealer", e
            except KeyboardInterrupt:
                print "OVERLORD: Closing gracefully..."
                subscriber.close()
                ctx.term()
                sys.exit()

#if __name__ == '__main__':
    #if len(sys.argv) < 2:
    #    print "Need a URL to the Dealer daemon"
    #else:
    #    url = sys.argv[1]
    #    main(url)
    #main(sim=True, has_dealer=False)
