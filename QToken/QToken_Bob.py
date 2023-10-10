
from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock
from netsquid.components.qsource import SourceStatus
from netsquid.qubits.operators import X,H,Z
from netsquid.components.qprogram import QuantumProgram
from netsquid.components.instructions import INSTR_X,INSTR_Z,INSTR_H

from random import randint



'''
Only used in this protocol.
input:
    basisInxList: Oroginal sets of qubits:(list of N)
        0:(0,+)  1:(0,-)  2:(1,+)  3:(1,-)
        4:(+,0)  5:(+,1)  6:(-,0)  7:(-,1)
    randMeas:(int 0/1)
        0: standard basis   1: H basis
    locRes:(list of 2*N)
        received measurement to check
    validList:(list of int)
        A list of index indicating valid qubits after filter. 
output:
    res: 
        the persentage of passed qubits among all qubits.
'''
def TokenCheck_LossTolerant(basisInxList,randMeas,locRes,validList):
    # padding for locRes
    tmpRes=[-1]*(2*len(basisInxList)-len(validList))
    if len(locRes)!=len(validList):
        print("Measurment length Error!")
        return []
    

    for i in range(len(validList)):
        tmpRes.insert(validList[i]-1, locRes[i])
        

    # checking
    failCount=0
    if randMeas==0:
        for i in range(len(basisInxList)):
            if basisInxList[i]<=1 and tmpRes[2*i]==0:
                pass
            elif basisInxList[i]<=3 and tmpRes[2*i]==1:
                pass
            elif basisInxList[i]%2==0 and tmpRes[2*i+1]==0:
                pass
            elif basisInxList[i]%2==1 and tmpRes[2*i+1]==1:
                pass
            else:
                failCount+=1
    else: # randMeas==1:
        for i in range(len(basisInxList)):
            if basisInxList[i]>=6 and tmpRes[2*i]==1:
                pass
            elif basisInxList[i]>=4 and tmpRes[2*i]==0:
                pass
            elif basisInxList[i]%2==0 and tmpRes[2*i+1]==0:
                pass
            elif basisInxList[i]%2==1 and tmpRes[2*i+1]==1:
                pass
            else:
                failCount+=1
    
    
    '''
    print("in TokenCheck_LossTolerant")
    print("randMeas: ",randMeas)
    print("len(locRes): ",len(locRes))           #scale /100
    print("failCount: ",failCount)                   #scale  /max 50
    print("len(basisInxList): ",len(basisInxList)) # 50
    '''
    
    
    return 1-(failCount-len(basisInxList)+len(locRes)/2)/(len(locRes)/2)


def TokenCheck(basisInxList,randMeas,locRes):
    
    #check parameters
    print(f"TokenCheck check parameters,basisInxList:{basisInxList},randMeas:{randMeas},locRes:{locRes} ")

    if 2*len(basisInxList)!=len(locRes):
        print("Measurment length Error!")
        print(f"basisInxList:{len(basisInxList)},locRes:{len(locRes)}")
        return []

    tmpRes=locRes

    # checking
    failCount=0
    if randMeas==0:
        for i in range(len(basisInxList)):
            if basisInxList[i]<=1 and tmpRes[2*i]==0:
                pass
            elif basisInxList[i]<=3 and tmpRes[2*i]==1:
                pass
            elif basisInxList[i]>3 and basisInxList[i]%2==0 and tmpRes[2*i+1]==0:
                pass
            elif basisInxList[i]>3 and basisInxList[i]%2==1 and tmpRes[2*i+1]==1:
                pass
            else:
                failCount+=1
    else: # randMeas==1:
        for i in range(len(basisInxList)):
            if basisInxList[i]>=6 and tmpRes[2*i]==1:
                pass
            elif basisInxList[i]>=4 and tmpRes[2*i]==0:
                pass
            elif basisInxList[i]<4 and basisInxList[i]%2==0 and tmpRes[2*i+1]==0:
                pass
            elif basisInxList[i]<4 and basisInxList[i]%2==1 and tmpRes[2*i+1]==1:
                pass
            else:
                #print("Fail",basisInxList[i]," ",tmpRes[2*i+1])
                failCount+=1
    
    
    '''
    print("in TokenCheck")
    print("randMeas: ",randMeas)
    print("len(locRes): ",len(locRes))           
    print("failCount: ",failCount)                   
    print("len(basisInxList): ",len(basisInxList)) 
    '''
    
    return 1-(failCount/len(basisInxList))  




