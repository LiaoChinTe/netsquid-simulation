import numpy as np
import pandas as pd
from argparse import ArgumentParser
from QToken.QToken_main import run_QToken_sim
from netsquid.components.models.qerrormodels import T1T2NoiseModel
import math


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--T1', type=float,
                        help="Quantum memory relaxation time (ns).")
    parser.add_argument('--T2', type=float,
                        help="Quantum memory dephasing time (ns).")

    args = parser.parse_args()
    mem_noise_model = T1T2NoiseModel(T1=args.T1, T2=args.T2)
    res_list = run_QToken_sim(memNoiseModel=mem_noise_model,
                              runTimes=10,
                              waitTime=10**9)
    res = np.average(res_list)
    error = np.std(res_list) / np.sqrt(len(res_list))
    print("Average rate of success: {} p/m {}".format(res, error))
    print("Rates of success: {}".format(res_list))
