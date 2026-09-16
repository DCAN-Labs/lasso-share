#!/bin/bash

set +x 
# determine data directory, run folders, and run templates
input_dir="/projects/standard/csandova/shared/projects/rae_neonatal/nnunet_inputs" # where to ograb input data
output_path="/projects/standard/csandova/shared/projects/rae_neonatal/derivatives/nnunet_outputs" # tier1 or s3 path that processed outputs will be pushed to
run_folder=`pwd`
subject_list="/projects/standard/csandova/shared/projects/rae_neonatal/code/nnunet_wrapper/subjects_to_process.txt" # optional: specifiy a list of subjects to run

process_folder="${run_folder}/run_files.nnunet"
process_template="template.nnunet"

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

# Method 1: Loop through list of subjects to create run files, use specified ses_id
cat ${subject_list} | while read line; do
	sed -e "s|SUBJECT|${line}|g" -e "s|INPUT|${input_dir}|g" -e "s|OUTPUT|${output_path}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}

	k=$((k+1))
done

chmod 775 -R ${process_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_nnunet.sh 

