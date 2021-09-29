from QToken.QToken_main import run_QToken_sim
from netsquid.components.models.qerrormodels import T1T2NoiseModel

T1 = 0.9605699461096662
T2 = 0.8951449861853965

mem_noise_model = T1T2NoiseModel(T1=((1 / (1 - T1)) - 1) * 3.6 * 10**12, T2=((1 / (1 - T2)) - 1) * 10**6)
res = run_QToken_sim(memNoiseModel=mem_noise_model, runTimes=2, waitTime=10**9)
print("This was my res", res)
