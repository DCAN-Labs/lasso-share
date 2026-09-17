function runnordic(wd,fn_magn_in,fn_phase_in,fn_out,noisevols)

%%% Set args as recommended for fMRI

ARG.magnitude_only=0 % set to 0 if input includes both magnitude + phase timeseries
ARG.temporal_phase=1 % set to 1 for fMRI
ARG.NORDIC=1 % set to 1 to enable NORDIC denoising
ARG.phase_filter_width=10 % use 10 for fMRI 
ARG.noise_volume_last=noisevols % set equal to number of noise frames at end of scan, if present

%%%

addpath(wd) 
cd(wd)

NIFTI_NORDIC(fn_magn_in,fn_phase_in,fn_out,ARG)

end