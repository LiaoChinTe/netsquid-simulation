import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
#from netsquid.protocols import NodeProtocol

from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *

from netsquid.components.qprogram import *
from netsquid.components.models.qerrormodels import *

from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel

from netsquid.components.models.qerrormodels import FibreLossModel
from netsquid.components.models.delaymodels import FibreDelayModel
#from pydynaa.core import Entity,EventHandler,EventType

from random import randint


from QToken_Alice import *
from QToken_Bob import * 



# implementation & hardware configure
def run_QToken_sim(runTimes=1,num_bits=100,fibre_len=0,waitTime=1,
        processNoiseModel=None,memNoiseModel=None,threshold=0.875,
        fibreLoss_init=0.2,fibreLoss_len=0.25,QChV=2.083*10**-4,CChV=2.083*10**-4):
    
    resList=[]
    
    for i in range(runTimes): 
        
        ns.sim_reset()

        # nodes====================================================================

        nodeA = Node("Alice", port_names=["portQA_1","portCA_1","portCA_2"])
        nodeB = Node("Bob"  , port_names=["portQB_1","portCB_1","portCB_2"])

        # processors===============================================================
        #noise_model=None
        Alice_processor=QuantumProcessor("processor_A", num_positions=2*10**5,
            mem_noise_models=memNoiseModel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=1, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=10,quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10,quantum_noise_model=processNoiseModel, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10,quantum_noise_model=processNoiseModel, parallel=True)])


        Bob_processor=QuantumProcessor("processor_B", num_positions=2*10**5,
            mem_noise_models=memNoiseModel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=1, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=10,quantum_noise_model=processNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10,quantum_noise_model=processNoiseModel, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10,quantum_noise_model=processNoiseModel, parallel=True)])


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
        
        

        Alice_protocol = AliceProtocol(nodeA,Alice_processor,num_bits,waitTime=waitTime)
        Bob_protocol = BobProtocol(nodeB,Bob_processor,num_bits,threshold=threshold)
        Bob_protocol.start()
        Alice_protocol.start()
        #ns.logger.setLevel(1)
        stats = ns.sim_run()
        
        resList.append(Bob_protocol.successfulRate) 
        print("Bob_protocol.successfulRate:",Bob_protocol.successfulRate)

    if not resList:
        return sum(resList)/len(resList)
        #return resList
    else:
        return 0


myMemNoise=T1T2NoiseModel(T1=10**6, T2=10**5)
myProcessNoise=DephaseNoiseModel(dephase_rate=0.004)



res=run_QToken_sim(runTimes=1,num_bits=100,fibre_len=10**-9,waitTime=10
    ,processNoiseModel=None,memNoiseModel=myMemNoise,threshold=0.875
    ,fibreLoss_init=0,fibreLoss_len=0,QChV=2.083*10**-4,CChV=2.083*10**-4)
print("res:",res," ")







