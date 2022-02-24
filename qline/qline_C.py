from netsquid.protocols import NodeProtocol
from netsquid.components import Clock

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)

class CharlieProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10,role=0): #role value:[-1,0,1] 1 is the first party to form key
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits

        self.role=role
        self.portList=["portQI","portQO","portCI","portCO"]

        # The four values below are related to the qline algorithm
        self.randR=[]
        self.randB=[]
        self.randC=[]
        self.randS=[]



    def run(self):
        mylogger.debug("CharlieProtocol running")

        

        if self.role==1:
            mylogger.debug("C case 1")

            # receive qubits
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.info("C1 received {}".format(myqlist))
            
            # choose random R,B values
            self.randR=Random_basis_gen(self.num_bits)
            self.randB=Random_basis_gen(self.num_bits)

            # send qubits to the next
            self.node.ports["portQO"].tx_output(myqlist)


        elif self.role==-1:
            mylogger.debug("C case -1")
            # choose random C,S values
            self.randC=Random_basis_gen(self.num_bits)
            self.randS=Random_basis_gen(self.num_bits)

            # receive qubits
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.debug("C-1 received{}".format(myqlist))

        else:
            mylogger.debug("C case 0")
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.debug("C0 received{}".format(myqlist))


            self.C_PassQubits(myqlist)

    def C_PassQubits(self,qlist):
        self.node.ports["portQO"].tx_output(qlist)



