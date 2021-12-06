#!/usr/bin/env python
# coding: utf-8



'''
QLine simulation 
Qubit sending direction
(A)------>(B)------>(C)------>(D)
According to roles in Qline, we have
(O)------>(I)------>(T)------>(D)
Indicating Origin,Initial,Target and Destination, where (I) can be (O) 
as well as (T) being (D).
Origin : First Node of this QLine.
Initial: The initial node that start to generate a key pair. 
Target : Target node that share a key pair with the initial node. 
Destination: Last node of this QLine.
Objective:
Establishes a shared key between any two nodes in QLine. 
'''

import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.protocols import Protocol,LocalProtocol
from netsquid.qubits import create_qubits
from netsquid.qubits.operators import X,H,Z
from netsquid.nodes.connections import DirectConnection
#from netsquid.components.models import  FibreDelayModel
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel

from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *
from netsquid.components.instructions import *
from netsquid.components.qprogram import *
from netsquid.components.models.qerrormodels import *
#from netsquid.components.models.qerrormodels import DepolarNoiseModel
from random import randint




# get output value from a Qprogram
def getPGoutput(Pg,key):
    resList=[]
    tempDict=Pg.output
    value = tempDict.get(key, "")[0]
    return value


# A Quantum processor class which is able to send qubits from Qmemory
class sendableQProcessor(QuantumProcessor):
    def sendfromMem(self,inx,senderNode,receiveNode):
        payload=self.pop(inx)
        senderNode.get_conn_port(receiveNode.ID,label='Q').tx_output(payload)



# Quantum program operations on Node A 
class QG_O(QuantumProgram):
    def __init__(self):
        super().__init__()
        
    def program(self):
        idx=self.get_qubit_indices(1)
        self.apply(INSTR_INIT, idx[0])
        yield self.run(parallel=False)

        
# Quantum program in initNode!=0 case
class QG_I(QuantumProgram):
    def __init__(self,r,b):
        self.r=r
        self.b=b
        super().__init__()
        
    def program(self):
        idx=self.get_qubit_indices(1)
        if self.b==1:
            #print("did X")
            self.apply(INSTR_X, qubit_indices=idx[0])
        if self.r==1:
            #print("did H")
            self.apply(INSTR_H, qubit_indices=idx[0])
        yield self.run(parallel=False)



# Quantum program operations usually on Node B
class QG_T(QuantumProgram):
    def __init__(self,c,s):
        self.c=c
        self.s=s
        super().__init__()
        
    def program(self):
        idx=self.get_qubit_indices(1)
        if self.s==1:
            #print("did H")
            self.apply(INSTR_H,qubit_indices=idx[0])
        if self.c==1:
            #print("did X")
            self.apply(INSTR_X,qubit_indices=idx[0]) 
        
        yield self.run(parallel=False)
        
        
class QG_D(QuantumProgram):
    def __init__(self):
        super().__init__()

    def program(self):
        idx=self.get_qubit_indices(1)
        self.apply(INSTR_MEASURE, qubit_indices=idx[0], output_key='R',physical=True) 
        
        yield self.run(parallel=False)




