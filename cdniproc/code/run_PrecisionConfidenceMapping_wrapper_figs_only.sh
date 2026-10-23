#!/bin/bash
#SBATCH -J job_submitter
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20gb
#SBATCH -t 1:00:00
#SBATCH -p msismall
#SBATCH -A faird


# Define input parameters
SUB=${1}
SES=${2}
TASK=${3}
BASEDIR=${4}
DERIVATIVESDIR=${5}
DTSERIESEXT=${6}
intrp_noise=${7}
percent_holdout=${8}
FD=${9}
NUM=${10}
shuffle_option=${11}
shuffle_chunk_size=${12}
SPLITHALF=${13}
SPLITPCT=${14}
STANDARDTM=${15}
JobName=${16}
ntasks=${17}
tmpspace=${18}
mem=${19}
time=${20}
mail=${21}
partitions=${22}
group=${23}
MIN=${24}

echo "SUB: ${SUB}"
echo "SES: ${SES}"
echo "TASK: ${TASK}"
echo "BASEDIR: ${BASEDIR}"
echo "DERIVATIVESDIR: ${DERIVATIVESDIR}"
echo "DTSERIESEXT: ${DTSERIESEXT}"
echo "intrp_noise: ${intrp_noise}"
echo "dtseries_in: ${DERIVATIVESDIR}/sub-${SUB}/ses-${SES}/func/sub-${SUB}_ses-${SES}_task-${TASK}_${DTSERIESEXT}"


#This is the directory where your outputs and run code will be stored. If running multiple subjects, make sure to incldue sub and ses in name since output names do not all contain this, so things will get overwritten
#NUM=100 # This is the number of perumtations you will run when testing, you can change to 1, so you don't submit 100 jobs at once. 
#MIN=${2} #Right now the code will split your data into two halves, so this number identifies how many minutes will be in each half. Adjust according to your data. 
S_KERNEL=2.55 #smoothing kernel
#intrp_noise=1 # If you have not run the spatially interpolated code on these data change flag to 1 
#DTSERIESEXT=space-fsLR_den-91k_desc-interpolated_bold.dtseries.nii
#DTSERIESEXT=space-fsLR_den-91k_desc-interpolated_bold_spatially_interpolated.dtseries.nii # When looking in your func folder identify the ending to your concatenated dtseries anything that comes after sub-${SUB}_ses-${SES}_task-${TASK}
SURF_ONLY=2 #This will use the ABCD SCAN network template, change to 1 to run surf only ABCD without SCAN
#shuffle_option=percent #you can change this to "run" and it will shuffle the data based on runs instead of a percent of data. Right now it will shuffle the data based on a given percent you identify below. 
#shuffle_option=TRs #other options are 'minutes', 'percent','TRs','run' you can change this to "run" and it will shuffle the data based on runs instead of a percent of data. Right now it will shuffle the data based on a given percent you identify below. 
#shuffle_option=bootstrap #other options are 'minutes', 'percent','TRs','run' you can change this to "run" and it will shuffle the data based on runs instead of a percent of data. Right now it will shuffle the data based on a given percent you identify below. 
#shuffle_option=TRs #other options are 'minutes', 'percent','TRs','run' you can change this to "run" and it will shuffle the data based on runs instead of a percent of data. Right now it will shuffle the data based on a given percent you identify below. 

