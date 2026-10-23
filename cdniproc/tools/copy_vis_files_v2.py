#!/usr/bin/env python3
"""
Copy visualization files from a pipeline subject directory.

Usage:
    copy_vis_files_v2.py <pipeline_subject_dir> [output_dir]

    pipeline_subject_dir : full path to the subject's pipeline output directory
                           e.g. .../fmriprep25.2.2-xcpd0.14.1/output/TCB27
    output_dir           : (optional) destination directory for copied files
                           defaults to <pipeline_subject_dir>/visualization_files
"""

import os
import sys
import glob
import shutil


def copy_vis_files(pipeline, output_dir=None):
    pipeline = pipeline.rstrip(os.sep)
    subjID = os.path.basename(pipeline)
    print(f"Subject ID: {subjID}")

    if output_dir is None:
        output_dir = os.path.join(pipeline, 'visualization_files')
    print(f"Output directory: {output_dir}")

    # Search within sub-*/ses-*/ inside the pipeline subject dir
    anat_base = os.path.join(pipeline, 'sub-*', 'ses-*', 'anat')
    func_base = os.path.join(pipeline, 'sub-*', 'ses-*', 'func')

    input_list = []
    input_list += glob.glob(os.path.join(anat_base, '*surf*'))
    input_list += glob.glob(os.path.join(anat_base, '*preproc*'))
    input_list += glob.glob(os.path.join(anat_base, '*FD_only.mat'))
    input_list += glob.glob(os.path.join(func_base, '*FD_only.mat'))
    input_list += glob.glob(os.path.join(func_base, '*inter*'))

    # Filter out non-native resolutions
    input_list = [f for f in input_list if 'res-' not in f]

    # PCM files — only if directory exists
    pcm_dir = os.path.join(pipeline, 'PCM', 'ExpData-fullm', 'figures', 'Percent_Holdout-100', 'ciftis')
    if os.path.exists(pcm_dir):
        input_list += glob.glob(os.path.join(pcm_dir, 'Probability_Maps_across_perms_TM_Percent_holdout_*_network_probability.dscalar.nii'))
        input_list += glob.glob(os.path.join(pcm_dir, 'Mode_of_Shuffled_dscalars_Percent_holdout_population_mode.dlabel.nii'))

    if not input_list:
        print("Warning: no files found to copy.")

    # Copy
    os.makedirs(output_dir, exist_ok=True)
    for f in input_list:
        try:
            shutil.copy2(f, output_dir)
            print(f"Copied: {os.path.basename(f)}")
        except Exception as e:
            print(f"Warning: could not copy {f}: {e}")

    print(f"\nDone. {len(input_list)} files copied to {output_dir}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("Usage: copy_vis_files_v2.py <pipeline_subject_dir> [output_dir]")

    pipeline   = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    copy_vis_files(pipeline, output_dir)
