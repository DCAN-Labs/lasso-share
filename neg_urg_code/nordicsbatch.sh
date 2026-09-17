#!/bin/bash -l
#SBATCH -J nordic
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=80G
#SBATCH -t 1:30:00
#SBATCH -p msismall
#SBATCH -o output_logs/nordicsbatch_%A_%a.out
#SBATCH -e output_logs/nordicsbatch_%A_%a.err
#SBATCH -A faird

module load matlab/R2019a
module load fsl/5.0.10

WD=$1
MAG=$2
PHASE=$3
NORDICHEAD=$4
NOISEVOLS=$5
NORDICDIR=$6

NVOLS_MAG=`fslinfo ${MAG} | grep -w dim4 | awk '{print $2}'`
NVOLS_PHASE=`fslinfo ${PHASE} | grep -w dim4 | awk '{print $2}'`

if [[ ${NVOLS_MAG} -ne ${NVOLS_PHASE} ]] ; then
	echo "ERROR: mag and phase timeseries have different nVols! skipping denoising but renaming..."
	echo cp ${MAG} ${WD}/${NORDICHEAD}.nii.gz
	cp ${MAG} ${WD}/${NORDICHEAD}.nii.gz
else
	# run NORDIC Matlab script
	echo matlab -nodisplay -nodesktop -r "addpath('/projects/standard/faird/shared/code/internal/utilities/Dcm2bids3_NORDIC_wrapper'); runnordic('$WD','$MAG','$PHASE','$NORDICHEAD',$NOISEVOLS)"
	matlab -nodisplay -nodesktop -r "addpath('/projects/standard/faird/shared/code/internal/utilities/Dcm2bids3_NORDIC_wrapper'); runnordic('$WD','$MAG','$PHASE','$NORDICHEAD',$NOISEVOLS)"
	# gzip output
	echo gzip ${WD}/${NORDICHEAD}.nii 
	gzip ${WD}/${NORDICHEAD}.nii 
fi

# copy sidecar
echo cp ${MAG::-7}.json ${WD}/${NORDICHEAD}.json
cp ${MAG::-7}.json ${WD}/${NORDICHEAD}.json

# get new number of volumes after noise volume removal 
NVOLS=`fslinfo ${WD}/${NORDICHEAD}.nii.gz | grep -w dim4 | awk '{print $2}'`
NEWVOLS=`echo "${NVOLS} - ${NOISEVOLS}" | bc`

# remove noise volumes
echo "removing ${NOISEVOLS} noise volumes from NORDIC timeseries..."
fslroi ${WD}/${NORDICHEAD}.nii.gz ${WD}/${NORDICHEAD}.nii.gz 0 $NEWVOLS

if [ -e "${WD}/${NORDICHEAD}.nii.gz" ]; then
    echo "NORDIC SUCCESSFUL"
else
    echo "expected output ${WD}/${NORDICHEAD}.nii.gz does not exist."
fi

# cleanup
#if [ -e "${WD}/${NORDICHEAD}.nii.gz" ]; then
#    echo "cleaning up..."
#    mv ${WD}/${NORDICHEAD}.nii.gz ${NORDICDIR}/${NORDICHEAD}.nii.gz 
#    echo "...done!"
#else
#    echo "expected output ${WD}/${NORDICHEAD}.nii.gz does not exist."
#fi
