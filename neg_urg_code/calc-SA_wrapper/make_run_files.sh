#!/bin/bash

set +x 
# determine data directory, run folders, and run templates
derivs_dir="/projects/standard/lewi1538/shared/projects/neg_urg/derivatives" # where to output data
ses_id="1"
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

# Method 4: Loop through tier1 bids dir
for i in `ls ${derivs_dir}/template_matching/ | awk '{print $1}'`; do
	# Check if folder is subject folder
	sub_text=`echo ${i} | awk -F"/" '{print $(NF-1)}' | awk -F"-" '{print $1}'`
	if [ "sub" = "${sub_text}" ]; then # if parsed text matches to "sub", continue
		subj_id=`echo ${i} | awk -F"/" '{print $(NF-1)}' | awk  -F"-" '{print $2}'`
		sed -e "s|SUBJECTID|${subj_id}|g" -e "s|SESID|${ses_id}|g" -e "s|DERIVS|${derivs_dir}|g" ${run_folder}/${process_template} > ${process_folder}/run${k}
		k=$((k+1))
	fi
done
				
chmod 775 -R ${process_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_calcSA.sh 

