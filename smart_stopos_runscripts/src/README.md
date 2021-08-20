# Instructions for performing smart-stopos optimizations

In this file you can find a nitty-gritty explanation of how to use `smart-stopos`. For a more high-level overview, as well as example use cases, check out the [associated paper](https://arxiv.org/abs/2010.16373).

## Setup

In order to start using `smart-stopos`, clone [the repository](https://gitlab.com/aritoka/smart-stopos) to a directory of your choosing. You may also want to add it to your virtual environment or your python path, but this is not strictly necessary.

## Required files

The following files, all present in this directory, are required to run optimizations using `smart-stopos`:

* `input_file.ini` - This file contains all required information about the optimization - the script running the simulation, what optimization algorithm to use, what parameters to optimize, in which directory to run, etc. More details follow below.
* `run_qtoken.py` - This is the script that runs the simulation. `smart-stopos` requires that it reads the optimization parameters (T1 and T2 in this case) as command line arguments and that it outputs the simulation results to a csv file.
* `analyse_function_output.py` - Performs post-processing on simulation results, combining outcomes from several parameter sets into a single file.
* `file_parsing_tools.py` - Utility functions used by `analyse_function_output.py`.
* `run_local.sh` - Bash script used to run the optimization. Execute ./run_local.sh on a terminal to do so.
* `run.sh` - Same as above, but used when running optimizations on a computing cluster.
* `stopos.job` - Relevant only when running optimizations on a computing cluster.
* `analysis.job` - Relevant only when running optimizations on a computing cluster.

## Structure of input file

Let us now go through all the arguments passed via the `input_file.ini` file.

Arguments related to programs & directories:

* `run_program` - Here you should pass the script running the simulation, the number of optimization parameters and the names of the parameters. In this case, this results in: run_qtoken.py 2 T1 T2
* `analysis_program` - The program used to post-process the data. `analyse_function_output.py` in this case.
* `sstoposdir` - The (absolute) path to the directory where the smart-stopos directory lives in your machine.
* `workdir` - The (absolute) path to where the optimization will be performed. It's the current working directory minus `src`.
* `venvdir` - The (absolute) path to your virtual environment, if you are using one.
* `nodes` - Number of cluster nodes to use in the computation. Relevant only when running optimizations on a computing cluster.
* `queue` - What queue to submit the optimization job to. Relevant only when running optimizations on a computing cluster.
* `time_run` - Time limit to set for running the simulations. Relevant only when running optimizations on a computing cluster.
* `time_analysis` - Time limit to set for analyzing the data and producing new candidate solutions. Relevant only when running optimizations on a computing cluster.
* `files` - Which files present in the directory must be copied in order for the simulation to work. This is required because `smart-stopos` will run different iterations of the simulation in different directories. To be safe, use `*.py` to ensure that all necessary files are copied.

Arguments related to the optimization process:

* `name_project` - Name of the project.
* `description` - Description of the project.
* `run_type` - Defines whether we want to perform an optimization or a parameter scan, which optimization algorithm to use and how many iterations to perform. To perform two generations using a genetic algorithm, write: optimization GA 2. To perform a parameter scan, write: single.
* `maximum` - Defines whether a maximization (True) or minimization (False) is performed.
* `number_parameters` - Number of optimization parameters
* `number_best_candidates` - How many sets of optimization parameters should be propagated to the following generation.
* `population_size` - Number of sets of optimization parameters that constitutes a generation's population, i.e. if `population_size = 100`, 100 sets of parameters are evaluated at each generation.
* `global_scale_factor` - Optimization algorithm hyperparameter.
* `global_width_distribution` - Optimization algorithm hyperparameter.
* `proba_mutation` - Genetic algorithm hyperparameter.
* `proba_crossover` - Genetic algorithm hyperparameter.

Arguments related to the optimization parameters (should be repeated for each optimization parameter):

* `name` - Name of the parameter.
* `min` - Minimum value the parameter is allowed to take.
* `max` - Maximum value the parameter is allowed to take.
* `number_points` - Number of values of this parameter in the initial generation.
* `distribution` - How the initial values should be distributed. Either at random or unifornmly in the defined interval.
* `scale_factor` - How mutations to the parameter should be scaled. Keeping this value at 1 is recommended.
* `type` - Whether the parameter is discrete or continuous.

## Notes

* In `smart_stopos_runscripts/output` an example of the output you get after running this example can be found.
* In order to run this example as is, change the `workdir`, `venvdir` and `sstoposdir` fields defined above.
* The `population_size` parameter does not apply for the first generation. The first generation's size is instead defined by the `number_points` of the optimization parameters. For example, if the optimization to be run has 3 parameters, which have [2, 3, 5] as values of `number_points`, then the population size of the first generation will be 2 * 3 * 5 = 30. 
