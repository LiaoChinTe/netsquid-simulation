from netsquid.util import simtools 
from netsquid import NANOSECOND
from netsquid.protocols import NodeProtocol
from netsquid.components import QuantumProgram

from random import randint

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import INSTR_R45, INSTR_R90, INSTR_R135, INSTR_R180, INSTR_R225, INSTR_R270, INSTR_R315

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)


class BobRotate(QuantumProgram):
    def __init__(self,num_bits,theta1,theta2):
        self.num_bits=num_bits
        self.theta1=theta1
        self.theta2=theta2
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        mylogger.debug("BobRotate running ")

        tmpA1=(self.theta1+4*self.x1)%8
        tmpA2=(self.theta2+4*self.x2)%8

        for i in range(self.num_bits):
            if i%2==0:
                self.zRotation(tmpA1,qList_idx[i])

            if i%2==1:
                self.zRotation(tmpA2,qList_idx[i])

        yield self.run(parallel=False)

    def zRotation(self,rotationInx,idx):
        if rotationInx == 1:
            self.apply(INSTR_R45, idx)
        if rotationInx == 2:
            self.apply(INSTR_R90, idx)
        if rotationInx == 3:
            self.apply(INSTR_R135, idx)
        if rotationInx == 4:
            self.apply(INSTR_R180, idx)
        if rotationInx == 5:
            self.apply(INSTR_R225, idx)
        if rotationInx == 6:
            self.apply(INSTR_R270, idx)
        if rotationInx == 7:
            self.apply(INSTR_R315, idx)


class MBQC_BobProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=2): 
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.portList=["portQI","portQO","portCO"]

        self.theta1=randint(0,7)
        self.theta2=randint(0,7)
        self.r1=randint(0,1)
        self.r2=randint(0,1)
        self.num_bits=num_bits

        

    def run(self):
        mylogger.debug("MBQC_BobProtocol running")
        

        # receive qubits from Alice
        port=self.node.ports["portQI"]
        yield self.await_port_input(port)
        qubits = port.rx_input().items
        mylogger.debug("B received qubits from A:{}".format(qubits))


