from netsquid.components.qprogram import QuantumProgram
from netsquid.protocols import NodeProtocol

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import *

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)



class MBQC_ServerProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=2): 
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.portList=["portQI","portC"]

        self.num_bits=num_bits

        

    def run(self):
        mylogger.debug("MBQC_ServerProtocol running")


        # receive qubits from Alice
        port=self.node.ports["portQI"]
        yield self.await_port_input(port)
        qubits = port.rx_input().items
        mylogger.debug("Server received qubits from Bob:{}".format(qubits))