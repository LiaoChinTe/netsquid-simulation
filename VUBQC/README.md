# UBQC Protocol
Author: ChinTe LIAO (liao.chinte@veriqloud.fr)

## Function

UBQC protocol contains two parts, computation and varification part. Current code contains only varification part.


## To Do

- Debugging on algorithm.


## Status

Works on NetSquid version 0.10.


12/01/2021
- Under debugging. The protocol should always return verified massage. However only half of the case did so.





## Verifiable UBQC


### Test subprotocol variable ranges
- range A=n*pi/8, n=[0,7]
- range B=n*pi/8, n=[0,15]
- theta1: A
- theta2: A
- r1:[0,1]
- r2:[0,1]

**results:**
- d :[1,2]
- p1:[0,1]
- p2:[0,1]
- z1:[0,1]
- z2:[0,1]
- delta1: A or B
- delta2: A or B

All angle measurements are rotated along Z-axis. Following 3 steps on a qubit:
rotate angle *-Ang* -> measure in X basis -> rotate angle *Ang*

### Test subprotocol variable Steps

 1. C randomly chooses d.
 2. S generates four qubits in |0> state.(label 1 to 4)
 3. S makes two EPR pairs: Apply H gate and CNOT gate with qubit label 1 and qubit label 2, same with 3 and 4.
 4. S sends two qubits (2 and 4) to C, now the two EPR pairs are shared.
 5. C if d value equal to 1, randomly chooses theta2 and r2, measure qubit 2 by theta2, assign result to p2.
 
      if d value equal to 2, measures qubit 2 in standard basis, assign result to z2.
 6. C sends ACK to S.
 7. S swaps memory position of qubit 1 with qubit 3.
 8. S sends ACK2 to C.
 9. C if d value equal to 1, measures qubit 4 in standard basis, assign result to z1.
 
      if d value equal to 2, randomly chooses theta1 and r1, measure qubit 4 by theta2, assign result to p1.
10. C sends ACK3 to S.
11. S apply CZ with qubits 1 and 3.
12. S sends ACK4 to C.
13. C if d value equal to 1, randomly chooses delta1, assign delta2=theta2+(p2+r2)*pi.

      if d value equal to 2, randomly chooses delta2, assign delta1=theta1+(p1+r1)*pi.
14. C sends delta1 and delta2 to S.
15. S measures the qubit 3 by delta1. And measures qubit 1 by delta2, assign results to m1 and m2.
16. S sends m1 and m2 to C
17. C if d value equal to 1, and (z1+r2)%2=m2, than verification passed.

      if d value equal to 2, and (z2+r1)%2=m1, than verification passed.
      
      else Not verified.
