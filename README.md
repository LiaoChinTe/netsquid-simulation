# NetSquid Protocols
Here are list of quantum network protocol simulations powered by NetSquid.



## File Structure

This part means to help readers understand how we arrange the codes. This understanding is necessary if you want to contribute to this repository or build something on top of these codes. 
This file structure might not be the best one for NetSquid simulation, I am open for discussion.
All protocols follows the same code structure shown below:

![NsFileStructure](https://github.com/LiaoChinTe/netsquid-simulation/blob/main/FileStructure.png)

Gray boxes are folders, other colored cells are pyhton files.
Reusable functions are located in 'lib/functions.py'.
Therefore, one must be extreamly careful modifing it.



- **function.py**

  Here we have functions and Quantum Programs that are reusable.

- **ProtocolX_partyX.py**

  A customized local protocol representing one of the party.


- **ProtocolX_main.py**

  The main function to run if you want to execute the simulation


- **ProtocolX_plot.py** -optional

  A function to plot statistical results of main function.


# Quantum Protocol List
## Quantum Key Distribution
- BB84
- E91/Ekert/EPR

## Quantum Money
- Quantum Token
- Quantum Cheque

## Quantum Teleportation
- Quantum State Teleportation

## Universal Blind Quantum Computing 
- Verifiable Universal Blind Quantum Computing

## Anonymous Transmission
- W-state Anonymous Transmission

## Others
- QLine
- Quantum Memory test


## Contact
ChinTe Liao
liao.chinte@veriqloud.fr
