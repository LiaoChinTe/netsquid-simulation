
import netsquid as ns
from netsquid.components.models import DephaseNoiseModel,DepolarNoiseModel,T1T2NoiseModel

import sys
scriptpath = "AnonymousTransmission/"
sys.path.append(scriptpath)

from ATw_run import run_AT_sim



if __name__ == '__main__':

    ns.sim_reset()
    #print (ns.__version__)

    #myNoiseModel1=DephaseNoiseModel(dephase_rate=6*10**4,time_independent=False)
    #myNoiseModel2=DepolarNoiseModel(depolar_rate=6*10**4,time_independent=False)
    myNoiseModel3=T1T2NoiseModel(T1=11, T2=0)
    #myNoiseModel4=DepolarNoiseModel(depolar_rate=0.01,time_independent=True)

    res=run_AT_sim(runtimes=1,numNodes=4,fibre_len=10**-9
        ,processorNoiseModel=None,memNoiseMmodel=myNoiseModel3
        ,loss_init=0,loss_len=0,t1=3720,t2=0)  

    res=print("Avg Fidelity index:",res)