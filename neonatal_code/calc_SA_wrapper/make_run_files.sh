#!/bin/bash

set +x 
# determine data directory, run folders, and run templates
derivs_dir="/projects/standard/csandova/shared/projects/rae_neonatal/derivatives" # where to output data
subject_list="/projects/standard/csandova/shared/projects/rae_neonatal/code/calc_SA_wrapper/missing_BCP_subjects_28Jul.txt" # optional: specifiy a list of subjects to run
run_folder=`pwd`

process_folder="${run_folder}/run_files.calcSA"
process_template="template.calcSA"

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

# Method 2: Loop through list of subject/session pairs to create run files; expecting file to be formatted "sub-SUBID,ses-SESID" with each pair on a new line
## Code when running neonatal subjects
#sesid=1
#while IFS=',' read -r subid age rest_of_line; do
	#sed -e "s|SUBJECTID|${subid}|g" -e "s|SESID|${sesid}|g" -e "s|DERIVS|${derivs_dir}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}
	#k=$((k+1))
#done < "$subject_list"
# Code when running BCP subjects
while IFS=',' read -r subid sesid rest_of_line; do
	sed -e "s|SUBJECTID|${subid}|g" -e "s|SESID|${sesid}|g" -e "s|DERIVS|${derivs_dir}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}
	k=$((k+1))
done < "$subject_list"

chmod 775 -R ${process_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_calcSA.sh 

