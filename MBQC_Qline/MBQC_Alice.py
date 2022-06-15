from netsquid.util import simtools 
from netsquid import NANOSECOND
from netsquid.protocols import NodeProtocol

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import *

import logging
#logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)


class AliceRotate(QuantumProgram):
    def __init__(self,num_bits,RList,BList):
        self.num_bits=num_bits
        self.RList=RList
        self.BList=BList
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        mylogger.debug("C1 running ")
        for i in range(self.num_bits):
            if self.BList[i]==1:
                self.apply(INSTR_X, qList_idx[i])

            if self.RList[i]==1:
                self.apply(INSTR_H, qList_idx[i])

        yield self.run(parallel=False)





class MBQC_AliceProtocol(NodeProtocol):
    def __init__(self,node,processor): #role value:[-1,0,1] 1 is the first party to form key
        super().__init__()
        
        self.node=node
        self.processor=processor
        
        self.portList=["portQI","portQO","portCO"]

        


    def showStatus(self,info):
        print(info)
        print("self.RList  = {}".format(self.RList))
        print("self.SList  = {}".format(self.SList))

        print("self.BList  = {}".format(self.BList))

        print("self.CList  = {}".format(self.CList))
        print("self.ResList= {}".format(self.ResList))
        print("\n")


    def run(self):
        mylogger.debug("MBQC_AliceProtocol running")

        
        # receive qubits
        port=self.node.ports["portQI"]
        yield self.await_port_input(port)
        myqlist = port.rx_input().items
        mylogger.debug("\nA1 received {}".format(myqlist))

        # put qubits in processor
        self.processor.put(myqlist)
            
            






