# Anonymous Transmission Protocol
Author: ChinTe LIAO (liao.chinte@veriqloud.fr)

## Function

Quantum Anonymous Transmission protocol works between multiple nodes. Currently our protocol is limited to 4 parties only.
It means to transfer infomation anonymously, meaning that the receiver does not know who send the massage.


![AT_Network](https://github.com/LiaoChinTe/netsquid-simulation/blob/main/AnonymousTransmission/AnonymousTransmission_Network.png)

In this specific simulation, we assume that sender and receiver are set to node #1 and #2 in order to build a classical channel for quantum teleportation. 

By doing so, it is not literary anonymous anymore. However it does not really affect any result of this simulation. Plus, we can easily modify such configuration by tunning the parameters of the protocol.



## Protocol Steps

1. Sender and receiver are assigned before the protocol starts
2. The **centerNode** (trusted third party) distributes 4-parties W state, and send to all **sideNodes**.
3. All **sideNodes** apart from sender and receiver perform standard basis measurement. Send the result to CenterNode.
4. CenterNode gethers all measurment results, abort protocol if any none=zero outcome is seen.
5. Sender is now able to teleport its quantum state to the receiver via the w-state qubits.



## To Do

- Import Quantum Teleportation.


## Status

Works on NetSquid version 0.10.


15/01/2021
- Finished all steps before teleportation
