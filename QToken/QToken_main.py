import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node

from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *

from netsquid.components.qprogram import *
from netsquid.components.models.qerrormodels import *

from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel

from netsquid.components.models.qerrormodels import FibreLossModel
from netsquid.components.models.delaymodels import FibreDelayModel

from random import randint
from netsquid.components.instructions import *

import math


import QToken_Alice 
import QToken_Bob

#from QToken import QToken_Alice
#from QToken import QToken_Bob


# implementation & hardware configure
def run_QToken_sim(runTimes=1,num_bits=10000,fibre_len=0,waitTime=1,
        processNoiseModel=None,memNoiseModel=None,threshold=0.875,
        fibreLoss_init=0,fibreLoss_len=0,QChV=2.083*10**-4,CChV=2.083*10**-4):
    
    resList=[]

    #print('received a noise model with T1: {} and T2: {}'.format(memNoiseModel.T1, memNoiseModel.T2))

    for i in range(runTimes): 
        
        ns.sim_reset()

        # nodes====================================================================

        nodeA = Node("Alice", port_names=["portQA_1","portCA_1","portCA_2"])
        nodeB = Node("Bob"  , port_names=["portQB_1","portCB_1","portCB_2"])

        # processors===============================================================
        #noise_model=None
        Alice_processor=QuantumProcessor("processor_A", num_positions=2*10**4,
            mem_noise_models=memNoiseModel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=5, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=5, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=10,quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=3700,quantum_noise_model=None, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=3700,quantum_noise_model=None, parallel=True)])


        Bob_processor=QuantumProcessor("processor_B", num_positions=2*10**4,
            mem_noise_models=memNoiseModel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=5, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=5, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=10,quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=3700,quantum_noise_model=None, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=3700,quantum_noise_model=None, parallel=True)])


        # channels==================================================================
        
        MyQChannel=QuantumChannel("QChannel_B->A",length=fibre_len
            ,models={"quantum_loss_model":
            FibreLossModel(p_loss_init=fibreLoss_init,p_loss_length=fibreLoss_len, rng=None),
            "delay_model": FibreDelayModel(c=QChV)})
        
        
        nodeB.connect_to(nodeA, MyQChannel,
            local_port_name =nodeB.ports["portQB_1"].name,
            remote_port_name=nodeA.ports["portQA_1"].name)
        
        
        MyCChannel= ClassicalChannel("CChannel_A->B",delay=fibre_len/CChV
            ,length=fibre_len)
        MyCChannel2 = ClassicalChannel("CChannel_B->A",delay=fibre_len/CChV
            ,length=fibre_len)
        
        
        nodeA.connect_to(nodeB, MyCChannel,
                            local_port_name="portCA_1", remote_port_name="portCB_1")
        nodeB.connect_to(nodeA, MyCChannel2,
                            local_port_name="portCB_2", remote_port_name="portCA_2")
        
        

        Alice_protocol = QToken_Alice.AliceProtocol(nodeA,Alice_processor,num_bits
            ,waitTime=waitTime,bitFlip0=0.95,bitFlip1=0.995)
        Bob_protocol = QToken_Bob.BobProtocol(nodeB,Bob_processor,num_bits,threshold=threshold)
        Bob_protocol.start()
        Alice_protocol.start()
        #ns.logger.setLevel(1)
        stats = ns.sim_run()
        
        resList.append(Bob_protocol.successfulRate) 
        #print("Bob_protocol.successfulRate:",Bob_protocol.successfulRate)
    
    if resList:
        # return sum(resList)/len(resList), np.std(resList) / np.sqrt(len(resList))
        return resList
    else:
        return 0
    

    
    #return MyCostFunction(t1=36*10**12,t2=4.9*10**6,p1=0.95,p2=0.995,Srate=Bob_protocol.successfulRate,T=10**6)


if __name__ == '__main__':
    myMemNoise=T1T2NoiseModel(T1=36*10**13, T2=10**9)  #6.4*4.9*10**6
    #myProcessNoise=DephaseNoiseModel(dephase_rate=0.004)

    res=run_QToken_sim(runTimes=10,num_bits=10**4,fibre_len=10**-9,waitTime=10**9
        ,processNoiseModel=None,memNoiseModel=myMemNoise,threshold=0.875
        ,fibreLoss_init=0,fibreLoss_len=0,QChV=2.083*10**-4,CChV=2.083*10**-4)
    print("res:",res," ")
