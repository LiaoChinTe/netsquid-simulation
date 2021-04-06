from random import randint
from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock

from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "../../lib/"
sys.path.append(scriptpath)
from functions import *

class ProtocolServer(NodeProtocol):

    
    def __init__(self,node,processor,port_names=["portQS_1","portCS_1","portCS_2"],realRound=0):
        super().__init__()
        self.node=node
        self.processor=processor
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1]
        self.portNameC2=port_names[2]
        self.sourceQList=[]
        self.port_output=[]
        self.realRound=realRound
        self.qubitNum=3
        
        
        self.S_Source = QSource("S_source") 
        self.S_Source.status = SourceStatus.EXTERNAL
        
        self.delta=[None,None,None]
        self.b=[None,None,None]
        
        
    def S_genQubits(self,num,freq=1e9):
        #generat qubits from source
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num)
        try:
            self.S_Source.ports["qout0"].bind_output_handler(self.S_put_prepareEPR)
            clock.ports["cout"].connect(self.S_Source.ports["trigger"])
        
        except:
            print("already connected")
        
        clock.start()
        
        
    def S_put_prepareEPR(self,message):
        self.port_output.append(message.items[0])
        if len(self.port_output)==self.qubitNum*2:
            self.processor.put(qubits=self.port_output)
            # PrepareEPRpairs
            prepareEPRpairs=PrepareEPRpairs(self.qubitNum)
            self.processor.execute_program(
                prepareEPRpairs,qubit_mapping=[i for  i in range(0, self.qubitNum*2)])
    
    
    def S_sendEPR(self,position):
        payload=self.processor.pop(position) # send the third one
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
        #Server generates six qubits in |0> state (labelled 1 to 6)
        #Server makes three EPR pairs: Apply H gate on qubit 1 and 
        # CNOT gate on qubit 1 (control) and qubit 2(target), 
        # same with qubits 3 and 4 and qubits 5 and 6.
        #---------------------------------------------------------------------
        self.S_genQubits(6)    # EPR pair formed when port received
        yield self.await_program(processor=self.processor)
        


        ## STEP 3
        # Server applies Control-Z on qubits 1 and 3 and on qubits 3 and 5.
        myQCZ=QCZ(position=[0,2])
        self.processor.execute_program(myQCZ,qubit_mapping=[0,1,2])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)

        myQCZ=QCZ(position=[2,4])
        self.processor.execute_program(myQCZ,qubit_mapping=[0,1,2,3,4])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)


        
        ## STEP 4
        #Server sends three qubits(2,4 and 6) to C, now the three EPR pairs are shared. 
        #---------------------------------------------------------------------
        self.S_sendEPR([1,3,5])
        
        
        for i in range(self.qubitNum): 
            ## STEP 9/11/14 in computational case  or STEP 10/13/16 in Verifiable case
            #Server measures qubit 1/3/5 with angle delta1/delta2/delta3,
            # assign results to b1/b2/b3. And sends them to Client.
            #---------------------------------------------------------------------
            port = self.node.ports["portCS_1"]
            yield self.await_port_input(port)
            rec=port.rx_input().items
            self.delta[i]=rec.pop(0)
            #print("S delta1,2:",self.delta[0]," and ",self.delta[1] )
        
            
            myAngleMeasure_b1b2=AngleMeasure([2*i],[self.delta[i]])
            self.processor.execute_program(myAngleMeasure_b1b2,qubit_mapping=[0,1,2,3,4,5])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)

            self.b[i] = myAngleMeasure_b1b2.output[str(2*i)][0]

            
            #Server sends b1/b2/b3
            #---------------------------------------------------------------------
            self.node.ports["portCS_2"].tx_output(self.b[i])

        
        