#shuffle_chunk_size=5 #if shuffle option is percent this will be the percent of the total data you want the chunks to be that will be shuffled in each permutation. If shuffle_option is 'minutes' this will define how many minutes each chunk should be. Then finally if shuffle_option is TRs it will ignore this and shuffle all of the TRs 
PIPELINE="xcpd" ## if runnin files with abcd output names change PIPELINE to abcd 
MAKEFIGS=1 #once you are done running all the perumtations and there are no more Failed perumtations change to 1 and run and it will make the figs for these data. 
#SPLITHALF=0 #the code now has the option to run SPLITHALF and or SPLITPCT. Split half is the version that shufles the data and splits it in half and runs template matching on both halves to test reliability between each half. If Split half is 1 it run this option if it is 0 it skips split half. 
#SPLITPCT=1 #If you are running SPLITPCT this allows you to split the data after shuffling at a given percent, say 80% and then runs template matching on that 80% of the data across all permutations. Set this to 1 if you want to run this option or 0 if you want to skip this option. Either way, the next value percent_holdout will need a value, but it will be ignored if SPLITPCT=0
#percent_holdout=80 # in the future I will rename this to percent keep or percent analyses or analyses segment but since it will be a lot of changes will keep as is for now until it is certain what I want to call it. But yes, I am aware calling the segment I am keeping holdout is incorrect. 
#TR=2 #Code will use TR=$(wb_command -file-information ${dtseries_in} -only-step-interval) to calculated TR so leave TR blank unless you want to overide that and input a different TR value.
#STANDARDTM=0 #Use this flag id you want to run standard template matching 


# Check if MIN variable is not set
if [ -z "${MIN}" ]; then
    dtseries_in=${DERIVATIVESDIR}/sub-${SUB}/ses-${SES}/func/sub-${SUB}_ses-${SES}_task-${TASK}_${DTSERIESEXT}
    TR=$(wb_command -file-information ${dtseries_in} -only-step-interval)
    totalTRs=$(wb_command -file-information ${dtseries_in} -only-number-of-maps)
    total_time_seconds=$(echo "$TR * $totalTRs" | bc)
    total_time_minutes=$(echo "scale=2; $total_time_seconds / 60" | bc)
    half_minutes=$(echo "scale=0; $total_time_minutes / 2" | bc)
    ten_percent_of_half=$(echo "$half_minutes * 0.20" | bc)
    rounded_ten_percent_of_half=$(echo "scale=0; $ten_percent_of_half / 1" | bc)
    MIN=$(echo "$half_minutes - $rounded_ten_percent_of_half" | bc)
    echo "MIN set to $MIN based on the calculations."
else
    echo "MIN is already set to $MIN."
fi

if [ "${intrp_noise}" == "1" ]; then
    dtseries_in="${DERIVATIVESDIR}/sub-${SUB}/ses-${SES}/func/sub-${SUB}_ses-${SES}_task-${TASK}_${DTSERIESEXT}"
    WB_CMD="/projects/standard/faird/shared/code/external/utilities/workbench/1.4.2/workbench/bin_rh_linux64/wb_command"
    runLocally=0
    matlab -nodisplay -nosplash -r "addpath('/projects/standard/faird/shared/code/internal/analytics/compare_matrices_to_assign_networks'); addpath('/projects/standard/faird/shared/code/internal/utilities/interpolate_noise_for_timeseries/'); infile='${dtseries_in}'; WB_CMD='${WB_CMD}'; runLocally=${runLocally}; interpolate_noise_for_timeseries(infile, WB_CMD, runLocally); exit;"
    intrp_noise=0
    base_name="${DTSERIESEXT%.dtseries.nii}"
    DTSERIESEXT="${base_name}_spatially_interpolated.dtseries.nii"
fi

# Rest of the script...

###########
## CHANGE SBATCH parameters you will want to run your main script. This includes user and time and other memory allocations. The code will then make a new run script in your BASEDIR to run.
# SBATCH parameters provided by the user you can change these based on the data and time you need to run this
current_datetime=$(date +"%Y%m%d%H%M%S")
outputlogs="${BASEDIR}/output_logs/${SUB}_${SES}_${percent_holdout}_${NUM}_${shuffle_option}_${SPLITHALF}_${SPLITPCT}_${STANDARDTM}_PCM_${current_datetime}_%A_%a.out"
errorlogs="${BASEDIR}/output_logs/${SUB}_${SES}_${percent_holdout}_${NUM}_${shuffle_option}_${SPLITHALF}_${SPLITPCT}_${STANDARDTM}_PCM_${current_datetime}_%A_%a.err"

