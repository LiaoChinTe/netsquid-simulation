from netsquid.components.models.qerrormodels import T1T2NoiseModel,DepolarNoiseModel,DephaseNoiseModel

import sys
scriptpath = "MBQC_Qline/"
sys.path.append(scriptpath)

from MBQC_run import run_MBQC_Qline_sim

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)


if __name__ == "__main__":

    m1count=0
    m2count=0
    xorcount=0

    for i in range(100):
        tmp=run_MBQC_Qline_sim()
        try:
            m1count+=tmp[0]
            m2count+=tmp[1]
            xorcount+=tmp[0]^tmp[1]
        except:
            mylogger.info("Error in return values!")
    
    mylogger.info("m1 count:{}, m2 count:{}, xor count:{}".format(m1count,m2count,xorcount))





