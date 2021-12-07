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



import qline_A
import qline_B
import qline_C


def createProcessor_QL(processorName,momNoise=None,gateNoice=None):

    myProcessor=QuantumProcessor(processorName, num_positions=2,
        mem_noise_models=momNoise, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=10, quantum_noise_model=gateNoice),
            PhysicalInstruction(INSTR_H, duration=10, quantum_noise_model=gateNoice),
            PhysicalInstruction(INSTR_MEASURE, duration=5, quantum_noise_model=gateNoice, parallel=True)])

    return myProcessor



def run_QLine_sim(numNode=3,fibreLen=10):

    ns.sim_reset()
    NodeList=[]
    ProcessorList=[]
    for i in range(numNode):

        # create nodes
        tmpNode=Node("Node_"+str(i), port_names=["portQI","portQO","portCI","portCO"]) # quantum/classical input/output
        NodeList.append(tmpNode)

        # create processor
        ProcessorList.append(createProcessor_QL(processorName="Processor_"+str(i)))

        # assign Charlie protocol
        if i!=0 and i!=numNode-1:
            myCharlieProtocol=qline_C.CharlieProtocol(node=NodeList[i],processor=ProcessorList[i])


    myAliceProtocol=qline_A.AliceProtocol(node=NodeList[0],processor=ProcessorList[0])
    myBobProtocol=qline_B.BobProtocol(node=NodeList[-1],processor=ProcessorList[-1])
    


    ns.sim_run()

    return 0






if __name__ == "__main__":

    tmp=run_QLine_sim(numNode=3,fibreLen=10)
    print(tmp)

