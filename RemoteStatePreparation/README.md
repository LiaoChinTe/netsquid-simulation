# Remote State Preparation Protocol



## Function

This protocol aims to prepare qubits with certain quantum state depend on all clients participated.



## Status

- 28/06/2021 First readme



## Protocol variables

### input 
- N : Numbers of Clients
- thetaX : X=[1,N] Indication of the angle rotated along Z-axis, input of every Client.
- tX : X=[1,N-1] Result value of . Intermediate value on server side.


### output
- output : a qubit with certain state.


## Protocol Steps

0. Hardware configuration. And create given number of clients.
1. The Clients prepare a qubit with certain state based on thetaX. 
Then send it to server. 
2. The Server applies CNOT according to the graph after receiving all qubits from Clients. 
3. The Server measures all qubits except from the last one.
