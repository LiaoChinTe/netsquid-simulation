from netsquid.protocols import NodeProtocol


import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *



'''
Anonymous Transmission in W-state

Star network
Side nodes

'''

class AT_Wstate_side(NodeProtocol):
    
    def __init__(self,node,processor,sender=False,receiver=False,portQlist=["portQside"]): 
        super().__init__()
        self.node=node
        self.processor=processor
        self.sender=sender
        self.receiver=receiver
        
        self.portQlist=portQlist
        self.wStateResult=None
        
        
    def run(self):
        print(self.processor.name)
        self.showIdentity()
        
        # Side receive a qubit from Center
        port=self.node.ports[self.portQlist[0]]
        yield self.await_port_input(port)
        wQubit = port.rx_input().items
        print("I received:",wQubit)
        self.processor.put(wQubit[0])
        
        # Side measures the qubit in standard basis if not sender or receiver.
        if (self.sender==False) and (self.receiver==False) :
            print(self.processor.name)
            self.myQMeasure = QMeasure([0])
            self.processor.execute_program(self.myQMeasure,qubit_mapping=[0])
            self.processor.set_program_done_callback(self.S_getPGoutput,once=True)
            self.processor.set_program_fail_callback(ProgramFail,info=self.processor.name,once=True)
        else:
            print("else case")
        
        yield self.await_program(processor=self.processor)
        print("self.wStateResult: ",self.wStateResult)
        
        
        
        
    def showIdentity(self):
        if self.sender==True:
            print("I am sender")
        elif self.receiver==True:
            print("I am receiver")
        else:
            print("I am normal side node")
            

    def S_getPGoutput(self):
        self.wStateResult=getPGoutput(self.myQMeasure)
        #print("wStateResult:",self.wStateResult)

