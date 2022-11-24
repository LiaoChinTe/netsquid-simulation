import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.nodes.connections import DirectConnection
from netsquid.components.models import  FibreDelayModel,QuantumErrorModel,FibreLossModel
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel

from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import QuantumProcessor,PhysicalInstruction
from netsquid.components.instructions import INSTR_CZ,INSTR_H,INSTR_MEASURE,INSTR_MEASURE_X
from netsquid.components.models.qerrormodels import T1T2NoiseModel,DepolarNoiseModel,DephaseNoiseModel

from random import randint
from difflib import SequenceMatcher

import QrotationTest_Alice

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import INSTR_R45,INSTR_R90,INSTR_R135,INSTR_R180,INSTR_R225,INSTR_R270,INSTR_R315,INSTR_Rv45,INSTR_Rv90,INSTR_Rv135,INSTR_Rv180,INSTR_Rv225,INSTR_Rv270,INSTR_Rv315



import logging
#logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)



def run_QrotationTest_sim(processorNoice=None,num_bits=1):

    

    ns.sim_reset()
    NodeAlice=Node("NodeAlice", port_names=["portQI","portQO","portCO"]) 
 

    # create processor===========================================================
    ProcessorAlice=QuantumProcessor("ProcessorAlice", num_positions=2,
        mem_noise_models=None, phys_instructions=[
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processorNoice),
            PhysicalInstruction(INSTR_MEASURE, duration=3700, quantum_noise_model=processorNoice, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=3700, quantum_noise_model=processorNoice, parallel=True),
            PhysicalInstruction(INSTR_CZ, duration=20000, quantum_noise_model=processorNoice, parallel=True),
            PhysicalInstruction(INSTR_R45, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R90, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R135, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R180, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R225, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R270, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R315, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_Rv45, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_Rv90, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_Rv135, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_Rv180, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_Rv225, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_Rv270, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_Rv315, duration=20000, quantum_noise_model=processorNoice,parallel=True)])

  


    myAliceProtocol=QrotationTest_Alice.QrotationTest_AliceProtocol(node=NodeAlice,processor=ProcessorAlice,num_bits=num_bits) 


    myAliceProtocol.start()
    
    #ns.logger.setLevel(1)


    #TimeStart=ns.util.simtools.sim_time(magnitude=ns.NANOSECOND)
    ns.sim_run()
    #print("myAliceProtocol.m:",myAliceProtocol.m)

    
    return myAliceProtocol.m







