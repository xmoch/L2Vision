#!/usr/bin/env python
#
# Launch
# by zdev
#
# Once you run this script, a web server will be available via localhost
# and via any IP addresses you have configured for the machine on the given
# port (defaults to 8000 if not specified).
#
# Command Line:
#
#   python Launch.py [portnumber]
#
# URL:
#
#   http://localhost/list
#
#------------------------------------------------------------------------------

from django.core.management import execute_manager
from l2v import L2VisionModel
from l2v import L2VisionSniffer
from l2v import L2VisionGrapher
import settings
import sys

#------------------------------------------------------------------------------
# main

st = L2VisionSniffer.SnifferThread()
gt = L2VisionGrapher.GrapherThread()
try:
    if len(sys.argv) == 1:
        port = 8000
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        print "Usage: python L2Vision.py [portnumber]"
        sys.exit(1)

    print "L2 Vision %s" % L2VisionModel._version

    print "Starting UDP sniffer"
    st.start()

    print "Starting grapher"
    gt.start()

    execute_manager(settings, ["django", "runserver", "--noreload", "0.0.0.0:%d" % port])
finally:
    print "Shutting down."
    st.running = False
    gt.running = False
