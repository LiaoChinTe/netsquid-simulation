

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
        
        self.C_delta1=None
        self.C_delta2=None
        self.m1=None
        self.m2=None
        
        
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
        
        
        
        
        ## STEP 2,3
        #S generates four qubits in |0> state.(label 1 to 4)
        #S makes two EPR pairs: Apply H gate and CNOT gate with 
        #  qubit label 1 and qubit label 2, same with 3 and 4
        #---------------------------------------------------------------------
        self.S_genQubits(4)    # EPR pair formed when port received
        yield self.await_program(processor=self.processor)
        
        
        
        
        ## STEP 4
        #S sends two qubits(2 and 4) to C, now the two EPR pairs are shared. 
        #---------------------------------------------------------------------
        self.S_sendEPR()
        
        
        
        ## STEP 6
        #C sends ACK to S
        #S receive ACK from C
        #---------------------------------------------------------------------
        port = self.node.ports["portCS_1"]
        yield self.await_port_input(port)
        ack=port.rx_input().items[0]
        if ack!='ACK':
            print("ACK ERROR!")
        
        # debug
        '''
        tmp1=self.processor.pop(2)[0]
        tmp2=self.processor.pop(0)[0]
        print("S qubit3:\n",tmp1.qstate.dm)
        print("S qubit1:\n",tmp2.qstate.dm)
        '''
        #self.processor.put([tmp1,tmp2],positions=[0,1])
        
        
        #!!
        ## STEP 7
        #S swaps memory position of qubit 1 with qubit 3.
        #---------------------------------------------------------------------
        myQSwap=QSwap(position=[0,2])
        self.processor.execute_program(myQSwap,qubit_mapping=[0,1,2])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)
        
        
        
        ## STEP 8
        #S sends ACK2 to C.
        #---------------------------------------------------------------------
        self.node.ports["portCS_2"].tx_output("ACK2")
        
        
        
        ## STEP 10
        #C sends ACK3 to S.
        #S receive ACK3 from C
        #---------------------------------------------------------------------
        port = self.node.ports["portCS_1"]
        yield self.await_port_input(port)
        ack=port.rx_input().items[0]
        if ack!='ACK3':
            print("ACK3 ERROR!")
        
        
        
        
        
        ## STEP 11
        #S apply Control-Z with qubits 1 and 3.
        #---------------------------------------------------------------------
        myQCZ=QCZ(position=[0,2])
        self.processor.execute_program(myQCZ,qubit_mapping=[0,1,2])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)
        
        
        
        
        
        ## STEP 12
        #S sends ACK4 to C.
        #C receive ACK4 from S
        #---------------------------------------------------------------------
        self.node.ports["portCS_2"].tx_output("ACK4")
        
        
        
        ## STEP 14
        #C sends delta1 and delta2 to S
        #S receive delta1 and delta2
        #---------------------------------------------------------------------
        port = self.node.ports["portCS_1"]
        yield self.await_port_input(port)
        tmp=port.rx_input().items
        self.C_delta1=tmp[0]
        self.C_delta2=tmp[1]
        
        
        
        
        
        ## STEP 15
        #S measures the qubit 3 by delta1. 
        # And measures qubit 1 by delta2, assign results to m1 and m2.
        #---------------------------------------------------------------------
        myAngleMeasure_m1m2=AngleMeasure([0,2],[self.C_delta1,self.C_delta2])
        self.processor.execute_program(myAngleMeasure_m1m2,qubit_mapping=[0,1,2])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)

        self.m1 = myAngleMeasure_m1m2.output['0'][0]
        self.m2 = myAngleMeasure_m1m2.output['2'][0]

        
        ## STEP 16
        #S sends m1 and m2 to C
        #---------------------------------------------------------------------
        self.node.ports["portCS_2"].tx_output([self.m1,self.m2])
        
        