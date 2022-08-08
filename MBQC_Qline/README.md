# Multiclient Blind Quantum Computation with Qline architecture

## Description
 This protocol demonstrates multiclient blind quantum computation using Qline architecture.
 Four parties are included in this protocol:
 - Source : The begining node of QLine. Able to initialize qubits.
 - Alice  : A middle node of QLine. Only able to do qubits rotation.
 - Bob    : A middle node of QLine. Only able to do qubits rotation.
 - Server : The end node of Qline. Able to do measurement.
 - TEE    : Trusted Execution Environment. Has only classical communication with other parties.

## How to use
  

## Status
- 02/08/2022 Completed and validated in the first test.
- 09/08/2022 Complete README for debugging.


## Protocol parameters

range_A: i*pi/8, for i in [0,7]
range_B: [0,1]

General:
- fiberLenth  : [km] Fiber length between two Nodes, long fibers cause more noise.

Alice :
- thetaA1: range_A
- thetaA2: range_A
- x1: range_B
- x2: range_B
- rA1: range_B
- rA2: range_B

Bob:
- thetaB1: range_A
- thetaB2: range_A
- rB1: range_B
- rB2: range_B
- phi1: range_A
- phi2: range_A

Server:
- quantum memory noise: 



## Steps



1. Source produces two |0> state qubits and applys Hadamard gate to each of them.
2. Source applies Control-Z gate on the two qubits.
3. Source sends the two qubits to Alice.
4. Alice randomly choose thetaA1,thetaA2 in range_A. And x1,x2,rA1,rA2 in range_B.
5. Alice rotate first qubit along axis-Z with angle: *thetaA1+x1\*pi*.
6. Alice rotate second qubit along axis-Z with angle: *thetaA2+x2\*pi*.
7. Alice sends two qubits to Bob.
8. Alice sends above 6 parameters to TEE. 
9. Bob randomly choose thetaB1,thetaB2,phi1,phi2 in range_A. And rB1,rB2 in range_B.
10. Bob sends above 6 parameters to TEE. 
11. Bob rotate first qubit along axis-Z with angle: thetaB1.
12. Bob rotate second qubit along axis-Z with angle: thetaB2.
13. Bob sends two qubits to Server.
14. TEE compute delta1 as *thetaA1+pi\*x1+thetaB1+(rA1^rB1)\*pi+phi1*.
15. TEE sends delta1 to Server.
16. Server receives delta1 from TEE. (might switch with step 17.)
17. Server receives qubits from Bob. (might switch with step 16.)
18. Server rotate the first qubit along axis-Z with angle: delta1.
19. Server applys Hadamard gate on the first qubit.
20. Server rotate the first qubit along axis-Z with angle: 90.
21. Server applys X measurement on the first qubit. Assign the result to m1. 
22. Server sends m1 to TEE.
23. TEE compute mt1 as *m1^(rA1^rB1)*.
24. TEE compute delta2 as *thetaA2+pi\*x2+thetaB2+(rA2^rB2)\*pi+phi2\*(-1)\*\*mt1*.
25. TEE sends delta2 to Server.
26. Server rotate the second qubit along axis-Z with angle: delta2.
27. Server applys Hadamard gate on the second qubit.
28. Server rotate the second qubit along axis-Z with angle: 90.
29. Server applys X measurement on the second qubit. Assign the result to m2. 
30. Server sends m2 to TEE.
31. TEE compute mt2 as m2^(rA2^rB2).




