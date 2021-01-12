from random import randint

from netsquid.protocols import NodeProtocol


import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

class ProtocolClient(NodeProtocol):
    
    
            
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
        
        self.z1=None
        self.z2=None
        self.p1=None
        self.p2=None
        
        self.theta1=None
        self.theta2=None
        self.r1=None
        self.r2=None
        
        self.delta1=None
        self.delta2=None
        
        self.m1=None
        self.m2=None
        
        self.verified=False
        
        # STEP 1
        self.d=randint(1,2)
        #print("C d: ",self.d)
    
    def run(self):
        
        ## STEP 0
        #C send round infomation 
        #---------------------------------------------------------------------
        self.node.ports[self.portNameC1].tx_output(self.rounds)
        
        
        
        ## STEP 4
        #C received two qubits from S
        #---------------------------------------------------------------------
        port = self.node.ports["portQC_1"]
        yield self.await_port_input(port)
        EPRpairs=port.rx_input().items
        self.processor.put(EPRpairs)
        
        
        
        
        ## STEP 5 
        #C if d value equal to 1, randomly chooses theta2 and r2, 
        #      measure qubit 2 by theta2, assign result to p2.
        #  if d value equal to 2, measures qubit 2 in standard basis, assign result to z2.
        #---------------------------------------------------------------------!!
        if self.d == 1 :
            #print("C case d=1")
            self.theta2=randint(0,7)
            self.r2=randint(0,1)
            # measured by theta2
            myAngleMeasure=AngleMeasure([0],[self.theta2])
            self.processor.execute_program(myAngleMeasure,qubit_mapping=[0])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            yield self.await_program(processor=self.processor)
        
            self.p2 = myAngleMeasure.output['0'][0]
        
        
        else:  # C case d=2
            # measure the only qubit in Z basis
            #print("C case d=2")
            myQMeasure=QMeasure([0])
            self.processor.execute_program(myQMeasure,qubit_mapping=[0])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            
            yield self.await_program(processor=self.processor)
            self.z2 = myQMeasure.output['0'][0]
        
        
        #print("C theta2: ",self.theta2)
        #print("C p2, z2: ",self.p2,self.z2)
        
        
        ## STEP 6
        #C sends ACK to S.
        #---------------------------------------------------------------------
        self.node.ports["portCC_1"].tx_output("ACK")

        
        ## STEP 8
        #S sends ACK2 to C
        #C receive ACK2 from S
        #---------------------------------------------------------------------
        port = self.node.ports["portCC_2"]
        yield self.await_port_input(port)   
        ack = port.rx_input().items[0]
        if ack!='ACK2':
            print("ACK2 ERROR!")
            
        
        
        ## STEP 9
        #C if d value equal to 1, measures qubit 4 in standard basis, assign result to z1.
        #  if d value equal to 2, randomly chooses theta1 and r1, 
        #  measure qubit 4 by theta2, assign result to p1.
        #---------------------------------------------------------------------
        if self.d==1:
            #print("C case d=1")
            myQMeasure=QMeasure([0]) 
            self.processor.execute_program(myQMeasure,qubit_mapping=[0,1])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            
            yield self.await_program(processor=self.processor)
            self.z1 = myQMeasure.output['0'][0]
            
        else:
            #print("C case d=2")
            self.theta1=randint(0,7)
            self.r1=randint(0,1)
            # measure by theta1
            myAngleMeasure=AngleMeasure([1],[self.theta1]) # first qubit
            self.processor.execute_program(myAngleMeasure,qubit_mapping=[0,1])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)
            
            yield self.await_program(processor=self.processor)
            self.p1 = myAngleMeasure.output['1'][0]
        
        
        
        
        ## STEP 10
        #C sends ACK3 to S.
        #S receive ACK3 from C
        #---------------------------------------------------------------------
        self.node.ports["portCC_1"].tx_output("ACK3")
        
        
        
        
        ## STEP 12
        #S sends ACK4 to C.
        #C receive ACK4 from S
        #---------------------------------------------------------------------
        port = self.node.ports["portCC_2"]
        yield self.await_port_input(port)
        ack = port.rx_input().items[0]
        if ack!='ACK4':
            print("ACK4 ERROR!")
        
        
        
        
        
        # STEP 13
        #C if d value equal to 1, randomly chooses delta1, assign delta2=theta2+(p2+r2)*pi.
        #  if d value equal to 2, randomly chooses delta2, assign delta1=theta1+(p1+r1)*pi.
        #---------------------------------------------------------------------
        if self.d==1:
            self.delta1=randint(0,7)                      # scale x8 ; 1 = 22.5 degree
            self.delta2=self.theta2+(self.p2+self.r2)*8
            self.delta2%=16
        else:    
            self.delta1=self.theta1+(self.p1+self.r1)*8
            self.delta1%=16
            self.delta2=randint(0,7)
        #print("C delta1 delta2:",self.delta1,self.delta2)
        
        
        
        
        
        # STEP 14
        #C sends delta1 and delta2 to S.
        #---------------------------------------------------------------------
        self.node.ports["portCC_1"].tx_output([self.delta1,self.delta2])
        
        
        
        
        # STEP 16
        #S sends m1 and m2 to C
        #C receive measurement results m1, m2 from S
        #---------------------------------------------------------------------
        port = self.node.ports["portCC_2"]
        yield self.await_port_input(port)
        measRes = port.rx_input().items
        self.m1=measRes[0]
        self.m2=measRes[1]
        
        
        
        
        # STEP 17
        #C if d value equal to 1, and (z1+r2)%2=m2, than verification passed.
        #  if d value equal to 2, and (z2+r1)%2=m1, than verification passed.
        #  else Not verified.
        #---------------------------------------------------------------------
        if self.d==1:
            if (self.z1+self.r2)%2== self.m2:
                self.verified=True
            else:
                self.verified=False
            #print("z1,r2,m2:",self.z1,self.r2,self.m2)
        else: # d==2 case 
            if (self.z2+self.r1)%2== self.m1:
                self.verified=True
            else:
                self.verified=False
            #print("z2,r1,m1:",self.z2,self.r1,self.m1)
            