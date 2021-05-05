from netsquid.protocols import NodeProtocol
from QToken_function import * 
from random import randint

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

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
        self.myQG_A_measure = None
        self.validList=[]

    # =======================================A run ============================
    def run(self):
        
        # receive qubits from B
        port=self.node.ports[self.portNameQ1]
        yield self.await_port_input(port)
        qubitPairs = port.rx_input().items
        
        #print("A received qubitPairs=",qubitPairs)
        self.validList,qubitPairs=QubitPairFilter(qubitPairs,1,2*self.num_bits)
        #print("A self.validList: ",self.validList)
        
        if len(self.validList)<1: # abort case
            
            return -1
        
        
        self.processor.put(qubitPairs)
        

        # A keep it for some time
        if self.waitTime>0:
            yield self.await_timer(duration=self.waitTime)

        message = "10101"    #use 10101 as request of challenge
        self.node.ports["portCA_1"].tx_output(message)

        #print("A received:",port.rx_input().items)
        port=self.node.ports[self.portNameC2]
        yield self.await_port_input(port)
        basis=port.rx_input().items[0]
        #print("basis:",basis)
        
        basisList=[basis for i in range(len(self.validList))]
        #print("A basisList:",basisList)
        
        
        #print("mem 1 used?  ",self.processor.get_position_used(2*self.num_bits))
        
        self.myQG_A_measure=QG_A_measure(basisList=basisList,num_bits=len(self.validList))
        self.processor.execute_program(
            self.myQG_A_measure, qubit_mapping=[i for  i in range(len(self.validList))])
        self.processor.set_program_fail_callback(ProgramFail,once=True)
        yield self.await_program(processor=self.processor)
        
        for i in range(len(self.validList)):
            tmp=bitFlipNoice(self.myQG_A_measure.output[str(i)][0],f0=0.95,f1=0.995,randomInteger=randint(0,100)) # add measurement noice by so
            self.loc_mesRes.append(tmp)    

            

        #print("A self.loc_mesRes:",self.loc_mesRes)
        
        # send measurement result
        self.node.ports[self.portNameC1].tx_output([self.loc_mesRes,self.validList])
        
        
        port=self.node.ports[self.portNameC2]
        yield self.await_port_input(port)
        Res=port.rx_input().items[0]
        #print("A received result:",Res)
        #print("Alice finished")
