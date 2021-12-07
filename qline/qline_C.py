from netsquid.protocols import NodeProtocol
from netsquid.components import Clock

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *


class CharlieProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10):
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits


    def run(self):
        print("CharlieProtocol running")


