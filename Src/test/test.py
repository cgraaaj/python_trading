import os
import sys

LOCATE_PY_FILENAME = __file__
LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
LOCATE_PY_PARENT_DIR = os.path.abspath(os.path.join(LOCATE_PY_DIRECTORY_PATH, ".."))
print(LOCATE_PY_FILENAME)
print(LOCATE_PY_DIRECTORY_PATH)
print(LOCATE_PY_PARENT_DIR)