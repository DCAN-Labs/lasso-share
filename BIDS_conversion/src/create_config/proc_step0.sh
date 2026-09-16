#!/bin/bash -l

#SBATCH -J PIP_proc0
#SBATCH -c 24
#SBATCH --mem=50G
#SBATCH -t 8:00:00
#SBATCH --mail-type=NONE
#SBATCH -p msismall
#SBATCH -o output_logs/PIP_proc0_%A_%a.out
#SBATCH -e output_logs/PIP_proc0_%A_%a.err
#SBATCH -A faird

singularity=`which singularity`
source /projects/standard/faird/shared/code/external/envs/miniconda3/load_miniconda3.sh
conda activate py11

SUB=${1}
SES=${2}

#set up directories
PARENT=/projects/standard/moser297/shared/projects/PIP
#dcm_s3_dir=s3://subpop/dicoms/${SUB}-ses${SES}/
dcm_dir=${PARENT}/data/DICOMs/${SUB}/${SUB}_ses${SES}/
rawbids_dir=${PARENT}/bids
fmriprep_in_dir=${PARENT}/derivatives/nordic

#run init
echo python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/init.py -p ${SUB} -s ${SES} -d ${dcm_dir} --jsononly
python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/init.py -p ${SUB} -s ${SES} -d ${dcm_dir} --jsononly


#alternate path
#dcm2bids_helper -d data/DICOMs/MN0002/MN0002_sesV1PFM1 -o helper/MN0002_sesV1PFM1
#python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/nii_to_tsv_gpt4.py -p ${SUB} -s ${SES} ${nii_dir} #nii_dir: helper/MN0002_sesV1PFM1/tmp_dcm2bids/helper/
#python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/tsv_to_json.py {subj.tsv}

# Check if there's an "imagetype" field in the json, if so remove
jq 'del(.. | .ImageType?)' ${SUB}_ses${SES}.json > tmp.json && mv tmp.json ${SUB}_ses${SES}.json

#mv to summaries dir
echo 'mv' ${SUB}_ses${SES}* summaries/.
mv ${SUB}_ses${SES}* summaries/.

#sync full dicom directory
#echo s3cmd sync --recursive --no-check-md5 --skip-existing ${dcm_s3_dir} ${dcm_scratch_dir}
#s3cmd sync --recursive --no-check-md5 --skip-existing ${dcm_s3_dir} ${dcm_scratch_dir}

#run_dcm2bids3
echo python /projects/standard/faird/shared/code/internal/utilities/cdniproc/dcm2bids3_dev.py -f summaries/${SUB}_ses${SES}.tsv -d ${dcm_dir} --all 
python /projects/standard/faird/shared/code/internal/utilities/cdniproc/dcm2bids3_dev.py -f summaries/${SUB}_ses${SES}.tsv -d ${dcm_dir} --all

#mv bids folder
echo 'make bids ses' folder
if [ ! -d ${PARENT}/bids/sub-${SUB} ]; then
  mkdir -p ${PARENT}/bids/sub-${SUB}
fi 
mv bids/sub-${SUB}/ses-${SES} ${PARENT}/bids/sub-${SUB}/.