from netsquid.protocols import NodeProtocol
from netsquid.components import Clock

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *


class CharlieProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10,isI=False,isT=False):
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits

        self.isI=isI
        self.isT=isT


    def run(self):
        print("CharlieProtocol running")


