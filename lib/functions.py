
import numpy as np

from netsquid.qubits.operators import Operator,create_rotation_op
from netsquid.components.instructions import *
from netsquid.components.qprogram import *
from netsquid.components.qprocessor import *

# General functions/Quantum programs

# Z Rotation operators 
theta = np.pi/8
# 16 types of rotations
# R0
R22 =create_rotation_op(   theta, rotation_axis=(0, 0, 1))
R45 =create_rotation_op( 2*theta, rotation_axis=(0, 0, 1))
R67 =create_rotation_op( 3*theta, rotation_axis=(0, 0, 1))
R90 =create_rotation_op( 4*theta, rotation_axis=(0, 0, 1))
R112=create_rotation_op( 5*theta, rotation_axis=(0, 0, 1))
R135=create_rotation_op( 6*theta, rotation_axis=(0, 0, 1))
R157=create_rotation_op( 7*theta, rotation_axis=(0, 0, 1))
R180=create_rotation_op(   np.pi, rotation_axis=(0, 0, 1))
R202=create_rotation_op( 9*theta, rotation_axis=(0, 0, 1))
R225=create_rotation_op(10*theta, rotation_axis=(0, 0, 1))
R247=create_rotation_op(11*theta, rotation_axis=(0, 0, 1))
R270=create_rotation_op(12*theta, rotation_axis=(0, 0, 1))
R292=create_rotation_op(13*theta, rotation_axis=(0, 0, 1))
R315=create_rotation_op(14*theta, rotation_axis=(0, 0, 1))
R337=create_rotation_op(15*theta, rotation_axis=(0, 0, 1))

#============================================================

INSTR_R22 = IGate('Z Rotated 22.5',operator=R22)
INSTR_R45 = IGate('Z Rotated 45'  ,operator=R45)
INSTR_R67 = IGate('Z Rotated 67.5',operator=R67)
INSTR_R90 = IGate('Z Rotated 90'    ,operator=R90)
INSTR_R112 = IGate('Z Rotated 112.5',operator=R112)
INSTR_R135 = IGate('Z Rotated 135'  ,operator=R135)
INSTR_R157 = IGate('Z Rotated 157.5',operator=R157)
#------------------------------------------------------------
INSTR_R180 = IGate('Z Rotated 180  ',operator=R180)
INSTR_R202 = IGate('Z Rotated 202.5',operator=R202)
INSTR_R225 = IGate('Z Rotated 225  ',operator=R225)
INSTR_R247 = IGate('Z Rotated 247.5',operator=R247)
INSTR_R270 = IGate('Z Rotated 270  ',operator=R270)
INSTR_R292 = IGate('Z Rotated 292.5',operator=R292)
INSTR_R315 = IGate('Z Rotated 315  ',operator=R315)
INSTR_R337 = IGate('Z Rotated 337.5',operator=R337)
#============================================================
INSTR_Rv22 = IGate('Z Rotated -22.5',operator=R22.inv)
INSTR_Rv45 = IGate('Z Rotated -45'  ,operator=R45.inv)
INSTR_Rv67 = IGate('Z Rotated -67.5',operator=R67.inv)
INSTR_Rv90 = IGate('Z Rotated -90'    ,operator=R90.inv)
INSTR_Rv112 = IGate('Z Rotated -112.5',operator=R112.inv)
INSTR_Rv135 = IGate('Z Rotated -135'  ,operator=R135.inv)
INSTR_Rv157 = IGate('Z Rotated -157.5',operator=R157.inv)
#------------------------------------------------------------
INSTR_Rv180 = IGate('Z Rotated -180  ',operator=R180.inv)
INSTR_Rv202 = IGate('Z Rotated -202.5',operator=R202.inv)
INSTR_Rv225 = IGate('Z Rotated -225  ',operator=R225.inv)
INSTR_Rv247 = IGate('Z Rotated -247.5',operator=R247.inv)
INSTR_Rv270 = IGate('Z Rotated -270  ',operator=R270.inv)
INSTR_Rv292 = IGate('Z Rotated -292.5',operator=R292.inv)
INSTR_Rv315 = IGate('Z Rotated -315  ',operator=R315.inv)
INSTR_Rv337 = IGate('Z Rotated -337.5',operator=R337.inv)


