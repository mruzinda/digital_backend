#! /usr/bin/env python
###############################################################
#
# one_punch_scan.py - A ZMQ pub client that listens to the
# ScanCoordinator to see what is being published.
#
# This differs from scan_overlord.py in that it receives any
# message that is published instead of filtering for particular
# keywords.
#
# The hope is that this code will be useful in seeing what
# information is being published by the ScanCoordinator
#
# Author: Richard Black (rallenblack@gmail.com)
#
###############################################################

#from ZMQJSONProxy import ZMQJSONProxyException
import zmq
from overlord_utils.DataStreamUtils import get_service_endpoints
from overlord_utils.PBDataDescriptor_pb2 import PBDataField
import sys

def main():
    # Initialize a ZMQ context
    ctx = zmq.Context()

    # Specify the URL for the ScanCoordinator
    # url = "tcp://gbtdata.gbt.nrao.edu:5559"
    url = "tcp://vegas-hpc10.gb.nrao.edu:5559"

    # Get a subscriber socket (ScanCoordinator is a publisher)
    subscriber = ctx.socket(zmq.SUB)

    # Get sub URL of ScanCoordinator publisher
    sub_url, _, _ = get_service_endpoints(ctx, url, 'ScanCoordinator', 'ScanCoordinator', 0)
    print sub_url

    # Connect
    subscriber.connect(sub_url)
    #subscriber.setsockopt(zmq.SUBSCRIBE, 'ScanCoordinator.ScanCoordinator:P:projectId')
    subscriber.setsockopt(zmq.SUBSCRIBE, '')

    # Constantly read from ScanCoordinator
    while True:
        try:
            topic, messagedata = subscriber.recv_multipart()
            print topic
            if 'cout' not in topic and 'scanRemaining' not in topic:
                print messagedata
                df = PBDataField()
                df.ParseFromString(messagedata)
                print df
        except KeyboardInterrupt:
            print "Closing gracefully..."
            subscriber.close()
            ctx.term
            sys.exit()


if __name__ == '__main__':
    main()
