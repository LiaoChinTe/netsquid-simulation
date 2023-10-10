# Quantum Token Protocol

## Description
 The protocol provides a way for issuing an unforgeable token which can only be verified by the issuer or other authorized party.
 Reference: [Quantum Token from Quantum Protocol Zoo](https://wiki.veriqloud.fr/index.php?title=Quantum_Token)

## How to use
  Protocol configurations are writen only in *QToken_run.py* file. Users could define the return value from any protocol attribute at the end of *run_QToken_sim()* function.
Users should not bother modifying the party files (QToken_Alice.py, QToken_Bob.py ), but only to check what attributes to be extracted later in *QToken_run.py*.
quantumToken_plot.py file in *script/* is used to plot statistics by calling *run_QToken_sim()* recursively.

## Status
- 18/08/2021 Fixed minor import issues.
- 05/05/2021 Imported from the old repository. Need further refine.
- 20/01/2023 Refined and added scripts.
- 10/10/2023 Refined README.

## Protocol parameters

- num_bits    : Number of qubits, higher value means higher security but higher cost in terms of qubits management.
- fiberLenth  : [km] Fiber length between two Nodes, long fiber cause more noise.
- depolar_rate: [Hz]/[prob] Parameter of deplar noise model, this will be a probability if timeIND is true.
- timeIND     : Time independency. If ture, depolar_rate will be a probability. Otherwise in Hz.
- threshold   : The threshold that token issuer sets. Value can only be 0 to 1. Higher value means lower tolerancy and higher security, but less verifying successful rate.
- waitTime    : [sec] The time between node A receiving the qubits and sending challange request.
- Cmes        : Customized challange request message, can be any classical message like 10101. Doesn't affect the protocl much.


## Steps
 1. (preparation stage) Node B prepares N random qubits and record the states.
 2. (preparation stage) Node B send the qubits(the token) to node A.
 3. Node A wait for T seconds.
 4. Node A send a challange request to node B to verify the token. (initialize the verification process)
 5. (verification stage) Node B replies a challange for Node A to solve. 
 6. (verification stage) Node A measures its qubits according to the challange.
 7. (verification stage) Node A send the measurement result to node B.
 8. (verification stage) Node B send the approval or deny.
