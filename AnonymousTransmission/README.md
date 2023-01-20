# Anonymous Transmission Protocol
Author: ChinTe LIAO (liao.chinte@veriqloud.fr)

## Function

Quantum Anonymous Transmission protocol works between multiple nodes. Currently our protocol is limited to 4 parties only.
The protocol aims to transfer infomation anonymously among a group of user, meaning that the receiver does not know who send the massage.


![AT_Network](https://github.com/LiaoChinTe/netsquid-simulation/blob/main/AnonymousTransmission/AnonymousTransmission_Network.png)

In this specific simulation, we assume that sender and receiver are set to node #1 and #2 in order to build a classical channel for quantum teleportation. 

By doing so, it is not literary anonymous anymore. However it does not really affect any result of this simulation. Plus, we can easily modify such configuration by tunning the parameters of the protocol.



## Protocol Steps

1. Sender and receiver roles are assigned to **sideNode** 1 and 2 before the protocol starts in this case. Sender prepares its qubit to be teleport.
2. The **centerNode** (trusted third party) distributes 4-parties W state, and send to all **sideNodes**.
3. All **sideNodes** apart from the sender and receiver perform standard basis measurement. Send results to the **centerNode**.
4. **CenterNode** gethers all measurment results, abort protocol if any none-zero results from measurements. Continue only if all results are 0.
5. Sender node apply Sender Quantum Teleportation protocol, While receiver node apply Receiver Quantum Teleportation protocol.
6. After those Teleportation protocol, The receiver should be able to receive the specific quantum state that sender prepared.



## Status

Works on NetSquid version 1.1.6

28/01/2021
- Finished importing Quantum Teleportation, and ready to run with 4 parties.

15/01/2021
- Finished all steps before teleportation

20/01/2023
- File arrangement modified.




