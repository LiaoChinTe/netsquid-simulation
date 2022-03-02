from netsquid.protocols import NodeProtocol
from netsquid.components import Clock

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)


class QG_Bmeasure(QuantumProgram):
    def __init__(self,num_bits):
        self.num_bits=num_bits
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        mylogger.info("B measure running ")
        for i in range(self.num_bits):
            self.apply(INSTR_MEASURE, qList_idx[i])

        yield self.run(parallel=False)


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

        if self.role==1:
            pass
        elif self.role==0:
            # receive qubits
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.info("\nB received {}".format(myqlist))


