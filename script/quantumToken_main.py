from netsquid.components.models.qerrormodels import T1T2NoiseModel,DephaseNoiseModel

import os
import sys
#print("main",os.path.dirname(os.path.abspath(__file__)))
scriptpath = str(os.path.dirname(os.path.abspath(__file__))) + "/../QToken/"
#print("main add path:",scriptpath)
sys.path.append(scriptpath)

from QToken_run import run_QToken_sim

if __name__ == '__main__':
    myMemNoise=T1T2NoiseModel(T1=36*10**12, T2=4.9*10**6)
    #myProcessNoise=DephaseNoiseModel(dephase_rate=0.004)
    #mem_noise_model = T1T2NoiseModel(T1=((1/(1-args.T1))-1)*3.6*10**12, T2=((1/(1-args.T2))-1)*10**6)

    res=run_QToken_sim(runTimes=2,num_bits=10,fibre_len=10**-9,waitTime=10**3
        ,processNoiseModel=myMemNoise,memNoiseModel=myMemNoise,threshold=0.875
        ,fibreLoss_init=0,fibreLoss_len=0,QChV=2.083*10**-4,CChV=2.083*10**-4)
    print("res:",res," ")
