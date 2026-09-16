#!/bin/bash -l
#SBATCH -J calcSA
#SBATCH -c 8
#SBATCH --mem=100gb
#SBATCH -t 02:00:00
#SBATCH --mail-user=lama0092@umn.edu
#SBATCH --mail-type=ALL
#SBATCH --tmp=100gb
#SBATCH -p msismall
#SBATCH -o output_logs/calc_SA_%A_%a.out
#SBATCH -e output_logs/calc_SA_%A_%a.err
#SBATCH -A lewi1538

cd run_files.calcSA

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
