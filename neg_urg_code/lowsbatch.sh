#!/bin/bash -l
#SBATCH -J generic_low
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH -t 2:00:00
#SBATCH -p msismall
#SBATCH -o output_logs/lowresources_%A_%a.out
#SBATCH -e output_logs/lowresoucses_%A_%a.err

/bin/bash -c "$@"