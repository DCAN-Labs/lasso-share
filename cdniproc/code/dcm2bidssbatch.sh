#!/bin/bash -l
#SBATCH -J dcm2bidssbatch
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=80G
#SBATCH -t 5:00:00
#SBATCH -p msismall
#SBATCH -o output_logs/dcm2bidssbatch_%A_%a.out
#SBATCH -e output_logs/dcm2bidssbatch_%A_%a.err

echo dcm2bids -d ${1} -p ${2} -s ${3} -c ${4} -o ${5}
dcm2bids -d ${1} -p ${2} -s ${3} -c ${4} -o ${5}