# class of quantum program
class QG_B_qPrepare(QuantumProgram):
    def __init__(self,num_bits,stateInxList):
        self.num_bits=num_bits
        self.stateInxList=stateInxList
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(2*self.num_bits)
        '''
        0:(0,+)  1:(0,-)  2:(1,+)  3:(1,-)
        4:(+,0)  5:(+,1)  6:(-,0)  7:(-,1)
        '''
        for i in range(self.num_bits):
            if self.stateInxList[i]==0:                           
                self.apply(INSTR_H, qList_idx[2*i+1])
            elif self.stateInxList[i]==1:                                
                self.apply(INSTR_X, qList_idx[2*i+1])
                self.apply(INSTR_H, qList_idx[2*i+1])
            elif self.stateInxList[i]==2:                                
                self.apply(INSTR_X, qList_idx[2*i])
                self.apply(INSTR_H, qList_idx[2*i+1])
            elif self.stateInxList[i]==3:                                
                self.apply(INSTR_X, qList_idx[2*i])
                self.apply(INSTR_X, qList_idx[2*i+1])
                self.apply(INSTR_H, qList_idx[2*i+1])
            elif self.stateInxList[i]==4:                                
                self.apply(INSTR_H, qList_idx[2*i])
            elif self.stateInxList[i]==5:                                
                self.apply(INSTR_H, qList_idx[2*i])
                self.apply(INSTR_X, qList_idx[2*i+1])
            elif self.stateInxList[i]==6:                                
                self.apply(INSTR_X, qList_idx[2*i])
                self.apply(INSTR_H, qList_idx[2*i])
            else : #"stateInx==7"
                self.apply(INSTR_X, qList_idx[2*i])
                self.apply(INSTR_H, qList_idx[2*i])
                self.apply(INSTR_X, qList_idx[2*i+1])
                
        yield self.run(parallel=False)


class BobProtocol(NodeProtocol):
    
    def __init__(self,node,processor,num_bits,threshold=0.854,
                port_names=["portQB_1","portCB_1","portCB_2"]):
        super().__init__()
        self.num_bits=num_bits
        self.node=node
        self.processor=processor
        self.portNameQ1=port_names[0]
        self.portNameC1=port_names[1]
        self.portNameC2=port_names[2]
        # init value assume that all qubits are lost
        self.sourceQList=[]
        self.basisInxList=[randint(0,7) for i in range(self.num_bits)]
        self.randMeas=randint(0,1) #0:Z basis(standard)   1:X basis(H)
        self.locRes = None
        self.threshold = threshold
        self.successfulRate=None
        self.validList=[]
        
        #generat qubits from source
        self.B_Source = QSource("Bank_source"
            ,status=SourceStatus.EXTERNAL) # enable frequency
        self.B_Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)
        


    # =======================================B run ============================
    def run(self):
        
        self.B_genQubits(self.num_bits,1e9)
        
        yield self.await_program(processor=self.processor)
        
        self.B_sendQubit()
        
        
        port = self.node.ports[self.portNameC1]
        yield self.await_port_input(port)
        #print(port.rx_input().items)
        reqMes = port.rx_input().items[0]
        if  reqMes == '10101':
    
            # send payload
            self.node.ports[self.portNameC2].tx_output(self.randMeas)
        else:
            print("req error!")
            print(reqMes)
    
        #print("B waiting for result")
        port = self.node.ports[self.portNameC1]
        yield self.await_port_input(port)
        [self.locRes, self.validList] = port.rx_input().items
        
        
        #drop self.validList
        #self.successfulRate = TokenCheck(self.basisInxList,self.randMeas,self.locRes) 
        self.successfulRate = TokenCheck_LossTolerant(self.basisInxList,self.randMeas,self.locRes,self.validList)
        print("B successfulRate:",self.successfulRate)
        
        # send result to A
        if self.successfulRate > self.threshold :
            # pass
            self.node.ports[self.portNameC2].tx_output(True)
        else:
            # you shall not pass!
            self.node.ports[self.portNameC2].tx_output(False)
        #print("Bob finished")
        
            

    def B_genQubits(self,num,freq=1e9):
        
        
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=2*num)
        try:
            clock.ports["cout"].connect(self.B_Source.ports["trigger"])
        except:
            pass
            #print("alread connected") 
            
        clock.start()
        
    def storeSourceOutput(self,qubit):
        self.sourceQList.append(qubit.items[0])
        if len(self.sourceQList)==2*self.num_bits:
            self.processor.put(qubits=self.sourceQList)
            
            inxList=[randint(0,7) for i in range(self.num_bits)]
            
            #print("inxList=",self.basisInxList)
            # apply H detector
            PG_qPrepare=QG_B_qPrepare(num_bits=self.num_bits,stateInxList=self.basisInxList)
            self.processor.execute_program(
                PG_qPrepare,qubit_mapping=[i for  i in range(0, 2*self.num_bits)])
            

            
    def B_sendQubit(self):
        #print("B_sendQubit")
        inx=list(range(2*self.num_bits))
        payload=self.processor.pop(inx)
        self.node.ports[self.portNameQ1].tx_output(payload)
      
