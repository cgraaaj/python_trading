import sys
import json
from datetime import datetime
import os
import subprocess

# res = ["a", "b"]
# print("hai " + sys.argv[1] + json.dumps(res))
LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
previousMonth = datetime.now().month - 1 or 12
subprocess.call(
    "{0}/logs/deleteLogs.sh {1}".format(
        LOCATE_PY_DIRECTORY_PATH,
        previousMonth if previousMonth / 10 > 1 else "0" + str(previousMonth),
    ),
    shell=True,
)
