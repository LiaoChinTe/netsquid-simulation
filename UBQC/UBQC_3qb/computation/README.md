# UBQC computational Protocol


## Function

UBQC computational protocol on three qubits.


## To Do


## Status

Works on NetSquid version 1.0.5





### Protocol variable ranges
- range C=n*pi/4, n=[0,7]

**results:**
- t : [1,2]
- theta1 : C
- theta2 : C
- theta3 : C
- phi1 : C
- phi2 : C
- phi3 : C
- bt1 : [0,1]
- bt2 : [0,1]
- bt3 : [0,1]
- delta1 : C
- delta2 : C
- delta3 : C
- r1 : [0,1]
- r2 : [0,1]
- r3 : [0,1]

All angle measurements are rotated along Z-axis. Following 3 steps on a qubit:
rotate angle *-Ang* -> measure in X basis -> rotate angle *Ang*

### Protocol Steps
1. Server generates six qubits in |0> state (labelled 1 to 6)
2. Server makes three EPR pairs: Apply H gate on qubit 1 and CNOT gate on qubit 1 (control) and qubit 2(target), 
same with qubits 3 and 4 and qubits 5 and 6.
3. Server applies Control-Z on qubits 1 and 3 and on qubits 3 and 5.
4. Server sends three qubits (2, 4, 6) to C, now the three EPR pairs are shared.
5. Client randomly chooses t and theta1, theta2, theta3.
6. Client measures qubit 2, 4, 6 with -theta1, -theta2 and -theta3 and assigns result to bt1, bt2 and bt3.
7. Client randomly chooses r1, r2 and r3.
8. Client assigns delta1 = phi1+theta1+(x+r1+bt1)*pi and sends delta1 to the Server.
10. Server measures qubit 1 with angle delta1, assign results to b1 and sends b1 to Client.
11. Client assigns delta2 = (-1)^(b1+r1)*phi2+theta2+(r2+bt2)*pi and sends delta2 to the Server.
12. Server measures qubit 3 with angle delta2, assign results to b2 and sends b2 to Client.
13. Client assigns delta3 = (-1)^(b2+r2)*phi3+theta3+(b1+r1+r3+bt3)*pi and sends delta2 to the Server.
14. Server measures qubit 5 with angle delta3, assign results to b3 and sends b3 to Client.
15. Client outputs o = b3 XOR r3.