# used by AnonymousTransmission
NToffoli_matrix = [[0, 1, 0, 0, 0, 0, 0, 0],
                   [1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 0, 0, 0, 0, 0],
                   [0, 0, 0, 1, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1]]

Operator_NToffoli = Operator(name='Operator_NToffoli', matrix=NToffoli_matrix)
INSTR_NToffoli = IGate('INSTR_NToffoli',operator=Operator_NToffoli)






# General functions/Quantum programs 

class PrepareEPRpairs(QuantumProgram):
    
    def __init__(self,pairs=1):
        self.pairs=pairs
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(2*self.pairs)
        # create multiEPR
        for i in range(2*self.pairs):
            if i%2==0:                           # List A case
                self.apply(INSTR_H, qList_idx[i])
            else:                                # List B case
                self.apply(INSTR_CNOT, [qList_idx[i-1], qList_idx[i]])
        yield self.run(parallel=False)

 

'''
General measurement function.
Measure the qubits hold by this processor by basisList.
input:
    basisList: List of int, 0 means standard basis, others means Hadamard basis
'''

class QMeasure(QuantumProgram):
    def __init__(self,basisList):
        self.basisList=basisList
        super().__init__()

    def program(self):
        #print("in QMeasure")
        for i in range(0,len(self.basisList)):
            if  self.basisList[i]== 0:  # basisList 0:Z  , 1:X     == 0   self.basisList[int(i/2)]
                self.apply(INSTR_MEASURE, 
                    qubit_indices=i, output_key=str(i),physical=True) 
            else:                              
                self.apply(INSTR_MEASURE_X, 
                    qubit_indices=i, output_key=str(i),physical=True)

        yield self.run(parallel=False)


'''
input:
    positionInx:int List : Index in Qmem to measure.
    angleInx:int List (each value from 0 to 8): Index indecating measurement angle along Z-axis. 
    Corresponding to degree 0, 45, 90, ...315.
output:

'''
class AngleMeasure(QuantumProgram):
    def __init__(self,positionInx,angleInx):
        self.positionInx=positionInx
        self.angleInx=angleInx
        super().__init__()

    def program(self):

        for pos,angle in zip(self.positionInx,self.angleInx):

            # make sure angle is in the acceptable range
            while angle<0:
                angle+=8
            while angle>=8:
                angle-=8
            
            if   angle == 1:
                self.apply(INSTR_Rv45,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R45,pos)
            elif angle == 2:
                self.apply(INSTR_Rv90,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R90,pos)
            elif angle == 3:
                self.apply(INSTR_Rv135,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R135,pos)
            elif angle== 4:
                self.apply(INSTR_Rv180,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R180,pos)
            elif angle== 5:
                self.apply(INSTR_Rv225,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R225,pos)
            elif angle== 6:
                self.apply(INSTR_Rv270,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R270,pos)
            elif angle== 7:
                self.apply(INSTR_Rv315,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R315,pos)
            
            else:  # angle== 0
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
        
        
        yield self.run(parallel=False)




