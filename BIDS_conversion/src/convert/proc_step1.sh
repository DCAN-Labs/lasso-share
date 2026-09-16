#!/bin/bash -l

#SBATCH -J PIP_proc1
#SBATCH -c 24
#SBATCH --mem=50G
#SBATCH -t 8:00:00
#SBATCH --mail-type=NONE
#SBATCH -p msismall
#SBATCH -o output_logs/PIP_proc1_%A_%a.out
#SBATCH -e output_logs/PIP_proc1_%A_%a.err
#SBATCH -A faird

singularity=`which singularity`
source /projects/standard/faird/shared/code/external/envs/miniconda3/load_miniconda3.sh
conda activate py11

SUB=${1}
SES=${2}

#set up directories
PARENT=/projects/standard/moser297/shared/projects/PIP
rawbids_dir=${PARENT}/bids
fmriprep_in_dir=${PARENT}/derivatives/nordic

#make nordic cmds
echo python /projects/standard/faird/shared/code/internal/utilities/cdniproc/tools/make_nordic_cmds_dev.py ${rawbids_dir}/sub-${SUB}/ses-${SES}/func/
python /projects/standard/faird/shared/code/internal/utilities/cdniproc/tools/make_nordic_cmds_dev.py ${rawbids_dir}/sub-${SUB}/ses-${SES}/func/

#mv to summaries dir
echo 'mv' ${PARENT}/nordic_cmd_sub-${SUB}_ses-${SES}.sh ${PARENT}/summaries/.
mv ${PARENT}/nordic_cmd_sub-${SUB}_ses-${SES}.sh ${PARENT}/summaries/.

echo 'make derivatives/nordic' folder
if [ ! -d ${fmriprep_in_dir} ]; then
  mkdir -p ${fmriprep_in_dir}
fi 

declare -a JOBIDS=()
echo 'submit NORDIC jobs'
nordicfile=${PARENT}/summaries/nordic_cmd_sub-${SUB}_ses-${SES}.sh
while IFS= read -r line; do
	#echo $line
	$line
done < "$nordicfile"


if [ ${#JOBIDS[@]} -eq 0 ]; then
        echo "All Permutations already run. No jobs were submitted. Exiting and moving on to figure making."
        # If you need to exit script entirely, uncomment the next line
        # exit 0
    else
        # Function to check the completion status of a job using sacct
        check_job_completion() {
            local job=$1
            jobState=$(sacct -j $job --format=State --noheader | head -n 1 | awk '{print $1}')
        
            if [[ $jobState =~ ^(COMPLETED|FAILED|CANCELLED)$ ]]; then
                return 1 # Job is completed (no longer running)
            else
                return 0 # Job is still running
            fi        }

        # Wait for all jobs to complete
        ALL_DONE=0
        while [ $ALL_DONE -eq 0 ]; do
            ALL_DONE=1
            for JOBID in "${JOBIDS[@]}"; do
                check_job_completion $JOBID
                if [ $? -eq 0 ]; then
                    echo "Waiting for job $JOBID to complete..."
                    ALL_DONE=0
                    sleep 60
                    break # Exit the for loop and wait before checking again
                fi
            done
        done

        echo "All SPLITPCT perm jobs completed"

    fi

#combine sessions
#run post nordic
#set IntendedFors