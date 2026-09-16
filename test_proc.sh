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
#SBATCH -A lewi1538

singularity=`which singularity`

SUB=${1}
SES=${2}

#set up directories
PARENT=/home/lewi1538/shared/projects/neg_urg
dcm_dir=${PARENT}/dicoms/${SUB}/
rawbids_dir=${PARENT}/bids
fmriprep_in_dir=${PARENT}/derivatives/nordic

#run init
echo python /home/faird/shared/code/internal/utilities/cdniproc/init_dev.py -p ${SUB} -s ${SES} -d ${dcm_dir} --jsononly
python /home/faird/shared/code/internal/utilities/cdniproc/init_dev.py -p ${SUB} -s ${SES} -d ${dcm_dir} --jsononly

#mv to summaries dir
echo 'mv' ${SUB}* summaries/.
mv ${SUB}* summaries/.

#sync full dicom directory
#echo s3cmd sync --recursive --no-check-md5 --skip-existing ${dcm_s3_dir} ${dcm_scratch_dir}
#s3cmd sync --recursive --no-check-md5 --skip-existing ${dcm_s3_dir} ${dcm_scratch_dir}

#run_dcm2bids3
echo python /home/faird/shared/code/internal/utilities/cdniproc/dcm2bids3_dev.py -f ${PARENT}/summaries/${SUB}.tsv -d ${dcm_dir} --all 
python /home/faird/shared/code/internal/utilities/cdniproc/dcm2bids3_dev.py -f summaries/${SUB}.tsv -d ${dcm_dir} --all

#make nordic cmds
echo python /home/faird/shared/code/internal/utilities/cdniproc/tools/make_nordic_cmds_dev.py ${rawbids_dir}/sub-${SUB}/ses-${SES}/func/
python /home/faird/shared/code/internal/utilities/cdniproc/tools/make_nordic_cmds_dev.py ${rawbids_dir}/sub-${SUB}/ses-${SES}/func/

#mv to summaries dir
echo 'mv' ${PARENT}/nordic_cmd_sub-${SUB}_ses-${SES} ${PARENT}/summaries/.
mv ${PARENT}/nordic_cmd_sub-${SUB}_ses-${SES} ${PARENT}/summaries/.

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


#combine sessions
#set IntendedFors
