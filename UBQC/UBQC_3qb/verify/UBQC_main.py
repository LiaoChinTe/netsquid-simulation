import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *
from netsquid.components.qprogram import *
from netsquid.components.models import  FibreDelayModel
from netsquid.components.models.qerrormodels import *
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel

from UBQC_client_verify import *

import sys
scriptpath = "../"
sys.path.append(scriptpath)

from UBQC_server import *


# implementation & hardware configure
def run_UBQC_sim(runtimes=1,fibre_len=10**-9,processorNoiseModel=None,memNoiseMmodel=None
               ,loss_init=0,loss_len=0,QChV=3*10**2,CChV=3*10**2): #loss_init=0.25,loss_len=0.2
    
    resList=[]
    successCount=0
    set_qstate_formalism(QFormalism.DM)
    
    
    for i in range(runtimes): 
        
        ns.sim_reset()

        # nodes====================================================================

        nodeServer = Node("Server", port_names=["portQS_1","portCS_1","portCS_2"])
        nodeClient = Node("Client"  , port_names=["portQC_1","portCC_1","portCC_2"])

        # processors===============================================================
        
        processorServer=QuantumProcessor("processorServer", num_positions=10,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=1,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CZ,duration=10,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10, parallel=True),
            PhysicalInstruction(INSTR_R45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R180, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R225, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R270, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R315, duration=1, parallel=True),
                
            PhysicalInstruction(INSTR_Rv45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv180, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv225, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv270, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv315, duration=1, parallel=True),
            
            PhysicalInstruction(INSTR_SWAP, duration=1, parallel=True)])
        
        
        
        processorClient=QuantumProcessor("processorClient", num_positions=10,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=10,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10, parallel=True),
            PhysicalInstruction(INSTR_R45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R180, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R225, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R270, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R315, duration=1, parallel=True),
                
                
            PhysicalInstruction(INSTR_Rv45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv180, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv225, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv270, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv315, duration=1, parallel=True)])


        # Quantum channels==================================================================
        
        
        MyQChannel=QuantumChannel("QChannel_S->C",delay=0,length=fibre_len
            ,models={"quantum_loss_model": FibreLossModel(p_loss_init=loss_init, p_loss_length=loss_len, rng=None)
            ,"delay_model": FibreDelayModel(c=QChV)})
        
        nodeServer.connect_to(nodeClient, MyQChannel,
            local_port_name =nodeServer.ports["portQS_1"].name,
            remote_port_name=nodeClient.ports["portQC_1"].name)
        
        # Classical channels ========================================================
        MyCChannel = ClassicalChannel("CChannel_C->S",delay=0
            ,length=fibre_len)
        MyCChannel2= ClassicalChannel("CChannel_S->C",delay=0
            ,length=fibre_len)
        

        nodeClient.connect_to(nodeServer, MyCChannel,
                            local_port_name="portCC_1", remote_port_name="portCS_1")
        nodeServer.connect_to(nodeClient, MyCChannel2,
                            local_port_name="portCS_2", remote_port_name="portCC_2")


        protocolServer = ProtocolServer(nodeServer,processorServer)
        protocolClient = ProtocolClient_V(nodeClient,processorClient,1)
        protocolServer.start()
        protocolClient.start()
        #ns.logger.setLevel(1)
        stats = ns.sim_run()
        
        
        resList.append(protocolClient.verified)
        
        
        
    for i in resList:
        if i==True:
            successCount+=1

    return successCount/runtimes


#print(ns.__version__)
res=run_UBQC_sim(runtimes=100,fibre_len=10**-9
    ,processorNoiseModel=None,memNoiseMmodel=None,loss_init=0,loss_len=0)

print(res)
