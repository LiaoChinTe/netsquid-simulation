import numpy as np
import pandas as pd
from argparse import ArgumentParser
from QToken.QToken_main import run_QToken_sim
from netsquid.components.models.qerrormodels import T1T2NoiseModel
import math


def myStepFunction(x):
    if x > 0:
        return x
    else:
        return 0 

def myCostFunction(t1,t2,p1,p2,Srate,T=0,SrateMin=0.875,Tmin=10**9,w1=1,w2=0,w3=1,sf=myStepFunction
    ,t1b=0.9091 ,t2b=0.8305,p1b=0.95,p2b=0.995):
    tmp1=w1*sf(SrateMin-Srate)
    tmp2=w2*sf(Tmin-T)
    #print("~~t1:",t1," t1b:",t1b)
    C=1/(1+math.log(t1,t1b))+1/(1+math.log(t2,t2b)) #+1/(1+math.log(p1,p1b))+1/(1+math.log(p2,p2b))
    tmp3=w3*C
    
    return tmp1+tmp2+tmp3


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--T1', type=float,
                        help="Quantum memory relaxation time (ns).")
    parser.add_argument('--T2', type=float,
                        help="Quantum memory dephasing time (ns).")
    #parser.add_argument('--wait_time', type=float,
    #                    help="Alice's waiting time (ns).")
    parser.add_argument('--filebasename', type=str,
                        help="Beginning of filename where results will be stored.")

    args = parser.parse_args()
    mem_noise_model = T1T2NoiseModel(T1=((1/(1-args.T1))-1)*3.6*10**12, T2=((1/(1-args.T2))-1)*10**6)
    res = run_QToken_sim(memNoiseModel=mem_noise_model, runTimes=2,waitTime=10**9)

    if res>0.875:
        print("O Srate ","==========================",res,"==========================================")
        
    else:
        print("X Srate ","==========================",res,"==========================================")


    cost = myCostFunction(t1=args.T1,t2=args.T2,p1=0.95,p2=0.995,Srate=res) #(1/(1-args.T1))-1

    df = pd.DataFrame(columns=["cost", "T1", "T2"])
    df.loc[0] = [cost, args.T1, args.T2]
    csv_filename = args.filebasename + '.csv'
    df.to_csv(csv_filename, index=False, header=False)
