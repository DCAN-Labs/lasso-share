#!/bin/bash -l
#SBATCH -J nordic
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=100gb
#SBATCH -t 04:00:00
#SBATCH --mail-user=lama0092@umn.edu
#SBATCH --mail-type=ALL
#SBATCH --tmp=100gb
#SBATCH -p msismall
#SBATCH -o output_logs/nordic_%A_%a.out
#SBATCH -e output_logs/nordic_%A_%a.err
#SBATCH -A faird

cd run_files.NORDIC

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
