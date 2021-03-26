import time

import netsquid as ns
import netsquid.components.instructions as instr
import numpy as np
from netsquid.components import QuantumChannel, QuantumProgram, ClassicalChannel, FibreDelayModel, DephaseNoiseModel, \
    T1T2NoiseModel, QSource, SourceStatus, FibreLossModel
from netsquid.components.qprocessor import QuantumProcessor, PhysicalInstruction
from netsquid.nodes import Node, Network, Connection
from netsquid.protocols import NodeProtocol, Signals
from netsquid.qubits import StateSampler
import netsquid.qubits.ketstates as ks
import matplotlib.pyplot as plt
import cascade

bob_keys = []
alice_keys = []

bob_corrected_keys = []


class EncodeQubitProgram(QuantumProgram):
    """
    Program to encode a bit according to a secret key and a basis.
    """

    def __init__(self, base, bit):
        super().__init__()
        self.base = base
        self.bit = bit

    def program(self):
        q1, = self.get_qubit_indices(1)
        # Don't init since qubits come initalised from the qsource
        # self.apply(instr.INSTR_INIT, q1)
        if self.bit == 1:
            self.apply(instr.INSTR_X, q1)
        if self.base == 1:
            self.apply(instr.INSTR_H, q1)
        yield self.run()


class RandomMeasurement(QuantumProgram):
    def __init__(self, base):
        super().__init__()
        self.base = base

    def program(self):
        q1, = self.get_qubit_indices(1)
        if self.base == 0:
            self.apply(instr.INSTR_MEASURE, q1, output_key="M")
        elif self.base == 1:
            self.apply(instr.INSTR_MEASURE_X, q1, output_key="M")
        yield self.run()


class KeyReceiverProtocol(NodeProtocol):
    """
    Protocol for the receiver of the key.
    """

    def __init__(self, node, key_size=10, port_names=("qubitIO", "classicIO")):
        super().__init__(node)
        self.node = node
        self.q_port = port_names[0]
        self.c_port = port_names[1]
        self.key_size = key_size
        self.key = None

    def run(self):
        # Select random bases
        bases = np.random.randint(2, size=self.key_size)
        results = []
        i = 0

        def record_measurement(measure_program):
            measurement_result = measure_program.output['M'][0]
            results.append(measurement_result)

        def measure_qubit(message):
            self.node.qmemory.put(message.items[0], positions=[i])
            measure_program = RandomMeasurement(bases[i])
            self.node.qmemory.set_program_done_callback(record_measurement, measure_program=measure_program, once=False)
            self.node.qmemory.execute_program(measure_program, qubit_mapping=[i])

        # Not sure why this timer has to have a huge number...
        delay_timer = 200000000
        for i in range(self.key_size):
            # Await a qubit from Alice
            self.node.ports[self.q_port].forward_input(self.node.qmemory.ports[f"qin{i}"])
            self.node.qmemory.ports[f"qin{i}"].bind_input_handler(measure_qubit)
            yield self.await_port_input(self.node.ports[self.q_port]) | self.await_timer(delay_timer)

        yield self.await_program(self.node.qmemory) | self.await_timer(delay_timer)
        # All qubits arrived, send bases
        self.node.ports[self.c_port].tx_output(bases)

        # Await matched indices from Alice and process key
        yield self.await_port_input(self.node.ports[self.c_port])
        matched_indices = self.node.ports[self.c_port].rx_input().items
        final_key = []

        for i in matched_indices:
            if i < len(results):
                final_key.append(results[i])

        self.key = final_key
        global bob_keys

        bob_keys.append(final_key)
        self.send_signal(signal_label=Signals.SUCCESS,
                         result=final_key)


class KeySenderProtocol(NodeProtocol):
    """
    Protocol for the sender of the key.
    """

    def __init__(self, node, key_size=10, port_names=("qubitIO", "classicIO")):
        super().__init__(node)
        self.node = node
        self.q_port = port_names[0]
        self.c_port = port_names[1]
        self.key_size = key_size
        self.key = None

    def run(self):
        secret_key = np.random.randint(2, size=self.key_size)
        bases = list(np.random.randint(2, size=self.key_size))

        self.node.qmemory.subcomponents['qubit_source'].status = SourceStatus.INTERNAL
        # Transmit encoded qubits to Bob
        for i, bit in enumerate(secret_key):
            # Await a qubit
            yield self.await_port_output(self.node.qmemory.subcomponents['qubit_source'].ports['qout0'])
            qubits = self.node.qmemory.subcomponents['qubit_source'].ports['qout0'].rx_output().items
            self.node.qmemory.put(qubits, positions=[0], replace=True)
            self.node.qmemory.execute_program(EncodeQubitProgram(bases[i], bit))
            yield self.await_program(self.node.qmemory)
            self.node.qmemory.pop(0)
            self.node.ports[self.q_port].tx_output(self.node.qmemory.ports['qout'].rx_output())
        self.node.qmemory.subcomponents['qubit_source'].status = SourceStatus.OFF

        # Await response from Bob
        yield self.await_port_input(self.node.ports[self.c_port])
        bob_bases = self.node.ports[self.c_port].rx_input().items[0]
        matched_indices = []
        for i in range(self.key_size):
            if bob_bases[i] == bases[i]:
                matched_indices.append(i)

        self.node.ports[self.c_port].tx_output(matched_indices)
        final_key = []
        for i in matched_indices:
            final_key.append(secret_key[i])
        self.key = final_key
        global alice_keys

        alice_keys.append(final_key)
        self.send_signal(signal_label=Signals.SUCCESS,
                         result=final_key)


