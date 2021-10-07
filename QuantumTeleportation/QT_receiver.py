from netsquid.protocols import NodeProtocol
from netsquid.qubits.qubitapi import *
#from netsquid.qubits.qformalism import *
from netsquid.qubits.qstate import QState
from netsquid.qubits import set_qstate_formalism, QFormalism


import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

'''
Bell state:

'''
class TP_ReceiverAdjust(QuantumProgram):
    
    def __init__(self,bellState,adjBase):
        super().__init__()
        self.bellState=bellState
        self.adjBase=adjBase
        
        
    def program(self):

        if self.bellState == 1:
            if self.adjBase[0]==1:
                self.apply(INSTR_Z, 0)  
            
            if self.adjBase[1]==1:
                self.apply(INSTR_X, 0)

        elif self.bellState == 3:
            if self.adjBase[0]==1:
                self.apply(INSTR_Z, 0)  
            
            if self.adjBase[1]==0:
                self.apply(INSTR_X, 0)


        else:
            print("R undefined case in TP_ReceiverAdjust")
                
        yield self.run(parallel=False)
        



        
class QuantumTeleportationReceiver(NodeProtocol):
    
    def __init__(self,node,processor,EPR_2,portNames=["portC_Receiver"],bellState=1,delay=0): 
        super().__init__()
        self.node=node
        self.processor=processor
        self.bellState=bellState

        self.resultQubit=EPR_2
        self.portNameCR1=portNames[0]
        self.receivedState=None
        self.processor.put(self.resultQubit)
        self.delay=delay

        set_qstate_formalism(QFormalism.DM)
        
    def run(self):
        
        port=self.node.ports[self.portNameCR1]
        yield self.await_port_input(port)
        res=port.rx_input().items
        #print("R get results:", res)
        

        # wait for delay ns
        if self.delay>0:
            yield self.await_timer(duration=self.delay)


        # edit EPR2 according to res
        myTP_ReceiverAdjust=TP_ReceiverAdjust(self.bellState,res)
        self.processor.execute_program(myTP_ReceiverAdjust,qubit_mapping=[0])
        #self.processor.set_program_done_callback(self.show_state,once=True) # see qstate
        self.processor.set_program_fail_callback(ProgramFail,info=self.processor.name,once=True)
        yield self.await_program(processor=self.processor)




    def show_state(self):
        set_qstate_formalism(QFormalism.DM)
        tmp=self.processor.pop(0)[0]
        print("R final state:",tmp.qstate.dm)