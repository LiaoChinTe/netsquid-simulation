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
            PhysicalInstruction(INSTR_MEASURE, duration=1000, quantum_noise_model=gateNoice, parallel=True)])

    return myProcessor



def run_QLine_sim(numNode=3,fibreLen=10,qdelay=0,cdelay=0):

    ns.sim_reset()
    NodeList=[]
    ProcessorList=[]
    for i in range(numNode):

        # create nodes
        tmpNode=Node("Node_"+str(i), port_names=["portQI","portQO","portCI","portCO"]) # quantum/classical input/output
        NodeList.append(tmpNode)

        # create processor
        ProcessorList.append(createProcessor_QL(processorName="Processor_"+str(i)))


        # channels==================================================================
        
        MyQChannel=QuantumChannel("QChannel_forward_"+str(i),delay=qdelay,length=fibreLen
            ,models={"myFibreLossModel": FibreLossModel(p_loss_init=0.2, p_loss_length=0.25, rng=None)})
        
        ## connections
        if i>0:
            NodeList[i-1].connect_to(NodeList[i], MyQChannel,
                local_port_name =NodeList[i-1].ports["portQO"].name,
                remote_port_name=NodeList[i].ports["portQI"].name)
        

            MyCChannel_F = ClassicalChannel("CChannel_forward_"+str(i),delay=cdelay,length=fibreLen)
            MyCChannel_B = ClassicalChannel("CChannel_backward_"+str(i),delay=cdelay,length=fibreLen)

            myDirectConnection=DirectConnection("DConnection_forward_"+str(i),channel_AtoB=MyCChannel_F,channel_BtoA=MyCChannel_B)
        
            NodeList[i-1].connect_to(NodeList[i], myDirectConnection,local_port_name="portCO", remote_port_name="portCI")
            



        # record time
        startTime=ns.sim_time()

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

