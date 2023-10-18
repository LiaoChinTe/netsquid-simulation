# Implementation notes
This document lists the essential steps to run smart-stopos, a tool which enable us to do backward simulation on NetSquid via regression.   
Assuming that a proper Python version(Python3) is already applied, and NetSquid installed.


## 1. Clone the smart-stopos repo
The core of smart-stopos is not included in this repository. 
One must clone one from [here](https://gitlab.com/aritoka/smart-stopos). 


## 2. Indicate essential file locations

Edit the following file:
 `.../netsquid-simulation/smart_stopos_runscripts/src/input_file.ini`

```
sstoposdir: /.../smart-stopos/   # The directory of the repo downloaded in the first step. 
workdir: /.../netsquid-simulation/smart_stopos_runscripts # The directory of this repo.
venvdir: # The directory of your virtual environment, or leave it empty.
```

## 3. Assign `number_points` & `population_size`

In the file:
 `.../netsquid-simulation/smart_stopos_runscripts/src/input_file.ini`
Parameter `population_size` in the GENERAL section is easy to cause errors if given a wrong value. It need to be percisely assigned as the multiplication of `number_points` values of each parameter. For example, if I have two parameters which has `number_points` values of [5,10], my `population_size` would need to be 5*10=50.


## 3. Export the launching function

During the regression procedure, the smart-stopos creates subfolders for optimization based on previous results. The new simulation launcher would have trouble locating the source file due to the constant changing of relative location. Therefore we need the following procedure to make sure the source can be always found by smart-stopos procedures.

In directory: `.../netsquid-simulation/smart_stopos_runscripts/src`
Type command:
`export PYTHONPATH="$PYTHONPATH:/.../netsquid-simulation/QToken/"`

replace `...` to your own path.




## 4. Launch the simulation

Simply run the file `run_local.sh` in directory: `.../netsquid-simulation/smart_stopos_runscripts/src`.
Output results can be found in `.../netsquid-simulation/smart_stopos_runscripts/output/`.

replace `...` to your own path.
