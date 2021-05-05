

import matplotlib.pyplot as plt

#threshold doesn't matter in this plot
def QuantumToken_plot():
    y_axis=[]
    x_axis=[]
    runTimes=3
    
    min_storetime=0
    max_storetime=10
    
    myMemNoise=T1T2NoiseModel(T1=10**6, T2=10**5)
    myProcessNoise=DephaseNoiseModel(dephase_rate=0.004)

    # first curve
    for i in range(min_storetime,max_storetime): # from 0 to 10**8 ns
        x_axis.append(i*10**4) # relate to unit
        y_axis.append(run_QToken_sim(runTimes=3,num_bits=10**2,fibre_len=5,waitTime=i*10**4
            ,processNoiseModel=myProcessNoise,memNoiseModel=myMemNoise,threshold=0.875
            ,fibreLoss_init=0.5,fibreLoss_len=0.2,QChV=2.083*10**-4,CChV=2.083*10**-4)) 


    plt.plot(x_axis, y_axis, 'bo-') #,label='fibre length=10'

    plt.title('Quantum Token')
    plt.ylabel('average successful rate')
    plt.xlabel('token kept time (ns)')

    plt.legend()
    plt.savefig('QTplotNN1.png')
    plt.show()


QuantumToken_plot()