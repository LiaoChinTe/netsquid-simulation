import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.components.qprocessor import QuantumProcessor,PhysicalInstruction
from netsquid.components.instructions import INSTR_X,INSTR_H,INSTR_MEASURE,INSTR_MEASURE_X
from netsquid.components.models.qerrormodels import FibreLossModel,T1T2NoiseModel,DepolarNoiseModel,DephaseNoiseModel
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel
from netsquid.components.models import  FibreDelayModel


from difflib import SequenceMatcher
from random import randint


import BB84_Alice
import BB84_Bob

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import ManualFibreLossModel

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)



'''

Key length filter, used for certain simulation

# function that filters vowels 
def lenfilter(var): 
    if len(var) <= 10 and len(var) > 6: 
        return True
    else: 
        return False
'''  



# implementation & hardware configure

def run_BB84_sim(runtimes=1,num_bits=20,fibreLen=10**-9,memNoiseMmodel=None,processorNoiseModel=None
               ,loss_init=0,loss_len=0,qdelay=0,sourceFreq=8e7,lenLoss=0,qSpeed=2*10**5,cSpeed=2*10**5,fibreNoise=0):
    
    MyKeyList_A=[]  # local protocol list A
    MyKeyList_B=[]  # local protocol list B
    MyKeyRateList=[]
    
    for i in range(runtimes): 
        
        ns.sim_reset()

        # nodes====================================================================

        nodeA = Node("Alice", port_names=["portQA_1","portCA_1","portCA_2"])
        nodeB = Node("Bob"  , port_names=["portQB_1","portCB_1","portCB_2"])

        # processors===============================================================
        #noise_model=None
        Alice_processor=QuantumProcessor("processor_A", num_positions=2*10**2,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=5, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=3700,quantum_noise_model=processorNoiseModel, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=3700,quantum_noise_model=processorNoiseModel, parallel=True)])


        Bob_processor=QuantumProcessor("processor_B", num_positions=2*10**2,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=5, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=3700,quantum_noise_model=processorNoiseModel, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=3700,quantum_noise_model=processorNoiseModel, parallel=True)])


        # channels==================================================================
        
        MyQChannel=QuantumChannel("QChannel_A->B",delay=qdelay
            ,length=fibreLen
            ,models={"myFibreLossModel": FibreLossModel(p_loss_init=0, p_loss_length=0, rng=None)
            ,"mydelay_model": FibreDelayModel(c=qSpeed)
            ,"myFibreNoiseModel":DepolarNoiseModel(depolar_rate=fibreNoise, time_independent=False)})
        
        
        nodeA.connect_to(nodeB, MyQChannel,
            local_port_name =nodeA.ports["portQA_1"].name,
            remote_port_name=nodeB.ports["portQB_1"].name)
        

        MyCChannel = ClassicalChannel("CChannel_B->A",delay=0,length=fibreLen
            ,models={"myCDelayModel": FibreDelayModel(c=cSpeed)})
        MyCChannel2= ClassicalChannel("CChannel_A->B",delay=0,length=fibreLen
            ,models={"myCDelayModel": FibreDelayModel(c=cSpeed)})
        

        nodeB.connect_to(nodeA, MyCChannel,
                            local_port_name="portCB_1", remote_port_name="portCA_1")
        nodeA.connect_to(nodeB, MyCChannel2,
                            local_port_name="portCA_2", remote_port_name="portCB_2")

        
        
        Alice_protocol = BB84_Alice.AliceProtocol(nodeA,Alice_processor,num_bits,sourceFreq=sourceFreq)
        Bob_protocol = BB84_Bob.BobProtocol(nodeB,Bob_processor,num_bits)
        Bob_protocol.start()
        Alice_protocol.start()
        #ns.logger.setLevel(1)

        startTime=ns.util.simtools.sim_time(magnitude=ns.NANOSECOND)
        mylogger.debug("startTime:{}\n".format(startTime))
        stats = ns.sim_run()
        
        endTime=Bob_protocol.endTime
        mylogger.debug("endTime:{}\n".format(endTime))
        
        
        # apply loss
        mylogger.debug("Alice's key before loss:{}\n".format(Alice_protocol.key))
        mylogger.debug("Bob's key before loss:{}\n".format(Bob_protocol.key))

        firstKey,secondKey=ManualFibreLossModel(key1=Alice_protocol.key,key2=Bob_protocol.key,numNodes=2
            ,fibreLen=fibreLen,iniLoss=0,lenLoss=lenLoss,algorithmFator=2) 
        
        mylogger.debug("Alice's key after loss:{}\n".format(firstKey))
        mylogger.debug("Bob's key after loss:{}\n".format(secondKey))


        
        MyKeyList_A.append(firstKey)
        MyKeyList_B.append(secondKey)
        

        mylogger.debug("Time used:{}\n".format((endTime-startTime)/10**9))
        
        #simple key length calibration
        s = SequenceMatcher(None, firstKey, secondKey)# unmatched rate
        MyKeyRateList.append(len(secondKey)*s.ratio()/(endTime-startTime)*10**9) #second

        mylogger.debug("key length:{}\n".format(len(secondKey)*s.ratio()))

        
    return MyKeyList_A, MyKeyList_B, MyKeyRateList








