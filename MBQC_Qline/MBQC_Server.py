from netsquid.components.qprogram import QuantumProgram
from netsquid.protocols import NodeProtocol

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import *

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)

