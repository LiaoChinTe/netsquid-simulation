from netsquid.components.models.qerrormodels import T1T2NoiseModel,DepolarNoiseModel,DephaseNoiseModel

import sys
scriptpath = "MBQC_Qline/"
sys.path.append(scriptpath)

from MBQC_run import run_MBQC_Qline_sim

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)


if __name__ == "__main__":



    run_MBQC_Qline_sim()