class QLine(Protocol):
    def __init__(self,nodeList,processorList
        ,fibreLen,initNodeID,targetNodeID,lossInd,lossLen):
        self.nodeList=nodeList
        self.processorList=processorList
        
        self.initNodeID=initNodeID
        self.targetNodeID=targetNodeID
        
        self.num_node=len(nodeList)
        self.fibre_len=fibreLen
        
        # A rand
        self.r=randint(0,1)
        self.b=randint(0,1)
        # B rand
        self.c=randint(0,1)
        self.s=randint(0,1)
        
        self.keyI=None
        self.keyT=None
        
        self.TimeF=0.0   #time recorded when started
        self.TimeD=0.0   #time cost for this bit to form
        
        #self.QfibreList=[]
        #self.CfibreList=[]
        
        
        # if not forwarded, connect them with Q,C fibres
        if self.nodeList[self.initNodeID].get_conn_port(
            self.initNodeID+1,label='Q')==None:
            
            #print("create fibres")
            # create quantum fibre and connect
            self.QfibreList=[QuantumChannel(name="QF"+str(i),length=self.fibre_len,
                p_loss_init=lossInd,p_loss_length=0.25) 
                for i in range(self.num_node-1)]

            for i in range(self.num_node-1):
                self.nodeList[i].connect_to(
                    self.nodeList[i+1],self.QfibreList[i],label='Q')


            # create classical fibre and connect 
            self.CfibreList=[DirectConnection("CF"+str(i)
                        ,ClassicalChannel(name="CFibre_forth", length=self.fibre_len)
                        ,ClassicalChannel(name="CFibre_back" , length=self.fibre_len))
                            for i in range(self.num_node-1)]
            for i in range(self.num_node-1):
                self.nodeList[i].connect_to(
                    self.nodeList[i+1],self.CfibreList[i],label='C')

                
                
            # do forward according to position
            
            # No need to forward if I next to T
            if self.initNodeID+1!=self.targetNodeID:
                self.ForwardSetting(self.initNodeID+1,self.targetNodeID)
                self.ForwardSettingBK(self.initNodeID,self.targetNodeID-1)

            # case I !=O nor next to O
            if self.initNodeID>=1:
                self.ForwardSetting(1,self.initNodeID)
                self.ForwardSettingBK(0,self.initNodeID-1)
                
            # case T !=D nor next to D 
            if self.targetNodeID<len(self.nodeList)-2:
                self.ForwardSetting(self.targetNodeID+1,self.nodeList[-1].ID)
                self.ForwardSettingBK(self.targetNodeID,self.nodeList[-1].ID-1)

        
        super().__init__()




    '''
    Fuction used to make forward operation between ports.
    The two nodes could have multiple nodes in between.
    
    (NodeID_X)=F=>(anyNodes)=F=>(NodeID_Y)
    
    input:
        NodeID_X:  The node id which start to forward.
        NodeID_Y: The node id which ends the forward. 
    '''
    def ForwardSetting(self,NodeID_X,NodeID_Y):
        
        if NodeID_Y-NodeID_X>=1:
            if not self.nodeList[NodeID_X+1].get_conn_port(
                NodeID_X,label='Q').forwarded_ports: 
                # if not done before(for multiple bits)
                for i in range(NodeID_X,NodeID_Y): # 
                    self.nodeList[i].get_conn_port(i-1,label='Q').forward_input(
                        self.QfibreList[i].ports["send"]) 
                    
                    self.nodeList[i].get_conn_port(i-1,label='C').forward_input(
                        self.nodeList[i+1].get_conn_port(
                        i,label='C'))


    def ForwardSettingBK(self,X,Y): # Y can not be D
        if Y-X>=1:
            for i in range(Y,X,-1): # loop times = Y-X, i=Y,Y-1...X+1
            
                self.nodeList[i].get_conn_port(
                    i+1,label='C').forward_input(
                    self.nodeList[i-1].get_conn_port(
                    i,label='C'))

                

    def start(self):
        super().start()
        
        # forware setting based on position of two nodes
            
        
        # T callback
        self.nodeList[self.targetNodeID].get_conn_port(
            self.targetNodeID-1,label='Q').bind_input_handler(
            self.T_Rec_HX)
        
        # record time to begin
        self.TimeF=ns.util.simtools.sim_time(magnitude=ns.NANOSECOND)
        
        self.O_QubitGen()
        

# O =========================================== 
    def O_Fail(self):
        print("O_Fail")
    
    # must
    def O_QubitGen(self):
        myQG_O=QG_O()
        self.processorList[0].execute_program(
            myQG_O,qubit_mapping=[0])
        self.processorList[0].set_program_fail_callback(
            self.O_Fail,once=True)
        
        if self.initNodeID==0: # if I==O !!!
            self.processorList[0].set_program_done_callback(
                self.I_QG_HX,once=True)
        else:     # I!=O
            self.processorList[0].set_program_done_callback(
                self.O_Send_I,once=True)
        
    
    # O != I
    def O_Send_I(self):
        # I callback
        self.nodeList[self.initNodeID].get_conn_port(
            self.initNodeID-1,label='Q').bind_input_handler(
            self.I_rec)
        # send qubits
        self.processorList[0].sendfromMem(
            senderNode=self.nodeList[0],inx=[0]
            ,receiveNode=self.nodeList[1]) 

