#!/bin/sh

# load module, create pool
module purge
module load 2019
module load Stopos/0.93-GCC-7.3.0-2.30

function read_input {
    # read general info from input file or set defaults
    opt_steps=0
    input_file=$1
    if [ $# -eq 0  ]; then
        input_file=input_file.ini #(default name)
    fi
    echo "Reading information from input file"
    nodes="$(awk '/nodes:/ {print $2}' < $input_file)"
    configfile="$(awk '/configfile:/ {print $2}' < $input_file)"
    paramfile="$(awk '/paramfile:/ {print $2}' < $input_file)"
    timerun="$(awk '/time_run:/ {print $2}' < $input_file)"
    timeanal="$(awk '/time_analysis:/ {print $2}' < $input_file)"
    queue="$(awk '/queue/ {print $2}' < $input_file)"
    fix_variables="$(awk '/fix_variables:/{$1=""; print $0}' < $input_file)"
    name=$(awk  '/name/ {for (i=2; i<=NF; i++) print $i}'< $input_file)
    description=$(awk '/description/ {for (i=2; i<=NF; i++) print $i}' < $input_file)
    venvdir="$(awk '/^venvdir:/{print $2; exit}' < $input_file)"
    condaenv="$(awk '/^condaenv:/{print $2}'< $input_file)"
    run_program="$(awk '/^run_program:/{print $2}' < $input_file)"
    if [[ -z $nodes ]]; then
        nodes=1
    fi
    if [[ -z $run_program ]]; then
        echo "ERROR: Must provide run_program in input file" 1>&2
        exit 1
    fi
    paramnames=($(awk '/^run_program:/{if (NF != 3 + $3) exit(1); for (i=4; i <= NF ; ++i) print $i}' "$input_file"))
    if [ -z $paramnames ]; then
        echo "ERROR: Must provide parameters to run_program" 1>&2
        exit 1
    fi
    sstoposdir="$(awk '/^sstoposdir:/{print $2}' < $input_file)"
    if [ -z $sstoposdir ]; then
        echo "WARNING: no sstoposdir defined; looking for repo in system" 1>&2
        sstoposdir=$(find ~/ -name ".git" | grep "smart-stopos\/" | sed "s/.git//")
        if [[ -z $sstoposdir ]]; then
            echo "No smart-stopos repository found" 1>&2
            exit 1
        fi
        # TODO: add error for when more than one repo found! Pipe it through wc?
        echo "Repo found at $sstoposdir"
    fi
    workdir="$(awk '/workdir:/ {print $2}' < $input_file )"
    if [ -z $workdir ]; then
        echo "WARNING: no workdir defined; using current directory" 1>&2
        workdir=$(echo "$PWD" | sed 's/src//')
        echo $workdir
    fi
    analysis_program="$(awk '/analysis_program/{print $2}' < $input_file)"
    if [ -z $analysis_program ]; then
        echo "WARNING: Are you sure no analysis_program is needed?" 1>&2
    fi
    
    files=($(awk '/files/ {for (i=2; i<=NF; i++) print $i}' < $input_file))
    if [[ -z $files ]]; then
        echo "WARNING: Are you sure no extra files are needed?" 1>&2
    fi
    run_type=$(awk '/run_type/ {print $2}' < $input_file)
    if [[ -z $run_type ]]; then
        echo "ERROR: Must provide run_type" 1>&2
        exit 1
    fi
    
    if [[ "$run_type" == "optimization" ]]; then
        algorithm=$(awk '/run_type/ {print $3}' < $input_file)
        opt_steps=$(awk '/run_type/ {print $4}' < $input_file)
        if [[ -z $algorithm || -z $opt_steps ]]; then
            echo "ERROR: Must provide algorithm and opt_steps in the run_type" 1>&2
            echo "eg. run_type: optimization GA 3" 1>&2
            exit 1
        fi
    fi
    if [ ! -z $timerun ]; then
        echo "changing stopos time"
        sed -i "s/time=.*/time=$timerun/" stopos.job
    fi
    
    if [ ! -z $timeanal ]; then
        sed -i "s/time=.*/time=$timeanal/" analysis.job
    fi
    echo "Finish reading input"
}

function print_information {
    echo "Printing simulation info"
    printf 'name run: %s\n' "$name"
    printf 'run program: %s\n' $run_program
    #printf 'files needed: %s\n' ${files[@]}
    printf 'workdir: %s\n' $workdir
    printf 'files needed: %s\n' $files
    printf 'sstoposdir: %s\n' $sstoposdir
    printf 'analysis_program: %s\n' $analysis_program
    printf 'run type: %s\n' $run_type
    if [[ ! -z $fix_variable ]]; then
        printf 'fix variables: %s\n' $fix_variables
    fi
    if [[ ! -z $venvdir ]]; then
        printf 'venv: %s\n' $venvdir
    elif [[ ! -z $condaenv ]]; then
        printf 'conda: %s\n' $condaenv
    fi
}

function create_directorystructure {
    echo "Creating directory structure"
    cd $workdir
    echo $workdir
    sourcedir=$workdir/src
    outputdir=$workdir/output
    time_stamp=$(date +'%Y-%m-%d_%H.%M')
    folder_name=$name\_$time_stamp
    
    mkdir -p $outputdir
    cd $sourcedir
    time_stamp=$(date +'%Y-%m-%d_%H.%M')
    folder_name=$name\_$time_stamp
    #folder_name=$name
    tmp_dir="$(mktemp -d -p /scratch-shared)"
    tmp_rundir=$tmp_dir/$folder_name
    mkdir $tmp_rundir
    run_dir=$tmp_dir/$folder_name/$run_type
    mkdir $run_dir
    echo "Simulation will be run in : $run_dir"
}

# arguments #nodes #opt_step
function submit_stopos_init {
    echo "submitting stopos"
    J_ID="$(sbatch --export=ALL,pool=$pool,node=$1,input_file=$input_file stopos.job| awk '{print $4}')"
    echo $J_ID >> $outputdir/jobs_ids_$folder_name
}

# arguments dependency nodes opt_step
function submit_stopos {
    echo "stopos dependency $1"
    J_ID="$(sbatch --dependency=afterok:$1 --export=ALL,pool=$pool,node=$2,queue=$queue,input_file=$input_file stopos.job | awk '{print $4}')"
    echo $J_ID >> $outputdir/jobs_ids_$folder_name
}

#arguments dependency opt_step,
function submit_analysis {
     echo "analysis dependency: $1" 
     J_ID="$(sbatch --dependency=afterok:$1 --export=ALL,input_file=$input_file,foldername=$folder_name,optstep=$2,tmpdir=$tmp_dir,pool=$pool,output=$outputdir,workdir=$workdir,optsteps=$opt_steps,sjobid=$J_ID analysis.job | awk '{print $4}')"
    echo $J_ID >> $outputdir/jobs_ids_$folder_name
}

function submit_analysis_array {
     echo "analysis dependency: $1" 
     J_ID="$(sbatch --dependency=afterok$1 --export=ALL,input_file=$input_file,foldername=$folder_name,optstep=$2,tmpdir=$tmp_dir,pool=$pool,output=$outputdir,workdir=$workdir,optsteps=$opt_steps,sjobid=$J_ID analysis.job | awk '{print $4}')"
    echo $J_ID >> $outputdir/jobs_ids_$folder_name
}


function single_run {
    if [[ $nodes == 1 ]]; then
        submit_stopos_init $nodes
        submit_analysis $J_ID 0
    elif [[ $nodes -gt 1 ]]; then
        for j in $(seq 1 $nodes)
        do
            submit_stopos_init $j
            array_jobids="${array_jobids}:${J_ID}"
        done
        echo "Jobs array: ${array_jobids[@]}"
        submit_analysis_array $array_jobids 0
    fi
}

function optimization_run {
    #opt_steps=$[$opt_steps -1]
    if [[ $nodes == 1 ]]; then
        for i in $(seq 0 $opt_steps)
        do
            # make directories structure
            mkdir -p opt_step\_$i
            opt_name=$run_dir/opt_step\_$i
            for file in "${files[@]}"
            do 
                cp -r $file $opt_name
                #echo "cp -r $file $opt_name"
            done
            cp $input_file stopos.job analysis.job $run_program $opt_name
            echo "Files copied to opt_step_$i"
            cd $opt_name
    	    if [[ $i == 0 ]]; then
                submit_stopos_init $nodes
                submit_analysis $J_ID $i
   		    elif [[ $i > 0 ]]; then
                submit_stopos $J_ID $nodes
                submit_analysis $J_ID $i
           fi
           cd $run_dir
        done

    elif [[ $nodes -gt 1 ]]; then
        for i in $(seq 0 $opt_steps)
        do
            # make directories structure
            mkdir -p opt_step\_$i
            opt_name=$run_dir/opt_step\_$i
            for file in "${files[@]}"
            do 
                cp -r $file $opt_name
                #echo "cp -r $file $opt_name"
            done
            cp -r $input_file stopos.job analysis.job $run_program $opt_name
            echo "Files copied to opt_step_$i"
            cd $opt_name
            if [[ $i == 0 ]]; then
                for j in $(seq 1 $nodes)
                do 
                    submit_stopos_init $j
                    array_jobids="${array_jobids}:${J_ID}"
                done
                submit_analysis_array $array_jobids $i
                unset array_jobids
   	        elif [[ $i > 0 ]]; then
                J_ID_analysis=$J_ID
                for j in $(seq 1 $nodes)
                do 

                    submit_stopos $J_ID_analysis $nodes
                    array_jobids="${array_jobids}:${J_ID}"
                done
                submit_analysis_array $array_jobids $i
                unset array_jobids
            fi
            cd $run_dir
        done
    fi
}

function single_run_configfile {
    if [[ $nodes == 1 ]]; then
        submit_stopos_init $nodes
        submit_analysis $J_ID 0
    elif [[ $nodes -gt 1 ]]; then
        for j in $(seq 1 $nodes)
        do
            submit_stopos_init $j
            array_jobids="${array_jobids}:${J_ID}"
        done
        echo "Jobs array: ${array_jobids[@]}"
        submit_analysis_array $array_jobids 0
    fi
}

function optimization_run_configfile {
    #opt_steps=$[$opt_steps -1]
    if [[ $nodes == 1 ]]; then
        for i in $(seq 0 $opt_steps)
        do
            # make directories structure
            mkdir -p opt_step\_$i
            opt_name=$run_dir/opt_step\_$i
            for file in "${files[@]}"
            do 
                cp -r $file $opt_name
            done
            cp $input_file $paramfile $configfile $run_program stopos.job analysis.job $opt_name
            echo "Files copied to opt_step_$i"
            cd $opt_name
    	    if [[ $i == 0 ]]; then
                submit_stopos_init $nodes
                submit_analysis $J_ID $i
   		    elif [[ $i > 0 ]]; then
                submit_stopos $J_ID $nodes
                submit_analysis $J_ID $i
           fi
           cd $run_dir
        done

    elif [[ $nodes -gt 1 ]]; then
        for i in $(seq 0 $opt_steps)
        do
            # make directories structure
            mkdir -p opt_step\_$i
            opt_name=$run_dir/opt_step\_$i
            for file in "${files[@]}"
            do 
                cp -r $file $opt_name
            done
            cp $input_file $paramfile $configfile $run_program stopos.job analysis.job $opt_name
            echo "Files copied to opt_step_$i"
            cd $opt_name
            if [[ $i == 0 ]]; then
                J_ID_analysis=$J_ID
                for j in $(seq 1 $nodes)
                do 
                    submit_stopos_init $J_ID_analysys $nodes
                    array_jobids="${array_jobids}:${J_ID}"
                done
                submit_analysis_array $array_jobids $i
                unset array_jobids
   	        elif [[ $i > 0 ]]; then
                for j in $(seq 1 $nodes)
                do 
                    submit_stopos $j
                    array_jobids="${array_jobids}:${J_ID}"
                done
                submit_analysis_array $array_jobids $i
                unset array_jobids
            fi
            cd $run_dir
        done
    fi
}

#======================main=========================
read_input $1
print_information

# Setting system variables
export PYTHONPATH=$PYTHONPATH:$sstoposdir
export PATH=$PATH:$sstoposdir/smartstopos/pools
export PATH=$PATH:$sstoposdir/smartstopos/duplicates

if [[ ! -z $venvdir ]]; then
        echo "sourcing venv"
		source $venvdir/activate
fi
if [[ ! -z $condaenv ]]; then
        echo "activating conda"
        # For Cartesius
		module load 2019
        module load Miniconda3
        conda activate $condaenv
fi

# create directory structure 
create_directorystructure
echo "sourcedir $sourcedir"
echo "tmpdir $tmp_dir"
echo "rundir $run_dir"

# copy files to rundir and go into it
cp -r $sourcedir/$input_file  $run_dir
cp -r $sourcedir/analysis.job  $run_dir
cp -r $sourcedir/stopos.job  $run_dir
for file in "${files[@]}"
    do 
        cp -r $sourcedir/$file $run_dir 
   done
   
echo "Files copied to running directory: $run_dir"
echo $tmp_rundir $name $pool >> $outputdir/running_directory_$folder_name
cd $run_dir

pool=$RANDOM
stopos create -p $pool
echo "Stopos pool $pool created"
create_initial_pool.py  --input_file $input_file || exit 
echo "Initial set of parameter created: param_set_0"
stopos -p $pool add param_set_0
echo "Parameters in param_set_0 added to pool $pool"

time_stamp=$(date +'%Y-%m-%d_%H.%M.%S')
echo "Simulations started at $time_stamp"

if [ -z "$configfile" ]; then
    if [[ "$run_type" == "single" ]]; then
        echo "Performing single run"
        single_run
    fi 
    
    if [[ "$run_type" == "optimization" ]]; then
        echo "Performing optimization"
        optimization_run
    fi
else
    if [[ "$run_type" == "single" ]]; then
        echo "Performing single run; config file"
        cp -r $sourcedir/$paramfile $run_dir
        cp -r $sourcedir/$configfile $run_dir
        single_run_configfile
    fi 
    
    if [[ "$run_type" == "optimization" ]]; then
        echo "Performing optimization; config file"
        cp -r $sourcedir/$paramfile $run_dir
        cp -r $sourcedir/$configfile $run_dir
        optimization_run_configfile
    fi
fi
echo "All jobs submitted; jobids stored in jobs_ids file; information about
running directory in runnning_directory file"
