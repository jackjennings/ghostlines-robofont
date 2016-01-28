import os
import sys


dirname = os.path.dirname(__file__)
lib_path = os.path.abspath(os.path.join(dirname, ".."))
packages_path = os.path.join(lib_path, "site-packages")
if packages_path not in sys.path:
    sys.path.append(packages_path)
