from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock,QuantumProgram
from netsquid.components.qsource import SourceStatus
from netsquid.components.instructions import INSTR_H,INSTR_X,INSTR_MEASURE,INSTR_MEASURE_X

import sys
scriptpath = "../../lib/"
sys.path.append(scriptpath)
from functions import Compare_basis,Random_basis_gen

import logging
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)

from BB84_Bob import BB84_CompareBasis


class QG_A_qPrepare(QuantumProgram):
    
    def __init__(self,num_bits,HbasisList,XbasisList):
        self.num_bits=num_bits
        self.HbasisList=HbasisList
        self.XbasisList=XbasisList
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)

        for i in range(self.num_bits):
            if self.XbasisList[i]%2==1:                           
                self.apply(INSTR_X, qList_idx[i])        

        for i in range(self.num_bits):
            if self.HbasisList[i]%2==1:                           
                self.apply(INSTR_H, qList_idx[i])
                                         
        yield self.run(parallel=False)


class QG_A_measure(QuantumProgram):
    def __init__(self,basisList,num_bits):
        self.basisList=basisList
        self.num_bits=num_bits
        super().__init__()


    def program(self):   
        for i in range(0,len(self.basisList*2),2):
            if self.basisList[int(i/2)] == 0:           # only even slot       
                self.apply(INSTR_MEASURE, 
                    qubit_indices=i, output_key=str(i),physical=True)  # standard basis
            else:                              # 1 case 
                self.apply(INSTR_MEASURE_X, 
                    qubit_indices=i, output_key=str(i),physical=True) # Hadamard basis
        yield self.run(parallel=False)
 



class AliceProtocol(NodeProtocol):
    
    def __init__(self,node,processor,num_bits,sourceFreq,
                port_names=["portQA_1","portCA_1","portCA_2"]):
        super().__init__()
        self.num_bits=num_bits
        self.node=node
        self.processor=processor
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1] #from
        self.portNameC2=port_names[2] #to
        self.EPRList=None
        self.HbasisList=Random_basis_gen(self.num_bits)
        self.XbasisList=Random_basis_gen(self.num_bits)
        self.loc_measRes=[]
        self.key=[]
        self.sourceQList=[]
        self.sourceFreq=sourceFreq
        
        #generat qubits from source
        self.A_Source = QSource("Alice_source",status=SourceStatus.EXTERNAL) # enable frequency
        self.A_Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)
        
    # =======================================A run ============================
    def run(self):

        

        # A generat qubits
        self.A_genQubits(self.num_bits,self.sourceFreq)
        
        # wait
        yield self.await_program(processor=self.processor)
        
        # send qubits
        #self.A_sendEPR()
        inx=list(range(self.num_bits))
        payload=self.processor.pop(inx)
        self.node.ports[self.portNameQ1].tx_output(payload)

        # receive B basis
        port=self.node.ports[self.portNameC1]
        yield self.await_port_input(port)
        basis_B = port.rx_input().items
        mylogger.info("A received basis from B:{}\n".format(basis_B))
        
        
        # send A basis to B
        self.node.ports[self.portNameC2].tx_output(self.HbasisList)

        nHbasis,nXbasis,matchA=BB84_CompareBasis(self.HbasisList,basis_B,self.XbasisList)
        mylogger.info("A nHbasis:{}\n nXbasis:{}\n matchA:{}\n".format(nHbasis,nXbasis,matchA))

        # receive matchB
        port=self.node.ports[self.portNameC1]
        yield self.await_port_input(port)
        matchB=port.rx_input().items
        mylogger.info("A received matchB:{}\n".format(matchB))

        # send matchA
        self.node.ports[self.portNameC2].tx_output(matchA)


        for n,item in enumerate(matchA):
            self.key.append(matchB[n]^item) #XOR

        mylogger.info("A key:{}\n".format(self.key))

        '''
        # compare basis
        self.loc_measRes=Compare_basis(self.basisList,basis_B,self.loc_measRes)
        
        self.key=''.join(map(str, self.loc_measRes))
        #print("A key:",self.key)
        '''


        

    def storeSourceOutput(self,qubit):
        self.sourceQList.append(qubit.items[0])
        if len(self.sourceQList)==self.num_bits:
            self.processor.put(qubits=self.sourceQList)
            
            # apply H detector
            PG_qPrepare=QG_A_qPrepare(num_bits=self.num_bits,HbasisList=self.HbasisList,XbasisList=self.XbasisList)
            self.processor.execute_program(
                PG_qPrepare,qubit_mapping=[i for  i in range(0, self.num_bits)])
    

    def A_genQubits(self,num,freq=8e7):
        
        
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num)
        try:
            clock.ports["cout"].connect(self.A_Source.ports["trigger"])
        except:
            pass
            #print("alread connected") 
            
        clock.start()
        
            
    def A_sendEPR(self):
        inx=list(range(self.num_bits))
        payload=self.processor.pop(inx)
        self.node.ports[self.portNameQ1].tx_output(payload)

    def showStatus(self):
        print("A Xbasis:",self.XbasisList)
        print("A Hbasis:",self.HbasisList)