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

import logging
from logging.handlers import WatchedFileHandler
import os
import sys
import signal

from ServerInterface import ServerInterface

def checkPrivileges():
    if (not os.geteuid() == 0):
         print ("Sorry, you have to run knock-server as root.")
         sys.exit(3)


def setup_logging():
    # Prepare root logger to log all INFO to stderr and DEBUG to file
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',
                                  '%x %X')
    stream_handler.setFormatter(formatter)
    file_handler = WatchedFileHandler('/tmp/knock.log', 'a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s'))
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)



def main(argv):
    checkPrivileges()
    #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/portknocking.log')
    setup_logging()
    knockServer = ServerInterface()

    signal.signal(signal.SIGINT, knockServer.gracefulShutdown)
    signal.signal(signal.SIGTERM, knockServer.gracefulShutdown)

    knockServer.listenForKnockRequests()

if __name__ == '__main__':

    main(sys.argv[1:])
