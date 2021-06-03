# VBQC Protocol
Author: ChinTe LIAO (liao.chinte@veriqloud.fr)


## Function

Verifiable Blind Quantum Computation.

VBQC full protocol which applies both computaional and verifiable subprotocols. 



## Status

Works on NetSquid version 1.0.5

- 02/04/2021 First readme





## Protocol variable & its ranges
- range C=n*pi/4, n=[0,7]
### input 
- x : [0,1] input bit
- phi1: [0,7] indecating angles in range C
- phi2: [0,7] indecating angles in range C
- phi3: [0,7] indecating angles in range C
- N : ∈N Number of total rounds
- d : [0,N] Number of computational rounds
- Threshold : [0,d] Max number of failed case tolerance.


### output
- output : [0:1] 


## Protocol Steps

0. Hardware configuration.
1. Randomly form a bit stream roundType filled by d ones and N-d zero. 
2. Loop through the roundType and implement computatinal BQC if the value is 1. 
Otherwise implement Verifiable BQC. Count the failed cases in verifiable cases.
3. Report abort if numbers of failed case > Threshold.
4. If not failed, compute the Hamming weight of the string output.
5. If the Hamming weight < d/2 set final output to 0. Set it to 1 otherwise.

