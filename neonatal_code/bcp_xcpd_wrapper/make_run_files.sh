#!/bin/bash

set +x 
# determine data directory, run folders, and run templates
tmp_dir="/tmp"
input_dir="s3://bcp-nibabies/nibabies-v25.0.1"
output_dir="/projects/standard/csandova/shared/projects/rae_neonatal/derivatives"
run_folder=`pwd`
subject_list="/projects/standard/csandova/shared/projects/rae_neonatal/code/bcp_xcpd_wrapper/BCP_subjects_w_ages.csv" # optional: specifiy a list of subjects to run

process_folder="${run_folder}/run_files.xcpd"
process_template="template.xcpd"

# if processing run folders (sMRI, fMRI,) exist delete them and recreate
if [ -d "${process_folder}" ]; then
	rm -rf "${process_folder}"
	mkdir -p "${process_folder}/logs"
else
	mkdir -p "${process_folder}/logs"
fi

# counter to create run numbers
k=0

# Loop through list of subjects with ages to create run files, use specified ses_id
while IFS=',' read -r subid ses age rest_of_line; do
	sed -e "s|SUBID|${subid}|g" -e "s|SESID|${ses}|g" -e "s|AGEMO|${age}|g" -e "s|DATADIR|${tmp_dir}|g" -e "s|INPUT|${input_dir}|g" -e "s|OUTPUT|${output_dir}|g" -e "s|RUNDIR|${run_folder}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}
	k=$((k+1))
done < "$subject_list"

email=`echo $USER@umn.edu`
group=`groups|cut -d" " -f1`

chmod 775 -R ${process_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_xcpd.sh 

