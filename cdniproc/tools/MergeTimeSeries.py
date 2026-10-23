function MergeTimeSeries(varargin)
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
% Original version written by Eric Feczko on 6/21/19
% Modified by Robert Hermosillo on 6/27/19 to fix a .mat motion reference bug.
% Modified by Robert Hermosillo on 10/01/19: added option to only merge
% time series
% Modified by Robert Hermosillo on 3/5/2020:
% Added an exit upon wb_command concatenation error.
% Added fix to the varargin  loop to skip every other input as a case, so
% that cell arguements would not break the loop.
% Add a fix to remove a hidden "end of line" characters when cells are provided.


output_file = 'thenamelessone';
% wb_command = 'wb_command';
output_motion_file = 'thenamelessone_motion_mat';
if isempty(varargin) == 0
    %for i = 1:size(varargin,2)
    for i = 1:2:size(varargin,2)
        if isstruct(varargin{i}) == 0
            switch(varargin{i})
                case('wb_command')
                    wb_command = varargin{i+1};
                case('TimeSeriesFiles')
                    tseries_fileinfo = varargin{i+1};
                case('MotionFiles')
                    motion_fileinfo = varargin{i+1};
                case('OutputFile')
                    output_file = varargin{i+1};
                case('MotionOutputFile')
                    motion_output_file = varargin{i+1};
            end
        end
    end
end

if exist('tseries_fileinfo','var') ~= 0
    if iscell(tseries_fileinfo)
        tseries_files = tseries_fileinfo;
    else
        fid = fopen(tseries_fileinfo);
        stuff = textscan(fid,'%s');
        tseries_files = stuff{1};
    end
end

if exist('motion_fileinfo','var') ~= 0
    if iscell(motion_fileinfo)
        motion_files = motion_fileinfo;
    else
        fid = fopen(motion_fileinfo);
        stuff = textscan(fid,'%s');
        motion_files = stuff{1};
    end
end

    %Make sure length of motion files matches length of timeseries
    if length(tseries_files) ~= length(motion_files)
        disp(['NOTE: Length of motion .conc file does not match length of ' ...
              'series .conc file.'])
    end

if exist('tseries_fileinfo','var') ~= 0
    merge_command = [ wb_command ' -cifti-merge ' output_file];
    for curr_tseries = 1:length(tseries_files)
        
        tempstr = char(tseries_files{curr_tseries});
        if iscell(tseries_fileinfo)
            
            %tempstr = tempstr(1:end-1); % add a fix here to remove a hidden "end of line" characters.
        else
        end
        merge_command = [merge_command ' -cifti ' tempstr ' ' ];
    end
    disp(['This command will be run: ' merge_command]) %Robert added this so the user can see what wb_command is being run.
    [status,cmdout] = system(merge_command);
    
    
    if status == 0 % Do not continue if there was in error wb_command
        disp('No concatenation issues.')
    else
        disp(cmdout)
        disp('Error while running merge. Exiting...');
        return
    end
end

if exist('motion_fileinfo','var') ~= 0
    if iscell(motion_fileinfo) % add a fix here to remove a hidden "end of line" characters.
        tempstr = char(motion_files{1});
        %         tempstr = tempstr(1:end-1);
        check_length = load(tempstr);
    else
        check_length = load(motion_files{1});
    end
    
    motion_data = cell(1,length(check_length.motion_data));
    clear check_length
    
    for curr_motion_file = 1:length(motion_files)
        if iscell(motion_fileinfo) % add a fix here to remove a hidden "end of line" characters.
            tempstr = char(motion_files{curr_motion_file});
            %tempstr = tempstr(1:end-1);
            temp_motion = load(tempstr);
        else
            temp_motion = load(motion_files{curr_motion_file});
        end
        
        for curr_threshold = 1:length(temp_motion.motion_data)
            %my_fields = motion_data{1};
            my_fields = temp_motion(1).motion_data{1};
            if curr_motion_file == 1
                motion_data{curr_threshold}.skip = temp_motion.motion_data{curr_threshold}.skip;
                if isfield(my_fields,'epi_TR') ==1 % assume that all FDs are strustured the same way.
                    motion_data{curr_threshold}.epi_TR = temp_motion.motion_data{curr_threshold}.epi_TR;
                end
                motion_data{curr_threshold}.FD_threshold = temp_motion.motion_data{curr_threshold}.FD_threshold;
                motion_data{curr_threshold}.frame_removal = temp_motion.motion_data{curr_threshold}.frame_removal;
                if isfield(my_fields,'format_string') ==1 % assume that all FDs are strustured the same way.
                    motion_data{curr_threshold}.format_string = temp_motion.motion_data{curr_threshold}.format_string;
                end
                motion_data{curr_threshold}.total_frame_count = temp_motion.motion_data{curr_threshold}.total_frame_count;
                motion_data{curr_threshold}.remaining_frame_count = temp_motion.motion_data{curr_threshold}.remaining_frame_count;
                motion_data{curr_threshold}.remaining_seconds = temp_motion.motion_data{curr_threshold}.remaining_seconds;
                motion_data{curr_threshold}.remaining_frame_mean_FD = temp_motion.motion_data{curr_threshold}.remaining_frame_mean_FD;
            else
                %motion_data{curr_threshold}.frame_removal(end+1:end+length(temp_motion.motion_data{curr_threshold}.frame_removal)) = temp_motion.motion_data{curr_threshold}.frame_removal;
                if isfield(my_fields,'epi_TR') ==1 % assume that all FDs are strustured the same way.
                    motion_data{curr_threshold}.epi_TR = temp_motion.motion_data{curr_threshold}.epi_TR;
                end
                if isfield(my_fields,'format_string') ==1
                    motion_data{curr_threshold}.format_string = [motion_data{curr_threshold}.format_string '+' temp_motion.motion_data{curr_threshold}.format_string];
                end
                if isfield(my_fields,'frame_removal') ==1
                    motion_data{curr_threshold}.frame_removal(end+1:end+length(temp_motion.motion_data{curr_threshold}.frame_removal)) = temp_motion.motion_data{curr_threshold}.frame_removal;
                    %motion_data{curr_threshold}.frame_removal = [motion_data{curr_threshold}.frame_removal; temp_motion.motion_data{curr_threshold}.frame_removal];
                end
                motion_data{curr_threshold}.total_frame_count = motion_data{curr_threshold}.total_frame_count + temp_motion.motion_data{curr_threshold}.total_frame_count;
                motion_data{curr_threshold}.remaining_frame_count = motion_data{curr_threshold}.remaining_frame_count + temp_motion.motion_data{curr_threshold}.remaining_frame_count;
                motion_data{curr_threshold}.remaining_seconds = motion_data{curr_threshold}.remaining_seconds + temp_motion.motion_data{curr_threshold}.remaining_seconds;
                motion_data{curr_threshold}.remaining_frame_mean_FD = motion_data{curr_threshold}.remaining_frame_mean_FD + temp_motion.motion_data{curr_threshold}.remaining_frame_mean_FD;
            end
        end
    end
    for curr_threshold = 1:length(temp_motion.motion_data)
        motion_data{curr_threshold}.remaining_frame_mean_FD = motion_data{curr_threshold}.remaining_frame_mean_FD/length(motion_files);
    end
    disp(['saving motion file :' motion_output_file]);
    save(motion_output_file,'motion_data'); %change variable to string for saving -RH
    disp('Done concatenating times series and motion files') %Aded display to let the user know when it is done running.
else
    disp('Done concatenating times series') %Aded display to let the user know when it is done running.
    
    
end

