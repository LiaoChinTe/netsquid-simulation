from random import randint
from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock

from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *


'''
Anonymous Transmission in W-state

Star network
Center node

'''

class AT_Wstate_center(NodeProtocol):

    
    def __init__(self,node,processor,numNode,portQlist,portClist): 
        super().__init__()
        self.numNode=numNode
        self.node=node
        self.processor=processor
        self.portQlist=portQlist
        self.portClist=portClist

        self.sourceQList=[]
        
        
        self.C_Source = QSource("center_source"
            ,status=SourceStatus.EXTERNAL) # enable frequency
        self.C_Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)
        
        
        
    def run(self):
        #print("C center run~")
        
        self.C_genQubits(self.numNode) # make W state too
        
        yield self.await_program(processor=self.processor)
        #print("C w-state qubits generation done, distributing qubits...")
        
        self.C_sendWstate()
        
        #print("C all ports:",self.portClist)

        # wait for measurement results
        #print("C waiting for measurement results from port ",self.portClist[3])
        

        resultsCollector=[]
        for i in range(self.numNode-1,1,-1):
            port = self.node.ports["PortCcenter1_"+str(i)]
            yield self.await_port_input(port)
            res=port.rx_input().items[0]
            #print("C center port ",i," received mes res:",res)
            resultsCollector.append(res)

        #print("C resultsCollector:",resultsCollector)
        
        if sum(resultsCollector)>=1:
            #print("C protocol aborted")
            for i in range(self.numNode):
                payload="Abort"
                self.node.ports["PortCcenter2_"+str(i)].tx_output(payload)
            return 1
        else:
            #print("C send approval to all sideNodes")
            for i in range(self.numNode):
                payload="Approved"
                self.node.ports["PortCcenter2_"+str(i)].tx_output(payload)

        #print("qubit gen finished")
        return 0
        
    def storeSourceOutput(self,qubit):
        self.sourceQList.append(qubit.items[0])
        if len(self.sourceQList)==self.numNode:
            #print("C sourceQList:",self.sourceQList,"putting in Qmem")
            self.processor.put(qubits=self.sourceQList)
            
            myMakeWstate = makeWstate(self.numNode)
            self.processor.execute_program(myMakeWstate,qubit_mapping=[i for i in range(self.numNode)])
            self.processor.set_program_fail_callback(ProgramFail,once=True)
            
            
            
    def C_genQubits(self,num,freq=1e9):
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num)
        try:
            clock.ports["cout"].connect(self.C_Source.ports["trigger"])
        except:
            pass    #print("alread connected") 
            
        clock.start()
    
    
    
    def C_sendWstate(self):
        #print("C in C_sendWstate")
        
        for i in reversed(range(self.numNode)):
            payload=self.processor.pop(i)
            #print("C i:",i," payload:",payload)
            #print("C output from center port: ",self.portQlist[i])
            self.node.ports[self.portQlist[i]].tx_output(payload)
            
