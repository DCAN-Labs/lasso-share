#!/bin/bash

set +x 
# determine data directory, run folders, and run templates
summary_dir="/projects/standard/lewi1538/shared/projects/neg_urg" # working dir
run_folder=`pwd`
subject_list="/projects/standard/lewi1538/shared/projects/neg_urg/code/BIDS_wrapper/subjects_to_process.txt" # optional: specifiy a list of subjects to run
ses=1 # all subjects only have one session

process_folder="${run_folder}/run_files.NORDIC"
process_template="template.nordic"

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
	sed -e "s|SUB|${line}|g" -e "s|SUMMARY|${summary_dir}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}

	k=$((k+1))
done

chmod 775 -R ${process_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_nordic.sh 

