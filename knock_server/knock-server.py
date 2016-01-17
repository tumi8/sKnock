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

import os, sys, pwd, grp, logging

import lib.daemonize

from knock_common.modules.Configuration import Configuration
from knock_common.modules.CertUtil import CertUtil

from modules.Firewall.Firewall import Firewall
from modules.KnockListener import KnockListener



def checkPrivileges():
    if (not os.geteuid() == 0):
         print "Sorry, you have to run knock-server as root."
   #     sys.exit(3)

def dropPrivileges():
    nobody = pwd.getpwnam('nobody')
    adm    = grp.getgrnam('adm')

    os.setgroups([adm.gr_gid])
    os.setgid(adm.gr_gid)
    os.setuid(nobody.pw_uid)

def main(argv):
    checkPrivileges()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    config = Configuration()

    certUtil = CertUtil(config)
    cryptoEngine = certUtil.initializeCryptoEngineForServer()
    with Firewall() as firewallHandler:
        knockListener = KnockListener(cryptoEngine, firewallHandler)

        # knockknock.daemonize.createDaemon()

        knockListener.processPossibleKnockPackets()
                
if __name__ == '__main__':
    main(sys.argv[1:])
