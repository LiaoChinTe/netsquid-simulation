from netsquid.components.qprogram import QuantumProgram
from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock
from netsquid.components.qsource import SourceStatus


import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)

class Dummy(QuantumProgram):
    def __init__(self):
        super().__init__()

    def program(self):

        yield self.run(parallel=False)


class QG_C1(QuantumProgram):
    def __init__(self,num_bits,RList,BList):
        self.num_bits=num_bits
        self.RList=RList
        self.BList=BList
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        mylogger.debug("C1 running ")
        for i in range(self.num_bits):
            if self.BList[i]==1:
                self.apply(INSTR_X, qList_idx[i])

            if self.RList[i]==1:
                self.apply(INSTR_H, qList_idx[i])

        yield self.run(parallel=False)


class AliceProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10,source_frq=1e9,role=0):
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits
        self.source_frq=source_frq

        self.sourceQList=[]

        #generat qubits from source
        self.A_Source = QSource("Alice_source",status=SourceStatus.EXTERNAL) # enable frequency
        self.A_Source.ports["qout0"].bind_output_handler(self.storeSourceOutput)

        #forward_output(self.node.ports["portQO"])
        #bind_output_handler(self.storeSourceOutput)

        self.role=role

        self.portList=["portQO","portCO"]

        # The two values below are related to the qline algorithm
        self.randR=[]
        self.randB=[]

        #self.SList=[]

        self.key=[]

    def showStatus(self,info):
        print(info)
        print("self.RList  = {}".format(self.RList))
        print("self.SList  = {}".format(self.SList))

        print("self.BList  = {}".format(self.BList))

        print("self.CList  = {}".format(self.CList))
        print("self.ResList= {}".format(self.ResList))
        print("\n")


    def run(self):
        mylogger.debug("AliceProtocol running")

        self.A_genQubits(num_bits=self.num_bits,freq=self.source_frq)


        # wait programe
        yield self.await_program(processor=self.processor)

        
        if self.role==1:

            mylogger.debug("A case 1")

            
            # choose random R,B values
            self.RList=Random_basis_gen(self.num_bits)
            self.BList=Random_basis_gen(self.num_bits)

            # Q program C1
            myQG_C1=QG_C1(num_bits=self.num_bits, RList=self.RList, BList=self.BList)
            self.processor.execute_program(myQG_C1,qubit_mapping=[i for  i in range(self.num_bits)])
            yield self.await_program(processor=self.processor)

            # send qubits to the next
            self.A_sendQubits()


            # wait for classical message 1
            port=self.node.ports["portCO"]
            yield self.await_port_input(port)
            payload = port.rx_input().items
            mylogger.debug("\nA1 received{}".format(payload))

            # temp
            self.ResList=payload[0]
            self.SList=payload[1]

            # Pick keys
            self.A1_formKey(rlist=self.RList,slist=payload[1],blist=self.BList)
            mylogger.info("\nA1 key:{}".format(self.key))

            # debug
            #self.showStatus("A1")

            # send classical infomation to C2/B2
            self.node.ports["portCO"].tx_output(self.RList)



        elif self.role==0:


            self.A_sendQubits()



    def A_genQubits(self,num_bits,freq=1e9):
        #set clock
        clock = Clock("clock", frequency=freq, max_ticks=num_bits)
        try:
            clock.ports["cout"].connect(self.A_Source.ports["trigger"])
        except:
            pass
        clock.start()

    # for Alice to store qubits in qmem
    def storeSourceOutput(self,qubit):

        self.sourceQList.append(qubit.items[0])
        if len(self.sourceQList)==self.num_bits:
            #mylogger.debug("qubit stored")
            self.processor.put(qubits=self.sourceQList)
            myDummy=Dummy()
            self.processor.execute_program(myDummy)
    
    def A_sendQubits(self):
        #mylogger.debug("A_sendEPR")
        inx=list(range(self.num_bits))
        payload=self.processor.pop(inx)
        self.node.ports["portQO"].tx_output(payload)


    def A1_formKey(self,rlist,slist,blist):
        if len(rlist)!=len(slist):
            mylogger.error("Rlist or Slist information missing! Aborting!")
            return 1
        for i,element in enumerate(rlist):
            if element==slist[i]:
                #mylogger.debug("{} r:{}, s:{}".format(i,rlist[i],slist[i]))
                self.key.append(blist[i])
        return 0

