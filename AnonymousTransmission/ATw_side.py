from netsquid.protocols import NodeProtocol
from netsquid.qubits.operators import X,H,Z,CNOT
import numpy as np

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import QMeasure,ProgramFail

QTpath = "QuantumTeleportation/"
sys.path.append(QTpath)
from QT_sender import QuantumTeleportationSender
from QT_receiver import QuantumTeleportationReceiver



'''
Anonymous Transmission in W-state

Star network
Side nodes

'''

class AT_Wstate_side(NodeProtocol):
    
    def __init__(self,node,processor,id,qubitToTeleport=None,sender=False,receiver=False
        ,portQlist=["PortQside"],portClist=["PortCside1","PortCside2"],t1=0,t2=0): 
        super().__init__()
        self.node=node
        self.processor=processor
        self.id=id
        self.qubitToTeleport=qubitToTeleport


        self.sender=sender
        self.receiver=receiver
        
        self.portQlist=portQlist
        self.portClist=portClist

        self.wStateResult=None

        self.myQT_Sender=None
        self.myQT_Receiver=None

        self.t1=t1
        self.t2=t2
        
    def run(self):
        #print(self.processor.name)
        #self.showIdentity()
        
        # Side receive a qubit from Center
        port=self.node.ports[self.portQlist[0]]
        yield self.await_port_input(port)
        wQubit = port.rx_input().items
        #print("S ID:",self.id," I received:",wQubit)
        self.processor.put(wQubit[0])
        
        # Side measures the qubit in standard basis if not sender or receiver.
        if (self.sender==False) and (self.receiver==False) :
            #print(self.processor.name)
            myQMeasure = QMeasure([0])
            self.processor.execute_program(myQMeasure,qubit_mapping=[0])
            self.processor.set_program_fail_callback(ProgramFail,info=self.processor.name,once=True)


            yield self.await_program(processor=self.processor)
            self.wStateResult = myQMeasure.output['0'][0]

            #print("S res ID:",self.id,"self.wStateResult: ",self.wStateResult)
            #print("S sending classical message from", self.portClist[0]," to center...")
            self.node.ports[self.portClist[0]].tx_output(self.wStateResult)


        #else:
            #print("S else case")
            #yield self.await_program(processor=self.processor)
            
        port=self.node.ports["PortCside2"]
        yield self.await_port_input(port)
        rec = port.rx_input().items
        #print("S ID:",self.id," I received ans:",rec)

        if rec[0] == 'Abort':
            #print("Aborting!")
            return 1



        
        # wait for t1 ns
        if self.t1>0:
            yield self.await_timer(duration=self.t1)

        # make teleportation
        if self.sender == True:
            #print("S sender teleporting")
           
            #print("qubitToTeleport:",self.qubitToTeleport)
            self.myQT_Sender = QuantumTeleportationSender(node=self.node,
                processor=self.processor,SendQubit=self.qubitToTeleport,EPR_1=self.processor.pop(0)[0],portNames=["PortTele_S"])
            
            self.myQT_Sender.start()

        elif self.receiver == True:
            #print("S receiver teleporting")
            self.myQT_Receiver = QuantumTeleportationReceiver(node=self.node,
                processor=self.processor,bellState=3,EPR_2=self.processor.pop(0)[0],portNames=["PortTele_R"],delay=self.t2)
            self.myQT_Receiver.start()

        #else:
            #print("else case")


        
        
    def showIdentity(self):
        if self.sender==True:
            print("S I am sender")
        elif self.receiver==True:
            print("S I am receiver")
        else:
            print("S I am normal side node")
            

