from random import randint
from netsquid.util import simtools 
from netsquid import NANOSECOND
from netsquid.protocols import NodeProtocol
from netsquid.components import QuantumProgram
from netsquid.components.instructions import INSTR_H,INSTR_CZ

import sys


scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import INSTR_R45, INSTR_R90, INSTR_R135, INSTR_R180, INSTR_R225, INSTR_R270, INSTR_R315

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)




class AliceRotate(QuantumProgram):
    def __init__(self,num_bits,theta1,theta2,x1,x2):
        self.num_bits=num_bits
        self.theta1=theta1
        self.theta2=theta2
        self.x1=x1
        self.x2=x2
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        mylogger.debug("AliceRotate running ")

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




class MBQC_AliceProtocol(NodeProtocol):
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
        mylogger.debug("MBQC_AliceProtocol running")

        
        # receive qubits
        port=self.node.ports["portQI"]
        yield self.await_port_input(port)
        myqlist = port.rx_input().items
        mylogger.debug("\nA received {}".format(myqlist))

        # put qubits in processor
        self.processor.put(myqlist)

        
        myAliceRotate=AliceRotate(self.num_bits,self.theta1,self.theta2,self.x1,self.x2)
        self.processor.execute_program(myAliceRotate,qubit_mapping=[i for  i in range(self.num_bits)])

        yield self.await_program(processor=self.processor)

        
        inx=list(range(self.num_bits))
        payload=self.processor.pop(inx)
        self.node.ports["portQO"].tx_output(payload)


    def showStatus(self,info):
        print(info)
        print("self.theta1  = {}".format(self.theta1))
        print("self.theta2  = {}".format(self.theta2))
        print("self.x1  = {}".format(self.x1))
        print("self.x2  = {}".format(self.x2))
        print("\n")