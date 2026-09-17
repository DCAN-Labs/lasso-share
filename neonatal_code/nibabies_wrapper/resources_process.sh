#!/bin/bash -l
#SBATCH -J nibabies
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH -c 7
#SBATCH --mem=240G
#SBATCH -t 12:00:00
#SBATCH -p agsmall,aglarge,ag2tb
#SBATCH --mail-user=mccol199@umn.edu
#SBATCH --mail-type=ALL
#SBATCH --tmp=200gb
#SBATCH -p msismall
#SBATCH -o output_logs/nibabies_%A_%a.out
#SBATCH -e output_logs/nibabies_%A_%a.err
#SBATCH -A btervocl

cd run_files.nibabies

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