'''
older one
input:
    positionInx:int List : Index in Qmem to measure.
    angleInx:int List (each value from 0 to 15): Index indecating measurement angle along Z-axis. #
output:
'''
class AngleMeasure_old(QuantumProgram):
    def __init__(self,positionInx,angleInx):
        self.positionInx=positionInx
        self.angleInx=angleInx
        super().__init__()

    def program(self):
        
        
        #print("in AngleMeasure")
        #print("self.positionInx",self.positionInx)
        #print("self.angleInx",self.angleInx)
        for pos,angle in zip(self.positionInx,self.angleInx):

            # make sure angle is in the acceptable range
            while angle<0:
                angle+=16
            while angle>=16:
                angle-=16
            
            if   angle == 1:
                self.apply(INSTR_Rv22,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R22,pos)
            elif angle == 2:
                self.apply(INSTR_Rv45,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R45,pos)
            elif angle == 3:
                self.apply(INSTR_Rv67,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R67,pos)
            elif angle== 4:
                self.apply(INSTR_Rv90,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R90,pos)
            elif angle== 5:
                self.apply(INSTR_Rv112,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R112,pos)
            elif angle== 6:
                self.apply(INSTR_Rv135,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R135,pos)
            elif angle== 7:
                self.apply(INSTR_Rv157,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R157,pos)
            elif angle== 8:
                self.apply(INSTR_Rv180,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R180,pos)
            elif angle== 9:
                self.apply(INSTR_Rv202,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R202,pos)
            elif angle== 10:
                self.apply(INSTR_Rv225,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R225,pos)
            elif angle== 11:
                self.apply(INSTR_Rv247,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R247,pos)
            elif angle== 12:
                self.apply(INSTR_Rv270,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R270,pos)
            elif angle== 13:
                self.apply(INSTR_Rv292,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R292,pos)
            elif angle== 14:
                self.apply(INSTR_Rv315,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R315,pos)
            elif angle== 15:
                self.apply(INSTR_Rv337,pos)
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
                self.apply(INSTR_R337,pos)
            else:  # angle== 0
                self.apply(INSTR_MEASURE_X,qubit_indices=pos, output_key=str(pos),physical=True)
        
        
        yield self.run(parallel=False)
        


'''
Swap the qubits hold by this processor by position.
input:
    position:list of int: indecate qubits to swap 

'''

class QSwap(QuantumProgram):
    def __init__(self,position):
        self.position=position
        super().__init__()
        if len(position)!=2:
            print("Error parameters in QSwap!")
        

    def program(self):
        #print("in QSwap ")
        self.apply(INSTR_SWAP, qubit_indices=self.position, physical=True)
        yield self.run(parallel=False)    




'''
Apply CZ in a Qmem.
input:
    position:(list of two. ex [0,1])position to apply CZ
'''
class QCZ(QuantumProgram):
    def __init__(self,position):
        self.position=position
        super().__init__()

    def program(self):
        #print("in QCZ ")
        self.apply(INSTR_CZ, qubit_indices=self.position, physical=True)
        yield self.run(parallel=False)
        
 






def logical_xor(str1, str2):
    return bool(str1) ^ bool(str2) 



def createProcessorAT(name='defaultProcessor',num_positions=4,memNoiseModel=None,processorNoiseModel=None):


    # teleportation needs X Z
    # Anonymous Transmission needs CNOT, MEASURE, TOFFOLI, NToffoli
    myProcessor=QuantumProcessor(name, num_positions=num_positions,
        mem_noise_models=memNoiseModel, phys_instructions=[
        PhysicalInstruction(INSTR_X, duration=1  , quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_Z, duration=1  , quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_H, duration=1  , quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_CNOT,duration=1, quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_MEASURE, duration=10  , quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_TOFFOLI, duration=10, quantum_noise_model=processorNoiseModel, parallel=False),
        PhysicalInstruction(INSTR_NToffoli, duration=10, quantum_noise_model=processorNoiseModel, parallel=False)])
    
    return myProcessor


class makeWstate(QuantumProgram):
    
    def __init__(self,numQubits=4):
        self.numQubits=numQubits
        super().__init__()
        
    def program(self):
        if self.numQubits%4==0:
            self.apply(INSTR_H, 2)
            self.apply(INSTR_H, 3)
            self.apply(INSTR_NToffoli, [3,2,1])
            self.apply(INSTR_TOFFOLI,qubit_indices=[3,2,0],physical=True) 
            self.apply(INSTR_CNOT, [0, 2])
            self.apply(INSTR_CNOT, [0, 3])
        else:
            print("numbers of qubits should be a multiple of 4")
        
        yield self.run(parallel=False)
        


def ProgramFail(info):
    print(info)
    print("programe failed!!")    
    

    