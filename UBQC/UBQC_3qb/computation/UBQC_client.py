from random import randint

from netsquid.protocols import NodeProtocol


import sys
scriptpath = "../../../lib/"
sys.path.append(scriptpath)
from functions import *

class ProtocolClient(NodeProtocol):
    
    def showValues(self):
        #,"delta1:",self.delta1,"delta2:",self.delta2
        print("phi:",self.phi,"b3,r3:",self.b[2],self.r[2],"theta:",self.theta
            ,"r:",self.r,"b",self.b,"bt:",self.bt)

            
    def ProgramFail(self):
        print("C programe failed!!")
    
    
    def __init__(self,node,processor,rounds,x,phi=[0,0,0]
        ,port_names=["portQC_1","portCC_1","portCC_2"],maxRounds=10):

        super().__init__()
        self.node=node
        self.processor=processor
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1]
        self.portNameC2=port_names[2]
        self.maxRounds=maxRounds
        self.rounds=rounds
        
        self.qubitNum=3
        self.phi=phi
        self.x=x
        self.theta=[None,None,None]
        self.delta=[None,None,None]
        self.r    =[None,None,None]
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
        
        
        
        for i in range(self.qubitNum):
            self.theta[i]=randint(0,7)

        
        
        ## STEP 6
        #Client measures qubit 2, 4, 6 with -theta1, -theta2 and -theta3 
        # and assigns result to bt1, bt2 and bt3.
        #---------------------------------------------------------------------

    
        # measured qubit2 by -theta1
        myAngleMeasure=AngleMeasure([0],[-self.theta[0]])
        self.processor.execute_program(myAngleMeasure,qubit_mapping=[0])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)
        self.bt[0] = myAngleMeasure.output['0'][0]

        # measured qubit4 by -theta2
        myAngleMeasure=AngleMeasure([1],[-self.theta[1]])
        self.processor.execute_program(myAngleMeasure,qubit_mapping=[0,1])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)
        self.bt[1] = myAngleMeasure.output['1'][0]


        # measure qubit6 by -theta3
        myAngleMeasure=AngleMeasure([2],[-self.theta[2]])
        self.processor.execute_program(myAngleMeasure,qubit_mapping=[0,1,2])
        self.processor.set_program_fail_callback(self.ProgramFail,once=True)
        yield self.await_program(processor=self.processor)
        self.bt[2] = myAngleMeasure.output['2'][0]
    
        
        
        ## STEP 7
        #Client randomly chooses r1, r2 and r3.
        #---------------------------------------------------------------------
        for i in range(self.qubitNum):
            self.r[i]=randint(0,1)
        



        for i in range(self.qubitNum):

            ## STEP 8/10/12
            #Client assigns delta1 = phi1+theta1+(x+r1+bt1)*pi 
            # and sends delta1 to the Server.
            #---------------------------------------------------------------------
            if i == 0:
                self.delta[i]=self.phi[0]+self.theta[0]+(self.x+self.r[0]+self.bt[0])*4 
            elif i == 1:
                self.delta[i]=self.phi[1]*(-1)**(self.b[0]+self.r[0])+self.theta[1]+(self.r[1]+self.bt[1])*4
            elif i == 2:
                self.delta[i]=self.phi[2]*(-1)**(self.b[1]+self.r[1])+self.theta[2]+(self.b[0]+self.r[0]+self.r[2]+self.bt[2])*4


            self.node.ports["portCC_1"].tx_output(self.delta[i])
            
            
            #Server sends b1/b2/b3
            # Receive
            #---------------------------------------------------------------------
            port = self.node.ports["portCC_2"]
            yield self.await_port_input(port)
            self.b[i] = port.rx_input().items[0]



        # STEP 14
        #Client outputs o = b3 XOR r3.
        #---------------------------------------------------------------------
        self.output=bool(self.b[2])^bool(self.r[2])
        self.output=int(self.output)

        '''
        #debug
        if self.x != self.output:
            self.showValues()
        '''

            
            
        
        
                
        
            