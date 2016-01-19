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
        return PROTOCOL.TCP if id else PROTOCOL.UDP

    @staticmethod
    def getId(protocol):
        return 1 if PROTOCOL.TCP == protocol else 0