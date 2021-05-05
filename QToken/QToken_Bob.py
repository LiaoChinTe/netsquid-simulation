
from netsquid.protocols import NodeProtocol
from QToken_function import * 
from netsquid.components import QSource,Clock
from netsquid.components.qsource import SourceStatus

from random import randint

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *


class BobProtocol(NodeProtocol):
    
    def __init__(self,node,processor,num_bits,threshold=0.854,
                port_names=["portQB_1","portCB_1","portCB_2"]):
        super().__init__()
        self.num_bits=num_bits
        self.node=node
        self.processor=processor
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1]
        self.portNameC2=port_names[2]
        # init value assume that all qubits are lost
        self.sourceQList=[]
        self.basisInxList=[randint(0,7) for i in range(self.num_bits)]
        self.randMeas=randint(0,1) #0:Z basis(standard)   1:X basis(H)
        self.locRes = None
        self.threshold = threshold
        self.successfulRate=None
        self.validList=[]
        
        #generat qubits from source
        self.B_Source = QSource("Bank_source"
            ,status=SourceStatus.EXTERNAL) # enable frequency
        self.B_Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)
        
        #print("basisInxList:",self.basisInxList)

    # =======================================B run ============================
    def run(self):
        
        self.B_genQubits(self.num_bits,1e9)
        
        yield self.await_program(processor=self.processor)
        
        self.B_sendQubit()
        
        
        port = self.node.ports[self.portNameC1]
        yield self.await_port_input(port)
        #print(port.rx_input().items)
        reqMes = port.rx_input().items[0]
        if  reqMes == '10101':
    
            # send payload
            #print("send rand measurement!")
            self.node.ports[self.portNameC2].tx_output(self.randMeas)
        else:
            print("req error!")
            print(reqMes)
    
        #print("B waiting for result")
        port = self.node.ports[self.portNameC1]
        yield self.await_port_input(port)
        [self.locRes, self.validList] = port.rx_input().items
        #print("B locRes:",self.locRes)
        #print("B valid list", self.validList)
        
        
        self.successfulRate=TokenCheck_LossTolerant(self.basisInxList,self.randMeas,self.locRes,self.validList)
        #print("B successfulRate:",self.successfulRate)
        
        # send result to A
        if self.successfulRate > self.threshold :
            # pass
            self.node.ports[self.portNameC2].tx_output(True)
        else:
            # you shall not pass!
            self.node.ports[self.portNameC2].tx_output(False)
        #print("Bob finished")
        
            

    def B_genQubits(self,num,freq=1e9):
        
        
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=2*num)
        try:
            clock.ports["cout"].connect(self.B_Source.ports["trigger"])
        except:
            pass
            #print("alread connected") 
            
        clock.start()
        
    def storeSourceOutput(self,qubit):
        self.sourceQList.append(qubit.items[0])
        if len(self.sourceQList)==2*self.num_bits:
            self.processor.put(qubits=self.sourceQList)
            
            inxList=[randint(0,7) for i in range(self.num_bits)]
            
            #print("inxList=",self.basisInxList)
            # apply H detector
            PG_qPrepare=QG_B_qPrepare(num_bits=self.num_bits,stateInxList=self.basisInxList)
            self.processor.execute_program(
                PG_qPrepare,qubit_mapping=[i for  i in range(0, 2*self.num_bits)])
            

            
    def B_sendQubit(self):
        #print("B_sendQubit")
        inx=list(range(2*self.num_bits))
        payload=self.processor.pop(inx)
        self.node.ports[self.portNameQ1].tx_output(payload)
      
