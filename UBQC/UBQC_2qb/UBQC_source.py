import logging
logger = logging.getLogger(__name__)

from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock
from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "../../lib/"
sys.path.append(scriptpath)
from functions import * #What we use from there: PrepareEPRpairs

class EPRGen(NodeProtocol):
    def __init__(self, node, processor, port_names=["ClCI", "ClQO", "SeQO", "ClCO", "SeCO"]):
        super().__init__()
        self.node = node
        self.processor = processor
        self.portClCI = self.node.ports[port_names[0]]
        self.portClQO = self.node.ports[port_names[1]]
        self.portSeQO = self.node.ports[port_names[2]]
        self.portClCO = self.node.ports[port_names[3]]
        self.portSeCO = self.node.ports[port_names[4]]
        self.round_idx = 0

        self.S_Source = QSource("S_source") 
        self.S_Source.ports["qout0"].bind_output_handler(self.S_put_prepareEPR,2)
        self.S_Source.status = SourceStatus.EXTERNAL

        self.port_output = []
        
    def S_genQubits(self,num,freq=1e9):
        #generate qubits from source
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num)
        try:
            clock.ports["cout"].connect(self.S_Source.ports["trigger"])
        
        except:
            logger.info("Already connected")
        
        clock.start()
        
    def S_put_prepareEPR(self,message):
        self.port_output.append(message.items[0])
        if len(self.port_output)==2:
            self.processor.put(qubits=self.port_output)
            prepareEPRpairs=PrepareEPRpairs(1)
            self.processor.execute_program(prepareEPRpairs,qubit_mapping=[0,1])
            self.processor.set_program_fail_callback(self.ProgramFail,once=True)

    def S_sendEPR(self):
        self.portClQO.tx_output(self.processor.pop([0])) # send qubit to client        
        self.portSeQO.tx_output(self.processor.pop([1])) # send qubit to server

        
    def run(self):
        #wait for a command to create and send an EPR pair
        yield self.await_port_input(self.portClCI)
        received_message=self.portClCI.rx_input().items
        logger.info(f"Recieved signal from Client: {received_message}" )
        self.round_idx = self.round_idx + 1
        if (received_message[0] == "generateEPR"):
            self.S_genQubits(2) # generate the pair
            yield self.await_program(processor=self.processor) 


            self.portClCO.tx_output(f"{self.round_idx}") #send idx to client
            self.portSeCO.tx_output(f"{self.round_idx}") #send idf to server
            
            self.S_sendEPR() #send each end of the pair
            # self.portClQO.tx_output(self.processor.pop([0])) # send qubit to client        
            # self.portSeQO.tx_output(self.processor.pop([1])) # send qubit to server

            logger.info(f'EPR pair generated and sent with round_idx: {self.round_idx}')
        else:
            logger.info("Recieved a command that was not understood")

    def ProgramFail(self):
        logger.info("Program failed!!")
