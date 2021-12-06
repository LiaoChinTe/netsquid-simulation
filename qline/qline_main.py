import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.protocols import Protocol,LocalProtocol
from netsquid.qubits import create_qubits
from netsquid.qubits.operators import X,H,Z
from netsquid.nodes.connections import DirectConnection
#from netsquid.components.models import  FibreDelayModel
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel

from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *
from netsquid.components.instructions import *
from netsquid.components.qprogram import *
from netsquid.components.models.qerrormodels import *
from random import randint


def createProcessor_QL(processorName,momNoise=None,gateNoice=None):

    myProcessor=QuantumProcessor(processorName, num_positions=2,
        mem_noise_models=momNoise, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=10, q_noise_model=gateNoice),
            PhysicalInstruction(INSTR_H, duration=10, q_noise_model=gateNoice),
            PhysicalInstruction(INSTR_MEASURE, duration=5, q_noise_model=gateNoice, parallel=True)])

    return myProcessor



def run_QLine_sim(numNode,):

    ns.sim_reset()
    NodeList=[]
    ProcessorList=[]
    for i in numNode:

        # create nodes
        tmpNode=Node("Node_"+str(i), port_names=["portQI","portQO","portCI","portCO"]) # quantum/classical input/output
        NodeList.append(tmpNode)

        # create processor
        ProcessorList.append(createProcessor_QL(processorName="Processor_"+str(i)))



    '''
    myQLine=QLine(nodeList=nodeList
        ,processorList=processorList
        ,fibreLen=fibreLen
        ,initNodeID=I,targetNodeID=T,lossInd=lossInd,lossLen=lossLen)

    myQLine.start()
    '''


    ns.sim_run()






if __name__ == "__main__":

    key_I,key_T,timeSpent=run_QLine_sim(I=0,T=3,maxKeyLen=100,fibreLen=10
        ,noise_model=None
        ,lossInd=0.2,lossLen=0.25)
    print("key_I: ",key_I)
    print("key_T: ",key_T)
    print("timeSpent: ",timeSpent)