import numpy as np
import pandas as pd
from argparse import ArgumentParser

from netsquid.components.models.qerrormodels import T1T2NoiseModel
import math

import os
import sys
scriptpath = str(os.path.dirname(os.path.abspath(__file__))) + "/../../QToken/"
sys.path.append(scriptpath)

from QToken_run import  run_QToken_sim


def myStepFunction(x):
    if x > 0:
        return x
    else:
        return 0 

def myCostFunction(t1,t2,p1,p2,Srate,T=0,SrateMin=0.875,Tmin=10**9,w1=1,w2=0,w3=1,sf=myStepFunction
    ,t1b=0.9091 ,t2b=0.8305,p1b=0.95,p2b=0.995):
    tmp1=w1*sf(SrateMin-Srate)
    tmp2=w2*sf(Tmin-T)
    C=1/math.log(t1,t1b)+1/math.log(t2,t2b) #+1/(1+math.log(p1,p1b))+1/(1+math.log(p2,p2b))
    tmp3=w3*C
    
    return tmp1+tmp2+tmp3

# The arguments T1 T2 are mandatory to run this script,
# their values are limited to 0 ~ 1.0, and T1>T2. 
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--T1', type=float,
                        help="Quantum memory relaxation time (ns),0<value<=1.")
    parser.add_argument('--T2', type=float,
                        help="Quantum memory dephasing time (ns),0<value<=1.")
    #parser.add_argument('--wait_time', type=float,
    #                    help="Alice's waiting time (ns).")
    parser.add_argument('--filebasename', type=str,
                        help="Beginning of filename where results will be stored.")

    args = parser.parse_args()
    mem_noise_model = T1T2NoiseModel(T1=((1/(1-args.T1))-1)*3.6*10**12, T2=((1/(1-args.T2))-1)*10**6) #scale up the real T1 T2 values
    res = run_QToken_sim(memNoiseModel=mem_noise_model,num_bits=10, runTimes=2,waitTime=10**9,
        fibreLoss_init=0.2,fibreLoss_len=0.25)

    print("running with T1:",args.T1," T2:",args.T2," succ_rate:",res)
    '''
    if res>0.875:
        print("O Srate ","==========================",res,"==========================================")
        
    else:
        print("X Srate ","==========================",res,"==========================================")
    '''

    cost = myCostFunction(t1=args.T1,t2=args.T2,p1=0.95,p2=0.995,Srate=sum(res)/len(res)) #(1/(1-args.T1))-1

    df = pd.DataFrame(columns=["cost", "T1", "T2"]) #, "res"
    df.loc[0] = [cost, args.T1, args.T2] #, res
    csv_filename = args.filebasename + '.csv'
    df.to_csv(csv_filename, index=False, header=False)
