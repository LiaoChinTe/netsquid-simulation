# plot function
import matplotlib.pyplot as plt

def QLinePlot():
    y_axis_keyRate=[]
    y_axis_QubitEfficiencyRate=[]
    x_axis=[]
    run_times=50
    maxKeyLen=100
    numNode=4
    fibreLen=10

    # first curve
    for i in range(1,numNode):
        keylenSum=0.0
        timeSum=0.0
        errorSum=0
        for _ in range(run_times):
            
            key_I,key_T,costTime=run_QLine_sim(I=0,T=i,
                maxKeyLen=maxKeyLen,fibreLen=fibreLen,
                noise_model=None) 
            
            #if key_I==key_T and key_I:  #else error happend, drop key, count 0 length
            keylenSum+=len(key_I)
            timeSum+=costTime
                    
        #x_axis.append(10**i)
        x_axis.append(i-1)
        if timeSum!=0:
            y_axis_QubitEfficiencyRate.append(keylenSum/run_times/maxKeyLen)
            #y_axis_keyRate.append(keylenSum/run_times/timeSum)
            #y_axis.append(keylenSum/run_times/maxKeyLen) #/timeSum*10**9
        else:
            y_axis_QubitEfficiencyRate.append(0)
            #y_axis_keyRate.append(0)

    plt.plot(x_axis, y_axis_QubitEfficiencyRate, 'go-',label='Qubit Efficiency Rate') 
    #plt.plot(x_axis, y_axis_keyRate, 'bo-',label='Key Rate') 
        
    plt.ylabel('Qubit Efficiency Rate') #average key length/Max qubits length
    plt.xlabel('distance (nodes in between)')#distance (nodes in between)
    
    
    plt.legend()
    plt.savefig('plot.png')
    plt.show()


if __name__ == "__main__":
    QLinePlot()