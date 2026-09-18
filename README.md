## Lasso Share

This repo contains CDNI processing code developed for MRI processing (from BIDS conversion through final XCP-D processed outputs) to be shared collaboratively with Lasso in support of ARIA studies.

To include:

- S3 wrappers for slurm parallel processing submissions
- Computing resources required
- Running dcm2bids for data that includes mag/phase files for NORDIC denoising followed by cuBIDS BIDS validation
- MRI processing pipeline workflow: BIBSNet > fMRIPrep > XCP-D


**See draft of [MRI BIDS Conversion & Processing](https://docs.google.com/document/d/1CCugm-_wS9c2b56J_0R6bcqgG_t72ofCpYKIikXt_wY/edit?tab=t.3na71if8sw3w) workflow.**

---

## BIDS Conversion

**See CDNI documentation for instructions:** 

- [DICOM to BIDS Conversion (Dcm2bids)](https://cdnis-brain.readthedocs.io/dcm2bids/)
- [NORDIC denoising and Dcm2bids3 NORDIC wrapper](https://cdnis-brain.readthedocs.io/nordic/)

### Included code

#### Generate config for conversion
See: `BIDS_conversion/src/create_config/*`

Includes K. Weldon's workflow for generating config file automatically from reading DICOM header info; generates a series of JSON and TSV files with sidecar information. 

#### NORDIC denoising
See: `BIDS_conversion/src/convert/proc_step1.sh`


#### Convert to BIDS
See: `BIDS_conversion/src/convert/dcm2bbids3_dev.py`


#### MSI Paths/Source Files for code included in this repo:

- `/projects/standard/moser297/shared/projects/PIP/code/proc-step0.sh`
- `nordic /projects/standard/moser297/shared/projects/PIP/code/proc-step1.sh`
- `/projects/standard/faird/shared/code/internal/utilities/cdniproc/dcm2bids3_dev.py`
- `/projects/standard/moser297/shared/projects/PIP/code/data_prep_bf.sh`
- `/projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/archive/init.py`


---

## BIDS Validation - cuBIDS [v1.2.1]

We use [cuBIDS](https://cubids.readthedocs.io/en/latest/index.html) for BIDS validation. See [CDNI Brain documentation](https://cdnis-brain.readthedocs.io/bids/). Note that we are only concerned about Errors, not Warnings, although it's helpful to keep both just in case to troubleshoot processing as needed. 

---

## MRI Processing - COMING SOON:

- rae's processing wrappers and scripts from the negative urgency and neonatal studies (to use as a starting point):
    - `/projects/standard/lewi1538/shared/projects/neg_urg/code/`
    - `/projects/standard/csandova/shared/projects/rae_neonatal/code/`

- To be added: BIBSNet SLURM wrapper
- 
### MRI Processing external dependencies:
	- ANTs 2.5.4
	- AFNI 16.1.13
	- GCC 9.2.0
    - MATLAB R2019a
	- FSL 6.0.x
	- LayNii 2.6.0
	- Connectome Workbench 2.0.1
- 

   


