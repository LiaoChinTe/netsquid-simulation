# NetSquid Protocols
This repository introduces several quantum protocol simulations which could be used in quantum communication related studies.
This document not only explains how the code was arranged, but also concludes what protocols has been developed and ready to be run as long as proper parameters are given.

Please find more information about quantum protocols [here](https://wiki.veriqloud.fr/index.php?title=Protocol_Library).





# How to use

Simulations can be run by python files in the script folder under the root directory. 
The full hardware configurations can be edited in **AnyProtocol_run.py** files in each protocol folder. 
Yet most of the key parameters can be assigned to the function **AnyProtocol_run()**
There's no need for users to modify other files.
Common functions shared by multiple protocols are located in lib/functions.py, which can be further expended. However modifying exsisting functions are not recommended since that might influence exsisting protocol.




# Quantum Protocol List
## Quantum Key Distribution
- E91/Ekert/EPR
- BB84
- QLine

## Quantum Money
- Quantum Token

## Quantum Teleportation
- Quantum State Teleportation

## Universal Blind Quantum Computing 
- Verifiable Blind Quantum Computing

## Anonymous Transmission
- W-state Anonymous Transmission



# Repository management

This part is for people who wants to expand the code. 
Following content will provide what you need to know before adding anything to the code.
This file arrangement might not be the best one for NetSquid simulation, but it is relatively clear and reusable.
All protocols in this repository follow the same idea in terms of file arrangement:

![RepositoryManagement](https://github.com/LiaoChinTe/netsquid-simulation/blob/main/FileStructure.png)

Gray boxes are folders, other colored cells are pyhton files.
Reusable functions are located in 'lib/functions.py'.
Therefore, one must be extreamly careful modifing it.

- **function.py**

  Contains functions and Quantum Programs that are reusable. Called by *ProtocolX_partyX.py*.

- **AnyProtocol_AnyParty.py**

  A customized local protocol representing one of the party. Protocol objects here are called by *ProtocolX_main.py*.


- **AnyProtocol_run.py**

  This file contains a *AnyProtocol_run()* function that describs the hardware configurations as well as default parameters.
  It calls multiple *ProtocolX_partyX.py* to perform protocol simulation. 


- **AnyProtocol_plot.py** -optional

  A function to plot statistical results via the *AnyProtocol_run()* function in *AnyProtocol_run.py*.



## Contact
ChinTe Liao
liao.chinte@veriqloud.fr
