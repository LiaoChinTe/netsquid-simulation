from random import randint

from netsquid.protocols import NodeProtocol


import sys
scriptpath = "../../../lib/"
sys.path.append(scriptpath)
from functions import *

class ProtocolClient(NodeProtocol):
    
    def showValues(self):
        #,"delta1:",self.delta1,"delta2:",self.delta2
        print("t:",self.t,"theta:",self.theta,"d:",self.d,"r:",self.r
            ,"b",self.b,"bt:",self.bt,"pass:",self.verified)

            
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
        
        self.qubitNum=3
        self.t=None
        self.theta=[None,None,None]
        self.d    =[None,None,None]
        self.r    =[None,None,None]
        self.delta=[None,None,None]
        self.b    =[None,None,None]
        self.bt   =[None,None,None]

        
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
        
        
        for i in range(self.qubitNum):
            self.theta[i]=randint(0,7)

        
        
        ## STEP 6
        #Client, if t=1, measures qubit 2 with -theta1, assign result to bt1. 
        # Then measures qubit 6 with -theta3, assgin result to bt3.
        # Then measures qubit 4 with standard basis, assign result to d2. 
        #If t=2, measures qubit 4 with -theta2, assign result to bt2. 
        # Then measures qubit 2 and qubit 6 with standard basis, assgin result to d1 and d3.       
        #---------------------------------------------------------------------!!

        if self.t == 1 :  #C case t=1
            # measured qubit2 by -theta1
            myAngleMeasure=AngleMeasure([0],[-self.theta[0]])
            self.processor.execute_program(myAngleMeasure,qubit_mapping=[0])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.bt[0] = myAngleMeasure.output['0'][0]

            # measured qubit6 by -theta3
            myAngleMeasure=AngleMeasure([2],[-self.theta[2]])
            self.processor.execute_program(myAngleMeasure,qubit_mapping=[0,1,2])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.bt[2] = myAngleMeasure.output['2'][0]


            # measure qubit4 by standard
            myQMeasure=QMeasureByPosition([0],position=[1])
            self.processor.execute_program(myQMeasure,qubit_mapping=[0,1])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.d[1] = myQMeasure.output['1'][0]
        
        
        elif self.t == 2:  # C case t=2
            # measured qubit4 by -theta
            myAngleMeasure=AngleMeasure([1],[-self.theta[1]])
            self.processor.execute_program(myAngleMeasure,qubit_mapping=[0,1])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.bt[1] = myAngleMeasure.output['1'][0]

            # measure qubit2 by standard
            myQMeasure=QMeasureByPosition([0,0],position=[0,2])
            self.processor.execute_program(myQMeasure,qubit_mapping=[0,1,2])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
            self.d[0] = myQMeasure.output['0'][0]
            self.d[2] = myQMeasure.output['2'][0]

        else:
            print("C t value ERROR !") 
        
        
        ## STEP 7
        #Client randomly chooses r1, r2 and r3.
        #---------------------------------------------------------------------
        for i in range(self.qubitNum):
            self.r[i]=randint(0,1)
        



        ## STEP 8
        #Client, if t=1, assign delta1 = theta1+(r1+d2+bt1)*pi, 
        # randomly assign delta2 in range C, 
        # and assign delta3 = theta3+(r3+d2+bt3)*pi. 
        #If t=2, randomly assign delta1 and delta3 in range C, 
        # assign delta2 = theta2+(r2+d1+d3+bt2)*pi.
        #---------------------------------------------------------------------
        if self.t==1:
            #print("C case t=1")
            self.delta[0]=self.theta[0]+(self.r[0]+self.d[1]+self.bt[0])*4
            self.delta[1]=randint(0,7)
            self.delta[2]=self.theta[2]+(self.r[2]+self.d[1]+self.bt[2])*4
            
        elif self.t==2:
            #print("C case t=2")
            self.delta[0]=randint(0,7)
            self.delta[2]=randint(0,7)
            self.delta[1]=self.theta[1]+(self.r[1]+self.d[0]+self.d[2]+self.bt[1])*4

        else:
            print("C t value ERROR !")       
        


        for i in range(self.qubitNum):

            ## STEP 9/12/15
            #Client send delta1/delta2/delta3  to server.
            #---------------------------------------------------------------------
            self.node.ports["portCC_1"].tx_output(self.delta[i])
            
            
            
            ## STEP 11/14/17
            #Server sends b1/b2/b3
            # Receive
            #---------------------------------------------------------------------
            port = self.node.ports["portCC_2"]
            yield self.await_port_input(port)
            self.b[i] = port.rx_input().items[0]



        if self.t==1:
            if self.b[0]==self.r[0] and self.b[2]==self.r[2]:
                self.verified=True
                #self.showValues()
            #self.showValues()
            #else:
            
        elif self.t==2:    
            if self.b[1]==self.r[1]:
                self.verified=True
                #self.showValues()
            #else:
        else:
            print("C t value ERROR !") 
        
                
        
            
