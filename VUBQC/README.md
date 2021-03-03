# UBQC Protocol
Author: ChinTe LIAO (liao.chinte@veriqloud.fr)

## Function

UBQC protocol contains two parts, computation and varification part. Current code contains only varification part.


## To Do

- Debugging on algorithm.


## Status

Works on NetSquid version 0.10.


01/02/2021
- Modify some algorithm mainly in Step 13,17.

12/01/2021
- Under debugging. The protocol should always return verified massage. However only half of the case did so.





## Verifiable UBQC


### Test subprotocol variable ranges
- t:[1,2]
- theta : C
- range C=n*pi/4, n=[0,7]

**results:**
- b1 :[0,1]
- b2 :[0,1]
- delta1: C
- delta2: C
- r :[0,1]

All angle measurements are rotated along Z-axis. Following 3 steps on a qubit:
rotate angle *-Ang* -> measure in X basis -> rotate angle *Ang*

### Test subprotocol2 variable Steps

1. Server generates four qubits in |0> state.(label 1 to 4)
2. Server makes two EPR pairs: Apply H gate on qubit 1 and CNOT gate on qubit 1(control) and qubit 2(target), same with 3 and 4. 
3. Server applies Control-Z on qubit 1 and 3.
4. Server sends two qubits (2 and 4) to C, now the two EPR pairs are shared.
5. Client randomly chooses t and theta.
6. Client, if t=1, measures qubit 2 with -theta, assign result to bt. Then measures qubit 4 with standard basis, assgin result to d.
   If t=2, measures qubit 4 with -theta, assign result to bt. Then measures qubit 2 with standard basis, assgin result to d.
7. Client send a ACK to server.
8. Client randomly chooses r.
9. Client, if t=1, assign delta1 = theta+(r+d+bt)*pi, randomly assign delta2 in range C.
   If t=2, randomly assign delta1 in range C, assign delta2 = theta+(r+d+bt)*pi.
10. Client send delta1 and delta2 to server.
11. Server measures qubit 1 and 3 in standard basis, assign results to b1 and b2.
12. Client, if t=1, varification passes if r=b1.
    If t=2, varification passes if r=b2.
