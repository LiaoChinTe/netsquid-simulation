from random import randint
from math import pi,sin,cos,exp

import numpy as np
import netsquid as ns

from netsquid.nodes.node import Node
from netsquid.components.instructions import *
from netsquid.components import QuantumMemory,QSource,Clock
from netsquid.components.qchannel import QuantumChannel 
from netsquid.components.cchannel import ClassicalChannel
from netsquid.components.models.qerrormodels import FibreLossModel
from netsquid.components.models.delaymodels import FibreDelayModel
from netsquid.components.qsource import SourceStatus
from netsquid.components.qprogram import *
from netsquid.components.models import DephaseNoiseModel,DepolarNoiseModel,T1T2NoiseModel

from netsquid.qubits.qubitapi import create_qubits

from ATw_center import *
from ATw_side import *


def createProcessorAT(name='defaultProcessor',num_positions=4,memNoiseModel=None,processorNoiseModel=None):


    # teleportation needs X Z
    # Anonymous Transmission needs CNOT, MEASURE, TOFFOLI, NToffoli
    myProcessor=QuantumProcessor(name, num_positions=num_positions,
        mem_noise_models=memNoiseModel, phys_instructions=[
        PhysicalInstruction(INSTR_X, duration=1  , quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_Z, duration=1  , quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_H, duration=1  , quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_CNOT,duration=1, quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_MEASURE, duration=10  , quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_TOFFOLI, duration=10, quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_NToffoli, duration=10, quantum_noise_model=processorNoiseModel, parallel=False)])
    
    return myProcessor


def AT_fidelityCalculate(originalDM,teleportedDM,theta_k):
    #print("AT_fidelityCalculate Fidelity:",np.trace(originalDM)+np.trace(teleportedDM))
    #print("teleportedDM:",teleportedDM)

    A=originalDM[0][0]*teleportedDM[0][0]+originalDM[0][1]*teleportedDM[1][0]
    B=originalDM[1][0]*teleportedDM[0][1]+originalDM[1][1]*teleportedDM[1][1]
    #print("a:",originalDM[0][0],"b:",teleportedDM[0][0],"c:",originalDM[0][1],"d:",teleportedDM[1][0])

    #print("A:\n",A)
    #print("B:\n",B)
    return (A+B)*sin(theta_k)




