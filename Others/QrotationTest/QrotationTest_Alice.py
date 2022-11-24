from netsquid.util import simtools 
from netsquid.protocols import NodeProtocol
from netsquid.components import QuantumProgram,QSource,Clock
from netsquid.components.instructions import INSTR_H,INSTR_CZ,INSTR_MEASURE,INSTR_MEASURE_X
from netsquid.components.qsource import SourceStatus,QSource

from netsquid.qubits import qstate 


import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from functions import RotateQubits

import logging
#logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)


class Dummy(QuantumProgram):
    def __init__(self):
        super().__init__()

    def program(self):

        yield self.run(parallel=False)



class AliceH(QuantumProgram):
    def __init__(self,num_bits):
        self.num_bits=num_bits
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        
        
        for i in range(self.num_bits):
            mylogger.debug("Alice apply H in position:{}".format(i))
            self.apply(INSTR_H, qList_idx[i])

        '''
            #if i%2==1:
            #    self.apply(INSTR_CZ, [i,i-1], physical=True) 
        '''
        yield self.run(parallel=False)



class AliceMeasureTest(QuantumProgram):
    def __init__(self,pos):
        self.pos=pos
        super().__init__()    
        
    def program(self):

        mylogger.debug("AliceMeasureTest measured pos:{}".format(self.pos))
        self.apply(INSTR_MEASURE_X,qubit_indices=self.pos, output_key=str(self.pos),physical=True) 
        
        yield self.run(parallel=False)



class QrotationTest_AliceProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=1): 
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits
        self.sourceQList=[]
        self.m=None
        

        self.Source = QSource("MySource",status=SourceStatus.EXTERNAL) # enable frequency
        self.Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)

    def run(self):

        #set clock
        clock = Clock("clock", frequency=6000, max_ticks=2)
        try:
            clock.ports["cout"].connect(self.Source.ports["trigger"])
        except:
            pass
        clock.start()

        yield self.await_program(processor=self.processor)
        


        mylogger.debug("rotate qubit1 with index:{}".format(1))
        myRotate1=RotateQubits([0],[-7]) 
        self.processor.execute_program(myRotate1,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)
        


        # measure
        myAliceMeasureTest=AliceMeasureTest(0) 
        self.processor.execute_program(myAliceMeasureTest,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)
        
        
        # get outcome
        self.m=myAliceMeasureTest.output[str(0)][0]
        mylogger.debug("measured m:{}".format(self.m))
        
        
        '''
        # rotate 2 qubits
        myAliceRotate=AliceRotate(self.num_bits,self.theta1,self.theta2,self.x1,self.x2)
        self.processor.execute_program(myAliceRotate,qubit_mapping=[i for  i in range(self.num_bits)])
        yield self.await_program(processor=self.processor)
        '''
        

    def storeSourceOutput(self,qubit):

        self.sourceQList.append(qubit.items[0])
        if len(self.sourceQList)==self.num_bits:
            mylogger.debug("qubit stored {}".format(self.sourceQList))
            self.processor.put(qubits=self.sourceQList)
            myAliceH=AliceH(self.num_bits)
            self.processor.execute_program(myAliceH,qubit_mapping=[i for  i in range(self.num_bits)]) 




