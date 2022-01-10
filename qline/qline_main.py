import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.protocols import LocalProtocol
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


def createProcessor_QL(processorName,capacity=20,momNoise=None,gateNoice=None):

    myProcessor=QuantumProcessor(processorName, num_positions=capacity,
        mem_noise_models=momNoise, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=10, quantum_noise_model=gateNoice),
            PhysicalInstruction(INSTR_H, duration=10, quantum_noise_model=gateNoice),
            PhysicalInstruction(INSTR_MEASURE, duration=1000, quantum_noise_model=gateNoice, parallel=True)])

    return myProcessor


'''
Variable "nodeNrole" indicates which two of the node are going to form shared keys.
Therefore it is important for it to fit certain conditions.

input:
    nodeNrole(list of bool): Elements=True means it is going to be one of the nodes to form shared keys. 
        There must be exactly two of them to be True.

output:
    Ture or False, means pass or not.

'''
def nodeRoleCheck(nodeNrole):
    trueCount=0
    for i in nodeNrole:
        if i==True:
            trueCount+=1
    if trueCount>2 or trueCount<2 :
        return False
    else:
        return True

def run_QLine_sim(nodeNrole=[True,False,True],fibreLen=10,qdelay=0,cdelay=0):

    ns.sim_reset()
    NodeList=[]
    ProcessorList=[]
    myCharlieProtocolList=[]

    #check value avalibility
    if nodeRoleCheck(nodeNrole)==False:
        print("Error nodes role assigning!")
        return 1


    for i in range(len(nodeNrole)):

        # create nodes===========================================================
        tmpNode=Node("Node_"+str(i), port_names=["portQI","portQO","portCI","portCO"]) # quantum/classical input/output
        NodeList.append(tmpNode)

        # create processor===========================================================
        ProcessorList.append(createProcessor_QL(processorName="Processor_"+str(i),momNoise=None,gateNoice=None))


        
        # channels in between nodes==============================================================
        if i>0:

            # Q channels==================================================================
        
            MyQChannel=QuantumChannel("QChannel_forward_"+str(i),delay=qdelay,length=fibreLen
                ,models={"myFibreLossModel": FibreLossModel(p_loss_init=0.2, p_loss_length=0.25, rng=None)})

            NodeList[i-1].connect_to(NodeList[i], MyQChannel,
                local_port_name =NodeList[i-1].ports["portQO"].name,
                remote_port_name=NodeList[i].ports["portQI"].name)

            # C channals==================================================================
            MyCChannel_F = ClassicalChannel("CChannel_forward_"+str(i),delay=cdelay,length=fibreLen)
            MyCChannel_B = ClassicalChannel("CChannel_backward_"+str(i),delay=cdelay,length=fibreLen)

            myDirectConnection=DirectConnection("DConnection_forward_"+str(i),channel_AtoB=MyCChannel_F,channel_BtoA=MyCChannel_B)
        
            NodeList[i-1].connect_to(NodeList[i], myDirectConnection,local_port_name="portCO", remote_port_name="portCI")
    



        # record time
        startTime=ns.sim_time()

        # assign Charlie protocol
        if i!=0 and i!=len(nodeNrole)-1:
            myCharlieProtocolList.append(qline_C.CharlieProtocol(node=NodeList[i],processor=ProcessorList[i])) 


    myAliceProtocol=qline_A.AliceProtocol(node=NodeList[0],processor=ProcessorList[0])
    myBobProtocol=qline_B.BobProtocol(node=NodeList[-1],processor=ProcessorList[-1])
    

    myBobProtocol.start()
    for Charlie in myCharlieProtocolList:
        Charlie.start()

    myAliceProtocol.start()

    ns.sim_run()

    return 0






if __name__ == "__main__":

    tmp=run_QLine_sim(nodeNrole=[False,True,True],fibreLen=10)
    print(tmp)

