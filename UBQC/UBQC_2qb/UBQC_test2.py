from random import randint

from netsquid.protocols import NodeProtocol
import netsquid as ns
from netsquid.nodes.node import Node
'''
UBQC Test2

1. Generate 2 qubits with |0>. Named q1, q2.

2. Apply X gate on q1 if random d = 1, apply H gate on q2.

3. Apply rotation along Z-axis according to random theta on q2.

4. Apply control-Z on q1 and q2.

5. Choose random r = 0 or 1.

6. Measure q2 with angle theta+(d+r)*pi, assign result to b.

7. Check whether r = b.

'''
from netsquid.components.qprocessor import *
from netsquid.components.qprogram import *
from netsquid.components.models import  FibreDelayModel
from netsquid.components.models.qerrormodels import *
from netsquid.components.qchannel import QuantumChannel

from netsquid.components import QSource,Clock

from netsquid.qubits.qubitapi import *
from netsquid.qubits.qformalism import *
from netsquid.qubits import operators as ops
from netsquid.qubits import ketstates
from netsquid.qubits import Stabilizer


from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *


class QTest2(QuantumProgram):
    def __init__(self,firstState,rotation,position):
        self.firstState=firstState
        self.rotation=rotation
        self.position=position

        super().__init__()

    def program(self):

        #print("in QTest2 self.position",self.position)

        if self.firstState == 1:
            self.apply(INSTR_X, qubit_indices=self.position[0], physical=True)

        
        self.apply(INSTR_H, qubit_indices=self.position[1], physical=True)
        
        
        
        if self.rotation == 1:
            self.apply(INSTR_R45,qubit_indices=self.position[1], physical=True)
        elif self.rotation == 2:
            self.apply(INSTR_R90,qubit_indices=self.position[1], physical=True)
        elif self.rotation == 3:
            self.apply(INSTR_R135,qubit_indices=self.position[1], physical=True)
        elif self.rotation == 4:
            self.apply(INSTR_R180,qubit_indices=self.position[1], physical=True)
        elif self.rotation == 5:
            self.apply(INSTR_R225,qubit_indices=self.position[1], physical=True)
        elif self.rotation == 6:
            self.apply(INSTR_R270,qubit_indices=self.position[1], physical=True)
        elif self.rotation == 7:
            self.apply(INSTR_R315,qubit_indices=self.position[1], physical=True)
        
        
        
        self.apply(INSTR_CZ, qubit_indices=self.position, physical=True)


        ''''''
        yield self.run(parallel=False)
        


