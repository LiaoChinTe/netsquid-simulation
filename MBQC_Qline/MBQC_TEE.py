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
        self.delta1=None

        self.thetaA1=None
        self.thetaA2=None
        self.rA1=None
        self.rA2=None
        self.xA1=None
        self.xA2=None

        self.thetaB1=None
        self.thetaB2=None
        self.rB1=None
        self.rB2=None
        self.phi1=None
        self.phi2=None
        
        self.delta2p=None
        self.delta2m=None
        
        self.m1=None

        

    def run(self):
        mylogger.debug("MBQC_TEEProtocol running")

        # receive from A
        port=self.node.ports["portC1"]
        yield self.await_port_input(port)
        info_A = port.rx_input().items
        mylogger.debug("TEE received info_A:{}".format(info_A))

        self.thetaA1=info_A[0][0]
        self.rA1=info_A[0][1]
        self.xA1=info_A[0][2]

       
        self.thetaA2=info_A[1][0]
        self.rA2=info_A[1][1]
        self.xA2=info_A[1][2]
        #[[self.theta1,self.r1,self.x1],[self.theta2,self.r2,self.x2]]

        # receive from B
        port=self.node.ports["portC2"]
        yield self.await_port_input(port)
        info_B = port.rx_input().items
        mylogger.debug("TEE received info_B:{}".format(info_B))


        self.thetaB1=info_B[0][0]
        self.rB1=info_B[0][1]
        self.phi1=info_B[0][2]

        self.thetaB2=info_B[1][0]
        self.rB2=info_B[1][1]
        self.phi2=info_B[1][2]

        # compute delta1
        self.delta1=(self.thetaA1+4*self.xA1+self.thetaB1+(self.rA1^self.rB1)*4+self.phi1)%8
        mylogger.debug("TEE self.delta1:{}".format(self.delta1))
        
        # send delta1 to server
        self.node.ports["portC3"].tx_output(self.delta1)


        # compute delta2
        self.delta2p=(self.thetaA2+4*self.xA2+self.thetaB2+(self.rA2^self.rB2)*4+self.phi2)%8
        self.delta2m=(self.thetaA2+4*self.xA2+self.thetaB2+(self.rA2^self.rB2)*4-self.phi2)%8
        if self.delta2m < 0:
            self.delta2m+=8

        mylogger.debug("TEE self.delta2p:{}".format(self.delta2p))
        mylogger.debug("TEE self.delta2m:{}".format(self.delta2m))


        # receive m1 from server
        port=self.node.ports["portC3"]
        yield self.await_port_input(port)
        self.m1 = port.rx_input().items[0]
        mylogger.debug("TEE received m1:{}".format(self.m1))

        # compute true m1
        


