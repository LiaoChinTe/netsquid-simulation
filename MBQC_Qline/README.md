# Multiclient Blind Quantum Computation with Qline architecture

## Description
 This protocol demonstrates multiclient blind quantum computation using Qline architecture.
 There are five parties included in this protocol:
 - Source : The begining node of QLine. Used mainly for initializing qubits.
 - Alice  : A middle node of QLine. Only able to do qubits rotation.
 - Bob    : A middle node of QLine. Only able to do qubits rotation.
 - Server : The end node of Qline. Used mainly for qubits measurement.
 - TEE    : Trusted Execution Environment. Has only classical communication with other parties. Has multiple channel connections with other parties.

## How to use
1. Configure protocol parameters (or use default) in *MBQC_Qline/MBQC_run.py*.
2. Set up the output and how to present it in *script/mbqc_main.py*.
3. run *python script/mbqc_main.py* to launch the simulation and show the output.

## Status
- 02/08/2022 Completed and validated in the first test.
- 09/08/2022 Complete README for debugging.
- 08/11/2022 Debugging protocol steps.


## Protocol parameters

range_A: i*pi/4, for i in [0,7]

range_B: [0,1]

General:
- fiberLenth  : [km] Fiber length between two Nodes, long fibers cause more noise.
- fiberLoss : [%/km] Qubits loss rate per kilometer in quantum fibers. 

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

Server:
- quantum memory noise



## Steps



1. Source produces two |0> state qubits and applys Hadamard gate to each of them.
2. Source applies Control-Z gate on the two qubits.
3. Source sends the two qubits to Alice.
4. Alice randomly choose thetaA1,thetaA2 in range_A. And x1,x2,rA1,rA2 in range_B.
5. Alice rotate first qubit along axis-Z with angle: *thetaA1*.
6. Alice rotate second qubit along axis-Z with angle: *thetaA2*.
7. Alice sends two qubits to Bob.
8. Alice sends above 6 parameters to TEE. 
9. Bob randomly choose thetaB1,thetaB2,phi1,phi2 in range_A. And rB1,rB2 in range_B.
10. Bob sends above 6 parameters to TEE. 
11. Bob rotate first qubit along axis-Z with angle: *thetaB1*.
12. Bob rotate second qubit along axis-Z with angle: *thetaB2*.
13. Bob sends two qubits to Server.
14. TEE compute delta1 as *thetaA1+pi\*x1+thetaB1+(rA1^rB1)\*pi+phi1*.
15. TEE sends delta1 to Server.
16. Server receives delta1 from TEE. (might switch with step 17.)
17. Server receives qubits from Bob. (might switch with step 16.)
18. Server rotate the first qubit along axis-Z with angle: *-delta1*.
19. Server applys X measurement on the first qubit. Assign the result to m1. 
20. Server sends m1 to TEE.
21. TEE compute mt1 as *m1^(rA1^rB1)*.
22. TEE compute delta2 as *thetaA2+pi\*x2+thetaB2+(rA2^rB2)\*pi+phi2\*(-1)\*\*mt1*.
23. TEE sends delta2 to Server.
24. Server rotate the second qubit along axis-Z with angle: *-delta2*.
25. Server applys X measurement on the second qubit. Assign the result to m2. 
26. Server sends m2 to TEE.
27. TEE compute mt2 as m2^(rA2^rB2).




