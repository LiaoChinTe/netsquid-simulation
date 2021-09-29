#!/bin/bash

function read_input {
    # read general info from input file or set defaults
    opt_steps=0
    input_file=$1
    if [ $# -eq 0  ]; then
        input_file=input_file.ini #(default name)
    fi
    echo "Reading information from input file $input_file" >&2
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
    if [[ -z $run_program ]]; then
        echo "ERROR: Must provide run_program in input file" 1>&2
        exit 1
    fi
    paramnames=($(awk '/^run_program:/{if (NF != 3 + $3) exit(1); for (i=4; i <= NF ; ++i) print $i}' "$input_file"))
    if [[ -z $paramnames ]]; then
        echo "ERROR: Must provide parameters to run_program" 1>&2
        exit 1
    fi
    sstoposdir="$(awk '/^sstoposdir:/{print $2}' < $input_file)"
    if [[ -z $sstoposdir ]]; then
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
    if [[ -z $workdir ]]; then
        echo "WARNING: no workdir defined; using current directory" 1>&2
        workdir=$(echo "$PWD" | sed 's/src//')
    fi

    analysis_program="$(awk '/analysis_program/{print $2}' < $input_file)"
    if [[ -z $analysis_program ]]; then
        echo "WARNING: Are you sure no analysis_program is needed?" 1>&2
    fi
    
    files=($(awk '/files/ {for (i=2; i<=NF; i++) print $i}' < $input_file))
    if [[ -z $files ]]; then
        echo "WARNING: Are you sure no extra files are needed?" 1>&2
    fi

    run_type=$(awk '/run_type/ {print $2}' < $input_file)
    if [[ -z $paramnames ]]; then
        echo "ERROR: Must provide run_type, either single or optimization" 1>&2
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
    echo "Finish reading input"

}

function print_information {
    printf 'name run: %s\n' "$name"
    printf 'run program: %s\n' $run_program
    printf 'files needed: %s\n' ${files[@]}
    printf 'workdir: %s\n' $workdir
    printf 'sstoposdir: %s\n' $sstoposdir
    printf 'analysis_program: %s\n' $analysis_program
    printf 'run type: %s\n' $run_type
    if [[ -v $fix_variable ]]; then
        printf 'fix variables: %s\n' $fix_variables
    fi
    if [[ ! -z $venvdir ]]; then
        printf 'venv: %s\n' $venvdir
    fi
    if [[ ! -z $condaenv ]]; then
        printf 'conda: %s\n' $venvdir
    fi
}

function create_directorystructure {
    echo "Creating directory structure"
    cd $workdir
    sourcedir=$workdir/src
    outputdir=$workdir/output
    time_stamp=$(date +'%Y-%m-%d_%H.%M')
    folder_name=$name\_$time_stamp
    
    mkdir -p $outputdir
    mkdir -p $outputdir/$folder_name
    run_dir=$outputdir/$folder_name/$run_type
    mkdir -p $run_dir
    echo "Simulation will be run in : $run_dir"

}

function single_run {
    count=0
    ncores=$(lscpu|awk '/^CPU\(s\):/ {print $2}')
    echo "Number cores: " $ncores
    echo "Running program.."
    while read -a variables
        do
		let ++count
        # check number variables equal to number parameters
        if [ "${#paramnames[@]}" != "${#variables[@]}" ]; then 
            exit 1
        fi
        # uncomment if too many varibles
        printf ' --filebasename test_%s' "$count"
        # comment if too many varibles
        #printf ' --filebasename test_%s' "${variables[@]}"
		for (( j=0 ; j < "${#variables[@]}"; ++j ))
		do 
            printf ' --%s %f' "${paramnames[j]}" "${variables[j]}"
		done
        printf '\0'
    done < param_set\_0  | xargs --null -n 1 -P $ncores -I '{}' -- sh -c "python3 $run_program $fix_variables {}"
    echo "Finished program"
	echo "Starting analysis"
    python3 $analysis_program || exit
	echo "Analysis finished"
}

function optimization_run {
    ncores=$(lscpu|awk '/^CPU\(s\):/ {print $2}')
    echo "Number cores: " $ncores
    opt_steps=$[$opt_steps -1]
    for i in $(seq 0 $opt_steps)
        do
		echo "Starting simulations opt_step $i"
        # copy files to opt_step
        mkdir -p opt_step\_$i
        cp -r $input_file param_set\_$i opt_step\_$i 
        for file in "${files[@]}" 
        do 
            echo $file
            cp -r $file opt_step\_$i 
        done
        if [[ $i > 0 ]]; then
           mv duplicates.csv opt_step\_$i
        fi
        opt_name=$run_dir/opt_step\_$i
        cd $opt_name
        while read -a variables
            do
	    	let ++count
            # check number variables equal to number parameters
            if [ "${#paramnames[@]}" != "${#variables[@]}" ]; then
                 exit 1
            fi
            # uncomment if too many varibles
            printf ' --filebasename test_%s' "$count"
            # comment if too many varibles
            # printf ' --filebasename test_%s_' "${variables[@]}"
	    	for (( j=0 ; j < "${#variables[@]}"; ++j ))
	    	do 
                printf ' --%s %s' "${paramnames[j]}" "${variables[j]}"
	    	done
            printf '\0'
        done < param_set\_$i  | xargs --null -n 1 -P $ncores -I '{}' -- sh -c "python3 $run_program $fix_variables {}"
		echo "Finished running parameters opt_step_$i"
		echo "Starting analysis opt_step $i"
        python3 $analysis_program || exit
        cd $run_dir
		echo "Creating new optimized parameters from results opt_step_$i"
        create_opt_pool.py  --input_file $input_file --opt_step $i --prev_directory $opt_name 
        if [[ $i < $opt_steps ]]; then
            remove_duplicates.py --step $i
		    echo "New parameters set created"
        fi
		echo ""
    done
}

function single_run_configfile {
    count=0
    ncores=$(lscpu|awk '/^CPU\(s\):/ {print $2}')
    echo "Number cores: " $ncores
    while read -a variables
        do
	    let ++count
        # modify file
        paramfile_count=$(echo $paramfile"_"$count)
        configfile_count=$(echo $configfile"_"$count)
        cp $paramfile $paramfile_count
        printf " --paramfile %s"$paramfile_count
        printf " --configfile %s"$configfile_count
        # uncomment if too many varibles
        printf " --filebasename test_%s""$count" 
        # comment if too many varibles
        #printf ' --filebasename %s ' "${variables[@]}"
        count_var=0
		for (( j=0 ; j < "${#variables[@]}"; ++j ))
		do 
            #variablesnames=$(echo "--${paramnames[j]}" "${variables[j]}")
        #    printf ' --%s %f' "${paramnames[j]}" "${variables[j]}"
            sed -i "s/^${paramnames[j]}: .*$/${paramnames[j]}: ${variables[j]}/" $paramfile_count  # to change values accordingly inside paramfile 
		done
        #printf '\0'
        sed "s/$paramfile.*$/$paramfile_count/"  $configfile >$configfile_count                 # only changing which paramfile is used in configfile, paramfile changed by runnign program
            #sed -i "s/^$param: .*$/$param: ${variables[$count_var]}/" $configfile  # to change values inside configfile 
    done < param_set\_0 | xargs --null -n 1 -P $ncores -I '{}' -- sh -c "python3 $run_program $fix_variables {}"
    rm "${configfile}"*
    rm "${paramfile}"*
	echo "Starting analysis"
    python3 $analysis_program || exit
	echo "Analysis finished"
}

function optimization_run_configfile {
    ncores=$(lscpu|awk '/^CPU\(s\):/ {print $2}')
    echo "Number cores: " $ncores
    opt_steps=$[$opt_steps -1]
    for i in $(seq 0 $opt_steps)
        do
		echo "Starting simulations opt_step $i"
        # copy files to opt_step
        mkdir -p opt_step\_$i
        cp -r $input_file $paramfile $configfile param_set\_$i opt_step\_$i 
        if [ ! -z $files ]; then
        for file in "${files[@]}"
        do
             cp -r "$file" opt_step\_$i
        done
        fi
        if [[ $i > 0 ]]; then
           mv duplicates.csv opt_step\_$i
        fi
        opt_name=$run_dir/opt_step\_$i
        cd $opt_name
        while read -a variables
            do
	        let ++count
            # uncomment if too many varibles
            # comment if too many varibles
            # printf ' --filebasename test_%s_ ' "${variables[@]}"
            # modify file
            configfile_count=$(echo $configfile"_"$count)
            paramfile_count=$(echo $paramfile"_"$count)
            cp $paramfile $paramfile_count
            printf " --configfile %s"$configfile_count
            printf " --paramfile %s"$paramfile_count
            printf ' --filebasename test_%s' "$count" 
            count_var=0
            for param in "${paramnames[@]}"
            do
                sed -i "s/$paramfile.*$/$paramfile_count/"  $configfile 
                sed -i "s/^$param .*$/$param ${variables[$count_var]}/"  $configfile 
                let ++count_var
            done
            cat $configfile > $configfile_count
		    for (( j=0 ; j < "${#variables[@]}"; ++j ))
	    	do 
                #printf ' --%s %f' "${paramnames[j]}" "${variables[j]}"
                sed -i "s/^${paramnames[j]}: .*$/${paramnames[j]}: ${variables[j]}/" $paramfile_count  
            done
            #printf '\0'
            done < param_set\_$i  | xargs --null -n 1 -P $ncores -I '{}' -- sh -c "python3 $run_program $fix_variables {}"
        rm "${configfile}"*
        rm "${paramfile}"*
        echo "Finished running parameters opt_step_$i"
		echo "Starting analysis opt_step $i"
        python3 $analysis_program || exit
        cd $run_dir
		echo "Creating new optimized parameters from results opt_step_$i"
        create_opt_pool.py  --input_file $input_file --opt_step $i --prev_directory $opt_name 
        if [[ $i < $opt_steps ]]; then
            remove_duplicates.py --step $i
		    echo "New parameters set created"
        fi
    done
}

#======================main=========================
read_input $1
print_information

# Setting system variables
export PYTHONPATH=$PYTHONPATH:$sstoposdir
export PATH=$PATH:$sstoposdir/smartstopos/pools
export PATH=$PATH:$sstoposdir/smartstopos/duplicates

if [[ -v $venvdir ]]; then
		source $venvdir/activate
fi

if [[ -v $condaenv ]]; then
        # For Cartesius
		module load 2019
        module load Miniconda3
        conda activate $condaenv
fi

# create directory structure 
create_directorystructure

# copy files to rundir and go into it
cp -r $sourcedir/$input_file $run_dir
cp -r $sourcedir/$paramfile $run_dir
cp -r $sourcedir/$configfile $run_dir
for file in "${files[@]}"
    do 
        cp -r $sourcedir/$file $run_dir 
   done
   
cd $run_dir

# create initial set of parameters
create_initial_pool.py  --input_file $input_file || exit 
echo "Initial set of parameter created: param_set_0"
echo $run_type
echo $configfile

if [ -z "$configfile" ]; then
    time_stamp=$(date +'%Y-%m-%d_%H.%M.%S')
    echo "Simulation started at $time_stamp"
    if [[ "$run_type" == "single" ]]; then
        echo "Performing single run"
        single_run
    fi 
    
    if [[ "$run_type" == "optimization" ]]; then
        echo "Performing optimization"
        optimization_run
    fi
else
    time_stamp=$(date +'%Y-%m-%d_%H.%M.%S')
    echo $time_stamp
    if [[ "$run_type" == "single" ]]; then
        echo "Performing single run; config file"
        single_run_configfile
    fi 
    
    if [[ "$run_type" == "optimization" ]]; then
        echo "Performing optimization; config file"
        optimization_run_configfile
    fi
fi
time_stamp=$(date +'%Y-%m-%d_%H.%M.%S')
echo "Simulation finished at $time_stamp"
