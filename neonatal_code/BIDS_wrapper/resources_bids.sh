#!/bin/bash -l
#SBATCH -J bids
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=100gb
#SBATCH -t 04:00:00
#SBATCH --mail-user=mccol199@umn.edu
#SBATCH --mail-type=ALL
#SBATCH --tmp=100gb
#SBATCH -p agsmall,ag2tb
#SBATCH -o output_logs/bids_%A_%a.out
#SBATCH -e output_logs/bids_%A_%a.err
#SBATCH -A btervocl

cd run_files.bids

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