figures_outputlogs="${BASEDIR}/output_logs/Sub-${SUB}_${SES}_${percent_holdout}_${NUM}_${shuffle_option}_${SPLITHALF}_${SPLITPCT}_${STANDARDTM}_PCM_FigsBANC_${current_datetime}_%A_%a.out"
figures_errorlogs="${BASEDIR}/output_logs/Sub-${SUB}_${SES}_${percent_holdout}_${NUM}_${shuffle_option}_${SPLITHALF}_${SPLITPCT}_${STANDARDTM}_PCM_FigsBANC_${current_datetime}_%A_%a.err"
## No need to change anything below this point.

# Ensure output directory exists
mkdir -p "$BASEDIR"
mkdir -p "${BASEDIR}/output_logs"


# Make a copy of the altered script to the output directory
#cp /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/main_script_run_PCM_dev.sh "${BASEDIR}/main_script_run_BANC.sh"
cp /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/main_script_run_PCM_bagging.sh "${BASEDIR}/main_script_run_BANC.sh"

#cp /projects/standard/miran045/shared/projects/SCAN_PD/experiments/make_dlabel_files/main_script_run_PCM.sh "${BASEDIR}/main_script_run_BANC.sh"
cp /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/make_figs_and_dscalars.sh "${BASEDIR}/make_figs_and_dscalars.sh"
cp /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/make_figs_and_dscalars_Percent_holdout.sh "${BASEDIR}/make_figs_and_dscalars_Percent_holdout.sh"
cp /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/Standard_Template_Matching.sh "${BASEDIR}/Standard_Template_Matching.sh"
# Update the SBATCH parameters in the copied script
sed -i "s/^#SBATCH -J .*/#SBATCH -J $JobName/" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s/^#SBATCH --ntasks=.*/#SBATCH --ntasks=$ntasks/" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s/^#SBATCH --tmp=.*/#SBATCH --tmp=$tmpspace/" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s/^#SBATCH --mem=.*/#SBATCH --mem=$mem/" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s/^#SBATCH -t .*/#SBATCH -t $time/" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s/^#SBATCH --mail-type=.*/#SBATCH --mail-type=$mail/" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s|^#SBATCH -p .*|#SBATCH -p $partitions|" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s|^#SBATCH -o .*|#SBATCH -o $outputlogs|" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s|^#SBATCH -e .*|#SBATCH -e $errorlogs|" "${BASEDIR}/main_script_run_BANC.sh"
sed -i "s/^#SBATCH -A .*/#SBATCH -A $group/" "${BASEDIR}/main_script_run_BANC.sh"

#Standard template matching
sed -i "s/^#SBATCH -J .*/#SBATCH -J $JobName/" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s/^#SBATCH --ntasks=.*/#SBATCH --ntasks=$ntasks/" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s/^#SBATCH --tmp=.*/#SBATCH --tmp=$tmpspace/" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s/^#SBATCH --mem=.*/#SBATCH --mem=$mem/" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s/^#SBATCH -t .*/#SBATCH -t $time/" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s/^#SBATCH --mail-type=.*/#SBATCH --mail-type=$mail/" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s|^#SBATCH -p .*|#SBATCH -p $partitions|" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s|^#SBATCH -o .*|#SBATCH -o $outputlogs|" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s|^#SBATCH -e .*|#SBATCH -e $errorlogs|" "${BASEDIR}/Standard_Template_Matching.sh"
sed -i "s/^#SBATCH -A .*/#SBATCH -A $group/" "${BASEDIR}/Standard_Template_Matching.sh"

## Change command for fig file 
sed -i "s/^#SBATCH -A.*/#SBATCH -A $group/" "${BASEDIR}/make_figs_and_dscalars.sh"

