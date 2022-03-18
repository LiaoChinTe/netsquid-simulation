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



class CharlieProtocol(NodeProtocol):
    def __init__(self,node,processor,num_bits=10,role=0): #role value:[-1,0,1] 1 is the first party to form key
        super().__init__()
        
        self.node=node
        self.processor=processor
        self.num_bits=num_bits

        self.role=role
        self.portList=["portQI","portQO","portCI","portCO"]

        # The four values below are related to the qline algorithm
        self.RList=[]
        self.BList=[]
        self.CList=[]
        self.SList=[]

        self.ResList=[]

        self.key=[]

        self.endTime=0


    def showStatus(self,info):
        print(info)
        print("self.RList  = {}".format(self.RList))
        print("self.SList  = {}".format(self.SList))

        print("self.BList  = {}".format(self.BList))

        print("self.CList  = {}".format(self.CList))
        print("self.ResList= {}".format(self.ResList))
        print("\n")


    def run(self):
        mylogger.debug("CharlieProtocol running")

        if self.role==1:
            mylogger.debug("C case 1")

            # receive qubits
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.debug("\nC1 received {}".format(myqlist))

            # put qubits in processor
            self.processor.put(myqlist)
            
            # choose random R,B values
            self.RList=Random_basis_gen(self.num_bits)
            self.BList=Random_basis_gen(self.num_bits)


            # Q program C1
            myQG_C1=QG_C1(num_bits=self.num_bits, RList=self.RList, BList=self.BList)
            self.processor.execute_program(myQG_C1,qubit_mapping=[i for  i in range(self.num_bits)])
            yield self.await_program(processor=self.processor)

            # send qubits to the next
            self.node.ports["portQO"].tx_output(myqlist)

            # wait for classical message 1
            port=self.node.ports["portCO"]
            yield self.await_port_input(port)
            payload = port.rx_input().items
            mylogger.debug("\nC1 received{}".format(payload))

            # temp
            self.ResList=payload[0]
            self.SList=payload[1]

            # Pick keys
            self.C1_formKey(rlist=self.RList,slist=payload[1],blist=self.BList)
            mylogger.debug("\nC1 key:{}".format(self.key))

            # debug
            #self.showStatus("C1")

            # send classical infomation to C2
            self.node.ports["portCO"].tx_output(self.RList)



        elif self.role==-1:
            mylogger.debug("C case -1")

            # receive qubits
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.debug("\nC2 received{}".format(myqlist))

            # put qubits in processor
            self.processor.put(myqlist)

            # choose random C,S values
            self.CList=Random_basis_gen(self.num_bits)
            self.SList=Random_basis_gen(self.num_bits)

            # Q program C2
            myQG_C2=QG_C2(num_bits=self.num_bits, CList=self.CList, SList=self.SList)
            self.processor.execute_program(myQG_C2,qubit_mapping=[i for  i in range(self.num_bits)])
            yield self.await_program(processor=self.processor)

            # send qubits to the next
            self.node.ports["portQO"].tx_output(myqlist)

            # wait for classical message 1
            port=self.node.ports["portCO"]
            yield self.await_port_input(port)
            self.ResList = port.rx_input().items
            mylogger.debug("\nC2 received{}".format(self.ResList))

            # send Res & s to C1
            self.node.ports["portCI"].tx_output([self.ResList,self.SList])

            # wait for classical message 2
            port=self.node.ports["portCI"]
            yield self.await_port_input(port)
            self.RList = port.rx_input().items
            #mylogger.debug("\nC2 received{}".format(self.RList))


            # pick key
            self.C2_formKey(rlist=self.RList,slist=self.SList)

            # record end time 
            self.endTime=simtools.sim_time(magnitude=NANOSECOND)

            # show result
            mylogger.debug("\nC2 key:{}".format(self.key))

            # debug
            #self.showStatus("C2")



        else:
            mylogger.debug("C case 0")

            # waiting for qubits
            port=self.node.ports["portQI"]
            yield self.await_port_input(port)
            myqlist = port.rx_input().items
            mylogger.debug("\nC0 received{}".format(myqlist))

            # pass qubits
            self.node.ports["portQO"].tx_output(myqlist)

            # wait for forwarding (back)
            port=self.node.ports["portCO"]
            yield self.await_port_input(port)
            payload = port.rx_input().items
            #mylogger.debug("\nC0 received{}".format(payload))

            # forwarding (back)
            self.node.ports["portCI"].tx_output(payload)


            # wait for forwarding (forward)
            port=self.node.ports["portCI"]
            yield self.await_port_input(port)
            payload = port.rx_input().items

            # forwarding (forward)
            self.node.ports["portCO"].tx_output(payload)




    def C1_formKey(self,rlist,slist,blist):
        if len(rlist)!=len(slist):
            mylogger.error("Rlist or Slist information missing! Aborting!")
            return 1
        for i,element in enumerate(rlist):
            if element==slist[i]:
                #mylogger.debug("{} r:{}, s:{}".format(i,rlist[i],slist[i]))
                self.key.append(blist[i])
        return 0


    def C2_formKey(self,rlist,slist):
        if len(rlist)!=len(slist):
            mylogger.error("Rlist or Slist information missing! Aborting!")
            return 1
        for i,element in enumerate(rlist):
            if element==slist[i]:
                #mylogger.debug("Reslist:{} Clist{}".format(self.ResList[i],self.CList[i]))
                self.key.append(self.ResList[i] ^ self.CList[i])
        return 0




