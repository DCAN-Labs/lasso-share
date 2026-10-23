#!/bin/bash -l

#SBATCH -J splitwrapper
#SBATCH -c 1
#SBATCH --mem=20G
#SBATCH -t 1:00:00
#SBATCH -p ag2tb,agsmall,aglarge
#SBATCH -A syliaw
#SBATCH -o output_logs/run_PCM_%A.out
#SBATCH -e output_logs/run_PCM_%A.err

# Set parameters
SUB=${1}
SES=${2}
TASK=${3}
DERIVATIVES=${4}
#PIPELINE=fmriprep-24.1.1-xcpd-0.9.1
#TASK=concatenated
FD=0.2
percent_holdout=100 # after shuffling the percent of data you want to run the analyses on for each permutation
figsonly=0

# BASEDIR is where all of your outputs will be stored. I have percent holdout in the name in case you want to test different percents, but I would leave it at 100 for default. 
BASEDIR=${DERIVATIVES}/${SUB}/PCM/${SES}/${TASK}/

echo ${BASEDIR}

if [ ! -d ${BASEDIR} ]; then
  mkdir -p ${BASEDIR}
#else
# rm -rf ${BASEDIR}
# mkdir -p ${BASEDIR}
fi  

DERIVATIVESDIR=${DERIVATIVES}/${SUB}/analysis_input_files/

# Load needed modules if not already loaded 
check_matlab=$(which matlab 2>&1 | grep -oP "/usr/bin/which:\K[^(]+")
if [[ ${check_matlab}="no matlab in" ]]; then
    echo "Loading matlab"
    module load matlab
fi
check_workbench=$(which workbench 2>&1 | grep -oP "/usr/bin/which:\K[^(]+")
if [[ ${check_workbench}="no workbench in" ]]; then
    echo "Loading workbench"
    module load workbench/1.5.0
fi

# Parameters for permutation jobs 
JobName="${SUB}_${TASK}"
ntasks=1
tmpspace="100gb"
mem="110gb"
time="9:00:00"
mail="NONE"
partitions="msismall,ag2tb"
group="syliaw"

# Setting up inputs
intrp_noise=0 # if you have not run interp_noise yet you should run it (1). Set to 0 to skip this step 

# what your dtseries ends in after sub-${SUB}_ses-${SES}_task-${TASK}_
DTSERIESEXT=space-fsLR_den-91k_desc-denoised_bold_spatially_interpolated.dtseries.nii
dtseries_in=${DERIVATIVESDIR}/sub-${SUB}_ses-${SES}_task-${TASK}_${DTSERIESEXT}
surf_L=(${DERIVATIVESDIR}/sub-${SUB}_*hemi-L_*desc-hcp_midthickness.surf.gii)
surf_R=(${DERIVATIVESDIR}/sub-${SUB}_*hemi-R_*desc-hcp_midthickness.surf.gii)
motion_file="${DERIVATIVESDIR}/sub-${SUB}_ses-${SES}_task-${TASK}_desc-abcc_qc_power_2014_FD_only.mat"

# Make sure all inputs exists and exit script if any of them are missing 
if [ ! -f ${dtseries_in} ]; then
    echo "This dtseries doesn't exist:" ${dtseries_in}
    exit 1
fi
if [ ! -f ${surf_L} ]; then
    echo "This surface file doesn't exist:" ${surf_L}
    exit 1
fi
if [ ! -f ${surf_R} ]; then
    echo "This surface file doesn't exist:" ${surf_R}
    exit 1
fi
if [ ! -f ${motion_file} ]; then
    echo "This motion file doesn't exist:" ${motion_file}
    exit 1
fi

#No need to change PCMwrapper unless you need to make changes to actual wrapper then, make a copy of it and point to that copy. 
if [ "$figsonly" -eq 1 ]; then
    PCMwrapper=/projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/wrappers/run_PrecisionConfidenceMapping_wrapper_figs_only.sh
else
    PCMwrapper=/projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/wrappers/run_PrecisionConfidenceMapping_wrapper_dev.sh
fi

NUM=100 # The number of perumtation you want to run
shuffle_option='bootstrap' #This could be bootstrap, bagging, TRs, minutes, runs
shuffle_chunk_size=5 #If minute this determins how large the chunk sizes are in minutes to shuffle. If doing shuffle_option='bagging' it will shuffle the TRs and this will determin to what minute you want to "bag" the data, i.e. bootstrap with replacement to a given minute. 

# These are the different options to run it. SPLITHALF=1 will split your data in half and run PCM on both halves. SPLITPCT will split at your percent_holdout number and run PCM on that amount of data, if using "bootstrap" you can keep percent_holdout=100. STANDARDTM=1 will run just standard template matching. You can turn all flags on to 1 or 0 depending on what you want to run. 
SPLITHALF=0
SPLITPCT=1 ## This option = 1 if you want to run the PCM code
STANDARDTM=0 ## This option 1 if you want to run standard template matching


## You don't need to change anything below this. But if you want to change the number of minutes it is using to run it, for example running it at 5 mins 10 mins 15 mins of your data 
#below. Also this is currently calculating your half mins for split half option. BUt if you want to put in a manual split half, you can input that above.  

# Get the TR and total number of TRs using wb_command
TR=$(wb_command -file-information ${dtseries_in} -only-step-interval)

motion_out=$(dirname "$motion_file")