sed -i "s|^#SBATCH -o .*|#SBATCH -o $figures_outputlogs|" "${BASEDIR}/make_figs_and_dscalars.sh"
sed -i "s|^#SBATCH -e .*|#SBATCH -e $figures_errorlogs|" "${BASEDIR}/make_figs_and_dscalars.sh"
sed -i "s|^#SBATCH -e .*|#SBATCH -e $figures_errorlogs|" "${BASEDIR}/make_figs_and_dscalars_Percent_holdout.sh"
sed -i "s|^#SBATCH -o .*|#SBATCH -o $figures_outputlogs|" "${BASEDIR}/make_figs_and_dscalars_Percent_holdout.sh"

sed -i "s/^#SBATCH -A.*/#SBATCH -A $group/" "${BASEDIR}/make_figs_and_dscalars_Percent_holdout.sh"



sed -i "/# START_LOG_PLACEHOLDER/c\echo \"The sub-\${SUB}_ses-\${SES}_task-\${TASK}_PERM-\${NUM} Job started at: \$(date)\" >> $outputlogs\necho \"The sub-\${SUB}_ses-\${SES}_task-\${TASK}_PERM-\${NUM} Job started at: \$(date)\" >> $errorlogs" "${BASEDIR}/main_script_run_BANC.sh"

sed -i "/# END_LOG_PLACEHOLDER/c\echo \"The sub-\${SUB}_ses-\${SES}_task-\${TASK}_PERM-\${NUM} Job ended at: \$(date)\" >> $outputlogs\necho \"The sub-\${SUB}_ses-\${SES}_task-\${TASK}_PERM-\${NUM} Job ended at: \$(date)\" >> $errorlogs" "${BASEDIR}/main_script_run_BANC.sh"

python3 /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/Check_sucessful_perms_percent_holdout.py "${BASEDIR}" "${SUB}" "${SES}" "${TASK}" "${NUM}" "${SURF_ONLY}" "${SPLITHALF}" "${SPLITPCT}" "${percent_holdout}"

# Check SPLITHALF and submit jobs if required
if [ "${SPLITHALF}" == "1" ]; then
    
    TMPSPLITPCT=0
    FAILED_CONC_FILE="${BASEDIR}/sub-${SUB}_ses-${SES}_failed_either_half.conc"
    
    if [ ! -f "$FAILED_CONC_FILE" ]; then
        echo "Failed permutations file not found: $FAILED_CONC_FILE"
        exit 1
    fi

    # declare -a JOBIDS=()

    # # Loop to submit jobs and collect job IDs
    # while read -r index; do
    #     echo "Processing Split half permutation: ${index}"
    #     echo running ${BASEDIR}/main_script_run_BANC.sh "${SUB}" "${SES}" "${TASK}" ${FD} ${index} ${MIN} ${S_KERNEL} "${DERIVATIVESDIR}" "${BASEDIR}" "${DTSERIESEXT}" ${SURF_ONLY} ${intrp_noise} "${shuffle_option}" ${shuffle_chunk_size} ${percent_holdout} ${SPLITHALF} ${TEMPSPLITPCT} "${PIPELINE}" ${TR}

    #     JOBID=$(sbatch ${BASEDIR}/main_script_run_BANC.sh "${SUB}" "${SES}" "${TASK}" ${FD} ${index} ${MIN} ${S_KERNEL} "${DERIVATIVESDIR}" "${BASEDIR}" "${DTSERIESEXT}" ${SURF_ONLY} ${intrp_noise} "${shuffle_option}" ${shuffle_chunk_size} ${percent_holdout} ${SPLITHALF} ${TMPSPLITPCT} "${PIPELINE}" ${TR} | awk '{print $4}')

    #     JOBIDS+=($JOBID)
    #     echo "Submitted job ${JOBID} for permutation ${index}"

    # done < "$FAILED_CONC_FILE"
    # # Check if there are no jobs submitted, and exit or skip as needed
    # if [ ${#JOBIDS[@]} -eq 0 ]; then
    #     echo "All Permutations already run. No jobs were submitted. Exiting and moving on to figure making."
    #     # If you need to exit script entirely, uncomment the next line
    #     # exit 0
    # else
    #     # Function to check the completion status of a job using sacct
    #     check_job_completion() {
    #         local job=$1
    #         jobState=$(sacct -j $job --format=State --noheader | head -n 1 | awk '{print $1}')
        
    #         if [[ $jobState =~ ^(COMPLETED|FAILED|CANCELLED)$ ]]; then
    #             return 1 # Job is completed (no longer running)
    #         else
    #             return 0 # Job is still running
    #         fi
    #     }

    #     # Wait for all jobs to complete
    #     ALL_DONE=0
    #     while [ $ALL_DONE -eq 0 ]; do
    #         ALL_DONE=1
    #         for JOBID in "${JOBIDS[@]}"; do
    #             check_job_completion $JOBID
    #             if [ $? -eq 0 ]; then
    #                 echo "Waiting for job $JOBID to complete..."
    #                 ALL_DONE=0
    #                 sleep 60
    #                 break # Exit the for loop and wait before checking again
    #             fi
    #         done
    #     done

    #         echo "All SPLITPCT perm jobs completed"

    # fi

    python3 /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/Check_sucessful_perms_percent_holdout.py "${BASEDIR}" "${SUB}" "${SES}" "${TASK}" "${NUM}" "${SURF_ONLY}" "${SPLITHALF}" "${TMPSPLITPCT}" "${percent_holdout}"

    if [ "${MAKEFIGS}" == "1" ]; then
        echo "Generating figures for SPLITHALF..."
        module load ffmpeg
        sbatch ${BASEDIR}/make_figs_and_dscalars.sh ${BASEDIR} ${BASEDIR}/sub-${SUB}_ses-${SES}_successful_half1.conc ${BASEDIR}/sub-${SUB}_ses-${SES}_successful_half2.conc 1
    fi