# I  ==================================================
    def I_Fail(self):
        self.qubitLoss=True
        print("I_Fail")   

    # O != I
    def I_rec(self,qubit):
        self.processorList[self.initNodeID].put(qubits=qubit.items)
        self.I_QG_HX()
        
    # must
    def I_QG_HX(self):
        myQG_I=QG_I(self.r,self.b)
        self.processorList[self.initNodeID].execute_program(
            myQG_I,qubit_mapping=[0])
        self.processorList[self.initNodeID].set_program_done_callback(
            self.I_QubitSend,once=True)
        self.processorList[self.initNodeID].set_program_fail_callback(
            self.I_Fail,once=True)
        

    # must
    def I_QubitSend(self):
        
        # I callback
        self.nodeList[self.initNodeID].get_conn_port(
            self.initNodeID+1, label='C').bind_input_handler(self.I_Compare)
        
        # send qubit
        self.processorList[self.initNodeID].sendfromMem(
            senderNode=self.nodeList[self.initNodeID],inx=[0]
            ,receiveNode=self.nodeList[self.initNodeID+1])
    
# T  ==================================================
    def T_Fail(self):
        self.qubitLoss=True
        print("T_Fail")
        
    # must
    def T_Rec_HX(self,qubit):
        self.processorList[self.targetNodeID].put(qubits=qubit.items)
        self.myQG_T=QG_T(self.c,self.s)
        
        # T HX
        self.processorList[self.targetNodeID].execute_program(
            self.myQG_T,qubit_mapping=[0])
        self.processorList[self.targetNodeID].set_program_fail_callback(
            self.T_Fail,once=True)
        
        # if T==D 
        if self.targetNodeID==len(self.nodeList)-1: 
            # send s R back to T then I
            self.processorList[self.targetNodeID].set_program_done_callback(
                self.D_QG_measure,once=True)
            
            
        # T!=D  send forward
        else: 
            # set T callback for R
            self.nodeList[self.targetNodeID].get_conn_port(
                self.targetNodeID+1, label='C').bind_input_handler(self.T_recR)
            # set callback for D
            self.nodeList[-1].get_conn_port(
                len(self.nodeList)-2, label='Q').bind_input_handler(self.D_rec)
            
            #send to D
            self.processorList[self.targetNodeID].set_program_done_callback(
                self.T_Send_D,once=True)
            
        
    # T!=D
    def T_Send_D(self):
        self.processorList[self.targetNodeID].sendfromMem(
            senderNode=self.nodeList[self.targetNodeID],inx=[0]
            ,receiveNode=self.nodeList[self.targetNodeID+1])

#  D ==================================================
    def D_Fail(self):
        self.qubitLoss=True
        print("D_Fail")

    # if T!=D
    def D_rec(self,qubit):
        self.processorList[-1].put(qubits=qubit.items)
        self.D_QG_measure()
        
    # must
    def D_QG_measure(self):
        self.myQG_D=QG_D()
        self.processorList[-1].execute_program(
            self.myQG_D,qubit_mapping=[0])
        self.processorList[-1].set_program_fail_callback(
            self.D_Fail,once=True)
        self.processorList[-1].set_program_done_callback(
            self.D_sendback,once=True)
        
        
    # must
    def D_sendback(self):
        self.R=getPGoutput(self.myQG_D,'R')
        self.nodeList[len(self.nodeList)-1].get_conn_port(
            len(self.nodeList)-2,label='C').tx_output([self.s,self.R])


#Following are phases that we use classical fibres only.

# C1 ==================================================

    # receive R then send back
    def T_recR(self,R):
        self.nodeList[self.targetNodeID].get_conn_port(
            self.targetNodeID-1,label='C').tx_output([self.s,R.items[0]])


# C2 ==================================================    
    def I_Compare(self,alist): # receives [self.s,self.R]
        if alist.items[0]==self.r: # if s == r
            self.keyI=self.b
        self.I_Response()

        
    def I_Response(self):
        # callback T compare
        self.nodeList[self.targetNodeID].get_conn_port(
            self.targetNodeID-1, label='C').bind_input_handler(self.T_Compare)
        self.nodeList[self.initNodeID].get_conn_port(
            self.initNodeID+1,label='C').tx_output(self.r)

