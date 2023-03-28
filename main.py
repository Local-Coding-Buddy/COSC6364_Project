import os
import sys
import copy
import random
import time
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString
from Route_setup.Make_Trips_file import *
from datetime import datetime
import sumolib
import winsound
from Core_code import *

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("No environment variable SUMO_HOME!")


network_file = ""
Rounad_name

if __name__ == "__main__":