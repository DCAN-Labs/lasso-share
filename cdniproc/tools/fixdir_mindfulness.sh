#!/bin/bash -l

#SBATCH -J fixdir
#SBATCH -c 4
#SBATCH --mem=100G
#SBATCH -t 1:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kweldon@umn.edu
#SBATCH -p ag2tb
#SBATCH -o output_logs/fixdir_%A_%a.out
#SBATCH -e output_logs/fixdir_%A_%a.err
#SBATCH -A nardosr

SUB=${1} 

#SUB-20001-01_vc50654_20211109/scans/

for directory in ${SUB}*; do
    echo $directory
    for dir2 in $directory/mnt/rose/shared/data/NARDOS/*/*/*; do
        if [ -d "$dir2" ]; then
            echo $dir2
            mv $dir2 $directory/.
            #unzip "$zipfile"
        fi
    done
    #rmdir $directory/scans
done

#for directory in ${SUB}*; do
#    echo $directory
#    rmdir $directory/scans
#    for dicomdir in $directory/*; do
#        if [ -d "$dicomdir" ]; then
#            echo $dicomdir
#            mv $dicomdir/resources/secondary/files/* $dicomdir/.
#            mv $dicomdir/resources/DICOM/files/* $dicomdir/.
#            rmdir $dicomdir/resources/secondary/files
#            rmdir $dicomdir/resources/DICOM/files
#            rmdir $dicomdir/resources/secondary
#            rmdir $dicomdir/resources/DICOM
#            rmdir $dicomdir/resources
#            #unzip "$zipfile"
#        fi
#    done
#done

#echo 'finished fixing directories'