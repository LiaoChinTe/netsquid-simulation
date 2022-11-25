from netsquid.components.qprogram import QuantumProgram
from netsquid.protocols import NodeProtocol
from netsquid.components.instructions import INSTR_H,INSTR_MEASURE,INSTR_MEASURE_X
from netsquid.qubits import qstate  # QState


from netsquid.qubits.qformalism import QFormalism, set_qstate_formalism
from netsquid.qubits.qubitapi import *

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import RotateQubits

import logging
#logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)


set_qstate_formalism(QFormalism.DM)

class ServerMeasure(QuantumProgram):
    def __init__(self,positionIndex):
        self.positionIndex=positionIndex
        super().__init__()
        
    def program(self):
        mylogger.debug("ServerMeasure positionIndex: {} ".format(self.positionIndex))

        #self.apply(INSTR_Rv90, qubit_indices=self.positionIndex, physical=True)
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


        # receive delta1 from TEE
        port=self.node.ports["portC"]
        yield self.await_port_input(port)
        self.delta1 = port.rx_input().items[0]
        mylogger.debug("Server received delta1 from TEE:{}".format(self.delta1))

        # receive qubits from Bob
        port=self.node.ports["portQI"]
        yield self.await_port_input(port)
        myqubitList = port.rx_input().items
        mylogger.debug("Server received qubits from Bob:{}".format(myqubitList))
        # put qubits in the processor
        self.processor.put(myqubitList)


        # apply rotation to the qubit 1
        mylogger.debug("Server rotate qubit1 with index:{} angle:{} pi".format(self.delta1,-self.delta1/4))
        myRotate1=RotateQubits([0],[-self.delta1]) #self.delta1
        self.processor.execute_program(myRotate1,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)
        

        # apply measurement to qubit 1
        myServerMeasure=ServerMeasure(0)
        self.processor.execute_program(myServerMeasure,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)
        # assign measurement output to m1
        self.m1=myServerMeasure.output[str(0)][0]
        mylogger.debug("Server measured m1:{}".format(self.m1))


        # send m1 to TEE
        self.node.ports["portC"].tx_output(self.m1)
        

        # receive delta2 
        port=self.node.ports["portC"]
        yield self.await_port_input(port)
        self.delta2 = port.rx_input().items[0]
        mylogger.debug("Server received self.delta2 from TEE:{}".format(self.delta2))


        # apply rotation to the qubit 2
        mylogger.debug("Server rotate qubit2 with index:{} angle:{} pi".format(self.delta2,self.delta2/4))
        myRotate2=RotateQubits([1],[-self.delta2])
        self.processor.execute_program(myRotate2,qubit_mapping=[i for  i in range(self.num_bits)]) #
        yield self.await_program(processor=self.processor)
        
        
        

        # peek qstate
        '''
        tmp=self.processor.peek(1)
        mylogger.debug("Server peek q2:{} \nstate:{}".format(tmp[0],tmp[0].qstate.qrepr.reduced_dm())) #.qstate #.qrepr.reduced_dm() #.qstate.dm
        '''

        # apply measurement to qubit 2
        #mylogger.debug("Start ServerMeasure")
        myServerMeasure2=ServerMeasure(1)
        self.processor.execute_program(myServerMeasure2,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)
        # assign measurement output to m1
        #mylogger.debug("Server check q2 output:{}".format(myServerMeasure2.output))
        self.m2=myServerMeasure2.output[str(1)][0]
        mylogger.debug("Server measured m2:{}".format(self.m2))


        # send m2 to TEE
        self.node.ports["portC"].tx_output(self.m2)
