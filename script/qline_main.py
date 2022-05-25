
from netsquid.components.models.qerrormodels import T1T2NoiseModel,DepolarNoiseModel,DephaseNoiseModel

import sys
scriptpath = "qline/"
sys.path.append(scriptpath)
from qline_run import run_QLine_sim


import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)


'''
The input variable 'nodeNrole' is a list of int which describes the length of this Qline 
as well as which of the two node are forming shared key.
An outer loop will be required to form shared keys among all nodes.

Note that the first node is always labeled with "A", and the last is always "B". 
All the others in the middle are "C". These labels are used for understanding the comments and Qline algorithm.
The key sharing nodes are also labeled with "1" or "2" following with the previous label.
For example, if the first node is forming shared key with the second node within a Qline of four.
The labels would be [A1,C2,C,B] and the 'nodeNrole' value be [1,-1,0,0].
'''
if __name__ == "__main__":

    mynodeNroleList=[[1,-1,0,0],[0,1,-1,0],[0,0,1,-1]]

    #[[1,-1,0,0],[0,1,-1,0],[0,0,1,-1],[1,0,-1,0],[1,0,0,-1],[0,1,0,-1]]   #[[1,-1]]     
    # #[[1,-1,0,0],[0,1,-1,0],[0,0,1,-1]]


    myfibreLen =5    # Length between 2 nodes

    keyRateList=[]
    keyLenList=[]
    timeCostList=[]


    mymemNoiseMmodel=T1T2NoiseModel(T1=10**6, T2=10**5)
    #myprocessorNoiseModel=DepolarNoiseModel(depolar_rate=500)
    myprocessorNoiseModel=DephaseNoiseModel(dephase_rate=0.004,time_independent=True)

    for mynodeNrole in mynodeNroleList:

        output=run_QLine_sim(rounds=2,nodeNrole=mynodeNrole,processorNoice=myprocessorNoiseModel,momNoise=mymemNoiseMmodel
            ,fibreLen=myfibreLen,num_bits=33,source_frq=12e4,qSpeed=2.083*10**5,cSpeed=2.083*10**5,fibreNoise=0,lenLoss=0.045)
        keyLenList.append(output[0])
        timeCostList.append(output[1])

        mylogger.info("Time used:{}s\n".format(output[1]/10**9))
        mylogger.info("Key Length:{}\n".format(output[0]))

        #keyRateList.append(keyrate)
        #post processing
        if output[1]!=0:
            keyrate=output[0]/output[1]*10**9
        else:
            mylogger.error("Time used can not be 0!! \n")

        # show/record figure of merits
        mylogger.info("key rate:{}\n".format(keyrate))
        # write
        listToPrint=''
        listToPrint=str(mynodeNrole)+'\n'
        listToPrint+=str(keyrate)+'\n\n'
        
        outF = open("keyOutput.txt", "a")
        outF.writelines(listToPrint)
        outF.close()

    mylogger.info("avg key rate:{}\n".format(sum(keyLenList)/sum(timeCostList)*10**9))

    listToPrint='average key rate:'
    listToPrint+=str(sum(keyLenList)/sum(timeCostList)*10**9)+'\n'
    listToPrint+='=====================\n'
    outF = open("keyOutput.txt", "a")
    outF.writelines(listToPrint)
    outF.close()

