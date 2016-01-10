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

import os, sys, getopt, logging

from struct import *

from knock_common.modules.Configuration import Configuration
from knock_common.modules.CertUtil import CertUtil
from knock_common.modules.CryptoEngine import CryptoEngine

from modules.Connection import Connection

def usage():
    print "Usage: knockknock.py -p <portToOpen> <host>"
    sys.exit(2)

def parseArguments(argv):
    try:
        port       = 0
        host       = ""
        opts, args = getopt.getopt(argv, "h:p:")
        
        for opt, arg in opts:
            if opt in ("-p"):
                port = arg
            else:
                usage()
                
        if len(args) != 1:
            usage()
        else:
            host = args[0]

    except getopt.GetoptError:           
        usage()                          

    if port == 0 or host == "":
        usage()

    return (port, host)


def verifyPermissions():
    if os.getuid() != 0:
        print 'Sorry, you must be root to run this.'
        sys.exit(2)    


def main(argv):

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    (port, host) = parseArguments(argv)


    logger = logging.getLogger(__name__)

    config = Configuration()

    certUtil = CertUtil(config)
    cryptoEngine = certUtil.initializeCryptoEngineForServer()


    logger.debug('Knocking %s on port %s', host, port)
    connectionHandler = Connection(10, 3)
    connectionHandler.knockOnPort(host, port)


    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
