#!/bin/bash -l
#SBATCH -J faceoff
#SBATCH --mem=50gb
#SBATCH -t 04:00:00
#SBATCH --mail-user=mccol199@umn.edu
#SBATCH --mail-type=ALL
#SBATCH -p agsmall,ag2tb
#SBATCH -o output_logs/faceoff_%A_%a.out
#SBATCH -e output_logs/faceoff_%A_%a.err
#SBATCH -A btervocl

module load ants
source /users/1/mccol199/.bashrc
cd /projects/standard/lewi1538/shared/projects/neg_urg/derivatives/cleaned_anats/

ID=NU005
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU007
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU008
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU009
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU010
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU011
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU0013
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU014
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU015
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU016
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU018
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU019
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU020
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz

ID=NU024
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T1w.nii.gz
PadsOff -i sub-${ID}_ses-1/sub-${ID}_ses-1_run-01_T2w.nii.gz