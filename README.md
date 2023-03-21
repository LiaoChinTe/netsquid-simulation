# NetSquid Protocols
This repository introduces several quantum protocol simulations which could be used in quantum communication related studies.
This document does not only explain how the code was arranged, but also concludes what protocol simulations has been developed and ready to be applied for research as long as proper parameters are given.

Protocols in this repository are simulated via [NetSquid](https://netsquid.org/)
More information about quantum protocols: [Quantum Protocol Zoo](https://wiki.veriqloud.fr/index.php?title=Protocol_Library).





# How to use

Simulations are usually launched by a python scripts in *./script/*. Usually named *AnyProtocol_main.py*. This file is also in charge of how many times we run such a protocol and what value to output from the simulation.  
The full hardware configurations can be edited in *AnyProtocol_run.py* in each protocol folder.
Normally, there's no need for users to modify other files than above two.
Common functions shared by multiple protocols are located in lib/functions.py, which can be further expanded. However modifying existing functions is not recommended since that might influence existing protocol.




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
- Multiclient blind quantum computation with Qline architecture

## Anonymous Transmission
- W-state Anonymous Transmission



# Repository management

This part is for people who want to expand the code. 
Following content will provide what you need to know before adding anything to the code.
This file arrangement might not be the best one for NetSquid simulation, but it is relatively clear and reusable.
All protocols in this repository follow the same idea in terms of file arrangement:

![RepositoryManagement](https://github.com/LiaoChinTe/netsquid-simulation/blob/main/FileStructure.png)

Gray boxes are folders, other colored cells are python files.
Reusable functions are located in 'lib/functions.py'.
Therefore, one must be extremely careful modifying it.


- **function.py**

  Contains functions and Quantum Programs that are reusable. Functions here are usually called by *AnyProtocol_AnyParty.py* in protocol folders.

- **AnyProtocol_AnyParty.py**

  A customized local protocol representing one of the parties.(As an object) Such objects are called by *AnyProtocol_run.py*.


- **AnyProtocol_run.py**

  This file contains a *AnyProtocol_run()* function which describs the hardware configurations as well as default parameters.
  It calls multiple *AnyProtocol_AnyParty.py* to perform protocol simulation. 


- **AnyProtocol_plot.py** -optional

  Contains a function to plot statistical results via the *AnyProtocol_run()* function in *AnyProtocol_run.py*.


# Reference
- [NetSquid](https://netsquid.org/)
- [Quantum Protocol Zoo](https://wiki.veriqloud.fr/index.php?title=Protocol_Library)

## Contact
ChinTe Liao
liao.chinte@veriqloud.fr
