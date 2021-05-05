from netsquid.components.qprogram import *
from netsquid.components.qprocessor import *
from netsquid.qubits.operators import X,H,Z
from netsquid.components.instructions import *



class QG_A_measure(QuantumProgram):
    def __init__(self,basisList,num_bits):
        self.basisList=basisList
        self.num_bits=num_bits
        super().__init__()


    def program(self):   
        for i in range(len(self.basisList)):
            if self.basisList[int(i)] == 0:    # standard basis
                self.apply(INSTR_MEASURE, 
                    qubit_indices=i, output_key=str(i),physical=True) 
            else:                              # 1 case # Hadamard basis
                self.apply(INSTR_MEASURE_X, 
                    qubit_indices=i, output_key=str(i),physical=True) 
        yield self.run(parallel=False)



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


#====================================================================================================

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
output:
    res: 
        the persentage of passed qubits among all qubits.
'''
def TokenCheck(basisInxList,randMeas,locRes):
    failCount=0
    if randMeas==0:
        for i in range(len(basisInxList)):
            if basisInxList[i]<=1 and locRes[2*i]==0:
                pass
            elif basisInxList[i]<=3 and locRes[2*i]==1:
                pass
            elif basisInxList[i]%2==0 and locRes[2*i+1]==0:
                pass
            elif basisInxList[i]%2==1 and locRes[2*i+1]==1:
                pass
            else:
                #print("false case1:",i)
                failCount+=1
    else: # randMeas==1:
        for i in range(len(basisInxList)):
            if basisInxList[i]>=6 and locRes[2*i]==1:
                pass
            elif basisInxList[i]>=4 and locRes[2*i]==0:
                pass
            elif basisInxList[i]%2==0 and locRes[2*i+1]==0:
                pass
            elif basisInxList[i]%2==1 and locRes[2*i+1]==1:
                pass
            else:
                #print("false case2:",i)
                failCount+=1
    
    return (len(basisInxList)-failCount)/len(basisInxList)


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
    else:
        pass
        
    for i in range(len(validList)):
        #print("val:",validList[i])
        #print("res:",locRes[i])
        tmpRes.insert(validList[i]-1, locRes[i])
        
    '''
    print("in TokenCheck_LossTolerant1")
    print("B locRes: ",locRes)
    print("B validList: ",validList)
    print("B LossTolerant tmpRes:",tmpRes)
    print("B len(tmpRes)",len(tmpRes)) 
    '''
     
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
                #print("false case1:",i)
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
                #print("false case2:",i)
                failCount+=1
    
    
    '''
    print("in TokenCheck_LossTolerant2")
    print("len(locRes): ",len(locRes))           #scale /100
    print("failCount: ",failCount)                   #scale  /max 50
    print("len(basisInxList): ",len(basisInxList)) # 50
    '''
    
    
    #valid 28 unvalid 22 pairs
    
    return 1-(failCount-len(basisInxList)+len(locRes)/2)/(len(locRes)/2)

    



        
        

    
'''
Only used for this protocol, cut integers that are not a complete pair.

input:
    myList: list of int
    minBound: int
    maxBound: int
output:
    A list of only complete pairs.

'''
def CutNonPair(myList,minBound,maxBound):
    for i in range(minBound,maxBound+1):
        if minBound==1 and i in myList:
            if i+1 in myList and i%2==1:
                pass
            elif i-1 in myList and i%2==0:
                pass
            else:
                myList.remove(i)
        elif minBound==0 and i in myList:
            if i+1 in myList and i%2==0:
                pass
            elif i-1 in myList and i%2==1:
                pass
            else:
                myList.remove(i)
    return myList
    
'''
Only used for this protocal. Since one qubit loss means a qubit pair can not been used.
This function is used for cutting useless qubits

input:
    qList: qubit list to filter.
    minBound: The minimum vlue of qubit index, usually 1. 
    MaxBound: The maximum vlue of qubit index.
    
output:
    Filtered qubit list.

'''
def QubitPairFilter(qList,minBound,MaxBound):    
    RemainList=[]
    for i in range(len(qList)):
        RemainList.append(int(qList[i].name[13:-len('-')-1]))    # get index from bits
    #print("remaining list num_inx: ",RemainList)
    RemainList=CutNonPair(RemainList,minBound,MaxBound)
    #print("filtered RemainList: ",RemainList)
    
    # adopt qList according to RemainList
    
    qlength=len(qList)
    for i in reversed(range(qlength)):
        tmp=int(qList[i].name[13:-len('-')-1])
        if tmp not in RemainList:
            qList.pop(i)
    
    #print("valid qList:",qList)
    
    return RemainList,qList