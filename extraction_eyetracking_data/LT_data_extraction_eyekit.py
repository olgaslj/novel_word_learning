# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 17:05:38 2021

@author: olgas
"""

# getting fixation durations from LT in NWL
# 11-1-21



from os import scandir #list files in a dir
import os
import pandas as pd
import eyekit
import re
from datetime import datetime


import numpy as _np
from eyekit.fixation import FixationSequence as _FixationSequence, Fixation as _Fixation
from eyekit.text import TextBlock as _TextBlock, InterestArea as _InterestArea
import numpy as _np

# first of many including regressions
def first_of_many_duration(interest_area, fixation_sequence):

   duration = None

   for fixation in fixation_sequence.iter_without_discards():

        if fixation in interest_area:

            if duration is not None:

                return duration

            duration = fixation.duration

   return None

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
os.chdir('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\Olga_experiment\Analyses_main\LT_data_extraction')

# import all 3 rotations and put them in a single dictionary
stimuli1 = pd.DataFrame(pd.read_csv("rot1.csv"))
stimuli2 = pd.DataFrame(pd.read_csv("rot2.csv"))
stimuli3 = pd.DataFrame(pd.read_csv("rot3.csv"))

stimuliTot = pd.concat([stimuli1,stimuli2,stimuli3],axis=0)

stimuliDict = {id:sentence for id, sentence in zip(stimuliTot['id_learning_sen'],stimuliTot['ek_target'])}

# define what will output look like
# output = {'sbj_id':[],'id_learning_sen':[],'target_order':[], 'target':[],'n_of_fix':[],'tot_dur_target':[],'init_dur':[],'fomf_withReg':[],'fom_noReg':[],'single_fix':[],'gaze_dur_target':[],'regs_in_target':[],'gopast_dur_target':[],'postcontext':[],'fomf_postcontext':[], 'single_postcontext':[], 'init_dur_postcontext':[]}

output = {'sbj_id':[],'id_learning_sen':[],'target_order':[], 'complexity':[], 'target':[],'n_of_fix':[],'tot_dur_target':[],'single_fix':[],'gaze_dur_target':[]}


for file in scandir("asc_output_files"): # scandir gets all the files in the directory
    trial_data = eyekit.io.import_asc(file.path,variables=['IMGLOAD CENTER'])[5:]
    
    word_counter_target = {}
    word_counter_postcontext = {}
    
    for i, trial in enumerate(trial_data):
        
        # define the setting
        id_learning_sen = trial['IMGLOAD CENTER'].split("_")[1]
        exp_sent = stimuliDict[id_learning_sen]      
        ek_exp_sent = eyekit.TextBlock(exp_sent,position=(100,550),font_face='Courier New',font_size=25,line_height=100) # transform sentences with marked IAs into eyekit textBlocks; 
        
        complexity = []
        
        if "sf" in id_learning_sen:
            complexity = "sf"
        elif "hf" in id_learning_sen:
            complexity = "hf"
        else:
            complexity = "lf"
        
        # fix the vertical drift
        eyekit.tools.snap_to_lines(trial['fixations'],ek_exp_sent,method='warp')

        
        # discard fixations that are too short
        eyekit.tools.discard_short_fixations(trial['fixations'],threshold=80) # from Pagan 2019 and common sense
        trial['fixations'].purge() # actually deletes those fix
        
        
        # define IAs
        target = ek_exp_sent['target']
        precontext = ek_exp_sent['precontext'] # this is not necessary
        postcontext = ek_exp_sent['postcontext']
       
        
        # extract fixations for IA target
        # first tell it to ignore punctuation
        if target.text[-1] in [":", "," , ";", ";"]:
            target_stripped = target.text[:-1]
            
        
            
        else:
            target_stripped = target.text
        
        # target_stripped = re.sub("[^a-zA-Z0-9]+", "", target.text)
        
        if target_stripped in word_counter_target:
           word_counter_target[target_stripped] += 1
        else:
           word_counter_target[target_stripped] = 1
        
        n_of_fix = eyekit.measure.number_of_fixations(target, trial['fixations'])
        tot_durations_target = eyekit.measure.total_fixation_duration(target,trial['fixations']) # get the total durations
        # init_dur = eyekit.measure.initial_fixation_duration(target,trial['fixations']) # get the initial (first fixation duration) durations
        # fomf_withReg = first_of_many_duration(target,trial['fixations']) # get the initial (first fixation duration) durations
        # fom_noReg = first_of_many_duration_noReg(target,trial['fixations']) # get the initial (first fixation duration) durations
        single_fix = single_fixations(target,trial['fixations'])
        gaze_durations_target = eyekit.measure.gaze_duration(target,trial['fixations']) # get the gaze durations
        # go_past_durations_target = eyekit.measure.go_past_duration(target,trial['fixations'])
        # regs_in_target = eyekit.measure.number_of_regressions_in(target,trial['fixations'])

        

        # # extract fixations for IA spillover
        # if postcontext.text in word_counter_postcontext:
        #     word_counter_postcontext[postcontext.text]+=1
        # else:
        #     word_counter_postcontext[postcontext.text]=1
        #     fomf_postcontext = first_of_many_duration_noReg(postcontext,trial['fixations']) # get the first of many fixations
        #     single_postcontext = single_fixations(postcontext,trial['fixations'])
        #     init_dur_postcontext = eyekit.measure.initial_fixation_duration(postcontext,trial['fixations'])
        # visualize
        # img=eyekit.vis.Image(1920,1080)
        # img.draw_text_block(ek_exp_sent)
        # img.draw_rectangle(target.box, color='red')
        # img.draw_fixation_sequence(trial['fixations'], number_fixations = True)
        # img.save(f"{file.name}_{i}_{id_learning_sen}.png")
        
        
        
#         img = eyekit.vis.Image(1000, 500)
# img.draw_text_block(txt)
# img.draw_rectangle(interest_area.box, color='red')
# img.draw_rectangle(precontext.box, color='blue')
# img.draw_fixation_sequence(fake_data)
# img.save('gopast.png')


# if 'sf' in 'id_learning' write sf in the column


        # writing the output file
        output['sbj_id'].append(file.name.split('_')[0])
        output['id_learning_sen'].append(id_learning_sen)
        output['target_order'].append(word_counter_target[target_stripped])
        output['complexity'].append(complexity)
        output['target'].append(target.text)
        output['n_of_fix'].append(n_of_fix)
        output['tot_dur_target'].append(tot_durations_target)
        # output['init_dur'].append(init_dur)
        # output['fomf_withReg'].append(fomf_withReg)
        # output['fom_noReg'].append(fom_noReg)
        output['single_fix'].append(single_fix)
        output['gaze_dur_target'].append(gaze_durations_target)
        # output['gopast_dur_target'].append(go_past_durations_target)
        # output['regs_in_target'].append(regs_in_target)
        # output['postcontext'].append(postcontext.text)
        # output['fomf_postcontext'].append(fomf_postcontext)
        # output['single_postcontext'].append(single_postcontext)
        # output['init_dur_postcontext'].append(init_dur_postcontext)
        # current_datetime = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
        
outputDF=pd.DataFrame(output)
outputDF.to_csv('output_LT_main_final_9-10-2023.csv', encoding = 'utf-8-sig')
 



