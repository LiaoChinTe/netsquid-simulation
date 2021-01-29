# Quantum Teleportation Protocol
Author: ChinTe LIAO (liao.chinte@veriqloud.fr)

## Function


According to different Bell states shared between sender and receiver, 
different adjustment on receiver's side should be applied.

![Bell_states](https://github.com/LiaoChinTe/netsquid-simulation/blob/main/Bell_states.png)
*-from https://en.wikipedia.org/wiki/Bell_state*


### In case 1:
- If receives 00, then apply nothing.
- If receives 01, then apply X.
- If receives 10, then apply Z.
- If receives 11, then apply X and Z.


### In case 3:
- If receives 00, then apply X.
- If receives 01, then apply nothing.
- If receives 10, then apply X and Z.
- If receives 11, then apply Z.


## Protocol Steps

Following protocol steps:
https://wiki.veriqloud.fr/index.php?title=Quantum_Teleportation


## To Do

- Extend to accept more Bell States.


## Status

Works on NetSquid version 0.10.

28/01/2021
- Add Bell State parameter, currently accept two Bell States. 

22/01/2021
- Upload first version