class ProtocolTest(NodeProtocol):

    def S_genQubits(self,num,freq=1e4):
        #generat qubits from source
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num)
        try:
            clock.ports["cout"].connect(self.S_Source.ports["trigger"])
        
        except:
            print("already connected")
        
        clock.start()



    def S_put_prepareState(self,message,numQubits=2):
        self.port_output.append(message.items[0])

        if len(self.port_output)==numQubits:
            #print("qubit1:\n",self.port_output[0].qstate.dm)
            #print("qubit2:\n",self.port_output[1].qstate.dm)
            
            self.processor.put(qubits=self.port_output)
            # Prepare States
            
            myprepareStates=QTest2(firstState=self.d,rotation=self.theta,position=[0,1]) #self.d self.theta  #parameter setting
            self.processor.execute_program(myprepareStates,qubit_mapping=[0,1])
            self.processor.set_program_fail_callback(ProgramFail,"QTest2 failed",once=True)



    def __init__(self,node,processor):
        super().__init__()

        self.node=node
        self.processor=processor

        self.theta=randint(0,7)

        self.S_Source = QSource("S_source") 
        self.S_Source.ports["qout0"].bind_output_handler(self.S_put_prepareState,2)
        self.S_Source.status = SourceStatus.EXTERNAL

        self.port_output=[]
        self.d=randint(0,1)
        self.r=randint(0,1)
        self.b=None
        self.XorRes=None
        self.passed=False



    def run(self):

        # gen qubits
        self.S_genQubits(2)   
        yield self.await_program(processor=self.processor)
        
        
        myqubits=self.processor.peek([0, 1])
        #print("two qubits:\n",ns.qubits.reduced_dm(myqubits))
        #print("qubit 1:\n",ns.qubits.reduced_dm(myqubits[0]))
        #print("qubit 2:\n",ns.qubits.reduced_dm(myqubits[1]))

        
        # measured by theta
        myAngleMeasure=AngleMeasure([1],[self.theta+(self.d+self.r)*4])
        self.processor.execute_program(myAngleMeasure,qubit_mapping=[0,1])
        self.processor.set_program_fail_callback(ProgramFail,"AngleMeasure Failed",once=True)
        yield self.await_program(processor=self.processor)

        self.b = myAngleMeasure.output['1'][0]

        #print("After Qtest2==================")
        #print("d:",self.d,"r:",self.r,"theta:",self.theta,"b:",self.b)
        # debug
        #print("after measurement==============")
        myqubits=self.processor.peek([0, 1])
        #print("two qubits:\n",ns.qubits.reduced_dm(myqubits))
        #print("qubit 1:\n",ns.qubits.reduced_dm(myqubits[0]))
        #print("qubit 2:\n",ns.qubits.reduced_dm(myqubits[1]))


        if self.r != self.b:
            self.passed=False
        else:
            self.passed=True

        '''
        xorRes=bool(self.d) ^ bool(self.r)
        if xorRes == True:
            self.XorRes = 1
        else:
            self.XorRes = 0
        
        if self.XorRes != self.b:
            self.passed=False
        else:
            self.passed=True

        '''

        #print("d:",self.d,"r:",self.r,"theta",self.theta,"XOR res:",self.XorRes," b:",self.b,"pass:",self.passed)
        
        
        




def run_UBQC_test(runtimes=1,fibre_len=10**-9,processorNoiseModel=None,memNoiseMmodel=None
               ,loss_init=0,loss_len=0,QChV=3*10**2,CChV=3*10**2): #loss_init=0.25,loss_len=0.2
    
    resList=[]
    successCount=0
    set_qstate_formalism(ns.qubits.QFormalism.DM)
    
    
    for i in range(runtimes): 
        
        ns.sim_reset()

        # nodes====================================================================

        nodeTest1 = Node("testNode1", port_names=["portQT_1"])
        nodeTest2 = Node("testNode2", port_names=["portQT_2"])
        # processors===============================================================
        
        processorTest1=QuantumProcessor("processorTest1", num_positions=2,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=1,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CZ,duration=10,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10, parallel=True),
            PhysicalInstruction(INSTR_R45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R180, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R225, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R270, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R315, duration=1, parallel=True),
                
            PhysicalInstruction(INSTR_Rv45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv180, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv225, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv270, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv315, duration=1, parallel=True),
            
            PhysicalInstruction(INSTR_SWAP, duration=1, parallel=True)])

        processorTest2=QuantumProcessor("processorTest2", num_positions=10,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=1,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CZ,duration=10,quantum_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10, parallel=True),
            PhysicalInstruction(INSTR_R22, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R67, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R112, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R157, duration=1, parallel=True),])



        MyQChannel=QuantumChannel("QChannel_1->2",delay=0,length=fibre_len
            ,models={"quantum_loss_model": FibreLossModel(p_loss_init=loss_init, p_loss_length=loss_len, rng=None)
            ,"delay_model": FibreDelayModel(c=QChV)})
        
        nodeTest1.connect_to(nodeTest2, MyQChannel,
            local_port_name =nodeTest1.ports["portQT_1"].name,
            remote_port_name=nodeTest2.ports["portQT_2"].name)


        myprotocolTest1 = ProtocolTest(nodeTest1,processorTest1)
        #myprotocolTest2 = ProtocolTest(nodeTest2,processorTest2)

        myprotocolTest1.start()
        #myprotocolTest2.start()

        #ns.logger.setLevel(1)
        print("version:",ns.__version__)
        stats = ns.sim_run()


        #print("theta:",myprotocolTest1.theta)
        if myprotocolTest1.passed==True:
            successCount+=1
    
    print(successCount)
    

run_UBQC_test(runtimes=100)