fi

# Check SPLITPCT and submit jobs if required
if [ "${SPLITPCT}" == "1" ]; then

    TEMPSPLITHALF=0
    # Path to the failed_either_half.conc file
    FAILED_CONC_FILE="${BASEDIR}/sub-${SUB}_ses-${SES}_failed_percent_holdout-${percent_holdout}.conc"
    echo "Permutations to run = ${FAILED_CONC_FILE}"
    # Check if the failed_either_half.conc file exists
    if [ ! -f "$FAILED_CONC_FILE" ]; then
        echo "Failed permutations file not found: $FAILED_CONC_FILE"
        exit 1
    fi


    # # Initialize an array to hold job IDs
    # declare -a JOBIDS=()

    # # Loop to submit jobs and collect job IDs
    # while read -r index; do
    #     echo "Processing failed permutation: ${index}"

    #     echo running ${BASEDIR}/main_script_run_BANC.sh "${SUB}" "${SES}" "${TASK}" ${FD} ${index} ${MIN} ${S_KERNEL} "${DERIVATIVESDIR}" "${BASEDIR}" "${DTSERIESEXT}" ${SURF_ONLY} ${intrp_noise} "${shuffle_option}" ${shuffle_chunk_size} ${percent_holdout} ${TEMPSPLITHALF} ${SPLITPCT} "${PIPELINE}" ${TR}

    #     JOBID=$(sbatch ${BASEDIR}/main_script_run_BANC.sh "${SUB}" "${SES}" "${TASK}" ${FD} ${index} ${MIN} ${S_KERNEL} "${DERIVATIVESDIR}" "${BASEDIR}" "${DTSERIESEXT}" ${SURF_ONLY} ${intrp_noise} "${shuffle_option}" ${shuffle_chunk_size} ${percent_holdout} ${TEMPSPLITHALF} ${SPLITPCT} "${PIPELINE}" ${TR} | awk '{print $4}')

    #     JOBIDS+=($JOBID)
    # done < "$FAILED_CONC_FILE"

    # # Check if there are no jobs submitted, and exit or skip as needed
    # if [ ${#JOBIDS[@]} -eq 0 ]; then
    #     echo "All Permutations already run. No jobs were submitted. Exiting and moving on to figure making."
    #     # If you need to exit script entirely, uncomment the next line
    #     # exit 0
    # else
    #     # Function to check the completion status of a job using sacct
    #     check_job_completion() {
    #         local job=$1
    #         jobState=$(sacct -j $job --format=State --noheader | head -n 1 | awk '{print $1}')
        
    #         if [[ $jobState =~ ^(COMPLETED|FAILED|CANCELLED)$ ]]; then
    #             return 1 # Job is completed (no longer running)
    #         else
    #             return 0 # Job is still running
    #         fi
    #     }

    #     # Wait for all jobs to complete
    #     ALL_DONE=0
    #     while [ $ALL_DONE -eq 0 ]; do
    #         ALL_DONE=1
    #         for JOBID in "${JOBIDS[@]}"; do
    #             check_job_completion $JOBID
    #             if [ $? -eq 0 ]; then
    #                 echo "Waiting for job $JOBID to complete..."
    #                 ALL_DONE=0
    #                 sleep 60
    #                 break # Exit the for loop and wait before checking again
    #             fi
    #         done
    #     done

    #     echo "All SPLITPCT perm jobs completed"

    # fi

    python3 /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/Check_sucessful_perms_percent_holdout.py "${BASEDIR}" "${SUB}" "${SES}" "${TASK}" "${NUM}" "${SURF_ONLY}" "${TEMPSPLITHALF}" "${SPLITPCT}" "${percent_holdout}"

    if [ "${MAKEFIGS}" == "1" ]; then
        echo "Generating figures for SPLITPCT..."
        module load ffmpeg
        JOBID=$(sbatch ${BASEDIR}/make_figs_and_dscalars_Percent_holdout.sh ${BASEDIR} ${BASEDIR}/sub-${SUB}_ses-${SES}_successful_percent_holdout-${percent_holdout}.conc ${percent_holdout} 1 | awk '{print $4}')

        # Ensure JOBID is non-empty and numeric (simple check example)
        if ! [[ "$JOBID" =~ ^[0-9]+$ ]]; then
            echo "Failed to submit job for making figures, or invalid job ID: $JOBID"
            exit 1
        fi
        #sbatch ${BASEDIR}/make_figs_and_dscalars.sh ${BASEDIR} ${BASEDIR}/sub-${SUB}_ses-${SES}_successful_percent_holdout-${percent_holdout}.conc ${BASEDIR}/sub-${SUB}_ses-${SES}_successful_percent_holdout-${percent_holdout}.conc 1
    fi
