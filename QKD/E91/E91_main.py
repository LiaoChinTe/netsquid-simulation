import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.qubits.operators import X,H,Z
from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *
from netsquid.components.instructions import *
from netsquid.components.models.qerrormodels import *
from random import randint
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel
from netsquid.components.models.qerrormodels import FibreLossModel

from difflib import SequenceMatcher

import E91_Alice
import E91_Bob

'''

Key length filter

# function that filters vowels 
def lenfilter(var): 
    if len(var) <= 10 and len(var) > 6: 
        return True
    else: 
        return False
'''  
    


# implementation & hardware configure

def run_E91_sim(runtimes=1,num_bits=20,fibre_len=10**-9,memNoiseMmodel=None,processorNoiseModel=None
               ,loss_init=0,loss_len=0):
    
    MyE91List_A=[]  # local protocol list A
    MyE91List_B=[]  # local protocol list B
    MyKeyRateList=[]
    
    for i in range(runtimes): 
        
        ns.sim_reset()

        # nodes====================================================================

        nodeA = Node("Alice", port_names=["portQA_1","portCA_1","portCA_2"])
        nodeB = Node("Bob"  , port_names=["portQB_1","portCB_1","portCB_2"])

        # processors===============================================================
        #noise_model=None
        Alice_processor=QuantumProcessor("processor_A", num_positions=3*10**3,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_INIT, duration=1, parallel=True),
            PhysicalInstruction(INSTR_X, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=10,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10,quantum_noise_model=processorNoiseModel, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10,quantum_noise_model=processorNoiseModel, parallel=True)])


        Bob_processor=QuantumProcessor("processor_B", num_positions=3*10**3,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_INIT, duration=1, parallel=True),
            PhysicalInstruction(INSTR_X, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=1,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10,quantum_noise_model=processorNoiseModel, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10,quantum_noise_model=processorNoiseModel, parallel=True)])


        # channels==================================================================
        
        MyQChannel=QuantumChannel("QChannel_A->B",delay=10
            ,length=fibre_len
            ,models={"myFibreLossModel": FibreLossModel(p_loss_init=0.2, p_loss_length=0.25, rng=None)})
        
        
        nodeA.connect_to(nodeB, MyQChannel,
            local_port_name =nodeA.ports["portQA_1"].name,
            remote_port_name=nodeB.ports["portQB_1"].name)
        

        MyCChannel = ClassicalChannel("CChannel_B->A",delay=0
            ,length=fibre_len)
        MyCChannel2= ClassicalChannel("CChannel_A->B",delay=0
            ,length=fibre_len)
        

        nodeB.connect_to(nodeA, MyCChannel,
                            local_port_name="portCB_1", remote_port_name="portCA_1")
        nodeA.connect_to(nodeB, MyCChannel2,
                            local_port_name="portCA_2", remote_port_name="portCB_2")

        
        startTime=ns.sim_time()
        #print("startTime:",startTime)
        
        Alice_protocol = E91_Alice.AliceProtocol(nodeA,Alice_processor,num_bits)
        Bob_protocol = E91_Bob.BobProtocol(nodeB,Bob_processor,num_bits)
        Bob_protocol.start()
        Alice_protocol.start()
        #ns.logger.setLevel(1)
        stats = ns.sim_run()
        
        endTime=Bob_protocol.endTime
        #print("endTime:",endTime)
        
        MyE91List_A.append(Alice_protocol.key)
        MyE91List_B.append(Bob_protocol.key)
        
        
        #simple key length calibration
        s = SequenceMatcher(None, Alice_protocol.key, Bob_protocol.key)# unmatched rate
        MyKeyRateList.append((len(Bob_protocol.key)*(1-s.ratio()))*10**9/(endTime-startTime)) #second
        
    return MyE91List_A, MyE91List_B, MyKeyRateList






#test
if __name__ == "__main__":
        
    mymemNoiseMmodel=T1T2NoiseModel(T1=11, T2=10)
    myprocessorNoiseModel=DepolarNoiseModel(depolar_rate=500)

    toWrite=run_E91_sim(runtimes=2,num_bits=20,fibre_len=20
            ,memNoiseMmodel=mymemNoiseMmodel,processorNoiseModel=myprocessorNoiseModel) #10**-9
    print(toWrite)




'''
# key pairs generation

#myErrorModel=DepolarNoiseModel(depolar_rate=50000)
myErrorModel=T1T2NoiseModel(T1=1100, T2=1000)
toWrite=run_E91_sim(runtimes=1,num_bits=10**4,fibre_len=10,noise_model=myErrorModel) #10**-9
#print(toWrite)

listToPrint=''
listToPrint=str(toWrite)
print(listToPrint)
outF = open("keyOutput8.txt", "w")
outF.writelines(listToPrint)
outF.close()
'''

