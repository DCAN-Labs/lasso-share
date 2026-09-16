#!/bin/bash

set +x 
# determine data directory, run folders, and run templates
summary_dir="/projects/standard/lewi1538/shared/projects/neg_urg" # where to output data
dicom_dir="/projects/standard/lewi1538/shared/projects/neg_urg/dicoms" # bucket that input data will be pulled from, provide full path to where subject subfolders are located
output_path="/projects/standard/lewi1538/shared/projects/neg_urg/bids" # tier1 or s3 path that processed outputs will be pushed to
run_folder=`pwd`
subject_list="/projects/standard/lewi1538/shared/projects/neg_urg/code/BIDS_wrapper/subjects_to_process.txt" # optional: specifiy a list of subjects to run
ses=1 # all subjects only have one session

process_folder="${run_folder}/run_files.bids"
process_template="template.bids"

email=`echo $USER@umn.edu`
group=`groups|cut -d" " -f1`

# if processing run folders (sMRI, fMRI,) exist delete them and recreate
if [ -d "${process_folder}" ]; then
	rm -rf "${process_folder}"
	mkdir -p "${process_folder}/logs"
else
	mkdir -p "${process_folder}/logs"
fi

# counter to create run numbers
k=0

### CHOOSE METHOD OF SUBJECT RUN FILE CREATION ###

# Method 1: Loop through list of subjects to create run files, use specified ses_id
cat ${subject_list} | while read line; do
	sed -e "s|SUB|${line}|g" -e "s|SES|${ses}|g" -e "s|SUMMARY|${summary_dir}|g" -e "s|DICOMS|${dicom_dir}|g" -e "s|OUTPUT|${output_path}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}

	k=$((k+1))
done

chmod 775 -R ${process_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_bids.sh 

