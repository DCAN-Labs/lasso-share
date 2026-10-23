#!/bin/bash -l
#SBATCH -J MRIQC
#SBATCH -c 12
#SBATCH --mem=900G
#SBATCH -t 4:00:00
#SBATCH -p ag2tb
#SBATCH -A smnelson
# SBATCH --mail-type=FULL
# SBATCH --mail-user=kweldon@umn.edu

echo 'Start'
module load singularity

RAM=870 # upper bound RAM memory limit

SUB=${1}
SES=${2}
subj_id=sub-${SUB}

data_dir=/projects/standard/smnelson/shared/projects/request/bids/
echo 'bidsdir: ' ${data_dir}
output_dir=//projects/standard/smnelson/shared/projects/request/mriqc/output/${SUB}/
echo 'outdir: ' ${output_dir}
work_dir=/projects/standard/smnelson/shared/projects/request/bids/mriqc/work_dir/${SUB}/
echo 'workdir: ' ${work_dir}


mkdir -p $output_dir
mkdir -p $work_dir

sif_img=/projects/standard/faird/shared/code/external/utilities/mriqc/mriqc_latest.sif

# run MRIQC pipeline
singularity run --cleanenv \
-B ${data_dir}:/bids_dir \
-B ${output_dir}:/output_dir \
-B ${work_dir}:/wd \
${sif_img} \
/bids_dir /output_dir participant --participant-label ${SUB} \
--ants-nthreads 8 \
--nprocs 12 \
--mem_gb $RAM \
-vv \
--verbose-reports \
-w /wd \
-m T1w T2w bold dwi

echo 'End'