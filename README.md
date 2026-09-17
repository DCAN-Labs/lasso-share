## Lasso Share

This repo contains CDNI processing code developed for MRI processing (from BIDS conversion through final XCP-D processed outputs) to be shared collaboratively with Lasso in support of ARIA studies.

To include:

- S3 wrappers for slurm parallel processing submissions
- Computing resources required
- Running dcm2bids for data that includes mag/phase files for NORDIC denoising followed by cuBIDS BIDS validation
- MRI processing pipeline workflow: BIBSNet > fMRIPrep > XCP-D

## BIDS Conversion

**See CDNI documentation for instructions:** 

- [DICOM to BIDS Conversion (Dcm2bids)](https://cdnis-brain.readthedocs.io/dcm2bids/)
- [NORDIC denoising and Dcm2bids3 NORDIC wrapper](https://cdnis-brain.readthedocs.io/nordic/)

### Included code

**MSI Paths/Source Files for code included in this repo:**

- `/projects/standard/moser297/shared/projects/PIP/code/proc-step0.sh`
- `nordic /projects/standard/moser297/shared/projects/PIP/code/proc-step1.sh`
- `/projects/standard/faird/shared/code/internal/utilities/cdniproc/dcm2bids3_dev.py`


FIND: `/projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/init.py`

## BIDS Validation - cuBIDS

We use [cuBIDS](https://cubids.readthedocs.io/en/latest/index.html) for BIDS validation. See [CDNI Brain documentation](https://cdnis-brain.readthedocs.io/bids/). Note that we are only concerned about Errors, not Warnings, although it's helpful to keep both just in case to troubleshoot processing as needed. 

## MRI Processing - COMING SOON:

- rae's processing wrappers and scripts from the negative urgency and neonatal studies (to use as a starting point):
    - `/projects/standard/lewi1538/shared/projects/neg_urg/code/`
    - `/projects/standard/csandova/shared/projects/rae_neonatal/code/`

   