def create_processor(dephase_rate, t_times, memory_size, add_qsource=False, q_source_probs=[1., 0.]):
    """Factory to create a quantum processor for each end node.

    Has three memory positions and the physical instructions necessary
    for teleportation.
    """

    gate_noise_model = DephaseNoiseModel(dephase_rate, time_independent=False)
    memory_noise_model = T1T2NoiseModel(T1=t_times['T1'], T2=t_times['T2'])

    physical_instructions = [
        PhysicalInstruction(instr.INSTR_INIT,
                            duration=1,
                            parallel=False,
                            q_noise_model=gate_noise_model),
        PhysicalInstruction(instr.INSTR_H,
                            duration=1,
                            parallel=False,
                            q_noise_model=gate_noise_model),
        PhysicalInstruction(instr.INSTR_X,
                            duration=1,
                            parallel=False,
                            q_noise_model=gate_noise_model),
        PhysicalInstruction(instr.INSTR_Z,
                            duration=1,
                            parallel=False,
                            q_noise_model=gate_noise_model),
        PhysicalInstruction(instr.INSTR_MEASURE,
                            duration=10,
                            parallel=False,
                            q_noise_model=gate_noise_model),
        PhysicalInstruction(instr.INSTR_MEASURE_X,
                            duration=10,
                            parallel=False,
                            q_noise_model=gate_noise_model)
    ]
    processor = QuantumProcessor("quantum_processor",
                                 num_positions=memory_size,
                                 mem_noise_models=[memory_noise_model] * memory_size,
                                 phys_instructions=physical_instructions)
    if add_qsource:
        qubit_source = QSource('qubit_source',
                               StateSampler([ks.s0, ks.s1], q_source_probs),
                               num_ports=1,
                               status=SourceStatus.OFF)
        processor.add_subcomponent(qubit_source,
                                   name='qubit_source')
    return processor


class QubitConnection(Connection):
    def __init__(self, length, dephase_rate, loss=(0, 0), name='QubitConn'):
        super().__init__(name=name)
        error_models = {'quantum_noise_model': DephaseNoiseModel(dephase_rate=dephase_rate,
                                                                 time_independent=False),
                        'delay_model': FibreDelayModel(length=length),
                        'quantum_loss_model': FibreLossModel(p_loss_init=loss[0], p_loss_length=loss[1])
                        }
        q_channel = QuantumChannel(name='q_channel',
                                   length=length,
                                   models=error_models
                                   )
        self.add_subcomponent(q_channel,
                              forward_output=[('B', 'recv')],
                              forward_input=[('A', 'send')])


def generate_network(node_distance=1e3, dephase_rate=0.2, key_size=15, t_time=None,
                     q_source_probs=(1., 0.), loss=(0, 0)):
    """
    Generate the network. For BB84, we need a quantum and classical channel.
    """
    if t_time is None:
        t_time = {'T1': 11, 'T2': 10}

    network = Network("BB84 Network")
    alice = Node("alice", qmemory=create_processor(dephase_rate, t_time, key_size, add_qsource=True,
                                                   q_source_probs=q_source_probs))
    bob = Node("bob", qmemory=create_processor(dephase_rate, t_time, key_size))
    network.add_nodes([alice, bob])
    q_conn = QubitConnection(length=node_distance, dephase_rate=dephase_rate, loss=loss)
    network.add_connection(alice,
                           bob,
                           label='q_chan',
                           connection=q_conn,
                           port_name_node1='qubitIO',
                           port_name_node2='qubitIO')
    network.add_connection(alice,
                           bob,
                           label="c_chan",
                           channel_to=ClassicalChannel('AcB', delay=10),
                           channel_from=ClassicalChannel('BcA', delay=10),
                           port_name_node1="classicIO",
                           port_name_node2="classicIO")
    return network


