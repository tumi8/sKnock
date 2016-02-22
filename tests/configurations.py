import os

class Settings: pass

config_server_valid = Settings()
config_server_valid.KNOCKPACKET_MIN_LENGTH = 800
config_server_valid.PORT_OPEN_DURATION_IN_SECONDS = 15
config_server_valid.TIMESTAMP_THRESHOLD_IN_SECONDS = 7

config_server_valid.crlFile = crlFile=os.path.join(os.path.dirname(__file__), 'data', 'devca_valid.crl')
config_server_valid.serverPFXFile = os.path.join(os.path.dirname(__file__), 'data', 'devserver_valid.pfx')
config_server_valid.PFXPasswd = 'portknocking'