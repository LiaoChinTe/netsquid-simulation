from random import randint

from netsquid.protocols import NodeProtocol


import sys
scriptpath = "../../lib/"
sys.path.append(scriptpath)
from functions import *

class ProtocolClient(NodeProtocol):
    
    def showValues(self):
        #,"delta1:",self.delta1,"delta2:",self.delta2
        print("t:",self.t,"theta:",self.theta,"d:",self.d,"r:",self.r
            ,"b1",self.b1,"b2",self.b2,"bt:",self.bt
            ,"pass:",self.verified)

            
    def ProgramFail(self):
        print("C programe failed!!")
    
    
    def __init__(self,node,processor,rounds,port_names=["portQC_1","portCC_1","portCC_2"],maxRounds=10):
        super().__init__()
        self.node=node
        self.processor=processor
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1]
        self.portNameC2=port_names[2]
        self.maxRounds=maxRounds
        self.rounds=rounds
        
        self.t=None
        self.theta=None
        self.d=None
        self.r=None
        
        self.delta1=None
        self.delta2=None
        
        self.b1=None
        self.b2=None
        self.bt=None
        
        self.verified=False
        
    
    def run(self):
        
        ## STEP 0
        #C send round infomation 
        #---------------------------------------------------------------------
        self.node.ports[self.portNameC1].tx_output(self.rounds)
        
        
        
        ## STEP 5
        #Client randomly chooses t and theta.
        #---------------------------------------------------------------------
        # receive qubits
        port = self.node.ports["portQC_1"]
        yield self.await_port_input(port)
        qList = port.rx_input().items
        self.processor.put(qList)
        
        self.t=randint(1,2)
        self.theta=randint(0,7)
        
        
        ## STEP 6
        #Client, if t=1, measures qubit 2 with -theta, assign result to b1. 
        # Then measures qubit 4 with standard basis, assgin result to d. 
        # If t=2, measures qubit 4 with -theta, assign result to b2. 
        # Then measures qubit 2 with standard basis, assgin result to d.        
        #---------------------------------------------------------------------!!

        if self.t == 1 :  #C case t=1
            # measured qubit2 by -theta
            myAngleMeasure=AngleMeasure([0],[-self.theta])
            self.processor.execute_program(myAngleMeasure,qubit_mapping=[0])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.bt = myAngleMeasure.output['0'][0]

            # measure qubit4 by standard
            myQMeasure=QMeasureByPosition([0],position=[1])
            self.processor.execute_program(myQMeasure,qubit_mapping=[0,1])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.d = myQMeasure.output['1'][0]
        
        
        elif self.t == 2:  # C case t=2
            # measured qubit4 by -theta
            myAngleMeasure=AngleMeasure([1],[-self.theta])
            self.processor.execute_program(myAngleMeasure,qubit_mapping=[0,1])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.bt = myAngleMeasure.output['1'][0]

            # measure qubit2 by standard
            myQMeasure=QMeasure([0])
            self.processor.execute_program(myQMeasure,qubit_mapping=[0])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.d = myQMeasure.output['0'][0]

        else:
            print("C t value ERROR !") 
        
        
        ## STEP 7
        #Client randomly chooses r.
        #---------------------------------------------------------------------
        self.r=randint(0,1)

        ## STEP 8
        #Client, if t=1, assign delta1 = theta+(r+d+bt)*pi, 
        # randomly assign delta2 in range C. 
        # If t=2, randomly assign delta1 in range C, 
        # assign delta2 = theta+(r+d+bt)*pi.
        #---------------------------------------------------------------------
        if self.t==1:
            #print("C case t=1")
            self.delta1=self.theta+(self.r+self.d+self.bt)*4
            self.delta2=randint(0,7)
            
        elif self.t==2:
            #print("C case t=2")
            self.delta1=randint(0,7)
            self.delta2=self.theta+(self.r+self.d+self.bt)*4

        else:
            print("C t value ERROR !")       
        

        ## STEP 9
        #Client send delta1 and delta2 to server.
        #---------------------------------------------------------------------
        self.node.ports["portCC_1"].tx_output([self.delta1, self.delta2])
        
        
        
        ## STEP 12
        #Client, if t=1, varification passes if r=b1. 
        # If t=2, varification passes if r=b2.
        #---------------------------------------------------------------------
        port = self.node.ports["portCC_2"]
        yield self.await_port_input(port)
        measRes = port.rx_input().items
        self.b1=measRes[0]
        self.b2=measRes[1]


        if self.t==1:
            if self.b1==self.r:
                self.verified=True
                #self.showValues()
            #self.showValues()
            #else:
            
        elif self.t==2:    
            if self.b2==self.r:
                self.verified=True
                #self.showValues()
            #else:
        else:
            print("C t value ERROR !") 
        
                
        
            