# C3 =====================================================================
    def T_Compare(self,r):
        self.qubitLoss=False
        if self.s==r.items[0]:
            self.keyT=self.R ^ self.c
        self.TimeD=ns.util.simtools.sim_time(magnitude=ns.NANOSECOND)-self.TimeF 
        #in nanoseconds    



def run_QLine_sim(I,T,maxKeyLen=1,fibreLen=10**-3,
    memNoise=None,noise_model=None,lossInd=0.2,lossLen=0.25):
    
    # Hardware configuration
    processorA=sendableQProcessor("processor_A", num_positions=2,
                mem_noise_models=memNoise, phys_instructions=[
                PhysicalInstruction(INSTR_INIT, duration=1, parallel=True),
                PhysicalInstruction(INSTR_X, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_H, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_MEASURE, duration=5
                    , q_noise_model=noise_model, parallel=True)])

    #mem_noise_models=[DepolarNoiseModel(0)] * 100
    processorB=sendableQProcessor("processor_B", num_positions=2,
                mem_noise_models=memNoise, phys_instructions=[
                PhysicalInstruction(INSTR_INIT, duration=1, parallel=True),
                PhysicalInstruction(INSTR_X, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_H, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_MEASURE, duration=5
                    , q_noise_model=noise_model, parallel=True)])

    processorC=sendableQProcessor("processor_C", num_positions=2,
                mem_noise_models=memNoise, phys_instructions=[
                PhysicalInstruction(INSTR_INIT, duration=1, parallel=True),
                PhysicalInstruction(INSTR_X, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_H, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_MEASURE, duration=5
                    , q_noise_model=noise_model, parallel=True)])

    processorD=sendableQProcessor("processor_D", num_positions=2,
                mem_noise_models=memNoise, phys_instructions=[
                PhysicalInstruction(INSTR_INIT, duration=1, parallel=True),
                PhysicalInstruction(INSTR_X, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_H, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_MEASURE, duration=5
                    , q_noise_model=noise_model, parallel=True)])
    
    processorE=sendableQProcessor("processor_E", num_positions=2,
                mem_noise_models=memNoise, phys_instructions=[
                PhysicalInstruction(INSTR_INIT, duration=1, parallel=True),
                PhysicalInstruction(INSTR_X, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_H, duration=2, q_noise_model=noise_model),
                PhysicalInstruction(INSTR_MEASURE, duration=5
                    ,q_noise_model=noise_model, parallel=True)])

    node_A = Node("A",ID=0)
    node_B = Node("B",ID=1)
    node_C = Node("C",ID=2)
    node_D = Node("D",ID=3)
    #node_E = Node("E",ID=4)
    
    nodeList=[node_A,node_B,node_C,node_D]
    processorList=[processorA,processorB,processorC,processorD]
    
    
    keyListI=[] # key for I, length unknown
    keyListT=[] # key for T, length unknown
    totalTime=0.0
    errorTimes=0
    
    for i in range(maxKeyLen):
        ns.sim_reset()
        myQLine=QLine(nodeList=nodeList
            ,processorList=processorList
            ,fibreLen=fibreLen
            ,initNodeID=I,targetNodeID=T,lossInd=lossInd,lossLen=lossLen)
        myQLine.start()
        ns.sim_run()
        
        if myQLine.keyI == myQLine.keyT and myQLine.keyI!=None:
            keyListI.append(myQLine.keyI)
            keyListT.append(myQLine.keyT)
            totalTime+=myQLine.TimeD
        
        elif myQLine.keyI != myQLine.keyT:
            errorTimes+=1
            #print(myQLine.keyI)
            #print(myQLine.keyT)
        
            
    return keyListI,keyListT,totalTime   #,errorTimes

#test
#ns.logger.setLevel(1)
if __name__ == "__main__":

    key_I,key_T,costTime=run_QLine_sim(I=0,T=3,maxKeyLen=100,fibreLen=10
        ,noise_model=None
        ,lossInd=0.2,lossLen=0.25)
    print("key_I: ",key_I)
    print("key_T: ",key_T)
    print("costTime: ",costTime)