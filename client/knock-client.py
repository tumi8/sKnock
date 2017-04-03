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

import logging, os, getopt, sys

from struct import *

from client.ClientInterface import ClientInterface
from common.definitions.Constants import PROTOCOL

def usage():
    print "Usage: knock-client.py [-u] -p <portToOpen> <host>"
    sys.exit(2)

def parseArguments(argv):
    port = 0
    host = ""
    ipv4 = False
    udp = False
    try:
        opts, args = getopt.getopt(argv, "uh:p:4")
        
        for opt, arg in opts:
            if opt in ("-p"):
                port = arg
            elif opt in ('-4'):
                ipv4 = True
            elif opt in ('-u'):
                udp = True
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

    protocol = PROTOCOL.UDP if udp else PROTOCOL.TCP
    return (port, host, protocol, ipv4)

def main(argv):

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    (port, host, protocol, ipv4) = parseArguments(argv)

    knockClient = ClientInterface()
    knockClient.knockOnPort(host, port, protocol, forceIPv4=ipv4)


    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
