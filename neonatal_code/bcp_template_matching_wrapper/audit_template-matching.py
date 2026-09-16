from datetime import datetime
from glob import glob
import pandas as pd 
import os

subjects = pd.read_csv("/projects/standard/csandova/shared/projects/rae_neonatal/code/bcp_xcpd_wrapper/BCP_subjects_w_ages.csv", names=["subject","session","age"],dtype=str)
statuses = pd.DataFrame(columns=["subject","session","age","finished"])
derivs = "/projects/standard/csandova/shared/projects/rae_neonatal/derivatives/bcp_template_matching/abcd"
outdir = "/projects/standard/csandova/shared/projects/rae_neonatal/code/bcp_template_matching_wrapper"

for index, row in subjects.iterrows():
    sub = row["subject"]
    ses = row["session"]
    status = os.path.exists(os.path.join(derivs, f"sub-{sub}",f"sub-{sub}_ses-{ses}_task-rest_space-fsLR_den-91k_desc-denoised_bold_spatially_interpolated_template_matched_Zscored_scanthresh3.dscalar.nii"))
    new_row = pd.DataFrame({"subject":[sub],"session":[ses],"age":[row["age"]],"finished":[status]})
    statuses = pd.concat([statuses,new_row],ignore_index=True)


today = datetime.today()
ran_on = today.strftime(f"%b-%d-%H%M")
statuses.to_csv(f"{outdir}/{ran_on}_template_matching_audit.csv",index=False)


