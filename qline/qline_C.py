from netsquid.protocols import NodeProtocol
from netsquid.components import Clock

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *


class CharlieProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10,role=0): #role value:[-1,0,1] 1 is the first party to form key
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits

        self.role=role
        self.portList=["portQI","portQO","portCI","portCO"]

    def run(self):
        print("CharlieProtocol running")

        port=self.node.ports["portQI"]
        yield self.await_port_input(port)
        tmp = port.rx_input().items
        print("C received",tmp)



