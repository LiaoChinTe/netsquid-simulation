import matplotlib.pyplot as plt
from netsquid.components.models.qerrormodels import *
from UBQC_main import *


def UBQC_plot():
    y_axis=[]
    x_axis=[]
    run_times=10
    min_dis=0
    max_dis=200
    
    #mymemNoiseMmodel=T1T2NoiseModel(T1=11, T2=10)
    #myprocessorNoiseModel=DepolarNoiseModel(depolar_rate=200)

    # first curve
    for i in range(min_dis,max_dis,5):
        
        x_axis.append(i)
        successRate=run_UBQC_sim(runtimes=run_times,fibre_len=i
            ,processorNoiseModel=None, memNoiseMmodel=None)
        #myprocessorNoiseModel   # mymemNoiseMmodel,loss_init=0.25,loss_len=0.2
        y_axis.append(successRate)



    plt.plot(x_axis, y_axis, 'go-',label='default fibre')
    
    plt.title('UBQC')
    plt.ylabel('verified rate')
    plt.xlabel('fibre length (km)')
    
    
    plt.legend()
    plt.savefig('plot7.png')
    plt.show()



UBQC_plot()