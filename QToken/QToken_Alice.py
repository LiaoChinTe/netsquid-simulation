from netsquid.protocols import NodeProtocol
from random import randint

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from lib.functions import *





'''
Only used for this protocol, cut integers that are not a complete pair.

input:
    myList: list of int
    minBound: int
    maxBound: int
output:
    A list of only complete pairs.

'''
def CutNonPair(myList,minBound,maxBound):
    for i in range(minBound,maxBound+1):
        if minBound==1 and i in myList:
            if i+1 in myList and i%2==1:
                pass
            elif i-1 in myList and i%2==0:
                pass
            else:
                myList.remove(i)
        elif minBound==0 and i in myList:
            if i+1 in myList and i%2==0:
                pass
            elif i-1 in myList and i%2==1:
                pass
            else:
                myList.remove(i)
    return myList



'''
Only used for this protocal. Since one qubit loss means a qubit pair can not been used.
This function is used for cutting useless qubits

input:
    qList: qubit list to filter.
    minBound: The minimum vlue of qubit index, usually 1. 
    MaxBound: The maximum vlue of qubit index.
    
output:
    Filtered qubit list.

'''
def QubitPairFilter(qList,minBound,MaxBound):    
    RemainList=[]
    for i in range(len(qList)):
        RemainList.append(int(qList[i].name[13:-len('-')-1]))    # get index from bits
    RemainList=CutNonPair(RemainList,minBound,MaxBound)

    
    # adopt qList according to RemainList
    
    qlength=len(qList)
    for i in reversed(range(qlength)):
        tmp=int(qList[i].name[13:-len('-')-1])
        if tmp not in RemainList:
            qList.pop(i)
    
    
    return RemainList,qList







class AliceProtocol(NodeProtocol):
    
    def __init__(self,node,processor,num_bits,waitTime,
                port_names=["portQA_1","portCA_1","portCA_2"]):
        super().__init__()
        self.num_bits=num_bits
        self.node=node
        self.processor=processor
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1]
        self.portNameC2=port_names[2]
        self.waitTime=waitTime
        self.tokenQlist = None
        self.loc_mesRes = []
        self.myQMeasure = None
        self.validList=[]

    # =======================================A run ============================
    def run(self):
        
        # receive qubits from B
        port=self.node.ports[self.portNameQ1]
        yield self.await_port_input(port)
        qubitPairs = port.rx_input().items
        
        self.validList,qubitPairs=QubitPairFilter(qubitPairs,1,2*self.num_bits)
        
        if len(self.validList)<1: # abort case
            
            return -1
        
        
        self.processor.put(qubitPairs)
        

        # A keep it for some time
        if self.waitTime>0:
            yield self.await_timer(duration=self.waitTime)

        message = "10101"    #use 10101 as request of challenge
        self.node.ports["portCA_1"].tx_output(message)

        port=self.node.ports[self.portNameC2]
        yield self.await_port_input(port)
        basis=port.rx_input().items[0]
        #print("basis:",basis)
        
        basisList=[basis for i in range(len(self.validList))]
        #print("A basisList:",basisList)
        
        

        self.myQMeasure=QMeasure(basisList=basisList)
        self.processor.execute_program(
            self.myQMeasure, qubit_mapping=[i for  i in range(len(self.validList))])
        self.processor.set_program_fail_callback(ProgramFail,once=True)

        yield self.await_program(processor=self.processor)
        
        for i in range(len(self.validList)):
            tmp=bitFlipNoice(self.myQMeasure.output[str(i)][0],f0=0.95,f1=0.995,randomInteger=randint(0,100)) # add measurement noice by so
            self.loc_mesRes.append(tmp)    

        
        
        # send measurement result
        self.node.ports[self.portNameC1].tx_output([self.loc_mesRes,self.validList])
        
        
        port=self.node.ports[self.portNameC2]
        yield self.await_port_input(port)
        Res=port.rx_input().items[0]
        #print("A received result:",Res)
        #print("Alice finished")
