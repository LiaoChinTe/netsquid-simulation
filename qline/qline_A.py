from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock
from netsquid.components.qsource import SourceStatus


import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *


class AliceProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10):
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits

        #generat qubits from source
        self.A_Source = QSource("Alice_source"
            ,status=SourceStatus.EXTERNAL) # enable frequency
        #self.A_Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)

    def run(self):
        print("AliceProtocol running")


