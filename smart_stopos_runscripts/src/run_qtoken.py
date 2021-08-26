import numpy as np
import pandas as pd
from argparse import ArgumentParser
from QToken.QToken_main import run_QToken_sim
from netsquid.components.models.qerrormodels import T1T2NoiseModel


def cost_function(success_rate, waiting_time_alice, cost_proportion_factor=1e12, threshold_success_rate=0.9):
    return cost_proportion_factor * np.heaviside(threshold_success_rate - success_rate, 1) - waiting_time_alice


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--T1', type=float,
                        help="Quantum memory relaxation time (ns).")
    parser.add_argument('--T2', type=float,
                        help="Quantum memory dephasing time (ns).")
    parser.add_argument('--wait_time', type=float,
                        help="Alice's waiting time (ns).")
    parser.add_argument('--filebasename', type=str,
                        help="Beginning of filename where results will be stored.")

    args = parser.parse_args()
    mem_noise_model = T1T2NoiseModel(T1=args.T1, T2=args.T2, waitTime=args.wait_time)
    res = run_QToken_sim(memNoiseModel=mem_noise_model, runTimes=2)
    cost = cost_function(success_rate=res, waiting_time_alice=args.wait_time)
    df = pd.DataFrame(columns=["cost", "T1", "T2", "wait_time"])
    df.loc[0] = [cost, args.T1, args.T2, args.wait_time]
    csv_filename = args.filebasename + '.csv'
    df.to_csv(csv_filename, index=False, header=False)
