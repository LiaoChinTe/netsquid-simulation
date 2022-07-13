from netsquid.components.qprogram import QuantumProgram
from netsquid.protocols import NodeProtocol
from netsquid.components.instructions import INSTR_H,INSTR_MEASURE,INSTR_MEASURE_X

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import RotateQubits

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)

class ServerHmeasure(QuantumProgram):
    def __init__(self,positionIndex):
        self.positionIndex=positionIndex
        super().__init__()
        
    def program(self):
        mylogger.debug("ServerHmeasure running ")
        mylogger.debug("positionIndex: {} ".format(self.positionIndex))

        self.apply(INSTR_H,qubit_indices=self.positionIndex, physical=True)
        self.apply(INSTR_MEASURE_X,qubit_indices=self.positionIndex, output_key=str(self.positionIndex),physical=True) 

        yield self.run(parallel=False)




class MBQC_ServerProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=2): 
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.portList=["portQI","portC"]

        self.num_bits=num_bits

        self.delta1=None
        self.delta2=None
        self.m1=None
        self.m2=None

    def run(self):
        mylogger.debug("MBQC_ServerProtocol running")


        # receive qubits from Bob
        port=self.node.ports["portQI"]
        yield self.await_port_input(port)
        qubits = port.rx_input().items
        mylogger.debug("Server received qubits from Bob:{}".format(qubits))

        # put qubits in processor
        self.processor.put(qubits)

        # apply rotation
        myRotate1=RotateQubits([0],[self.delta1])
        self.processor.execute_program(myRotate1,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)

        # apply H and measurement
        myServerHmeasure=ServerHmeasure(0)
        self.processor.execute_program(myServerHmeasure,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)

        # assign measurement output to m1
        self.m1=myServerHmeasure.output[str(0)][0]
        mylogger.debug("Server m1:{}".format(self.m1))

        # send m1 to TEE
        self.node.ports["portC"].tx_output(self.m1)
        

        # receive delta2 
        port=self.node.ports["portC"]
        yield self.await_port_input(port)
        self.delta2 = port.rx_input().items[0]
        mylogger.debug("Server received self.delta2 from TEE:{}".format(self.delta2))


        # apply rotation
        myRotate2=RotateQubits([0],[self.delta1])
        self.processor.execute_program(myRotate2,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)

        # apply H and measurement
        myServerHmeasure=ServerHmeasure(0)
        self.processor.execute_program(myServerHmeasure,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)


        # assign measurement output to m1
        self.m2=myServerHmeasure.output[str(0)][0]
        mylogger.debug("Server m2:{}".format(self.m2))


        # send m2 to TEE
        self.node.ports["portC"].tx_output(self.m2)
