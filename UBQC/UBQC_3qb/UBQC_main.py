import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *
from netsquid.components.qprogram import *
from netsquid.components.models import  FibreDelayModel
from netsquid.components.models.qerrormodels import *
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel


from UBQC_server import *

import sys
scriptpath = "compute/"
sys.path.append(scriptpath)
scriptpath = "verify/"
sys.path.append(scriptpath)

from UBQC_client_compute import *
from UBQC_client_verify import *

NUM_QBITS=3

# implementation & hardware configure
def run_UBQC_sim(x,phi,runBoolArray=[0,1],fibre_len=10**-9,processorNoiseModel=None,memNoiseMmodel=None,
    loss_init=0,loss_len=0,QChV=3*10**2,CChV=3*10**2,threshold=0.9): #loss_init=0.25,loss_len=0.2
    
    
    verifyFailCount=0
    outputList=[]
    set_qstate_formalism(QFormalism.DM)

    for i,j in enumerate(runBoolArray): 
        
        ns.sim_reset()
        

        # nodes====================================================================

        nodeServer = Node("Server", port_names=["portQS_1","portCS_1","portCS_2"])
        nodeClient = Node("Client"  , port_names=["portQC_1","portCC_1","portCC_2"])

        # processors===============================================================
        
        processorServer=QuantumProcessor("processorServer", num_positions=NUM_QBITS*2,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=5, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=10,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CZ,duration=10,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10, parallel=True),
            PhysicalInstruction(INSTR_R45, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R90, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R135, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R180, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R225, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R270, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R315, duration=20, parallel=True),
                
            PhysicalInstruction(INSTR_Rv45, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv90, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv135, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv180, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv225, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv270, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv315, duration=20, parallel=True),])
        
        
        
        processorClient=QuantumProcessor("processorClient", num_positions=NUM_QBITS,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=5, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=5, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=10,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10, parallel=True),
            PhysicalInstruction(INSTR_R45, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R90, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R135, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R180, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R225, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R270, duration=20, parallel=True),
            PhysicalInstruction(INSTR_R315, duration=20, parallel=True),
                
                
            PhysicalInstruction(INSTR_Rv45, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv90, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv135, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv180, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv225, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv270, duration=20, parallel=True),
            PhysicalInstruction(INSTR_Rv315, duration=20, parallel=True)])


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
        

        # Channel connections ========================================================
        nodeClient.connect_to(nodeServer, MyCChannel,
                            local_port_name="portCC_1", remote_port_name="portCS_1")
        nodeServer.connect_to(nodeClient, MyCChannel2,
                            local_port_name="portCS_2", remote_port_name="portCC_2")


        


        protocolServer = ProtocolServer(nodeServer,processorServer)
        if j==1: # Compute case
            protocolClient = ProtocolClient_C(nodeClient,processorClient,x=x,phi=phi,rounds=i)
        else :   # Verify case
            protocolClient = ProtocolClient_V(nodeClient,processorClient,rounds=i)

        protocolServer.start()
        protocolClient.start()
        #ns.logger.setLevel(1)
        stats = ns.sim_run()
        
        if j==1:
            outputList.append(protocolClient.output)
        
        elif j==0 and protocolClient.output==0 :  # protocolClient.output==0 means not verified
            verifyFailCount+=1

    
    
    if verifyFailCount/len(runBoolArray)>threshold: # abort case
        return -1
    

    if sum(outputList)/len(outputList)>=0.5:  #count avg to see whuch (0 or 1) is closer
        return 1
    else:
        return 0
    



# run simulation

runs=3000
failCount=0
abortCount=0

for k in range(runs):
    # input value test===========================================================
    phi1=randint(0,7)
    x=randint(0,1)
    phi=[phi1,0,-phi1]

    #print(ns.__version__)
    #runBoolArray 1:comute case   0:verify case: 1: pass
    myNoiseModel=DephaseNoiseModel(dephase_rate=0.01,time_independent=True)
    res=run_UBQC_sim(x=x,phi=[phi1,0,-phi1],runBoolArray=[0,1,0,1,0,1,0,1,0,1],
        fibre_len=10**-9,processorNoiseModel=myNoiseModel,memNoiseMmodel=None,loss_init=0,loss_len=0,threshold=0.9)
    if res == -1:
        abortCount+=1
    elif x!=res:
        failCount+=1
    #print(res)

avgAbortRate=abortCount/runs
avgCorrectRate=(runs-abortCount-failCount)/(runs-abortCount)
print("avgCorrectRate:",avgCorrectRate,"\navgAbortRate:",avgAbortRate)