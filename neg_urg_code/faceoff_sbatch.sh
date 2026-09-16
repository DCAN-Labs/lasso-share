#!/bin/bash -l
#SBATCH -J faceoff
#SBATCH --mem=50gb
#SBATCH -t 04:00:00
#SBATCH --mail-type=NONE
#SBATCH -p agsmall,ag2tb
#SBATCH -o output_logs/faceoff_%A_%a.out
#SBATCH -e output_logs/faceoff_%A_%a.err
#SBATCH -A faird

module load ants
source /users/1/mccol199/.bashrc
cd /projects/standard/lewi1538/shared/projects/neg_urg/derivatives/cleaned_anats/

ID=001
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz