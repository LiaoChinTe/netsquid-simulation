
from netsquid.protocols import NodeProtocol
from netsquid.qubits.qubitapi import *
from netsquid.qubits.qformalism import *

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *


class TP_ReceiverAdjust(QuantumProgram):
    
    def __init__(self,adjBase):
        super().__init__()
        self.adjBase=adjBase
        
        
    def program(self):
        
        if self.adjBase[0]==1:
            self.apply(INSTR_Z, 0)  
        
        if self.adjBase[1]==1:
            self.apply(INSTR_X, 0)
            
        yield self.run(parallel=False)
        



        
class QuantumTeleportationReceiver(NodeProtocol):
    
    def __init__(self,node,processor,EPR_2,portNames=["portC_Receiver"]): 
        super().__init__()
        self.node=node
        self.processor=processor
        self.resultQubit=EPR_2
        self.portNameCR1=portNames[0]
        #set_qstate_formalism(QFormalism.DM)
        
        self.processor.put(self.resultQubit)
        
    def run(self):
        
        port=self.node.ports[self.portNameCR1]
        yield self.await_port_input(port)
        res=port.rx_input().items
        print("R get results:", res)
        
        # edit EPR2 according to res
        myTP_ReceiverAdjust=TP_ReceiverAdjust(res)
        self.processor.execute_program(myTP_ReceiverAdjust,qubit_mapping=[0])
        self.processor.set_program_done_callback(self.show_state,once=True)
        self.processor.set_program_fail_callback(ProgramFail,once=True)
        
    def show_state(self):
        set_qstate_formalism(QFormalism.DM)
        tmp=self.processor.pop(0)[0]
        print("final state:\n",tmp.qstate.dm)