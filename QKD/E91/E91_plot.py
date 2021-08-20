# plot function
# users would need to install matplotlib for running this script


from netsquid.components.models.qerrormodels import *
import matplotlib.pyplot as plt
import E91_main

def E91_plot():
    y_axis=[]
    x_axis=[]
    run_times=5
    num_bits=20
    min_dis=0
    max_dis=50
    
    mymemNoiseMmodel=T1T2NoiseModel(T1=11, T2=10)
    myprocessorNoiseModel=DepolarNoiseModel(depolar_rate=200)

    # first curve
    for i in range(min_dis,max_dis,5):
        
        x_axis.append(i)
        key_list_A,key_list_B,keyRateList=E91_main.run_E91_sim(run_times,num_bits,fibre_len=i
            ,processorNoiseModel=myprocessorNoiseModel,memNoiseMmodel=mymemNoiseMmodel) 
        
        y_axis.append(sum(keyRateList)/run_times/10**6)
        
        
        
    plt.plot(x_axis, y_axis, 'go-',label='depolar_rate=200Hz')
    
    '''
    y_axis.clear() 
    x_axis.clear()
    
    
    myprocessorNoiseModel=DepolarNoiseModel(depolar_rate=2000)
    # second curve
    for i in range(min_dis,max_dis,5):
        
        x_axis.append(i)
        key_list_A,key_list_B,keyRateList=E91_main.run_E91_sim(run_times,num_bits,fibre_len=i
            ,processorNoiseModel=myprocessorNoiseModel,memNoiseMmodel=mymemNoiseMmodel) 
        
        y_axis.append(sum(keyRateList)/run_times)
        
        
        
    plt.plot(x_axis, y_axis, 'bo-',label='depolar_rate=2000')
    '''
    
    plt.title('QKD E91')
    plt.ylabel('key rate Mb/s')
    plt.xlabel('fibre lenth (km)')
    
    
    plt.legend()
    plt.savefig('keyRate9.png')
    plt.show()

    

E91_plot()

