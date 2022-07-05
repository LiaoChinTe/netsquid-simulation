from netsquid.components.qprogram import QuantumProgram
from netsquid.protocols import NodeProtocol

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
#from functions import *

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)





class MBQC_TEEProtocol(NodeProtocol):
    def __init__(self,node,num_bits=2): 
        super().__init__()
        
        self.node=node
        self.portList=["portC1","portC2","portC3"]
        self.num_bits=num_bits

        
        
        

        

    def run(self):
        mylogger.debug("MBQC_TEEProtocol running")

        # receive from A
        port=self.node.ports["portC1"]
        yield self.await_port_input(port)
        info_A = port.rx_input().items
        mylogger.debug("TEE received info_A:{}".format(info_A))

        # receive from B
        port=self.node.ports["portC2"]
        yield self.await_port_input(port)
        info_B = port.rx_input().items
        mylogger.debug("TEE received info_B:{}".format(info_B))