from distutils.log import error
import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.qubits import create_qubits
from netsquid.qubits.operators import X,H,Z
from netsquid.nodes.connections import DirectConnection
from netsquid.components.models import  FibreDelayModel,QuantumErrorModel,FibreLossModel
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel

from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import QuantumProcessor,PhysicalInstruction
from netsquid.components.instructions import INSTR_X,INSTR_H,INSTR_MEASURE
from netsquid.components.models.qerrormodels import T1T2NoiseModel,DepolarNoiseModel,DephaseNoiseModel

from random import randint
from difflib import SequenceMatcher


import qline_A
import qline_B
import qline_C

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import ManualFibreLossModel

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)


'''
return number of detectors used in this QLine
'''
def detectorCount_QL(num_nodes):
    return num_nodes-1


'''
Create quantum processor only for Qline.
For conviniency, I apply the same processor for Alice, Bob and Charlie.
Alice and Chalies do not need measurement instruction.
'''
def createProcessor_QL(processorName,capacity=300,momNoise=None,processorNoice=None):

    myProcessor=QuantumProcessor(processorName, num_positions=capacity,
        mem_noise_models=momNoise, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=5, quantum_noise_model=processorNoice),
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processorNoice),
            PhysicalInstruction(INSTR_MEASURE, duration=3700, quantum_noise_model=processorNoice, parallel=True)])

    return myProcessor


'''
Variable "nodeNrole" indicates which two of the node are going to form shared keys.
Therefore it is important for it to fit certain conditions.

input:
    nodeNrole(list of int): The position of Elements=1 and Elements=-1 in the list indicates two parties forming a shared key.
        There must be exactly one of them to be 1 and -1.

output:
    Ture or False, Ture=pass.

'''
def nodeRoleCheck(nodeNrole):
    oneCount=0
    minusOneCount=0
    for i in nodeNrole:
        if i==1:
            oneCount+=1
        elif i==-1:
            minusOneCount+=1
    if oneCount!=1 or minusOneCount!=1 :
        return False
    else:
        return True






