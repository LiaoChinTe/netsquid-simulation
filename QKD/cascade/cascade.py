import netsquid as ns
from netsquid.components import ClassicalChannel
from netsquid.nodes import Node, Network, Connection

import numpy as np
from netsquid.protocols import NodeProtocol, Signals
import matplotlib.pyplot as plt


def next_pow_2(n):
    n = int(n)
    count = 0
    if n and not (n & (n - 1)):
        return n
    while n != 0:
        n >>= 1
        count += 1
    return 1 << count


def binary_parity_check(key, order, block_length):
    parities = []
    num_blocks = int(np.ceil(len(key) / block_length))
    for i in range(num_blocks):
        if len(key) >= (i + 1) * block_length:
            block = [key[j] for j in order[i * block_length: (i + 1) * block_length]]
        else:
            block = [key[j] for j in order[i * block_length:]]
        parities.append(sum(block) % 2)
    return parities


class SenderProtocol(NodeProtocol):
    def __init__(self, node, key, c_port_name="classicIO"):
        super().__init__(node)
        self.node = node
        self.c_port = c_port_name
        self._key = key

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, k):
        self._key = k

    def run(self):
        while True:
            self.node.ports[self.c_port].reset()
            yield self.await_port_input(self.node.ports[self.c_port])
            indices = self.node.ports[self.c_port].rx_input().items
            parity = sum([self.key[i] for i in indices]) % 2
            self.node.ports[self.c_port].tx_output(parity)


class ReceiverProtocol(NodeProtocol):
    def __init__(self, node, key, qber=1e-1, rate=0.73, c_port_name="classicIO", seed=1000):
        super().__init__(node)
        self.node = node
        self.c_port = c_port_name
        self.qber = qber
        self.rate = rate
        self.passes = 4
        np.random.seed(seed)
        blocksizes = next_pow_2(np.ceil(rate / qber))
        self.blocks = [blocksizes * 2 ** i for i in range(self.passes)]
        if key is not None:
            self._key = key
            self.corrected_key = np.copy(key)
            self.cur_order = list(range(len(self.corrected_key)))

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, k):
        self._key = k
        self.corrected_key = np.copy(self._key)
        self.cur_order = list(range(len(self.corrected_key)))

    def get_cur_block(self, block_length, iteration):
        if len(self.cur_order) >= (iteration + 1) * block_length:
            return self.cur_order[iteration * block_length: (iteration + 1) * block_length]
        else:
            return self.cur_order[iteration * block_length:]

    def run(self):
        for i in range(self.passes):
            np.random.shuffle(self.cur_order)
            parities = binary_parity_check(self.corrected_key, self.cur_order, self.blocks[i])

            for j, parity in enumerate(parities):
                indices = self.get_cur_block(self.blocks[i], j)
                self.node.ports[self.c_port].reset()
                self.node.ports[self.c_port].tx_output(indices)
                yield self.await_port_input(self.node.ports[self.c_port])
                alice_parity = self.node.ports[self.c_port].rx_input().items[0]
                if parity != alice_parity:
                    cur_block = indices
                    while len(cur_block) != 1:
                        right = cur_block[len(cur_block) // 2:]
                        left = cur_block[:len(cur_block) // 2]

                        self.node.ports[self.c_port].reset()
                        self.node.ports[self.c_port].tx_output(left)
                        yield self.await_port_input(self.node.ports[self.c_port])
                        p = self.node.ports[self.c_port].rx_input().items[0]
                        if p != sum([self.corrected_key[i] for i in left]) % 2:
                            cur_block = left
                        else:
                            cur_block = right
                    self.corrected_key[cur_block[0]] = (self.corrected_key[cur_block[0]] + 1) % 2


def generate_network():
    """
    Generate the network. For BB84, we need a quantum and classical channel.
    """

    network = Network("Classical Network")
    alice = Node("alice")
    bob = Node("bob")

    network.add_nodes([alice, bob])
    network.add_connection(alice,
                           bob,
                           label="c_chan",
                           channel_to=ClassicalChannel('AcB', delay=10),
                           channel_from=ClassicalChannel('BcA', delay=10),
                           port_name_node1="classicIO",
                           port_name_node2="classicIO")
    return network


if __name__ == "__main__":
    n = generate_network()
    node_a = n.get_node("alice")
    node_b = n.get_node("bob")

    key = np.random.choice([0, 1], 1000)
    key2 = np.copy(key)

    key2[0] = (key2[0] + 1) % 2
    key2[101] = (key2[101] + 1) % 2
    key2[500] = (key2[500] + 1) % 2
    key2[888] = (key2[888] + 1) % 2
    key2[588] = (key2[588] + 1) % 2
    key2[308] = (key2[308] + 1) % 2
    key2[988] = (key2[988] + 1) % 2
    key2[750] = (key2[750] + 1) % 2

    p1 = SenderProtocol(node_a, key=key)
    p2 = ReceiverProtocol(node_b, key=key2)

    p1.start()
    p2.start()

    stats = ns.sim_run()
    print(sum(np.bitwise_xor(p2.corrected_key, key)))