#if [ "${intrp_noise}" == "1" ]; then
#    dtseries_in="${DERIVATIVESDIR}/sub-${SUB}_ses-${SES}_task-${TASK}_${DTSERIESEXT}"
#    WB_CMD="/common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command"
#    runLocally=0
#    matlab -nodisplay -nosplash -r "addpath('/projects/standard/faird/shared/code/internal/analytics/compare_matrices_to_assign_networks'); addpath('/projects/standard/faird/shared/code/internal/utilities/interpolate_noise_for_timeseries/'); infile='${dtseries_in}'; WB_CMD='${WB_CMD}'; runLocally=${runLocally}; interpolate_noise_for_timeseries(infile, WB_CMD, runLocally); exit;"
#    intrp_noise=0
#    base_name="${DTSERIESEXT%.dtseries.nii}"
#    DTSERIESEXT="${base_name}_spatially_interpolated.dtseries.nii"
#    dtseries_in=${DERIVATIVESDIR}/sub-${SUB}/ses-${SES}/func/sub-${SUB}_ses-${SES}_task-${TASK}_${DTSERIESEXT}
#fi

echo "This is dtseries ${dtseries_in} and DTSERIESEXT is ${DTSERIESEXT}"
ls ${dtseries_in}

totalTRs=$(wb_command -file-information ${dtseries_in} -only-number-of-maps)
total_time_seconds=$(echo "$TR * $totalTRs" | bc)
total_time_minutes=$(echo "scale=2; $total_time_seconds / 60" | bc)
half_minutes=$(echo "scale=0; $total_time_minutes / 2" | bc)
percent2round=0.15
n_percent_of_half=$(echo "$half_minutes * ${percent2round}" | bc)
rounded_n_percent_of_half=$(echo "scale=0; $n_percent_of_half / 1" | bc)

#If you don't have a half min point it will calculate it and use that here. 
if [ -z "${MIN}" ]; then
    MIN=$(echo "$half_minutes - $rounded_n_percent_of_half" | bc)
fi

echo "Half of the data is ${half_minutes} so using a buffer of ${percent2round} to round the half down to account for motion. Change percent2round if needed"
echo "Final Cut off for half the data are defined at: ${MIN} here"

if [[ "$motion_file" == *.hdf5 ]]; then
    matlab -nodisplay -nosplash -r "addpath('/projects/standard/faird/shared/code/internal/utilities/xcpd2dcanmotion/'); xcpd2dcanmotion('${motion_file}', '${motion_out}'); exit;"
    motion_file="${motion_file%.hdf5}_power_2014_FD_only.mat"
fi

echo "New motion file path: ${motion_file}"

#startmins=5
#increment=5
#endmins=60
#if you want to do different increments of time you can change this, but if just running on total scan use this. 
startmins="full"
increment="full"
endmins="full"
keep_from='start'

#for minutes in $(seq $startmins $increment $endmins); do
minutes=full
    echo "Processing truncated dtseries min: ${minutes}"

    mkdir -p ${BASEDIR}/ExpData-${minutes}m/
    funcout=${BASEDIR}/ExpData-${minutes}m/sub-${SUB}/ses-${SES}/func
    mkdir -p ${funcout}
    anatout=${BASEDIR}/ExpData-${minutes}m/sub-${SUB}/ses-${SES}/anat
    mkdir -p ${anatout}
    cp ${surf_L} ${anatout}/sub-${SUB}_ses-${SES}_space-fsLR_den-32k_hemi-L_desc-hcp_midthickness.surf.gii
    cp ${surf_R} ${anatout}/sub-${SUB}_ses-${SES}_space-fsLR_den-32k_hemi-R_desc-hcp_midthickness.surf.gii

    newBASEDIR=${BASEDIR}/ExpData-${minutes}m
    newDTSERIESEXT=truncated_bold.dtseries.nii
    newTASK=${TASK}-${minutes}minutes
    ls ${newBASEDIR}/sub-${SUB}/ses-${SES}/func
    echo "addpath('/projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/'); extract_minutes_dtseries_and_motion('${dtseries_in}', '${motion_file}', '${funcout}', '${TR}', '${minutes}', '${keep_from}');"
    matlab -nodisplay -nosplash -r "addpath('/projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/'); extract_minutes_dtseries_and_motion('${dtseries_in}', '${motion_file}', '${funcout}', '${TR}', '${minutes}', '${keep_from}',[],'${SUB}', '${SES}', '${TASK}'); exit;"
    
    sbatch ${PCMwrapper} ${SUB} ${SES} ${newTASK} ${newBASEDIR} ${newBASEDIR} ${newDTSERIESEXT} ${intrp_noise} ${percent_holdout} ${FD} ${NUM} ${shuffle_option} ${shuffle_chunk_size} ${SPLITHALF} ${SPLITPCT} ${STANDARDTM} ${JobName} ${ntasks} ${tmpspace} ${mem} ${time} ${mail} ${partitions} ${group} ${MIN}
#done

# ## After everything is done running run this to get the thresholded images and maps
# thresholds="0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 0.91 0.92 0.93 0.94 0.95 0.96 0.97 0.98 0.99"
# sbatch /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/threshold_confidence_maps.sh --figdir1 ${newBASEDIR}/figures/Percent_Holdout-100/ciftis/ --thresholds "${thresholds}"

## Once the above is done running I ran the below to convert the dscalars to dlables and make images. 
#for i in ${newBASEDIR}/figures/Percent_Holdout-100/ciftis/Thresholded-0*/PCM_confidence_map_to_bin_all-networks_thresh-*dscalar.nii
#do
#     /projects/standard/faird/shared/code/internal/analytics/compare_matrices_to_assign_networks/dscalar2dlabel.sh "$i"
#     /projects/standard/faird/shared/code/internal/utilities/figure_maker/quick_network_pic.sh "$i"
# done
