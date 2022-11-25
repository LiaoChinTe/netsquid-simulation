from distutils.log import error
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

import MBQC_Alice
import MBQC_Source
import MBQC_Bob
import MBQC_TEE
import MBQC_Server




import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import ManualFibreLossModel,INSTR_R45,INSTR_R90,INSTR_R135,INSTR_R180,INSTR_R225,INSTR_R270,INSTR_R315,INSTR_Rv45,INSTR_Rv90,INSTR_Rv135,INSTR_Rv180,INSTR_Rv225,INSTR_Rv270,INSTR_Rv315



import logging
#logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)



def run_MBQC_Qline_sim(fibreLen=10,processorNoice=None,momNoise=None
    ,qSpeed=2*10**5,cSpeed=2*10**5,source_frq=1e9,fibreNoise=0):

    

    ns.sim_reset()

    NodeSource=Node("NodeSource", port_names=["portQO"])                  # quantum/classical input/output
    NodeAlice=Node("NodeAlice", port_names=["portQI","portQO","portCO"]) 
    NodeBob=Node("NodeBob"  , port_names=["portQI","portQO","portCO"]) 
    NodeServer=Node("NodeServer"  , port_names=["portQI","portC"]) 
    NodeTEE=Node("NodeTEE"  , port_names=["portC1","portC2","portC3"]) 
 

    # create processor===========================================================
    ProcessorSource=QuantumProcessor("ProcessorSource", num_positions=2,
        mem_noise_models=momNoise, phys_instructions=[
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processorNoice),
            PhysicalInstruction(INSTR_CZ, duration=3700, quantum_noise_model=processorNoice)])

    ProcessorAlice=QuantumProcessor("ProcessorAlice", num_positions=2,
        mem_noise_models=momNoise, phys_instructions=[
            PhysicalInstruction(INSTR_R45, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R90, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R135, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R180, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R225, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R270, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R315, duration=20000, quantum_noise_model=processorNoice,parallel=True)])

    ProcessorBob=QuantumProcessor("ProcessorBob", num_positions=2,
        mem_noise_models=momNoise, phys_instructions=[
            PhysicalInstruction(INSTR_R45, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R90, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R135, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R180, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R225, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R270, duration=20000, quantum_noise_model=processorNoice,parallel=True),
            PhysicalInstruction(INSTR_R315, duration=20000, quantum_noise_model=processorNoice,parallel=True)])


    ProcessorServer=QuantumProcessor("ProcessorServer", num_positions=2,
        mem_noise_models=momNoise, phys_instructions=[
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processorNoice),
            PhysicalInstruction(INSTR_MEASURE, duration=3700, quantum_noise_model=processorNoice, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=3700, quantum_noise_model=processorNoice, parallel=True),
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

    # No Q processor needed for TEE

            
    # channels in between nodes==============================================================


    # Q channels(one way cannel)==================================================================

    MyQChannel1=QuantumChannel("QChannel_1",delay=0,length=fibreLen
        ,models={"myQFibreLossModel": FibreLossModel(p_loss_init=0, p_loss_length=0, rng=None)
        ,"myDelayModel": FibreDelayModel(c=qSpeed)
        ,"myFibreNoiseModel":DepolarNoiseModel(depolar_rate=fibreNoise, time_independent=False)}) # c km/s

    MyQChannel2=QuantumChannel("QChannel_2",delay=0,length=fibreLen
        ,models={"myQFibreLossModel": FibreLossModel(p_loss_init=0, p_loss_length=0, rng=None)
        ,"myDelayModel": FibreDelayModel(c=qSpeed)
        ,"myFibreNoiseModel":DepolarNoiseModel(depolar_rate=fibreNoise, time_independent=False)}) # c km/s

    MyQChannel3=QuantumChannel("QChannel_2",delay=0,length=fibreLen
        ,models={"myQFibreLossModel": FibreLossModel(p_loss_init=0, p_loss_length=0, rng=None)
        ,"myDelayModel": FibreDelayModel(c=qSpeed)
        ,"myFibreNoiseModel":DepolarNoiseModel(depolar_rate=fibreNoise, time_independent=False)}) # c km/s


    NodeSource.connect_to(NodeAlice, MyQChannel1,
        local_port_name =NodeSource.ports["portQO"].name,
        remote_port_name=NodeAlice.ports["portQI"].name)

    NodeAlice.connect_to(NodeBob, MyQChannel2,
        local_port_name =NodeAlice.ports["portQO"].name,
        remote_port_name=NodeBob.ports["portQI"].name)
    
    NodeBob.connect_to(NodeServer, MyQChannel3,
        local_port_name =NodeBob.ports["portQO"].name,
        remote_port_name=NodeServer.ports["portQI"].name)

    # C channals(bidirectional)==================================================================

    myCChannel_AliceToTEE = ClassicalChannel("myCChannel_AliceToTEE",delay=0,length=fibreLen
        ,models={"myCDelayModel": FibreDelayModel(c=cSpeed)})
    myCChannel_BobToTEE = ClassicalChannel("myCChannel_BobToTEE",delay=0,length=fibreLen
        ,models={"myCDelayModel": FibreDelayModel(c=cSpeed)})

    
    NodeAlice.connect_to(NodeTEE, myCChannel_AliceToTEE,local_port_name="portCO", remote_port_name="portC1")
    NodeBob.connect_to(NodeTEE, myCChannel_BobToTEE,local_port_name="portCO", remote_port_name="portC2")

    myCChannel_ServerToTEE = ClassicalChannel("MyCChannel_ServerToTEE",delay=0,length=fibreLen
        ,models={"myCDelayModel": FibreDelayModel(c=cSpeed)})
    myCChannel_TEEToServer = ClassicalChannel("MyCChannel_TEEToServer",delay=0,length=fibreLen
        ,models={"myCDelayModel": FibreDelayModel(c=cSpeed)})

    myDirectConnection=DirectConnection("Server_TEE_DirectConnection"
        ,channel_AtoB=myCChannel_ServerToTEE,channel_BtoA=myCChannel_TEEToServer)

    NodeServer.connect_to(NodeTEE, myDirectConnection,local_port_name="portC", remote_port_name="portC3")
        


    mySourceProtocol=MBQC_Source.MBQC_SourceProtocol(node=NodeSource,processor=ProcessorSource)
    myAliceProtocol=MBQC_Alice.MBQC_AliceProtocol(node=NodeAlice,processor=ProcessorAlice)
    myBobProtocol=MBQC_Bob.MBQC_BobProtocol(node=NodeBob,processor=ProcessorBob)
    myTEEProtocol=MBQC_TEE.MBQC_TEEProtocol(node=NodeTEE)
    myServerProtocol=MBQC_Server.MBQC_ServerProtocol(node=NodeServer,processor=ProcessorServer) 


    myServerProtocol.start()
    myTEEProtocol.start()
    myBobProtocol.start()
    myAliceProtocol.start()
    mySourceProtocol.start()
    
    #ns.logger.setLevel(1)


    TimeStart=ns.util.simtools.sim_time(magnitude=ns.NANOSECOND)
    ns.sim_run()
    

    
    return myTEEProtocol.m1, myTEEProtocol.m2







