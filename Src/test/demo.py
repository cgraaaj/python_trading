import sys
import json
from datetime import datetime
import os
import subprocess
import time
from dateutil import tz
import pandas as pd
import numpy as np
import pickle
sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
from nsetools.nse import Nse
from driver import Driver

nse = Nse()
dri = Driver()

l = [{'a': 123,'c':123}, {'b': 123}, {'a': 123,'c':123}]
l = [dict(t) for t in {tuple(d.items()) for d in l}]
print(l)