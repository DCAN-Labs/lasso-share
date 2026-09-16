#!/bin/bash -l
#SBATCH -J nnunet
#SBATCH -p a100-4     
#SBATCH --gres=gpu:a100:1
#SBATCH --ntasks=1
#SBATCH --mem=100gb
#SBATCH -t 04:00:00
#SBATCH --mail-type=NONE
#SBATCH --tmp=100gb
#SBATCH -o output_logs/nnunet_%A_%a.out
#SBATCH -e output_logs/nnunet_%A_%a.err
#SBATCH -A csandova

cd run_files.nnunet

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
