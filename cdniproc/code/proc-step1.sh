#!/bin/bash -l

#SBATCH -J proc1
#SBATCH -c 24
#SBATCH --mem=500G
#SBATCH -t 12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kweldon@umn.edu
#SBATCH -p ag2tb,agsmall,aglarge
#SBATCH -o output_logs/proc1_%A_%a.out
#SBATCH -e output_logs/proc1_%A_%a.err
#SBATCH -A nardosr

singularity=`which singularity`

SUB=${1}
SES=${2}

#set up directories
PARENT=/scratch.global/kweldon/test
dcm_s3_dir=s3://subpop/dicoms/${SUB}-ses${SES}/
dcm_scratch_dir=${PARENT}/dicoms/${SUB}-ses${SES}/
rawbids_dir=${PARENT}/bids
fmriprep_in_dir=${PARENT}/derivatives/nordic

#run init
echo python /projects/standard/faird/shared/code/internal/utilities/cdniproc/init_dev.py -p ${SUB} -s ${SES} -d ${dcm_scratch_dir} --jsononly
python /projects/standard/faird/shared/code/internal/utilities/cdniproc/init_dev.py -p ${SUB} -s ${SES} -d ${dcm_scratch_dir} --jsononly

#mv to summaries dir
echo 'mv' ${SUB}-ses${SES}* summaries/.
mv ${SUB}-ses${SES}* summaries/.

#sync full dicom directory
echo s3cmd sync --recursive --no-check-md5 --skip-existing ${dcm_s3_dir} ${dcm_scratch_dir}
s3cmd sync --recursive --no-check-md5 --skip-existing ${dcm_s3_dir} ${dcm_scratch_dir}

#run_dcm2bids3
echo python /projects/standard/faird/shared/code/internal/utilities/cdniproc/dcm2bids3_dev.py -f ${PARENT}/summaries/${SUB}-ses${SES}.tsv -d ${dcm_scratch_dir} --all 
python /projects/standard/faird/shared/code/internal/utilities/cdniproc/dcm2bids3_dev.py -f summaries/${SUB}-ses${SES}.tsv -d ${dcm_scratch_dir} --all

#make nordic cmds
echo python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/tools/make_nordic_cmds_dev.py ${rawbids_dir}/sub-${SUB}/ses-${SES}/func/
python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/tools/make_nordic_cmds_dev.py ${rawbids_dir}/sub-${SUB}/ses-${SES}/func/

#mv to summaries dir
echo 'mv' ${PARENT}/nordic_cmd_sub-${SUB}_ses-${SES} ${PARENT}/summaries/.
mv ${PARENT}/nordic_cmd_sub-${SUB}_ses-${SES} ${PARENT}/summaries/.

echo 'make derivatives/nordic' folder
if [ ! -d ${fmriprep_in_dir} ]; then
  mkdir -p ${fmriprep_in_dir}
fi 

declare -a JOBIDS=()
echo 'submit NORDIC jobs'
nordicfile=${PARENT}/summaries/nordic_cmd_sub-${SUB}_ses-${SES}
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
#set IntendedFors
