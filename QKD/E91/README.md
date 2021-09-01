# Quantum E91 Protocol

## Description
 E91 is a protocol that belongs to Quantum Key Distribution(QKD in short) protocol category. All QKD protocols aims to 
establish a symetric key pair between two parties.(Alice and Bob in this case) 
 Reference: [Quantum Key Distribution from Quantum Protocol Zoo](https://wiki.veriqloud.fr/index.php?title=BB84_Quantum_Key_Distribution)

## How to use

  Protocol configurations are writen only in XXX_main.py file. Users could choose the return value from any protocol attribute at the end of run_XXX_sim function by calling XXX_protocol.any_attribute. Attrbute list could be found in the party files (XXX_Alice.py, XXX_Bob.py ), which users should not bother modifying.
  
  XXX_plot.py file is use to plot statistics by calling run_XXX_sim function mutiple times. It is not needed for singular simulation run.

  Simply run XXX_main.py file by python should run an example for you.

## Status
- 01/09/2021 Release this README.

## Protocol parameters
- runtimes    : How many times to run this protocol.

- num_bits    : Number of qubits, higher value means higher security but higher cost in terms of qubits management.
- fiberLenth  : [km] Fiber length between two Nodes, long fiber cause more noise.
- memNoiseMmodel : Noise model to apply in quantum memory for both parties.
- processorNoiseModel : Noise model to apply in quantum operation for both parties. Detail configurations can be further applied on QuantumProcessor objects.
- loss_init   : Initial propability to loss a qubit in quantum fiber.
- loss_len    : [Prob/km]Propability to loss a qubit in quantum fiber by length.


## Steps
 1. Party A randomly decides N basis and generate EPR pairs accordindly. Now we have 2N qubits.
 2. Party A sends half of the EPR pairs to party B. Now the EPR pairs are shared.
 3. Party B randomly decides N basis and measure the received qubits accordingly.
 4. Party B sends his basis information to party A.
 5. Party A compares her basis with B's, send information about matched basis to party B. And apply measurement accordingly to her own qubits. The outcome is the key on A's side.
 6. Party B compares his basis with A's. Then filts out the unusable bit string. The remaining is the key on B's side.
