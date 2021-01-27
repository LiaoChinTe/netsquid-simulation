from netsquid.protocols import NodeProtocol
from netsquid.qubits.operators import X,H,Z,CNOT

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

QTpath = "../QuantumTeleportation/"
sys.path.append(QTpath)
from sender_QT import *
from receiver_QT import *



'''
Anonymous Transmission in W-state

Star network
Side nodes

'''

class AT_Wstate_side(NodeProtocol):
    
    def __init__(self,node,processor,id,sender=False,receiver=False
        ,portQlist=["PortQside"],portClist=["PortCside1","PortCside2"]): 
        super().__init__()
        self.node=node
        self.processor=processor
        self.id=id

        self.sender=sender
        self.receiver=receiver
        
        self.portQlist=portQlist
        self.portClist=portClist

        self.wStateResult=None
        self.receivedState=None
        
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
            
        port=self.node.ports["PortCside2"]
        yield self.await_port_input(port)
        rec = port.rx_input().items
        print("S ID:",self.id," I received ans:",rec)

        if rec[0] == 'Abort':
            print("Aborting!")
            return 1

        '''
        # test
        if self.sender == True:
            self.node.ports[self.portClist[2]].tx_output("ttest")
        elif self.receiver == True:
            port=self.node.ports[self.portClist[2]]
            yield self.await_port_input(port)
            rec = port.rx_input().items
            print("S ID:",self.id," I received test:",rec)
        else:
            print("else case")
        '''


        # make original qubits
        oriQubit = create_qubits(1)[0]
        #operate(oriQubit, X)
        #print("oriQubit:",oriQubit)
        # make 
        if self.sender == True:
            print("S sender teleporting")
            myQT_Sender = QuantumTeleportationSender(node=self.node,
                processor=self.processor,SendQubit=oriQubit,EPR_1=self.processor.pop(0)[0],portNames=["PortTele_S"])
            
            myQT_Sender.start()

        elif self.receiver == True:
            print("S receiver teleporting")
            myQT_Receiver = QuantumTeleportationReceiver(node=self.node,
                processor=self.processor,EPR_2=self.processor.pop(0)[0],portNames=["PortTele_R"])
            myQT_Receiver.start()

            self.receivedState=myQT_Receiver.receivedState
            #print("S self.receivedState:",self.receivedState)
        else:
            print("else case")


        
        
    def showIdentity(self):
        if self.sender==True:
            print("S I am sender")
        elif self.receiver==True:
            print("S I am receiver")
        else:
            print("S I am normal side node")
            

