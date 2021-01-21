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
    
    def __init__(self,node,processor,id,sender=False,receiver=False,portQlist=["PortQside"],portClist=["PortCside"]): 
        super().__init__()
        self.node=node
        self.processor=processor
        self.id=id

        self.sender=sender
        self.receiver=receiver
        
        self.portQlist=portQlist
        self.portClist=portClist

        self.wStateResult=None
        
        
    def run(self):
        #print(self.processor.name)
        self.showIdentity()
        
        # Side receive a qubit from Center
        port=self.node.ports[self.portQlist[0]]
        yield self.await_port_input(port)
        wQubit = port.rx_input().items
        print("S ID:",self.id," I received:",wQubit)
        self.processor.put(wQubit[0])
        
        # Side measures the qubit in standard basis if not sender or receiver.
        if (self.sender==False) and (self.receiver==False) :
            #print(self.processor.name)
            myQMeasure = QMeasure([0])
            self.processor.execute_program(myQMeasure,qubit_mapping=[0])
            self.processor.set_program_fail_callback(ProgramFail,info=self.processor.name,once=True)


            yield self.await_program(processor=self.processor)
            self.wStateResult = myQMeasure.output['0'][0]

            print("S res ID:",self.id,"self.wStateResult: ",self.wStateResult)


            #if self.id==3:
                # send result to center
            print("S sending classical message from", self.portClist[0]," to center...")
            self.node.ports[self.portClist[0]].tx_output(self.wStateResult)


        else:
            print("S else case")
            #yield self.await_program(processor=self.processor)
            
    
        
        
        
        
        #self.portClist[0]
        
    def showIdentity(self):
        if self.sender==True:
            print("S I am sender")
        elif self.receiver==True:
            print("S I am receiver")
        else:
            print("S I am normal side node")
            