fi


if [ "${STANDARDTM}" == "1" ]; then
        
        TMPSPLITPCT=0
        TMPSPLITHALF=0
        
        declare -a JOBIDS=()

        # Loop to submit jobs and collect job IDs
        index=1
        echo "Processing Standard Template Matching: ${index}"
        echo running ${BASEDIR}/Standard_Template_Matching.sh "${SUB}" "${SES}" "${TASK}" ${FD} ${index} ${MIN} ${S_KERNEL} "${DERIVATIVESDIR}" "${BASEDIR}" "${DTSERIESEXT}" ${SURF_ONLY} ${intrp_noise} "${shuffle_option}" ${shuffle_chunk_size} ${percent_holdout} ${TMPSPLITHALF} ${TMPSPLITPCT} "${PIPELINE}" ${STANDARDTM} ${TR} 

        JOBID=$(sbatch ${BASEDIR}/Standard_Template_Matching.sh "${SUB}" "${SES}" "${TASK}" ${FD} ${index} ${MIN} ${S_KERNEL} "${DERIVATIVESDIR}" "${BASEDIR}" "${DTSERIESEXT}" ${SURF_ONLY} ${intrp_noise} "${shuffle_option}" ${shuffle_chunk_size} ${percent_holdout} ${TMPSPLITHALF} ${TMPSPLITPCT} "${PIPELINE}" ${STANDARDTM} ${TR} | awk '{print $4}')
    
        JOBIDS+=($JOBID)
        echo "Submitted job ${JOBID} for permutation ${index}"
fi 



