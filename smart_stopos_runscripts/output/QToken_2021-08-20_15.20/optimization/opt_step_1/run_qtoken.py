import pandas as pd
from argparse import ArgumentParser
from QToken.QToken_main import run_QToken_sim
from netsquid.components.models.qerrormodels import T1T2NoiseModel


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--T1', type=float,
                        help="Quantum memory relaxation time (ns).")
    parser.add_argument('--T2', type=float,
                        help="Quantum memory dephasing time (ns).")
    parser.add_argument('--filebasename', type=str,
                        help="Beginning of filename where results will be stored.")

    args = parser.parse_args()
    mem_noise_model = T1T2NoiseModel(T1=args.T1, T2=args.T2)
    res = run_QToken_sim(memNoiseModel=mem_noise_model, runTimes=2)

    df = pd.DataFrame(columns=["res", "T1", "T2"])
    df.loc[0] = [res, args.T1, args.T2]
    csv_filename = args.filebasename + '.csv'
    df.to_csv(csv_filename, index=False, header=False)