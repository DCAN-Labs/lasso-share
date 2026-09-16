#!/bin/bash

set +x 
# determine data directory, run folders, and run templates
deriv_dir="/projects/standard/csandova/shared/projects/rae_neonatal/derivatives/xcpd/bcp"
output_dir="/projects/standard/csandova/shared/projects/rae_neonatal/derivatives"
run_folder=`pwd`
#subject_list="/projects/standard/csandova/shared/projects/rae_neonatal/code/bcp_xcpd_wrapper/BCP_subjects_w_ages.csv" # optional: specifiy a list of subjects to run
subject_list="/projects/standard/csandova/shared/projects/rae_neonatal/code/bcp_template_matching_wrapper/rerun_BCP_subjects_7-Apr.csv"

process_folder="${run_folder}/run_files.abcd-tempmatch"
process_template="template.abcd-tempmatch"

email=`echo $USER@umn.edu`
group=`groups|cut -d" " -f1`

# if processing run folders (sMRI, fMRI,) exist delete them and recreate
if [ -d "${process_folder}" ]; then
	rm -rf "${process_folder}"
	mkdir -p "${process_folder}"
else
	mkdir -p "${process_folder}"
fi

# counter to create run numbers
k=0

# Loop through list of subjects with ages to create run files, use specified ses_id
while IFS=',' read -r subid sesid age rest_of_line; do
	sed -e "s|SUBID|${subid}|g" -e "s|SESID|${sesid}|g" -e "s|DERIVS|${deriv_dir}|g" -e "s|OUTPUT|${output_dir}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}
	k=$((k+1))
done < "$subject_list"

chmod 775 -R ${process_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_process.sh 

