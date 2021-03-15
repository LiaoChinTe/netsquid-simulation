from random import randint
from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock

from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

class ProtocolServer(NodeProtocol):

    
    def __init__(self,node,processor,port_names=["portQS_1","portCS_1","portCS_2"],realRound=5):
        super().__init__()
        self.node=node
        self.processor=processor
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1]
        self.portNameC2=port_names[2]
        self.sourceQList=[]
        self.port_output=[]
        self.realRound=realRound
        
        
        self.S_Source = QSource("S_source") 
        self.S_Source.ports["qout0"].bind_output_handler(self.S_put_prepareEPR,4)
        self.S_Source.status = SourceStatus.EXTERNAL
        
        self.delta1=None
        self.delta2=None
        self.b1=None
        self.b2=None
        
        
    def S_genQubits(self,num,freq=1e9):
        #generat qubits from source
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num)
        try:
            clock.ports["cout"].connect(self.S_Source.ports["trigger"])
        
        except:
            print("already connected")
        
        clock.start()
        
        
    def S_put_prepareEPR(self,message,numQubits=4):
        self.port_output.append(message.items[0])
        if len(self.port_output)==numQubits:
            self.processor.put(qubits=self.port_output)
            # PrepareEPRpairs
            prepareEPRpairs=PrepareEPRpairs(int(numQubits/2))
            self.processor.execute_program(
                prepareEPRpairs,qubit_mapping=[i for  i in range(0, numQubits)])
    
    
    def S_sendEPR(self):
        payload=self.processor.pop([1,3]) # send the third one
        self.node.ports[self.portNameQ1].tx_output(payload)        
        

        
    def ProgramFail(self):
        print("S programe failed!!")
    
    
    def run(self):
        
        ## STEP 0 
        #S recieved round information
        #---------------------------------------------------------------------
        port = self.node.ports["portCS_1"]
        yield self.await_port_input(port)
        rounds = port.rx_input().items
        #print("S received rounds:",rounds)
        
        
        
        
        ## STEP 1,2
        #Server generates four qubits in |0> state.(label 1 to 4)
        #Server makes two EPR pairs: Apply H gate on qubit 1 and CNOT gate 
        # on qubit 1(control) and qubit 2(target), same with 3 and 4.
        #---------------------------------------------------------------------
        self.S_genQubits(4)    # EPR pair formed when port received
        yield self.await_program(processor=self.processor)
        
        ## STEP 3
        myQCZ=QCZ(position=[0,2])
        self.processor.execute_program(myQCZ,qubit_mapping=[0,1,2])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)

        
        ## STEP 4
        #S sends two qubits(2 and 4) to C, now the two EPR pairs are shared. 
        #---------------------------------------------------------------------
        self.S_sendEPR()
        
        
        
        ## STEP 10
        #Server measures qubit 1 and 3 with angle delta1 and delta2, 
        #assign results to b1 and b2.
        #---------------------------------------------------------------------
        port = self.node.ports["portCS_1"]
        yield self.await_port_input(port)
        rec=port.rx_input().items
        self.delta1=rec.pop(0)
        self.delta2=rec.pop(0)
        #print("S delta1,2:",self.delta1," and ",self.delta2 )
      
        
        myAngleMeasure_b1b2=AngleMeasure([0,2],[self.delta1,self.delta2])
        self.processor.execute_program(myAngleMeasure_b1b2,qubit_mapping=[0,1,2])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)

        self.b1 = myAngleMeasure_b1b2.output['0'][0]
        self.b2 = myAngleMeasure_b1b2.output['2'][0]

        ## STEP 11
        #S sends b1 and b2 to C
        #---------------------------------------------------------------------
        self.node.ports["portCS_2"].tx_output([self.b1,self.b2])
        
        