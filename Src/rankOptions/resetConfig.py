from configparser import ConfigParser
import os

config = ConfigParser()
currDir = os.path.dirname(os.path.abspath(__file__))
configFile = os.path.join(currDir, 'config.cfg')
config.set('DEFAULT', 'sessionCounter', '1')
with open(configFile, 'w') as cfg:
    config.write(cfg)