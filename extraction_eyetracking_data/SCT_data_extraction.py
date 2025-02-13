# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 18:01:31 2021

@author: olgas
"""
# getting fixation durations from ET_SCT task in NWL
# 4-1-21


import os
from os import scandir #list files in a dir
import pandas as pd
import eyekit


import numpy as _np
from eyekit.fixation import FixationSequence as _FixationSequence, Fixation as _Fixation
from eyekit.text import TextBlock as _TextBlock, InterestArea as _InterestArea
import numpy as _np

def discard_long_fixations(fixation_sequence, threshold=1200):
    """
    Given a `eyekit.fixation.FixationSequence`, discard all fixations that are
    longer than some threshold value. Operates directly on the sequence and
    does not return a copy.
    """
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type eyekit.FixationSequence")
    for fixation in fixation_sequence.iter_without_discards():
        if fixation.duration > threshold:
            fixation.discard()


# first of many excluding regressions
def first_of_many_duration_noReg(interest_area, fixation_sequence):
    """
    Given an interest area and fixation sequence, return the first of many fixations duration
    if there is more than one fixation during the first pass in the interest area.
    Return None if there is more than one fixation only when more than one pass is considered.
    Return None if there is a single fixation during the first pass.
    First of many fixations is the first fixation in an interest area only in cases
    there is more than one fixation in the first pass.
    
    """
    duration = None
    current_pass = None
    next_pass = 1
    entered = False
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            entered = True
            if current_pass is None:  # first fixation in a new pass
                current_pass = next_pass # we are in the first pass now
                if duration is not None: # if in the first pass there is a fixation, give me its duration
                    return duration 
                duration = fixation.duration # give me the duration of the first fixation in the first pass
            elif current_pass is not None: # check if there is more than one pass; if yes, we want duration to stay as it was in the first pass
                if current_pass >= 1:
                    return duration
        if entered: # if we are in the interest area
            if interest_area.is_before(fixation): # if IA is before the fixation, we want to keep only the first fixation from the first pass
                return None
            if interest_area.is_after(fixation): # if IA, is after the fixation, we want to keep only the first fixation from the first pass
                    return None
    return None

# single fixations
def single_fixations(interest_area, fixation_sequence):
    fixations_in_first_pass = []
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            fixations_in_first_pass.append(fixation)
        elif fixations_in_first_pass:
            # The current fixation is not in the IA (implied by the else), but
            # at least one previous fixation was in the IA (i.e. the
            # fixations_in_first_pass list is not empty). In other words, the
            # current fixation is the first one to exit the IA, so we break
            # out of the for loop.
            break
    if len(fixations_in_first_pass) == 1: # if there is only one fixation in the first pass, that is single fixation
        return fixations_in_first_pass[0].duration # ...so return the duration of the first (and only) one
    return None # in any other situation, return None



# set wd
os.chdir('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\Olga_experiment\Analyses_main\SCT_data_extraction')

# import both rotations and put them in a single dictionary
stimuli = {1:pd.read_csv("sct_stim_rot1_revised.csv"), 2:pd.read_csv("sct_stim_rot2_revised.csv")}

# define what will output look like
output = {'sbj_id':[],'rot':[],'sent_id':[],'congruency':[],'baseword':[],'count_fix':[],'tot_dur':[],'init_dur':[],'single_fix':[],'fomf_dur':[],'gaze_dur':[], "ssp_dur":[]}



for file in scandir("asc_files//all"): # scandir gets all the files in the directory
    sbj_data_path = f"behavioral_files//all//{file.name.split('.')[0] + '.csv'}" # get the names of the behavioral outputs; I don't understand why split at '.' and not '_' (file names are formated as 1_1.csv)
    dataF=pd.read_csv(sbj_data_path) # create a df with outputs from all subjects (only behavioral data)
    trial_data = eyekit.io.import_asc(file.path) # get eye tracking data
    exp_trials = trial_data[-18:] # select the last 18 trials (because the first 5 were practice)
    rotation = (dataF["rot"][0]) # define rotation
    
    for row, trial in zip(dataF.itertuples(),exp_trials): # merge/zip the df with behavioral data and eyetracking data
        congruency = row[7] # get congruency info, needed for output later # first with complexity 3 # second 6 # together 7
        sent_id = row[3] # get id of each sentence # first with complexity 2 #second 2 # together 3
        exp_sent = stimuli[rotation]['ek_target'][sent_id-1] # define sentences with marked IAs in the input files

        ek_exp_sent = eyekit.TextBlock(exp_sent,position=(100,550),font_face='Courier New',font_size=25,line_height=100) # transform sentences with marked IAs into eyekit textBlocks; 
                                                                                                                         # we checked the position manually because in the experimental code
                                                                                                                         # it's defined as pos=(0,0) and left aligned, but this seems accurate;
                                                                                                                         # font_size is the same as psychopy's height apparently
        
        # fix the vertical drift
        eyekit.tools.snap_to_lines(trial['fixations'],ek_exp_sent,method='warp')
        
        # discard fixations that are too short
        eyekit.tools.discard_short_fixations(trial['fixations'],threshold=80) # from Pagan 2019 and common sense
        trial['fixations'].purge()
        
        # #discard fixations that are too long
        # discard_long_fixations(trial['fixations'],threshold = 1200) # by looking at histogram
        # trial['fixations'].purge()         # actually deletes those fix                                                                                         
        
        
        # # this is to create images if you want to visualize                                                                                                                 
        img=eyekit.vis.Image(1920,1080)
        img.draw_text_block(ek_exp_sent)
        img.draw_rectangle(ek_exp_sent['baseword'].box, color='red')
        img.draw_fixation_sequence(trial['fixations'], number_fixations=True)
        img.save(f"images_all//{file.name}_{sent_id}.png")
        
       
        baseword = ek_exp_sent['baseword'] # define the IA variable
        
        count_fix = eyekit.measure.number_of_fixations(baseword, trial['fixations'])
        tot_durations = eyekit.measure.total_fixation_duration(baseword,trial['fixations']) # get the total durations
        fomf_durations = first_of_many_duration_noReg(baseword,trial['fixations']) # get the initial (first fixation duration) durations
        initial_durations = eyekit.measure.initial_fixation_duration(baseword, trial['fixations'])
        single_fix = single_fixations(baseword, trial['fixations'])
        gaze_durations = eyekit.measure.gaze_duration(baseword,trial['fixations']) # get the gaze durations
        ss_pass_durations = eyekit.measure.second_pass_duration(baseword, trial['fixations'])
        
        # writing the output file
        output['sbj_id'].append(file.name.split('_')[0])
        output['rot'].append(rotation)
        output['sent_id'].append(sent_id)
        output['congruency'].append(congruency)
        output['baseword'].append(baseword.text)
        output['count_fix'].append(count_fix)
        output['tot_dur'].append(tot_durations)
        output['init_dur'].append(initial_durations)
        output['single_fix'].append(single_fix)
        output['fomf_dur'].append(fomf_durations)
        output['gaze_dur'].append(gaze_durations)
        output['ssp_dur'].append(ss_pass_durations)
        
        print(f"Processed '{file}'.")

outputDF=pd.DataFrame(output)
outputDF.to_csv('output_ETSCT_main_final_10-10-23.csv',encoding = 'utf-8-sig')

        

        
        
        

