from netsquid.protocols import NodeProtocol
from netsquid.components import Clock

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)

class BobProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10,role=0):
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits


        self.role=role
        self.portList=["portQI","portCI"]

        # The two values below are related to the qline algorithm
        self.randC=[]
        self.randS=[]


    def run(self):
        mylogger.debug("BobProtocol running")


