

from netsquid.protocols import NodeProtocol

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

class TP_SenderTeleport(QuantumProgram):
    
    def __init__(self):
        super().__init__()
        
    def program(self):
        
        # EPR-like        
        self.apply(INSTR_CNOT, [0, 1])
        self.apply(INSTR_H, 0) 
        
        self.apply(INSTR_MEASURE,qubit_indices=0, output_key='0',physical=True) # measure the origin state
        self.apply(INSTR_MEASURE,qubit_indices=1, output_key='1',physical=True) # measure the epr1
        
        yield self.run(parallel=False)



class QuantumTeleportationSender(NodeProtocol):
    
    def __init__(self,node,processor,SendQubit,EPR_1,portNames=["portC_Sender"]): 
        super().__init__()
        self.node=node
        self.processor=processor
        self.SendQubit=SendQubit
        self.EPR_1=EPR_1
        self.measureRes=None
        self.portNameCS1=portNames[0]
        
        self.processor.put([SendQubit,EPR_1])
        
        
        
    def run(self):
        
        # Entangle the two qubits and measure
        myTP_SenderTeleport=TP_SenderTeleport()
        self.processor.execute_program(myTP_SenderTeleport,qubit_mapping=[0,1])
        self.processor.set_program_fail_callback(ProgramFail,info=self.processor.name,once=True)
        
        yield self.await_program(processor=self.processor)
        self.measureRes=[myTP_SenderTeleport.output['0'][0],myTP_SenderTeleport.output['1'][0]]

        # Send results to Receiver
        self.node.ports[self.portNameCS1].tx_output(self.measureRes)
        
        