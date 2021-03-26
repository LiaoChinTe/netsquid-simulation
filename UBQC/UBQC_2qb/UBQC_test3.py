from random import randint
import logging
logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


from netsquid.protocols import NodeProtocol
import netsquid as ns
from netsquid.nodes.node import Node
from netsquid.qubits.qformalism import *
from netsquid.components.qprocessor import *
from netsquid.components.qprogram import *
from netsquid.components.models import  FibreDelayModel
from netsquid.components.models.qerrormodels import *
from netsquid.components.qchannel import QuantumChannel
from netsquid.components.cchannel import ClassicalChannel

from netsquid.protocols import NodeProtocol
from netsquid.components import QSource,Clock

from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "../../lib/"
sys.path.append(scriptpath)

from functions import *
import misc

import UBQC_client
import UBQC_server
import UBQC_source

## Testing the source module
def run_UBQC_sim(fibre_len = 10**-9,
                 processorNoiseModel = None,
                 memNoiseMmodel = None,
                 loss_init = 0,
                 loss_len = 0,
                 QChV = 3*10**2,
                 CChV = 3*10**2): #loss_init=0.25,loss_len=0.2
    
    set_qstate_formalism(QFormalism.DM)

    ns.sim_reset()

    # nodes====================================================================
    nodeSource = Node("Source", port_names=["SeQO","ClQO","SeCO", "ClCO", "ClCI"])
    nodeServer = Node("Server", port_names=["ClCO","SoQI","ClCI", "SoCI"])
    nodeClient = Node("Client", port_names=["SeCO","SoCO","SoQI","SeCI", "SoCI"])

    # processors===============================================================

    processorClient=QuantumProcessor("processorClient", num_positions=10, mem_noise_models=memNoiseMmodel, phys_instructions=misc.std_physical_inst_set)
    processorServer=QuantumProcessor("processorServer", num_positions=10, mem_noise_models=memNoiseMmodel, phys_instructions=misc.std_physical_inst_set)
    processorSource=QuantumProcessor("processorSource", num_positions=10, mem_noise_models=memNoiseMmodel, phys_instructions=misc.std_physical_inst_set)

    # Channels==================================================================       

    QChannelSoSe = QuantumChannel("QChannelSoSe", delay=0, length=fibre_len, models={"quantum_loss_model": FibreLossModel(p_loss_init=loss_init, p_loss_length=loss_len, rng=None), "delay_model": FibreDelayModel(c=QChV)})
    QChannelSoCl = QuantumChannel("QChannelSoCl", delay=0, length=fibre_len, models={"quantum_loss_model": FibreLossModel(p_loss_init=loss_init, p_loss_length=loss_len, rng=None), "delay_model": FibreDelayModel(c=QChV)})

    CChannelClSo = ClassicalChannel("CChannelClSo", delay=0, length=fibre_len)
    CChannelClSe = ClassicalChannel("CChannelClSe", delay=0, length=fibre_len)
    CChannelSeCl = ClassicalChannel("CChannelSeCl", delay=0, length=fibre_len)
    CChannelSoSe = ClassicalChannel("CChannelSoSe", delay=0, length=fibre_len)
    CChannelSoCl = ClassicalChannel("CChannelSoCl", delay=0, length=fibre_len)


    # Connecting channels ========================================================

    nodeSource.connect_to(nodeServer, QChannelSoSe, local_port_name = nodeSource.ports["SeQO"].name, remote_port_name = nodeServer.ports["SoQI"].name)
    nodeSource.connect_to(nodeClient, QChannelSoCl, local_port_name = nodeSource.ports["ClQO"].name, remote_port_name = nodeClient.ports["SoQI"].name)

    nodeSource.connect_to(nodeServer, CChannelSoSe, local_port_name = nodeSource.ports["SeCO"].name, remote_port_name = nodeServer.ports["SoCI"].name)
    nodeSource.connect_to(nodeClient, CChannelSoCl, local_port_name = nodeSource.ports["ClCO"].name, remote_port_name = nodeClient.ports["SoCI"].name)

    nodeClient.connect_to(nodeSource, CChannelClSo, local_port_name = nodeClient.ports["SoCO"].name, remote_port_name = nodeSource.ports["ClCI"].name)
    nodeClient.connect_to(nodeServer, CChannelClSe, local_port_name = nodeClient.ports["SeCO"].name, remote_port_name = nodeServer.ports["ClCI"].name)

    nodeServer.connect_to(nodeClient, CChannelSeCl, local_port_name = nodeServer.ports["ClCO"].name, remote_port_name = nodeClient.ports["SeCI"].name)

    protocolServer = UBQC_server.EPRTest(nodeServer, processorServer)
    protocolClient = UBQC_client.EPRTest(nodeClient, processorClient)
    protocolSource = UBQC_source.EPRGen(nodeSource, processorSource)

    protocolServer.start()
    logger.info("Starting Server")
    protocolSource.start()
    logger.info("Starting Source")
    protocolClient.start()
    logger.info("Starting Client")
    #ns.logger.setLevel(1)
    stats = ns.sim_run()
        

for i in range(10):
    logger.info(f'run: {i}')
    res = run_UBQC_sim(fibre_len=10**-9, processorNoiseModel=None,memNoiseMmodel=None,loss_init=0,loss_len=0)


