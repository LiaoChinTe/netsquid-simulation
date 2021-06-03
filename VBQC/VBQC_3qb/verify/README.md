# VBQC Protocol
Author: ChinTe LIAO (liao.chinte@veriqloud.fr)

## Function

VBQC protocol test on three qubits.


## To Do


## Status

Works on NetSquid version 1.0.5

-15/03/2021 Finalize steps.


## Verifiable BQC


### Protocol variable ranges
- range C=n*pi/4, n=[0,7]

**results:**
- t : [1,2]
- theta1 : C
- theta2 : C
- theta3 : C
- d1 : [0,1]
- d2 : [0,1]
- d3 : [0,1]
- bt1 : [0,1]
- bt2 : [0,1]
- bt3 : [0,1]
- b1 : [0,1]
- b2 : [0,1]
- b3 : [0,1]
- delta1 : C
- delta2 : C
- delta3 : C
- r1 : [0,1]
- r2 : [0,1]
- r3 : [0,1]

All angle measurements are rotated along Z-axis. Following 3 steps on a qubit:
rotate angle *-Ang* -> measure in X basis -> rotate angle *Ang*

### Protocol Steps

1. Server generates six qubits in |0> state.(label 1 to 6)
2. Server makes three EPR pairs: Apply H gate on qubit 1 and CNOT gate on qubit 1(control) and qubit 2(target), same with 3 and 4, 5 and 6. 
3. Server applies Control-Z on qubit 1 and 3 and on qubit 3 and 5.
4. Server sends three qubits (2, 4 and 6) to C, now the three EPR pairs are shared.
5. Client randomly chooses t and theta1, theta2, theta3.
6. Client, if t=1, measures qubit 2 with -theta1, assign result to bt1. Then measures qubit 6 with -theta3, assgin result to bt3.Then measures qubit 4 with standard basis, assign result to d2. 
   If t=2, measures qubit 4 with -theta2, assign result to bt2. Then measures qubit 2 and qubit 6 with standard basis, assgin result to d1 and d3.
7. Client randomly chooses r1, r2 and r3.
8. Client, if t=1, assign delta1 = theta1+(r1+d2+bt1)*pi, randomly assign delta2 in range C, and assign delta3 = theta3+(r3+d2+bt3)*pi.
   If t=2, randomly assign delta1 and delta3 in range C, assign delta2 = theta2+(r2+d1+d3+bt2)*pi.
9. Client sends delta1.
10. Server measures qubit 1 with angle delta1, assign results to b1.
11. Server sends b1
12. Client sends delta2.
13. Server measures qubit 3 with angle delta2, assign results to b2.
14. Server sends b2.
15. Client sends delta3.
16. Server measures qubit 5 with angle delta3, assign results to b3.
17. Server sends b3 to client.
18. Client, if t=1, varification passes if r1=b1 and r3=b3.
    If t=2, varification passes if r2=b2.
