'''
Simulation of comparison between QLine and BB84. No post processing included.
Used for Paris QCI project.
How to use:
1. Configure this file for desired simulation.
2. Under root directory, run: 'python script/qciSim.py'

'''

import matplotlib.pyplot as plt
from netsquid.components.models.qerrormodels import T1T2NoiseModel,DepolarNoiseModel,DephaseNoiseModel

import sys
scriptpath = "QKD/BB84/"
sys.path.append(scriptpath)

scriptpath = "qline/"
sys.path.append(scriptpath)


#from QKD/BB84 
from BB84_main import run_BB84_sim
from qline_main import run_QLine_sim



def QLinePlot():
    y_axis_keyRate_bb84=[]
    y_axis_keyRate_qline=[]
    y_axis_costRate_bb84=[]
    y_axis_costRate_qline=[]

    x_axis=[]
    fibreNoise=0.1
    fibreLenMax=14


    mymemNoiseMmodel=T1T2NoiseModel(T1=10**6, T2=10**5)
    #myprocessorNoiseModel=DepolarNoiseModel(depolar_rate=500)
    myprocessorNoiseModel=DephaseNoiseModel(dephase_rate=0.004,time_independent=True)

    
    for i in range(7,fibreLenMax,1):

        # first index
        MyKeyList_A, MyKeyList_B, MyKeyRateList=run_BB84_sim(runtimes=30,num_bits=100,fibreLen=i
            ,sourceFreq=12e4,lenLoss=0.045,fibreNoise=0
            ,memNoiseMmodel=mymemNoiseMmodel,processorNoiseModel=myprocessorNoiseModel
            ,qSpeed=2.083*10**5,cSpeed=2.083*10**5) 
            
        
        #y_axis_keyRate_bb84.append(sum(MyKeyRateList)/len(MyKeyRateList))
        if sum(MyKeyRateList)!=0:
            #y_axis_costRate_bb84.append(3/sum(MyKeyRateList)*len(MyKeyRateList)) # case1    #=================================================
            #y_axis_costRate_bb84.append(3/sum(MyKeyRateList)*len(MyKeyRateList)*3/2) # case2
            #y_axis_costRate_bb84.append(3/sum(MyKeyRateList)*len(MyKeyRateList)*3) # case3 case4
            y_axis_costRate_bb84.append(3/sum(MyKeyRateList)*len(MyKeyRateList)*4) # case5
        else:
            y_axis_costRate_bb84.append(0)
        x_axis.append(i)

        # second index
        # Qline config
        mynodeNroleList=[[1,-1,0,0],[0,1,-1,0],[0,0,1,-1]]
        keyRateList_qline=[]
        for mynodeNrole in mynodeNroleList:
            output=run_QLine_sim(rounds=10,nodeNrole=mynodeNrole,processorNoice=myprocessorNoiseModel,momNoise=mymemNoiseMmodel
                ,fibreLen=i,num_bits=33,source_frq=12e4,qSpeed=2.083*10**5,cSpeed=2.083*10**5,fibreNoise=0,lenLoss=0.045)
            keyRateList_qline.append(output[0]/output[1]*10**9)

        #y_axis_keyRate_qline.append(sum(keyRateList_qline)/len(keyRateList_qline)) #keyLenList/timeCostList
        if sum(keyRateList_qline)!=0:
            #y_axis_costRate_qline.append(1/sum(keyRateList_qline)*len(keyRateList_qline)) # case1 case2 case3  #==============================
            #y_axis_costRate_qline.append(1/sum(keyRateList_qline)*len(keyRateList_qline)*2) # case4
            y_axis_costRate_qline.append(1/sum(keyRateList_qline)*len(keyRateList_qline)*3/4) # case5
        else:
            y_axis_costRate_qline.append(0)

    plt.plot(x_axis, y_axis_costRate_bb84, 'go-',label='BB84') 
    plt.plot(x_axis, y_axis_costRate_qline, 'bo-',label='QLine') 
    plt.ylabel('cost per bit per second') #average key length/Max qubits length
    plt.xlabel('distance (km)') #distance (nodes in between)
    plt.title('Comparison between Qline and BB84 case 5')
    plt.tight_layout()
    
    plt.legend()
    plt.savefig('case5_2.png', bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    QLinePlot()