#!/bin/bash -l
#SBATCH -J prebibsnet
#SBATCH -p a100-4     
#SBATCH --gres=gpu:a100:1
#SBATCH --ntasks=1
#SBATCH --mem=50gb
#SBATCH -t 04:00:00
#SBATCH --mail-user=mccol199@umn.edu
#SBATCH --mail-type=ALL
#SBATCH --tmp=100gb
#SBATCH -o logs/prebibsnet_%A.out
#SBATCH -e logs/prebibsnet_%A.err
#SBATCH -A joh03032

input_dir=/home/csandova/shared/projects/rae_neonatal/bids
output_path=/home/csandova/shared/projects/rae_neonatal/prebibsnet

if [ ! -d ${output_path}/${subject} ]; then
	mkdir -p ${output_path}/${subject}
fi

## load dependencies
module load singularity
singularity=`which singularity`

## Run prebibsnet to skull strip and resize images
env -i ${singularity} run \
-B ${input_dir}:/input \
-B ${output_path}/${subject}:/output \
-B /home/csandova/shared/projects/rae_neonatal/code/nnunet_wrapper/license.txt:/opt/freesurfer/license.txt \
/projects/standard/faird/shared/code/internal/pipelines/bibsnet_container/bibsnet_v3.4.1.sif \
/input /output participant -v -end prebibsnet -w ${output_path}/${subject}
