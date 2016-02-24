KNOCK_ID='a'
KNOCK_VERSION=(0,0,1)


class IP_VERSION:
    V4=4
    V6=6

class PROTOCOL:
    TCP = 'tcp'
    UDP = 'udp'

    @staticmethod
    def getById(id):
        if id == 1:
            return PROTOCOL.TCP
        elif id == 0:
            return PROTOCOL.UDP
        else:
            return None

    @staticmethod
    def getId(protocol):
        if PROTOCOL.TCP == protocol:
            return 1
        elif PROTOCOL.UDP == protocol:
            return 0
        else:
            return None

class FIREWALL_POLICY:
    DROP = 'drop'
    REJECT = 'reject'
    NONE = 'none'