# Copyright (C) 2015-2016 Daniel Sel
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

import logging, subprocess

import iptc

from knock_server.definitions import Constants

LOG = logging.getLogger(__name__)

IPTABLES_CHAIN_KNOCK = 'knock'
IPTABLES_CHAIN_INPUT = 'INPUT'

def getIPTablesRuleForClient(port, ipVersion, protocol, addr):
    if ipVersion == Constants.IP_VERSION.V4 and iptc.is_table_available(iptc.Table.FILTER):
        rule = iptc.Rule()
        rule.target = iptc.Target(rule, 'RETURN')
        rule.src = addr
        rule.protocol = protocol
        rule.create_match(protocol).dport = str(port)
        LOG.debug("Created Rule For IPv%s Request: PORT=%s, HOST=%s PROTOCOL=%s", ipVersion, port, addr, protocol)

    elif ipVersion == Constants.IP_VERSION.V6 and iptc.is_table_available(iptc.Table6.FILTER):
        rule = iptc.Rule6()
        rule.target = iptc.Target(rule, 'RETURN')
        rule.src = addr
        rule.protocol = protocol
        rule.create_match(protocol).dport = str(port)
        LOG.debug("Created Rule For IPv%s Request: PORT=%s, HOST=%s PROTOCOL=%s", ipVersion, port, addr, protocol)

    else:
        LOG.error("Could not construct Rule For IPv%s Request: PORT=%s, HOST=%s PROTOCOL=%s", ipVersion, port, addr, protocol)

    return rule

def getIPTablesChainForVersion(ipVersion, chain):
    if ipVersion == Constants.IP_VERSION.V4 and iptc.is_table_available(iptc.Table.FILTER):
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), chain)
    elif ipVersion == Constants.IP_VERSION.V6 and iptc.is_table_available(iptc.Table6.FILTER):
        chain = iptc.Chain(iptc.Table6(iptc.Table6.FILTER), chain)
    else:
        LOG.error("Could not find chain \'%s\' for IPv%s IPTables", chain, ipVersion)

    return chain


# TODO: Set Policy to DROP
def setupIPTablesPortKnockingChainAndRedirectTraffic():
    if iptc.is_table_available(iptc.Table.FILTER):
        tableV4 = iptc.Table(iptc.Table.FILTER)
        try:
            knockChainV4 = getIPTablesChainForVersion(Constants.IP_VERSION.V4, IPTABLES_CHAIN_KNOCK)
            knockChainV4.flush()
        except iptc.IPTCError:
            knockChainV4 = tableV4.create_chain(IPTABLES_CHAIN_KNOCK)

        inputChainV4 = getIPTablesChainForVersion(Constants.IP_VERSION.V4, IPTABLES_CHAIN_INPUT)

        redirectRuleV4 = iptc.Rule()
        redirectRuleV4.target = iptc.Target(redirectRuleV4, IPTABLES_CHAIN_KNOCK)

        deleteIPTablesRuleIgnoringError(redirectRuleV4, inputChainV4)
        inputChainV4.insert_rule(redirectRuleV4)

        establishedRuleV4 = iptc.Rule()
        establishedRuleV4.create_match('state').state = "RELATED,ESTABLISHED"
        establishedRuleV4.target = iptc.Target(establishedRuleV4, 'ACCEPT')

        deleteIPTablesRuleIgnoringError(establishedRuleV4, inputChainV4)
        inputChainV4.insert_rule(establishedRuleV4)

        LOG.debug("Setup Port-knocking IPTables Configuration for IPv4")

    if iptc.is_table_available(iptc.Table6.FILTER):
        tableV6 = iptc.Table6(iptc.Table6.FILTER)
        try:
            knockChainV6 = getIPTablesChainForVersion(Constants.IP_VERSION.V6, IPTABLES_CHAIN_KNOCK)
            knockChainV6.flush()
        except iptc.IPTCError:
            knockChainV6 = tableV6.create_chain(IPTABLES_CHAIN_KNOCK)

        inputChainV6 = getIPTablesChainForVersion(Constants.IP_VERSION.V6, IPTABLES_CHAIN_INPUT)

        redirectRuleV6 = iptc.Rule6()
        redirectRuleV6.target = iptc.Target(redirectRuleV6, IPTABLES_CHAIN_KNOCK)

        deleteIPTablesRuleIgnoringError(redirectRuleV6, inputChainV6)
        inputChainV6.insert_rule(redirectRuleV6)

        establishedRuleV6 = iptc.Rule6()
        establishedRuleV6.create_match('state').state = "RELATED,ESTABLISHED"
        establishedRuleV6.target = iptc.Target(establishedRuleV6, 'ACCEPT')

        deleteIPTablesRuleIgnoringError(establishedRuleV6, inputChainV6)
        inputChainV6.insert_rule(establishedRuleV6)

        LOG.debug("Setup Port-knocking IPTables Configuration for IPv6")



def insertEmergencySSHAccessRule():
    if iptc.is_table_available(iptc.Table.FILTER):
        ruleV4 = iptc.Rule()
        ruleV4.target = iptc.Target(ruleV4, 'ACCEPT')
        ruleV4.protocol = 'tcp'
        ruleV4.create_match('tcp').dport = '22'

        chainV4 = iptc.Chain(iptc.Table(iptc.Table.FILTER), 'INPUT')
        deleteIPTablesRuleIgnoringError(ruleV4, chainV4)
        chainV4.insert_rule(ruleV4)

        LOG.debug("Inserted Emergency SSH Access Rule for IPv4")

    if iptc.is_table_available(iptc.Table6.FILTER):
        ruleV6 = iptc.Rule6()
        ruleV6.target = iptc.Target(ruleV6, 'ACCEPT')
        ruleV6.protocol = 'tcp'
        ruleV6.create_match('tcp').dport = '22'

        chainV6 = iptc.Chain(iptc.Table6(iptc.Table6.FILTER), 'INPUT')
        deleteIPTablesRuleIgnoringError(ruleV6, chainV6)
        chainV6.insert_rule(ruleV6)

        LOG.debug("Inserted Emergency SSH Access Rule for IPv6")



def backupIPTablesState():
    if iptc.is_table_available(iptc.Table.FILTER):
        subprocess.call('iptables-save > /tmp/iptables.bak', shell=True)
        LOG.debug("Backed up current IPTables Rules to /tmp/iptables.bak")
    if iptc.is_table_available(iptc.Table6.FILTER):
        subprocess.call('ip6tables-save > /tmp/ip6tables.bak', shell=True)
        LOG.debug("Backed up current IPTables Rules to /tmp/ip6tables.bak")


def restoreIPTablesState():
    if iptc.is_table_available(iptc.Table.FILTER):
        subprocess.call('iptables-restore < /tmp/iptables.bak', shell=True)
        LOG.debug("Restored IPTables Rules from /tmp/iptables.bak")
        subprocess.call('rm /tmp/iptables.bak', shell=True)
        LOG.debug("Cleaned up backup file /tmp/iptables.bak")
    if iptc.is_table_available(iptc.Table6.FILTER):
        subprocess.call('ip6tables-restore < /tmp/ip6tables.bak', shell=True)
        LOG.debug("Restored IPTables Rules from /tmp/ip6tables.bak")
        subprocess.call('rm /tmp/iptables.bak', shell=True)
        LOG.debug("Cleaned up backup file /tmp/ip6tables.bak")

def deleteIPTablesRuleIgnoringError(rule, chain):
    try:
        chain.delete_rule(rule)
    except iptc.IPTCError:
        pass