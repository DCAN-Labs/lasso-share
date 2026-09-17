#!/bin/bash

set +x 
# determine data directory, run folders, and run templates
tmp_dir="/tmp"
input_dir="/projects/standard/lewi1538/shared/projects/neg_urg/derivatives/fmriprep"
output_dir="/projects/standard/lewi1538/shared/projects/neg_urg/derivatives"
run_folder=`pwd`
subject_list="/projects/standard/lewi1538/shared/projects/neg_urg/code/xcpd_wrapper/subjects_w_rest.txt" # optional: specifiy a list of subjects to run
ses=1 # all subjects only have one session

process_folder="${run_folder}/run_files.xcpd"
process_template="template.xcpd"

email=`echo $USER@umn.edu`
group=`groups|cut -d" " -f1`

# if processing run folders exist delete them and recreate
if [ -d "${process_folder}" ]; then
	rm -rf "${process_folder}"
	mkdir -p "${process_folder}"
else
	mkdir -p "${process_folder}"
fi

# counter to create run numbers
k=0

# Loop through list of subjects with ages to create run files, use specified ses_id
while IFS=',' read -r subid age rest_of_line; do
	sed -e "s|SUBID|${subid}|g" -e "s|SESID|${ses}|g" -e "s|DATADIR|${tmp_dir}|g" -e "s|INPUT|${input_dir}|g" -e "s|OUTPUT|${output_dir}|g" -e "s|RUNDIR|${run_folder}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}
	k=$((k+1))
done < "$subject_list"

chmod 775 -R ${process_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_process.sh 

