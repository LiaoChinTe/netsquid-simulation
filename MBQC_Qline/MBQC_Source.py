from netsquid.components.qprogram import QuantumProgram
from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock
from netsquid.components.instructions import INSTR_H,INSTR_CZ
from netsquid.components.qsource import SourceStatus


import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)

class Dummy(QuantumProgram):
    def __init__(self):
        super().__init__()

    def program(self):

        yield self.run(parallel=False)


class SourceGen(QuantumProgram):
    def __init__(self,num_bits):
        self.num_bits=num_bits
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        mylogger.debug("SourceGen running ")

        for i in range(self.num_bits):
            self.apply(INSTR_H, qList_idx[i])

            if i%2==1:
                self.apply(INSTR_CZ, [i,i-1], physical=True) 

        yield self.run(parallel=False)



class MBQC_SourceProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=2,source_frq=1e6):
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits
        self.source_frq=source_frq

        self.sourceQList=[]

        #generat qubits from source
        self.MBQC_Source = QSource("MBQC_source",status=SourceStatus.EXTERNAL) # enable frequency
        self.MBQC_Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)

        self.portList=["portQO"]




    def run(self):
        mylogger.debug("SourceProtocol running")

        self.A_genQubits(num_bits=self.num_bits,freq=self.source_frq)

        
        # Q program C1
        mylogger.debug("self.num_bits:{}".format(self.num_bits)) 
        mySourceGen=SourceGen(num_bits=self.num_bits)
        self.processor.execute_program(mySourceGen,qubit_mapping=[i for  i in range(self.num_bits)]) 
        yield self.await_program(processor=self.processor)

        # send qubits to Alice
        mylogger.debug("Sending qubits to Alice")
        inx=list(range(self.num_bits))
        payload=self.processor.pop(inx)
        self.node.ports["portQO"].tx_output(payload)








    def A_genQubits(self,num_bits,freq=1e6):
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num_bits)
        mylogger.debug("source freq:{}".format(freq))
        try:
            clock.ports["cout"].connect(self.MBQC_Source.ports["trigger"])
        except:
            pass
        clock.start()

    # for Source to store qubits in qmem
    def storeSourceOutput(self,qubit):

        self.sourceQList.append(qubit.items[0])
        if len(self.sourceQList)==self.num_bits:
            mylogger.debug("qubit stored")
            self.processor.put(qubits=self.sourceQList)
            myDummy=Dummy()
            self.processor.execute_program(myDummy)
    
