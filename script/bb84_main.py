
from netsquid.components.models.qerrormodels import T1T2NoiseModel,DepolarNoiseModel,DephaseNoiseModel

import sys
scriptpath = "QKD/BB84/"
sys.path.append(scriptpath)

from BB84_run import run_BB84_sim

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)


if __name__ == "__main__":
        
    mymemNoiseMmodel=T1T2NoiseModel(T1=10**6, T2=10**5)
    #myprocessorNoiseModel=DepolarNoiseModel(depolar_rate=500)
    myprocessorNoiseModel=DephaseNoiseModel(dephase_rate=0.004,time_independent=True)

    toWrite=run_BB84_sim(runtimes=3,num_bits=100,fibreLen=5
        ,memNoiseMmodel=mymemNoiseMmodel,processorNoiseModel=myprocessorNoiseModel,fibreNoise=0 
        ,sourceFreq=12e4,lenLoss=0.045
        ,qSpeed=2.083*10**5,cSpeed=2.083*10**5) #10**-9  
    
    
    mylogger.debug("key list A:{}\n".format(toWrite[0]))
    mylogger.debug("key list B:{}\n".format(toWrite[1]))
    mylogger.debug("key rate list:{}\n".format(toWrite[2]))

    keyrate=sum(toWrite[2])/len(toWrite[2])
    mylogger.info("Average key rate:{}\n".format(keyrate))
    mylogger.info("cost/bit/sec :{}\n".format(4/keyrate))


    '''
    # write to file

    listToPrint=''
    listToPrint=str(toWrite)
    
    outF = open("keyOutput8.txt", "w")
    outF.writelines(listToPrint)
    outF.close()
    '''