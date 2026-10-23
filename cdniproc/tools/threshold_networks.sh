#!/bin/bash


parent=/scratch.global/kweldon/attune/derivatives/fmriprep-24.1.1-xcpd-0.9.1/GPA59/
file_dir=${parent}/visualization_files/
network_file=${parent}/network_thresholds.txt
#make a binary
tail -n +2 ${network_file} | while read -r network source threshold; do
	echo "Network: $network"
	echo "Source: $source"
	echo "Threshold: $threshold"
	echo ${source}
	if [[ "$source" = "ABCD" ]]; then
		in_file=${file_dir}/abcd_${network}_network_thres.dscalar.nii
		out_file=${file_dir}/abcd_${network}_${threshold}thres_binary.dscalar.nii
		wb_command -cifti-math "x >= $threshold" ${out_file} -var x ${in_file}
		echo wb_command -cifti-math "x >= $threshold" ${out_file} -var x ${in_file}
	else
		in_file=${file_dir}/Probability_Maps_across_perms_TM_Percent_holdout_${network}_network_probability.dscalar.nii
		out_file=${file_dir}/pcm_${network}_${threshold}thres_binary.dscalar.nii
		#wb_command -cifti-math 'x >= ${threshold}' ${out_file} -var x ${in_file}
		echo wb_command -cifti-math "x >= $threshold" ${out_file} -var x ${in_file}
		wb_command -cifti-math "x >= $threshold" ${out_file} -var x ${in_file}
		#wb_command -cifti-math "x * (x >= 2.5)" -fixnan 0 ${out_file} -var x ${in_file}
	fi
	echo "----"
done

#wb_command -cifti-math 'x >= ${threshold}' ${out_file} -var x ${in_file}

#make a probalistic
#addpath(genpath('/projects/standard/faird/shared/code/external/utilities/gifti-1.6/'));
#addpath('/projects/standard/faird/shared/code/internal/utilities/Matlab_CIFTI');
#mycifti = ciftiopen('/projects/standard/rando149/shared/projects/ABCD_net_template_matching_2.0/results/probabilistic_maps/SCAN_network_thres.dscalar.nii','/common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command')
#mydata = mycifti.cdata;
#mydata(mydata<=0.2) = nan;
#mycifti.cdata = mydata;
#ciftisave(mycifti, '/scratch.global/kweldon/STD/myoutputSCAN_cont.dscalar.nii','/common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command')

tail -n +2 ${network_file} | while read -r network source threshold; do
	echo "Network: $network"
	echo "Source: $source"
	echo "Threshold: $threshold"
	echo ${source}
	if [[ "$source" = "ABCD" ]]; then
		in_file=${file_dir}/abcd_${network}_network_thres.dscalar.nii
		out_file=${file_dir}/abcd_${network}_${threshold}thres_prob.dscalar.nii
		if [[ "$threshold" != 1 ]]; then
			matlab -nodisplay -nosplash -r "addpath(genpath('/projects/standard/faird/shared/code/external/utilities/gifti-1.6/'));addpath('/projects/standard/faird/shared/code/internal/utilities/Matlab_CIFTI');mycifti=ciftiopen('${in_file}','/common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command');mydata=mycifti.cdata;mydata(mydata<=${threshold})=nan;mycifti.cdata=mydata;ciftisave(mycifti,'${out_file}','/common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command');exit;"
		else
			cp $in_file $out_file
		fi
	else
		in_file=${file_dir}/Probability_Maps_across_perms_TM_Percent_holdout_${network}_network_probability.dscalar.nii
		out_file=${file_dir}/pcm_${network}_${threshold}thres_prob.dscalar.nii
		if [[ "$threshold" != 1 ]]; then
			matlab -nodisplay -nosplash -r "addpath(genpath('/projects/standard/faird/shared/code/external/utilities/gifti-1.6/'));addpath('/projects/standard/faird/shared/code/internal/utilities/Matlab_CIFTI');mycifti=ciftiopen('${in_file}','/common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command');mydata=mycifti.cdata;mydata(mydata<=${threshold})=nan;mycifti.cdata=mydata;ciftisave(mycifti,'${out_file}','/common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command');exit;"
		else
			cp $in_file $out_file

		fi
	fi
	echo "----"
done