def run_AT_sim(runtimes=1,numNodes=4,fibre_len=10**-9,processorNoiseModel=None,memNoiseMmodel=None
    ,loss_init=0,loss_len=0,QChV=3*10**-4,t1=0,t2=0):

    sum_fidelity=0
    set_qstate_formalism(QFormalism.DM)

    for k in range(runtimes):

        for m in range(runtimes):
            #k=50
            #m=50
            success_flag=False

            while success_flag==False:

                # initialize
                ns.sim_reset()
                
                sideProcessorList=[]
                sideNodeList=[]
                centerQPortNameList=[]
                centerCPortNameList=[]
                QchannelList=[]
                CchannelList1=[]
                CchannelList2=[]

                '''
                senderID=randint(0,numNodes-1)
                receiverID=randint(0,numNodes-1)
                while receiverID==senderID:
                    receiverID=randint(0,numNodes-1)
                '''
                senderID=0
                receiverID=1

                

                
                # build star network hardware components
                ## create side processors, nodes, port, channel (depend on scale)===========================
                for i in range(numNodes):
                    ### processors================================================================
                    sideProcessorList.append(
                        createProcessorAT(name="ProcessorSide_"+str(i)
                        ,memNoiseModel=memNoiseMmodel,processorNoiseModel=processorNoiseModel))
                    
                    ### nodes=====================================================================
                    #### add additional ports for teleportation
                    if i == senderID:
                        sideNodeList.append(Node("Node_"+str(i), port_names=["PortQside","PortCside1","PortCside2","PortTele_S"]))
                    elif i == receiverID:
                        sideNodeList.append(Node("Node_"+str(i), port_names=["PortQside","PortCside1","PortCside2","PortTele_R"]))
                    else:
                        sideNodeList.append(Node("Node_"+str(i), port_names=["PortQside","PortCside1","PortCside2"]))
                    
                    ### channels, Quantum and calssical=============================================
                    QchannelList.append(QuantumChannel("QChannel_Center->Side_"+str(i),delay=10,length=fibre_len
                        ,models={"quantum_loss_model":
                        FibreLossModel(p_loss_init=loss_init,p_loss_length=loss_len, rng=None),
                        "delay_model": FibreDelayModel(c=QChV)}))

                    CchannelList1.append(ClassicalChannel("CChannel_Side->Center_"+str(i),delay=10,length=fibre_len))
                    CchannelList2.append(ClassicalChannel("CChannel_Center->Side_"+str(i),delay=10,length=fibre_len))

                    #### add channel for teleportation
                    myTeleportChannel=ClassicalChannel("CChannel_Sender->Receiver",delay=10,length=fibre_len)

                    ### record port list for center node===========================================
                    centerQPortNameList.append("PortQcenter_"+str(i))
                    centerCPortNameList.append("PortCcenter1_"+str(i))
                    centerCPortNameList.append("PortCcenter2_"+str(i))

                ## create center node and processor=======================================================
                allCenterPorts=[]
                allCenterPorts.extend(centerQPortNameList)
                allCenterPorts.extend(centerCPortNameList)
                #print("allCenterPorts: ",allCenterPorts)

                CenterNode=Node("CenterNode", port_names=allCenterPorts)
                CenterProcessor=createProcessorAT(name="ProcessorCenter")
                


                ## connect(depend on scale)==================================================================
                for i in range(numNodes):    
                    ### Quantum Center to side
                    CenterNode.connect_to(sideNodeList[i], QchannelList[i],
                        local_port_name =CenterNode.ports["PortQcenter_"+str(i)].name,
                        remote_port_name=sideNodeList[i].ports["PortQside"].name)

                    ### Classical side to Center
                    tmpRemotePortName="PortCcenter1_"+str(i)
                    #print("connecting classical channel:",i," side node:",sideNodeList[i].name," channel:",CchannelList1[i].name,"remote port:", tmpRemotePortName )
                    sideNodeList[i].connect_to(CenterNode, CchannelList1[i],
                        local_port_name="PortCside1", remote_port_name=tmpRemotePortName)
                    
                    ### Classical Center to side
                    tmpRemotePortName="PortCcenter2_"+str(i)
                    #print("connecting classical channel:",i," side node:",sideNodeList[i].name," channel:",CchannelList2[i].name,"remote port:", tmpRemotePortName )
                    CenterNode.connect_to(sideNodeList[i], CchannelList2[i],
                        local_port_name=tmpRemotePortName , remote_port_name="PortCside2")
                    
                ### Classical teleport channel
                sideNodeList[senderID].connect_to(sideNodeList[receiverID], myTeleportChannel,
                    local_port_name="PortTele_S", remote_port_name="PortTele_R")
                
                
                # make original qubits
                dmList=[]
                theta_k=pi/(2*runtimes)+k*pi/runtimes
                phi_m=pi/runtimes+2*m*pi/runtimes
                #print("phi_m:",phi_m)
                #print("i:",i)
                dm1=(cos(theta_k/2))**2
                #print("exp(i*phi_m):",exp(i*phi_m))
                #exp(1j*phi_m)
                #exp((-1j)*phi_m)
                dm2=cos(theta_k/2)*sin(theta_k/2)*(cos(phi_m)+1j*sin(phi_m))
                dm3=cos(theta_k/2)*sin(theta_k/2)*(cos(phi_m)-1j*sin(phi_m))
                dm4=(sin(theta_k/2))**2

                dmList.append(np.array([[dm1,dm2],[dm3,dm4]])) 
                #dmList.append(np.array([[0.36,0.48],[0.48,0.64]]))
                
                oriQubitList = create_qubits(1)
                #print("S oriQubitList:\n",oriQubitList,"\ndmList:",dmList)
                newQubitList=AssignStatesBydm(oriQubitList,dmList)
                #print("MAIN Qubit state to be teleport:\n",newQubitList[0].qstate.qrepr.reduced_dm())
                #operate(newQubitList[0], H)


                # create protocol object
                myProtocol_center = AT_Wstate_center(CenterNode,CenterProcessor,numNodes
                    ,portQlist=centerQPortNameList,portClist=centerCPortNameList)
                myProtocol_sideList=[]
                ## create side protocol
                for i in range(numNodes):
                    if i==senderID:
                        # create sender
                        myProtocol_sideList.append(AT_Wstate_side(sideNodeList[i],sideProcessorList[i],id=i
                        , qubitToTeleport=newQubitList[0], sender=True,portClist=["PortCside1","PortCside2","PortTele_S"],t1=t1,t2=t2))
                    elif i==receiverID:
                        # create receiver
                        myProtocol_sideList.append(AT_Wstate_side(sideNodeList[i],sideProcessorList[i],id=i,receiver=True,
                            portClist=["PortCside1","PortCside2","PortTele_R"],t1=t1,t2=t2))
                    else:
                        # create normal side node
                        myProtocol_sideList.append(AT_Wstate_side(sideNodeList[i],sideProcessorList[i],id=i,t1=t1,t2=t2))
                    
                
                
                for sideProtocols in myProtocol_sideList:
                    sideProtocols.start()
                    
                myProtocol_center.start()
                
                
                #ns.logger.setLevel(1)
                ns.sim_run()
                
                if myProtocol_sideList[1].myQT_Receiver :
                    success_flag=True

                    # assigned state
                    #print("MAIN original receivedState:\n",dmList[0])

                    dm_tele=myProtocol_sideList[1].myQT_Receiver.receivedQubit.qstate.qrepr.reduced_dm()
                    #print("MAIN final receivedState:\n",dm_tele)
                    sum_fidelity+=AT_fidelityCalculate(dmList[0],dm_tele,theta_k)
                    
                #else:
                    #print("Aborted!!")
    return pi*sum_fidelity/2/(runtimes**2)
    
#test
if __name__ == '__main__':

    ns.sim_reset()
    #print (ns.__version__)

    myNoiseModel1=DephaseNoiseModel(dephase_rate=6*10**4,time_independent=False)
    #myNoiseModel2=DepolarNoiseModel(depolar_rate=6*10**4,time_independent=False)
    #myNoiseModel3=T1T2NoiseModel(T1=11, T2=0)
    #myNoiseModel4=DepolarNoiseModel(depolar_rate=0.01,time_independent=True)

    res=run_AT_sim(runtimes=1,numNodes=4,fibre_len=10**-9
        ,processorNoiseModel=None,memNoiseMmodel=myNoiseModel1
        ,loss_init=0,loss_len=0,t1=3720,t2=0)  

    res=print("Avg Fidelity index:",res)