from netsquid.components.models.qerrormodels import T1T2NoiseModel,DephaseNoiseModel

import matplotlib.pyplot as plt

import sys
scriptpath = "QToken/"
sys.path.append(scriptpath)

from QToken_run import run_QToken_sim


#threshold doesn't matter in this plot
def QuantumToken_plot():
    y_axis=[]
    x_axis=[]
    runTimes=1
    
    
    myMemNoise=T1T2NoiseModel(T1=36000*10**9, T2=10**9)
    #myProcessNoise=DephaseNoiseModel(dephase_rate=0.004)

    myXarray=[0,20,40,60]

    # first curve
    for i,j in enumerate(myXarray): # from 0 to 10**8 ns
        x_axis.append(i) # relate to unit
        y_axis.append(run_QToken_sim(runTimes=runTimes,num_bits=20,fibre_len=10**-9,waitTime=j
            ,processNoiseModel=None,memNoiseModel=myMemNoise,threshold=0.875
            ,fibreLoss_init=0,fibreLoss_len=0,QChV=2.083*10**-4,CChV=2.083*10**-4)) 


    plt.plot(x_axis, y_axis, 'bo-') #,label='fibre length=10'

    plt.title('Quantum Token')
    plt.ylabel('average successful rate')
    plt.xlabel('token kept time (ns)')

    #plt.legend()
    plt.savefig('QTplot1.png')
    plt.show()


QuantumToken_plot()