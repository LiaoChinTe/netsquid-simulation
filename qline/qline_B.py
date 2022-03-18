from netsquid.util import simtools 
from netsquid import NANOSECOND
from netsquid.protocols import NodeProtocol

import sys
scriptpath = "../lib/"
sys.path.append(scriptpath)
from functions import *

import logging
#logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)


class QG_Bmeasure(QuantumProgram):
    def __init__(self,num_bits):
        self.num_bits=num_bits
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        #for i in range(len(self.basisList)):
        mylogger.debug("B measure running ")
        for i in range(self.num_bits):
            self.apply(INSTR_MEASURE, qList_idx[i], output_key=str(i), physical=True)

        yield self.run(parallel=False)

class QG_C2(QuantumProgram):
    def __init__(self,num_bits,CList,SList):
        self.num_bits=num_bits
        self.CList=CList
        self.SList=SList
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(self.num_bits)
        mylogger.debug("C2 running ")
        for i in range(self.num_bits):
            if self.SList[i]==1:
                self.apply(INSTR_H, qList_idx[i], physical=True)

            if self.CList[i]==1:
                self.apply(INSTR_X, qList_idx[i], physical=True)
        yield self.run(parallel=False)


class BobProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10,role=0):
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits


        self.role=role
        self.portList=["portQI","portCI"]

        # The two values below are related to the qline algorithm
        self.randC=[]
        self.randS=[]
        self.BmeasRes=[]

        self.SList=[]
        self.key=[]

        self.endTime=0

    def run(self):
        mylogger.debug("BobProtocol running")

        if self.role==-1:
            mylogger.debug("B case -1")

            # receive qubits
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.debug("\nB2 received{}".format(myqlist))

            # put qubits in processor
            self.processor.put(myqlist)

            # choose random C,S values
            self.CList=Random_basis_gen(self.num_bits)
            self.SList=Random_basis_gen(self.num_bits)

            # Q program C2
            myQG_C2=QG_C2(num_bits=self.num_bits, CList=self.CList, SList=self.SList)
            self.processor.execute_program(myQG_C2,qubit_mapping=[i for  i in range(self.num_bits)])
            yield self.await_program(processor=self.processor)



            # Q program Bmeasure
            self.myQG_Bmeasure=QG_Bmeasure(num_bits=self.num_bits)
            self.processor.execute_program(self.myQG_Bmeasure,qubit_mapping=[i for  i in range(self.num_bits)])
            yield self.await_program(processor=self.processor)

            # get meas result
            #mylogger.debug("\nB pre BmeasRes {}".format(self.myQG_Bmeasure.output))
            for i in range(self.num_bits):
                tmp=self.myQG_Bmeasure.output[str(i)][0]
                self.BmeasRes.append(tmp)
            self.ResList=self.BmeasRes


            # send Res & s to C1
            self.node.ports["portCI"].tx_output([self.ResList,self.SList])

            # wait for classical message 2
            port=self.node.ports["portCI"]
            yield self.await_port_input(port)
            self.RList = port.rx_input().items
            #mylogger.debug("\nB2 received{}".format(self.RList))


            # pick key
            self.B2_formKey(rlist=self.RList,slist=self.SList)

            # record end time 
            self.endTime=simtools.sim_time(magnitude=NANOSECOND)

            # show result
            mylogger.debug("\nB2 key:{}".format(self.key))

            # debug
            #self.showStatus("C2")



        elif self.role==0:
            # receive qubits
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.debug("\nB received {}".format(myqlist))

            # put qubits in processor
            self.processor.put(myqlist)

            # Q program Bmeasure
            self.myQG_Bmeasure=QG_Bmeasure(num_bits=self.num_bits)
            self.processor.execute_program(self.myQG_Bmeasure,qubit_mapping=[i for  i in range(self.num_bits)])
            yield self.await_program(processor=self.processor)

            # get meas result
            for i in range(self.num_bits):
                tmp=self.myQG_Bmeasure.output[str(i)][0]
                self.BmeasRes.append(tmp)

            mylogger.debug("\nB BmeasRes {}".format(self.BmeasRes))

            # send meas back
            self.node.ports["portCI"].tx_output(self.BmeasRes)



    def B2_formKey(self,rlist,slist):
        if len(rlist)!=len(slist):
            mylogger.error("Rlist or Slist information missing! Aborting!")
            return 1
        for i,element in enumerate(rlist):
            if element==slist[i]:
                #mylogger.debug("Reslist:{} Clist{}".format(self.ResList[i],self.CList[i]))
                self.key.append(self.ResList[i] ^ self.CList[i])
        return 0

