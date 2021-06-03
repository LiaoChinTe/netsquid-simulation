from random import randint

from netsquid.protocols import NodeProtocol
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *
from netsquid.components.qprogram import *
from netsquid.components.models import  FibreDelayModel
from netsquid.components.models.qerrormodels import *
from netsquid.components.qchannel import QuantumChannel

from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock

from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "../../lib/"
sys.path.append(scriptpath)
from functions import *


class ProtocolTest(NodeProtocol):

    def S_genQubits(self,num,freq=1e9):
        #generat qubits from source
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num)
        try:
            clock.ports["cout"].connect(self.S_Source.ports["trigger"])
        
        except:
            print("already connected")
        
        clock.start()

    def S_put_prepareEPR(self,message,numQubits=2):
        self.port_output.append(message.items[0])
        if len(self.port_output)==numQubits:
            self.processor.put(qubits=self.port_output)
            # PrepareEPRpairs
            myprepareEPRpairs=PrepareEPRpairs(int(numQubits/2))
            self.processor.execute_program(myprepareEPRpairs,qubit_mapping=[i for  i in range(0, numQubits)])
            self.processor.set_program_fail_callback(ProgramFail,once=True)


    def __init__(self,node,processor):
        super().__init__()

        self.node=node
        self.processor=processor

        self.S_Source = QSource("S_source") 
        self.S_Source.ports["qout0"].bind_output_handler(self.S_put_prepareEPR,2)
        self.S_Source.status = SourceStatus.EXTERNAL

        self.port_output=[]
        self.theta=None
        self.b1=None
        self.b2=None

    def run(self):

        # gen EPR pairs
        self.S_genQubits(4)    # EPR pair formed when port received
        yield self.await_program(processor=self.processor)
        #print("EPR done")


        self.theta=randint(0,7)
        # measured by theta
        myAngleMeasure=AngleMeasure([0,1],[self.theta,-self.theta])
        self.processor.execute_program(myAngleMeasure,qubit_mapping=[0,1])
        self.processor.set_program_fail_callback(ProgramFail,once=True)
        yield self.await_program(processor=self.processor)

        self.b1 = myAngleMeasure.output['0'][0]
        self.b2 = myAngleMeasure.output['1'][0]

        if self.b1 != self.b2:
            print("b1:",self.b1," b2:",self.b2)
    

def run_UBQC_test(runtimes=1,fibre_len=10**-9,processorNoiseModel=None,memNoiseMmodel=None
               ,loss_init=0,loss_len=0,QChV=3*10**2,CChV=3*10**2): #loss_init=0.25,loss_len=0.2
    
    resList=[]
    successCount=0
    set_qstate_formalism(QFormalism.DM)
    
    
    for i in range(runtimes): 
        
        ns.sim_reset()

        # nodes====================================================================

        nodeTest1 = Node("testNode1", port_names=["portQT_1"])
        nodeTest2 = Node("testNode2", port_names=["portQT_2"])
        # processors===============================================================
        
        processorTest1=QuantumProcessor("processorTest1", num_positions=2,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=1, q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=1,q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CZ,duration=10,q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_MEASURE, duration=10, parallel=True),
            PhysicalInstruction(INSTR_MEASURE_X, duration=10, parallel=True),
            PhysicalInstruction(INSTR_R22, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R67, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R112, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R157, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R180, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R202, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R225, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R247, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R270, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R292, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R315, duration=1, parallel=True),
            PhysicalInstruction(INSTR_R337, duration=1, parallel=True),
                
            PhysicalInstruction(INSTR_Rv22, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv45, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv67, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv90, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv112, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv135, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv157, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv180, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv202, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv225, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv247, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv270, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv292, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv315, duration=1, parallel=True),
            PhysicalInstruction(INSTR_Rv337, duration=1, parallel=True),
            
            PhysicalInstruction(INSTR_SWAP, duration=1, parallel=True)])

        processorTest2=QuantumProcessor("processorTest2", num_positions=10,
            mem_noise_models=memNoiseMmodel, phys_instructions=[
            PhysicalInstruction(INSTR_X, duration=1, q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_Z, duration=1, q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_H, duration=1, q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CNOT,duration=1,q_noise_model=processorNoiseModel),
            PhysicalInstruction(INSTR_CZ,duration=10,q_noise_model=processorNoiseModel),
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


        stats = ns.sim_run()


run_UBQC_test(runtimes=1000)