'''
The input variable 'nodeNrole' is a list of int which describes the length of this Qline 
as well as which of the two node are forming shared key.
An outer loop will be required to form shared keys among all nodes.

Note that the first node is always labeled with "A", and the last is always "B". 
All the others in the middle are "C". These labels are used for understanding the comments and Qline algorithm.
The key sharing nodes are also labeled with "1" or "2" following with the previous label.
For example, if the first node is forming shared key with the second node within a Qline of four.
The labels would be [A1,C2,C,B] and the 'nodeNrole' value be [1,-1,0,0].
'''
def run_QLine_sim(rounds=1,nodeNrole=[1,0,-1],num_bits=20,fibreLen=10,processorNoice=None,momNoise=None
    ,qSpeed=2*10**5,cSpeed=2*10**5,source_frq=1e9,fibreNoise=0,lenLoss=0):

    #keyRateList=[]
    keyLenList=[]
    timecostList=[]

    for i in range(rounds):

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
            if i == 0:
                tmpNode=Node("Node_"+str(i), port_names=["portQO","portCO"]) # quantum/classical input/output
            elif i == len(nodeNrole):
                tmpNode=Node("Node_"+str(i), port_names=["portQI","portCI"]) # quantum/classical input/output
            else:
                tmpNode=Node("Node_"+str(i), port_names=["portQI","portQO","portCI","portCO"]) # quantum/classical input/output
            
            NodeList.append(tmpNode)

            # create processor===========================================================
            ProcessorList.append(createProcessor_QL(processorName="Processor_"+str(i),momNoise=momNoise
                ,processorNoice=processorNoice))


            
            # channels in between nodes==============================================================
            if i>0:

                # Q channels(one way cannel)==================================================================
            
                MyQChannel=QuantumChannel("QChannel_forward_"+str(i),delay=0,length=fibreLen
                    ,models={"myQFibreLossModel": FibreLossModel(p_loss_init=0, p_loss_length=0, rng=None)
                    ,"myDelayModel": FibreDelayModel(c=qSpeed)
                    ,"myFibreNoiseModel":DepolarNoiseModel(depolar_rate=fibreNoise, time_independent=False)}) # c km/s


                NodeList[i-1].connect_to(NodeList[i], MyQChannel,
                    local_port_name =NodeList[i-1].ports["portQO"].name,
                    remote_port_name=NodeList[i].ports["portQI"].name)

                # C channals(bidirectional)==================================================================
                MyCChannel_F = ClassicalChannel("CChannel_forward_"+str(i),delay=0,length=fibreLen
                    ,models={"myCDelayModel": FibreDelayModel(c=cSpeed)})
                MyCChannel_B = ClassicalChannel("CChannel_backward_"+str(i),delay=0,length=fibreLen
                    ,models={"myCDelayModel": FibreDelayModel(c=cSpeed)})

                myDirectConnection=DirectConnection("DConnection_forward_"+str(i),channel_AtoB=MyCChannel_F,channel_BtoA=MyCChannel_B)
            
                NodeList[i-1].connect_to(NodeList[i], myDirectConnection,local_port_name="portCO", remote_port_name="portCI")
        



            # record time
            startTime=ns.sim_time()

            # assign Charlie protocol
            if i!=0 and i!=len(nodeNrole)-1:
                myCharlieProtocolList.append(qline_C.CharlieProtocol(node=NodeList[i],processor=ProcessorList[i]
                    ,role=nodeNrole[i],num_bits=num_bits)) 


        myAliceProtocol=qline_A.AliceProtocol(node=NodeList[0],processor=ProcessorList[0],role=nodeNrole[0]
            ,num_bits=num_bits,source_frq=source_frq)
        myBobProtocol=qline_B.BobProtocol(node=NodeList[-1],processor=ProcessorList[-1],role=nodeNrole[-1]
            ,num_bits=num_bits)
        

        myBobProtocol.start()
        for Charlie in myCharlieProtocolList:
            Charlie.start()

        myAliceProtocol.start()
        #ns.logger.setLevel(1)


        TimeStart=ns.util.simtools.sim_time(magnitude=ns.NANOSECOND)
        ns.sim_run()
        
        
        # extract first key
        if nodeNrole[0] == 1:
            firstKey = myAliceProtocol.key
        else:
            for C in myCharlieProtocolList:
                if C.key:
                    firstKey=C.key

        # extract endtime value and second key
        if nodeNrole[-1] == -1:
            TimeEnd=myBobProtocol.endTime
            secondKey=myBobProtocol.key
        else:
            for C in myCharlieProtocolList:
                if C.endTime != 0:
                    TimeEnd=C.endTime
                    secondKey=C.key
                
        
        # apply key losses
        firstKey,secondKey=ManualFibreLossModel(key1=firstKey,key2=secondKey,numNodes=len(nodeNrole)
            ,fibreLen=fibreLen*3,iniLoss=0,lenLoss=lenLoss)  #0.067
        



        timeUsed=TimeEnd-TimeStart # in ns
        timeUsed*=len(nodeNrole) # considering 
        if timeUsed!=0:
            timecostList.append(timeUsed)
            s = SequenceMatcher(None, firstKey, secondKey)# unmatched rate
            keyLenList.append(len(secondKey)*s.ratio()) #second

            #mylogger.info("key length:{}\n".format(len(secondKey)*s.ratio()))
        else:
            mylogger.error("Time used can not be 0!! \n")

    
        

    #return [[firstKey,secondKey],(TimeEnd-TimeStart)] #return time used in nanosec
    #return sum(keyRateList)/len(keyRateList)*10**9 # return keyRate
    return [sum(keyLenList)/len(keyLenList),sum(timecostList)/len(timecostList)]







