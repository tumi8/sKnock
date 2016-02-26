#!/usr/bin/env python

__author__ = "Daniel Sel"
__email__  = "daniel-sel@hotmail.com"
__license__= """
Copyright (c) 2015 Daniel Sel <daniel-sel@hotmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA

"""

import grp
import logging
import os
import pwd
import sys

from knock_server.ServerInterface import ServerInterface


def checkPrivileges():
    if (not os.geteuid() == 0):
         print "Sorry, you have to run knock-server as root."
         sys.exit(3)

def main(argv):
    checkPrivileges()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename=os.path.join(os.path.dirname(__file__), 'portknocking.log'))
    #signal.signal(signal.SIGINT, shutdownHandler)
    #signal.signal(signal.SIGTERM, shutdownHandler)
    knockServer = ServerInterface()
    knockServer.runKnockDaemon()

    print os.getpid()

    import signal
    import time

    #time.sleep(30)
    #os.kill(os.getpid(), signal.SIGINT)
                
if __name__ == '__main__':
    main(sys.argv[1:])
