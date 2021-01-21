from random import randint
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

from ATw_center import *
from ATw_side import *



def run_AT_sim(numNodes=4,fibre_len=10**-9,processorNoiseModel=None,memNoiseMmodel=None,loss_init=0,loss_len=0
              ,QChV=3*10**-4):
    
    # initialize
    ns.sim_reset()
    
    sideProcessorList=[]
    sideNodeList=[]
    centerQPortNameList=[]
    centerCPortNameList=[]
    QchannelList=[]
    CchannelList=[]
    
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
        sideProcessorList.append(createProcessorAT(name="ProcessorSide_"+str(i)))
        
        ### nodes=====================================================================
        sideNodeList.append(Node("Node_"+str(i), port_names=["PortQside","PortCside"]))
        
        ### channels, Quantum and calssical=============================================
        QchannelList.append(QuantumChannel("QChannel_Center->Side_"+str(i),delay=10,length=fibre_len
            ,models={"quantum_loss_model":
            FibreLossModel(p_loss_init=loss_init,p_loss_length=loss_len, rng=None),
            "delay_model": FibreDelayModel(c=QChV)}))

        CchannelList.append(ClassicalChannel("CChannel_Side->Center_"+str(i),delay=10,length=fibre_len))

        ### record port list for center node===========================================
        centerQPortNameList.append("PortQcenter_"+str(i))
        centerCPortNameList.append("PortCcenter_"+str(i))


    ## create center node and processor=======================================================
    allCenterPorts=[]
    allCenterPorts.extend(centerQPortNameList)
    allCenterPorts.extend(centerCPortNameList)
    print("allCenterPorts: ",allCenterPorts)

    CenterNode=Node("CenterNode", port_names=allCenterPorts)
    CenterProcessor=createProcessorAT(name="ProcessorCenter")
    


    ## connect(depend on scale)==================================================================
    for i in range(numNodes):    
        CenterNode.connect_to(sideNodeList[i], QchannelList[i],
            local_port_name =CenterNode.ports["PortQcenter_"+str(i)].name,
            remote_port_name=sideNodeList[i].ports["PortQside"].name)


        tmpRemotePortName="PortCcenter_"+str(i)
        #print("connecting classical channel:",i," side node:",sideNodeList[i].name," channel:",CchannelList[i].name,"remote port:", tmpRemotePortName )
        sideNodeList[i].connect_to(CenterNode, CchannelList[i],
            local_port_name="PortCside", remote_port_name=tmpRemotePortName)
        
    




    # create protocol object
    myProtocol_center = AT_Wstate_center(CenterNode,CenterProcessor,numNodes
        ,portQlist=centerQPortNameList,portClist=centerCPortNameList)
    myProtocol_sideList=[]
    ## create side protocol
    for i in range(numNodes):
        if i==senderID:
            # create sender
            myProtocol_sideList.append(AT_Wstate_side(sideNodeList[i],sideProcessorList[i],id=i,  sender=True))
        elif i==receiverID:
            # create receiver
            myProtocol_sideList.append(AT_Wstate_side(sideNodeList[i],sideProcessorList[i],id=i,receiver=True))
        else:
            # create normal side node
            myProtocol_sideList.append(AT_Wstate_side(sideNodeList[i],sideProcessorList[i],id=i))
        
    
    
    for sideProtocols in myProtocol_sideList:
        sideProtocols.start()
        
    myProtocol_center.start()
    
    
    #ns.logger.setLevel(1)
    ns.sim_run()
    




#test
run_AT_sim(numNodes=4,fibre_len=10**-9
    ,processorNoiseModel=None,memNoiseMmodel=None,loss_init=0,loss_len=0)