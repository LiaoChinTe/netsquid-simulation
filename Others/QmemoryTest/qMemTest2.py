import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.protocols import NodeProtocol,Protocol
from netsquid.components import QuantumMemory, DepolarNoiseModel ,DephaseNoiseModel
from netsquid.qubits import create_qubits
from netsquid.components.component import Component
from netsquid.qubits.qformalism import *




class QMemoryDelay(Protocol):
    
    # base functions =======================================================
    def __init__(self,noiseModel,num_bits=1,delay=0): 
        super().__init__()

        set_qstate_formalism(QFormalism.DM)
        self.my_memory = QuantumMemory("QMemory", num_bits, 
            memory_noise_models=noiseModel)   
        self.num_bits=num_bits
        self.delay=delay
        self.qList=[]

        
    
    def run(self):

        self.qList = create_qubits(self.num_bits,system_name="Q")
        #print("Run1:",self.qList)
        self.my_memory.put(self.qList) 
        
        yield self.await_timer(duration=self.delay)
        
        self.qList=self.my_memory.peek(list(np.arange(self.num_bits)))
        #print("Run2:",self.qList)






import matplotlib.pyplot as plt

def QuantumMem_plot():
    x_axis=[]
    y_axis=[]
    num_bits=1
    timeIND=False
    min_time=0
    max_time=7000000 #ns
    

    rate=1000
    myDephaseNoiseModel=DephaseNoiseModel(dephase_rate=rate)
    myDepolarNoiseModel=DepolarNoiseModel(depolar_rate=rate)

    #first line
    
    depolar_rate=1000
    
    for i in range(min_time,max_time,50000):
        ns.sim_reset()
        x_axis.append(i/1000)

        

        myQMemoryDelay=QMemoryDelay(noiseModel=myDepolarNoiseModel,num_bits=num_bits,delay=i)
        myQMemoryDelay.start()
        ns.sim_run()

        y_axis.append(myQMemoryDelay.qList[0].qstate.qrepr.reduced_dm()[1][1].real) # only take the first qubit from DM 
        # and take the probability of bit flip
     
    
    plt.plot(x_axis, y_axis, 'go-',label='DepolarNoiseModel rate = 1000')
    
    
    
    #second line
    
    x_axis.clear()
    y_axis.clear()
    depolar_rate=500
    
    for i in range(min_time,max_time,50000):
        ns.sim_reset()
        x_axis.append(i/1000)


        myQMemoryDelay2=QMemoryDelay(noiseModel=myDephaseNoiseModel,num_bits=num_bits,delay=i)
        myQMemoryDelay2.start()
        ns.sim_run()
        y_axis.append(myQMemoryDelay2.qList[0].qstate.qrepr.reduced_dm()[1][1].real)
        
        
        
    plt.plot(x_axis, y_axis, 'bo-',label='DephaseNoiseModel rate = 1000')
    
    
    
    plt.title('Noise Effects on qubits')
    plt.ylabel('average qubit error rate ')
    plt.xlabel('time stayed in quantum memory (μs)')

    plt.legend()
    plt.savefig('QMem6.png')
    plt.show()
    


QuantumMem_plot()



