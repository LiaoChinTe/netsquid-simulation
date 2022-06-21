from netsquid.util import simtools 
from netsquid import NANOSECOND
from netsquid.protocols import NodeProtocol

from random import randint

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import *

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)



class MBQC_BobProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=2): 
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.portList=["portQI","portQO","portCO"]

        self.theta1=randint(0,7)
        self.theta2=randint(0,7)
        self.x1=randint(0,1)
        self.x2=randint(0,1)
        self.num_bits=num_bits

        

    def run(self):
        mylogger.debug("MBQC_BobProtocol running")
        
        port=self.node.ports["portQI"]
        yield self.await_port_input(port)
        qubits = port.rx_input().items
        mylogger.debug("B received qubits from A:{}".format(qubits))
