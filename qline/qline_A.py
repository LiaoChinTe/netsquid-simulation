from netsquid.components.qprogram import QuantumProgram
from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock
from netsquid.components.qsource import SourceStatus


import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *



class Dummy(QuantumProgram):
    def __init__(self):
        super().__init__()

    def program(self):

        yield self.run(parallel=False)




class AliceProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10,source_frq=1e9):
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits
        self.source_frq=source_frq

        self.sourceQList=[]

        #generat qubits from source
        self.A_Source = QSource("Alice_source",status=SourceStatus.EXTERNAL) # enable frequency
        self.A_Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)

        #forward_output(self.node.ports["portQO"])
        #bind_output_handler(self.storeSourceOutput)


    def run(self):
        print("AliceProtocol running")

        self.A_genQubits(num_bits=self.num_bits,freq=self.source_frq)
        
        # wait
        yield self.await_program(processor=self.processor)

        print("qubits ready")


    def A_genQubits(self,num_bits,freq=1e9):
        #set clock
        print("in A_genQubits")
        clock = Clock("clock", frequency=freq, max_ticks=num_bits)
        print("num_bits:",num_bits)
        try:
            
            clock.ports["cout"].connect(self.A_Source.ports["trigger"])
        except:
            pass
        #print("ticking")
        clock.start()

    # for Alice to store qubits in qmem
    def storeSourceOutput(self,qubit):

        self.sourceQList.append(qubit.items[0])
        if len(self.sourceQList)==self.num_bits:
            print("qubit stored")
            self.processor.put(qubits=self.sourceQList)
            myDummy=Dummy()
            self.processor.execute_program(myDummy)
    

