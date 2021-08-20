from netsquid.protocols import NodeProtocol

import sys
scriptpath = "../../lib/"
sys.path.append(scriptpath)
from functions import *



'''
To add value -1 on tarList at positions given by lossList.
input:
    lossList: A list indecates positions to add -1. (list of int)
    tarList: List to add -1. (list of any)
output:
    tarList: target List.(list of any)
'''
def AddLossCase(lossList,tarList):
    for i in range(len(lossList)):
        tarList.insert(lossList[i],-1)
    return tarList




'''
input:
    Pg: A quantum program (QuantumProgram)
output:
    resList: A list of outputs from the given quantum program, 
    also sorted by key.(list of int)
'''

def getPGoutput(Pg):
    resList=[]
    tempDict=Pg.output
    if "last" in tempDict:
        del tempDict["last"]
        
    # sort base on key
    newDict=sorted({int(k) : v for k, v in tempDict.items()}.items())
    
    #take value
    for k, v in newDict:
        resList.append(v[0])
    return resList


class QG_B_measure(QuantumProgram):
    def __init__(self,basisList,num_bits):
        self.basisList=basisList
        self.num_bits=num_bits
        super().__init__()


    def program(self):   
        for i in range(len(self.basisList)):
            if self.basisList[i] == 0:                  # standard basis
                self.apply(INSTR_MEASURE, 
                    qubit_indices=i, output_key=str(i),physical=True) 
            else:                              # 1 case # Hadamard basis
                self.apply(INSTR_MEASURE_X, 
                    qubit_indices=i, output_key=str(i),physical=True) 
        yield self.run(parallel=False)



class BobProtocol(NodeProtocol):
    
    def __init__(self,node,processor,num_bits,
                port_names=["portQB_1","portCB_1","portCB_2"]):
        super().__init__()
        self.num_bits=num_bits
        self.node=node
        self.processor=processor
        self.qList=None
        self.loc_measRes=[-1]*self.num_bits
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1]
        self.portNameC2=port_names[2]
        # init value assume that all qubits are lost
        self.key=None
        self.PG_B=None
        self.lossList=[]
        self.firstLoss=0
        self.endTime=None

    # =======================================B run ============================
    def run(self):
        
        qubitList=[]
        
        #receive qubits from A
        
        port = self.node.ports[self.portNameQ1]
        qubitList=[]
        
        #receive qubits from A
        
        
        yield self.await_port_input(port)
        qubitList.append(port.rx_input().items)
        #print("B received qubits:",qubitList)
        self.B_checkLoss(qubitList[0])
        
        
        #put qubits into B memory
        for qubit in qubitList:
            self.processor.put(qubit)
        
        self.myQG_B_measure=QG_B_measure(
            basisList=self.basisList,num_bits=self.num_bits)
        self.processor.execute_program(
            self.myQG_B_measure,qubit_mapping=[i for  i in range(0,self.num_bits)])
        
        # get meas result
        self.processor.set_program_done_callback(self.B_getPGoutput,once=True)
        
        yield self.await_program(processor=self.processor)
        

        # add Loss case
        self.loc_measRes=AddLossCase(self.lossList,self.loc_measRes)
        self.basisList=AddLossCase(self.lossList,self.basisList)
        
        # add first loss
        if self.firstLoss>=1:   
            for i in range(self.firstLoss):
                self.loc_measRes.insert(0,-1)
                self.basisList.insert(0,-1)
        
        # self.B_send_basis()
        self.node.ports[self.portNameC1].tx_output(self.basisList)
        
        # wait for A's basisList
        port=self.node.ports[self.portNameC2]
        yield self.await_port_input(port)
        basis_A=port.rx_input().items
        #print("B received basis_A:",basis_A)
        
        self.loc_measRes=Compare_basis(self.basisList,basis_A,self.loc_measRes)
        
        self.key=''.join(map(str, self.loc_measRes))
        #print("B key:",self.key)
        self.endTime=ns.sim_time()
        
        
    def B_checkLoss(self,qList):
        num_inx=int(qList[0].name[14:-len('-')-1]) # get index from bits

        self.lossList=[]
        for idx,qubit in enumerate(qList):
            loc_num=int(qubit.name[14:-len('-')-1]) # received qubit
            found_flag=True
            while(found_flag and len(self.lossList)<self.num_bits):
                if loc_num==num_inx:
                    found_flag=False
                else:
                    self.lossList.append(idx)
                num_inx+=2
                
        # init B's basisList
        self.basisList=Random_basis_gen(len(qList))
        
        # check for first N qubit loss
        if self.num_bits-len(self.lossList)>len(qList):
            # first qubit loss detected
            # value of self.firstLoss indecats how many qubits are lost
            self.firstLoss=self.num_bits-len(qList)-len(self.lossList)  
        else:
            self.firstLoss=0

    
    def B_getPGoutput(self):
        self.loc_measRes=getPGoutput(self.myQG_B_measure)