def run_experiment(fibre_length, dephase_rate, key_size, t_time=None, runs=100, q_source_probs=(1., 0.), loss=(0, 0)):
    if t_time is None:
        t_time = {'T1': 10001, 'T2': 10000}

    global bob_keys, alice_keys, bob_corrected_keys
    bob_keys = []
    alice_keys = []
    bob_corrected_keys = []

    for _ in range(runs):
        ns.sim_reset()

        n = generate_network(fibre_length, dephase_rate, key_size, t_time, q_source_probs, loss)

        node_a = n.get_node("alice")
        node_b = n.get_node("bob")
        p1 = KeySenderProtocol(node_a, key_size=key_size)
        p2 = KeyReceiverProtocol(node_b, key_size=key_size)

        p1.start()
        p2.start()

        ns.sim_run()

        c1 = cascade.SenderProtocol(node_a, key=alice_keys[-1])
        c2 = cascade.ReceiverProtocol(node_b, key=bob_keys[-1])

        c1.start()
        c2.start()

        ns.sim_run()
        bob_corrected_keys.append(c2.corrected_key)

    def keys_match(key1, key2):
        if len(key1) != len(key2):
            return False
        for j in range(len(key1)):
            if key1[j] != key2[j]:
                return False
        return True

    _stats = {'MISMATCHED_KEYS': 0, 'MATCHED_KEYS': 0, 'CORRECTED_MATCHED': 0}
    for i, bob_key in enumerate(bob_keys):
        alice_key = alice_keys[i]
        if not keys_match(alice_key, bob_key):
            _stats['MISMATCHED_KEYS'] += 1
        else:
            _stats['MATCHED_KEYS'] += 1

    for i, bob_key in enumerate(bob_corrected_keys):
        alice_key = alice_keys[i]
        if keys_match(alice_key, bob_key):
            _stats['CORRECTED_MATCHED'] += 1
    return _stats


def plot_fibre_length_experiment(runs=100):
    lengths = np.linspace(0, 10000, 4)
    phases = np.linspace(0.2, 0.5, 2)
    for phase in phases:
        data = []
        for length in lengths:
            print(f'Running l={length}, p={phase}')
            ns.sim_reset()
            data.append(
                run_experiment(
                    fibre_length=length,
                    dephase_rate=phase,
                    key_size=50,
                    runs=runs,
                    t_time={'T1': 11, 'T2': 10},
                    q_source_probs=[1., 0.],
                )
            )
        correct_keys = [d['MATCHED_KEYS'] / runs for d in data]
        error_correct_keys = [d['CORRECTED_MATCHED'] / runs for d in data]
        plt.plot([l / 1000 for l in lengths], correct_keys,
                 marker='.',
                 linestyle='solid',
                 label=f'Dephase Rate={phase}')
        plt.plot([l / 1000 for l in lengths], error_correct_keys,
                 marker='.',
                 linestyle='dashed',
                 label=f'Dephase Rate={phase}')
        plt.legend()
        plt.title('Key Distribution Efficiency Over Fibre')
        plt.ylim(0, 1.1)
        plt.xlabel('Length (km)')
        plt.ylabel('Percentage of correctly transmitted keys')
    plt.show()


def plot_loss_experiment(runs=100):
    lengths = np.linspace(0, 10, 6)
    losses = np.linspace(0, 0.01, 5)
    for loss in losses:
        data = []
        for length in lengths:
            print(f'Running l={length}, p_loss={loss}')
            ns.sim_reset()
            data.append(run_experiment(fibre_length=length,
                                       dephase_rate=0,
                                       key_size=25,
                                       runs=runs,
                                       t_time={'T1': 11, 'T2': 10},
                                       q_source_probs=[1., 0.],
                                       loss=(0, loss)),
                        )
        correct_keys = [d['MATCHED_KEYS'] / runs for d in data]
        plt.plot([l / 1000 for l in lengths], correct_keys,
                 marker='.',
                 linestyle='solid',
                 label=f'Loss Rate={loss}')
        plt.legend()
        plt.title('Key Distribution Efficiency Over Fibre')
        plt.ylim(0, 1.1)
        plt.xlabel('Length (km)')
        plt.ylabel('Percentage of correctly transmitted keys')
    plt.show()


def plot_key_length_vs_length(runs=100):
    lengths = np.linspace(0, 10, 5)
    sizes = np.linspace(15, 100, 4, dtype=int)
    for size in sizes:
        data = []
        for length in lengths:
            print(f'Running l={length}, size={size}')
            ns.sim_reset()
            data.append(run_experiment(fibre_length=length,
                                       dephase_rate=0,
                                       key_size=size,
                                       runs=runs,
                                       t_time={'T1': 11, 'T2': 10},
                                       q_source_probs=[1., 0.],
                                       loss=(0, 0.01)),
                        )
        correct_keys = [d['MATCHED_KEYS'] / runs for d in data]
        plt.plot([l / 1000 for l in lengths], correct_keys,
                 marker='.',
                 linestyle='solid',
                 label=f'Key Size={size}')
        plt.legend()
        plt.title('Key Distribution Efficiency Over Fibre')
        plt.ylim(0, 1.1)
        plt.xlabel('Length (km)')
        plt.ylabel('Percentage of correctly transmitted keys')
    plt.show()


if __name__ == '__main__':
    start = time.time()
    plot_fibre_length_experiment()
    # plot_loss_experiment(runs=300)
    # plot_key_length_vs_length(runs=200)
    # print(f'Finished in {time.time() - start} seconds.')

    # print(
    #     run_experiment(
    #         fibre_length=5000,
    #         dephase_rate=0.5,
    #         key_size=1000,
    #         runs=10,
    #         # t_time={'T1': 11, 'T2': 10},
    #         q_source_probs=[1., 0.],
    #         # loss=(0.000005, 0.000005),
    #         error_correction=True
    #     )
    # )
