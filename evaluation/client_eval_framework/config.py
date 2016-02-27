import os

class Settings: pass
config = Settings()

config.jobCfgUrl = "https://home.in.tum.de/~sel/BA/eval-control/job.cfg"
config.jobCfgFile = os.path.join(os.path.dirname(__file__), 'job.cfg')