import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *
from netsquid.components.qprogram import *
from netsquid.components.models import  FibreDelayModel
from netsquid.components.models.qerrormodels import *
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel


from RPS_server import *
from RPS_client import *


# implementation & hardware configure
def run_RSP_sim(NumOfClients=1,fibre_len=10**-9,processorNoiseModel=None
    ,memNoiseMmodel_S=None,memNoiseMmodel_C=None
    ,loss_init=0,loss_len=0,QChV=3*10**2,CChV=3*10**2):
    
    
    set_qstate_formalism(QFormalism.DM)
    ns.sim_reset()

    # create server components

    ## nodes====================================================================
    ServerPortList=[]
    for i in range(NumOfClients): 
        ServerPortList.append("portQS_"+str(i+1)) #number from 1 to NumOfClients

    nodeServer = Node("Server", port_names=ServerPortList)

    ## processors===============================================================
        
    processorServer=QuantumProcessor("processorServer", num_positions=NumOfClients,
        mem_noise_models=memNoiseMmodel_S, phys_instructions=[
        PhysicalInstruction(INSTR_CNOT,duration=20000,quantum_noise_model=processorNoiseModel),
        PhysicalInstruction(INSTR_MEASURE, duration=3700, parallel=True),
        PhysicalInstruction(INSTR_MEASURE_X, duration=3700, parallel=True)])


    # create clients components

    nodeClientList=[]
    processorClientList=[]
    QchanelList=[]
    for i in range(NumOfClients): 

        ## nodes====================================================================

        nodeClientList.append(Node("Client_"+str(i+1)  , port_names=["portQC_1"]))

        ## processors===============================================================
    
        processorClientList.append(QuantumProcessor("processorClient_"+str(i+1), num_positions=1,
            mem_noise_models=memNoiseMmodel_C, phys_instructions=[
            PhysicalInstruction(INSTR_R45, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_R90, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_R135, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_R180, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_R225, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_R270, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_R315, duration=20000, parallel=True),
                
                
            PhysicalInstruction(INSTR_Rv45, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_Rv90, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_Rv135, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_Rv180, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_Rv225, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_Rv270, duration=20000, parallel=True),
            PhysicalInstruction(INSTR_Rv315, duration=20000, parallel=True)]))



        # Quantum channels==================================================================
        
        QchanelList.append(QuantumChannel("QChannel_C->S_"+str(i+1),delay=0,length=fibre_len
            ,models={"quantum_loss_model": FibreLossModel(p_loss_init=loss_init, p_loss_length=loss_len, rng=None)
            ,"delay_model": FibreDelayModel(c=QChV)}))
        
        ## connect ports
        nodeClientList[i].connect_to(nodeServer, QchanelList[i],
            local_port_name =nodeClientList[i].ports["portQC_1"].name,
            remote_port_name=nodeServer.ports["portQS_"+str(i+1)].name)


        protocolRSP_Client = RSP_Client(nodeClientList[i],processorClientList[i],NumOfClients)



    protocolRSP_Server = RSP_Server(nodeServer,processorServer,NumOfClients)
    
    

    protocolRSP_Server.start()
    for i in range(NumOfClients):
        protocolRSP_Client.start()
    
    #ns.logger.setLevel(1)
    stats = ns.sim_run()
        



'''
# run simulation

runs=10

for k in range(runs):
    # input value test===========================================================
    

    #print(ns.__version__)

    mymemNoiseMmodel=T1T2NoiseModel(T1=36000*10**9, T2=10**9) #1.46
    #myProccessorNoiseModel1=DephaseNoiseModel(dephase_rate=0.01,time_independent=True)
    myProccessorNoiseModel2=DepolarNoiseModel(depolar_rate=0.01,time_independent=True)

    res=run_RSP_sim()

    #print(res)

'''