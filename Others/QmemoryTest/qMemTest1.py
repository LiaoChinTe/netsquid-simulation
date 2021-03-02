import numpy as np
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.protocols import Protocol
from netsquid.components import QuantumMemory, DepolarNoiseModel #,DephaseNoiseModel
from netsquid.qubits import create_qubits
from netsquid.components.component import Component
from netsquid.qubits.qformalism import *




class QMemoryDelay(Protocol):
    
    
    # base functions =======================================================
    def __init__(self,num_bits=1,depolar_rate=0,timeIND=False,delay=0): 
        super().__init__()
        set_qstate_formalism(QFormalism.DM)
        self.my_memory = QuantumMemory("QMemory", num_bits, 
            memory_noise_models=DepolarNoiseModel(depolar_rate=depolar_rate,
            time_independent=timeIND))   
        self.num_bits=num_bits
        self.delay=delay
        self.qList=[]
        self.start()
        
        
        
    def stop(self):
        super().stop()
        self._running = False
        
    def is_connected(self):
        super().is_connected()
        pass
        
    
    def start(self):
        super().start()
        self.qList = create_qubits(self.num_bits,system_name="Q")
        self.my_memory.put(self.qList) 
        
        
        My_waitENVtype = ns.pydynaa.EventType("WAIT_EVENT", "Wait for N nanoseconds")
        self._schedule_after(self.delay, My_waitENVtype) # self.delay
        self._wait_once(ns.EventHandler(self.popMem),entity=self
            ,event_type=My_waitENVtype) # can't add event_type
        
    
    # my functions ============================================
    def popMem(self,event):
        #print("time: ",ns.sim_time())
        # pop out from qmem
        self.qList=self.my_memory.pop(list(np.arange(self.num_bits)))
         




import matplotlib.pyplot as plt

def QuantumMem_plot():
    x_axis=[]
    y_axis=[]
    num_bits=1
    timeIND=False
    min_time=0
    max_time=7000000 #ns
    
    
    
    #first line
    
    depolar_rate=1000
    
    for i in range(min_time,max_time,50000):
        ns.sim_reset()
        x_axis.append(i/1000)
        Qt=QMemoryDelay(num_bits=num_bits,depolar_rate=depolar_rate,delay=i)
        
        ns.sim_run()
    
        y_axis.append(Qt.qList[0].qstate.qrepr.reduced_dm()[1][1].real) # only take the first qubit from DM 
        # and take the probability of bit flip
     
    
    plt.plot(x_axis, y_axis, 'go-',label='depolar rate = 1000')
    
    
    
    #second line
    
    x_axis.clear()
    y_axis.clear()
    depolar_rate=500
    
    for i in range(min_time,max_time,50000):
        ns.sim_reset()
        x_axis.append(i/1000)
        Qt2=QMemoryDelay(num_bits=num_bits,depolar_rate=depolar_rate,delay=i)
        ns.sim_run()
        y_axis.append(Qt2.qList[0].qstate.qrepr.reduced_dm()[1][1].real)
        
        
        
    plt.plot(x_axis, y_axis, 'bo-',label='depolar rate = 500')
    
    
    
    # 3rd line
    x_axis.clear()
    y_axis.clear()
    depolar_rate=50
    
    for i in range(min_time,max_time,50000):
        ns.sim_reset()
        x_axis.append(i/1000)
        Qt3=QMemoryDelay(num_bits=num_bits,depolar_rate=depolar_rate,delay=i)
        ns.sim_run()
        y_axis.append(Qt3.qList[0].qstate.qrepr.reduced_dm()[1][1].real)
    
    
    plt.plot(x_axis, y_axis, 'ro-',label='depolar rate = 50')
    
    
    
    plt.title('Depolar Noise Effects on qubits')
    plt.ylabel('average qubit error rate ')
    plt.xlabel('time stayed in quantum memory (μs)')

    plt.legend()
    plt.savefig('QMem.png')
    plt.show()



QuantumMem_plot()



