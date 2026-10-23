#!/bin/bash -l

#SBATCH -J seedmap
#SBATCH -c 24
#SBATCH --mem=100G
#SBATCH -t 1:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kweldon@umn.edu
#SBATCH -p ag2tb,agsmall,aglarge
#SBATCH -o output_logs/seedmap_%A_%a.out
#SBATCH -e output_logs/seedmap_%A_%a.err
#SBATCH -A bell0130

#SUB=GPA22
#SES=01

SUB=${1}
SES=${2}

TASK=restNORDIC
PARENT=/scratch.global/kweldon/attune/derivatives/fmriprep-24.0.1-xcpd-0.10.7/
INPUTFILES=${PARENT}/${SUB}/analysis_input_files/
SEEDMAPDIR=${PARENT}/${SUB}/seedmaps/${SES}/
SEEDMAPDIRBASE=${PARENT}/${SUB}/seedmaps/

if [ ! -d ${SEEDMAPDIR} ]; then
  mkdir -p ${SEEDMAPDIR}
fi  

module load matlab/R2019a 
module load workbench/1.5.0

#confmap=${SEEDMAPDIRBASE}/cortex_only_roi.dscalar.nii

##orig file
confmap=${PARENT}/${SUB}/PCM/combined/${TASK}/ExpData-fullm/figures/Percent_Holdout-100/ciftis/Probability_Maps_across_perms_TM_Percent_holdout_SCAN_network_probability.dscalar.nii

#echo ${confmap}
#exit 0

label_base=SCAN_conf_clusters

dtseries=${INPUTFILES}/sub-${SUB}_ses-${SES}_task-${TASK}_space-fsLR_den-91k_desc-denoised_bold_spatially_interpolated.dtseries.nii 

motionfile=${INPUTFILES}/sub-${SUB}_ses-${SES}_task-${TASK}_desc-abcc_qc_power_2014_FD_only.mat

left_surf=${INPUTFILES}/sub-${SUB}_hemi-L_space-fsLR_den-32k_desc-hcp_midthickness.surf.gii

right_surf=${INPUTFILES}/sub-${SUB}_hemi-R_space-fsLR_den-32k_desc-hcp_midthickness.surf.gii


thr=0.8

#sh /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/confmap2seed.sh --confmap ${confmap} --dtseries ${dtseries} --left_surf ${left_surf} --right_surf ${right_surf} --thr ${thr} --outdir ${SEEDMAPDIR} --label_base ${label_base} --motion_conc ${motionfile}
sh /projects/standard/faird/shared/code/internal/analytics/TemplateShuffle/code/functions/confmap2seed_kw.sh --confmap ${confmap} --dtseries ${dtseries} --left_surf ${left_surf} --right_surf ${right_surf} --thr ${thr} --outdir ${SEEDMAPDIR} --label_base ${label_base} --motion_conc ${motionfile}

#maximum=1

#how many clusters?
maximum=$(wb_command -file-information ${SEEDMAPDIR}/SCAN_conf_clusters_clust-thr0.dscalar.nii | awk '/Map[[:space:]]+Minimum[[:space:]]+Maximum/ {getline; print int($3)}')
#find out TR
TR=$(wb_command -file-information ${dtseries} -only-step-interval)

echo 'making seedmaps!'
#make a seedmap for every cluster
for ((i=1; i<=maximum; i++)); do
echo ${i}
#python /projects/standard/faird/shared/code/internal/utilities/seed_map_wrapper/seed_map_wrapper.py 1.761 ${SEEDMAPDIR}/dt.conc ${SEEDMAPDIR}/clust_pt.conc ${i} -mre /common/software/install/migrated/matlab/R2019a/v96 -wb /common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command --fd-threshold 0.2 --left ${SEEDMAPDIR}/left_surf.conc --right ${SEEDMAPDIR}/right_surf.conc --motion ${SEEDMAPDIR}/motion.conc --output ${SEEDMAPDIR}/clusters/
python /projects/standard/faird/shared/code/internal/utilities/seed_map_wrapper/seed_map_wrapper.py ${TR} ${SEEDMAPDIR}/dt.conc ${SEEDMAPDIR}/clust_pt.conc ${i} -mre /common/software/install/migrated/matlab/R2019a/v96 -wb /common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command --fd-threshold 0.2 --left ${SEEDMAPDIR}/left_surf.conc --right ${SEEDMAPDIR}/right_surf.conc --motion ${SEEDMAPDIR}/motion.conc --output ${SEEDMAPDIR}/clusters/
done

#make a seedmap for the combined cluster
python /projects/standard/faird/shared/code/internal/utilities/seed_map_wrapper/seed_map_wrapper.py ${TR} ${SEEDMAPDIR}/dt.conc ${SEEDMAPDIR}/bin_pt.conc 1 -mre /common/software/install/migrated/matlab/R2019a/v96 -wb /common/software/install/migrated/workbench/1.5.0/bin_rh_linux64/wb_command --fd-threshold 0.2 --left ${SEEDMAPDIR}/left_surf.conc --right ${SEEDMAPDIR}/right_surf.conc --motion ${SEEDMAPDIR}/motion.conc --output ${SEEDMAPDIR}/
