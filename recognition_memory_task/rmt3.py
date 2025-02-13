# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 09:28:30 2020

@author: olgas
"""


# Recognition memory task for NWL
# Olga
# 5-10-2020
# version with different input files for us_te because of the dumbass randomization


# import packages
from psychopy import visual, core, event, gui
import pandas as pd
import random as rn
import os
import os.path
import numpy as np
import copy
import re

# SET WORKING DIRECTORY
os.chdir('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\Olga_experiment\Recognition_Memory_Task')


# SET UP THE ENVIRONMENT

timeStamp = core.getAbsTime()

# get subject info
expInfo = {'ID':'', 'Rot':''}
dlg = gui.DlgFromDict(dictionary=expInfo, title="RMT", order=['ID', 'Rot'])
if not dlg.OK: 
    core.quit() 


# use subj no to set seed
seed = int(expInfo['ID'])
rn.seed(seed) # I HAVE TO CHANGE THIS NUMBER FOR EACH PARTICIPANT
np.random.seed(seed)


#load the practice and stimulus set
practice_sent = pd.read_csv('practice_sentences.csv')
ts_ue = pd.read_csv('RMT_trainedStem_untrainedEnding_14-11-20.csv')
us_te = pd.read_csv('RMT_untrainedStem_trainedEnding_08-12-20.csv')

#select the correct rotation, the same as it was in the Learning Task
rot_no = int(expInfo['Rot'])
# rot_no = 1

if rot_no==1:
    stimuli_set = pd.read_csv('RMT_rot1_16-11-20_revised.csv')
elif rot_no==2:
    stimuli_set = pd.read_csv('RMT_rot2_18-11-20_revised.csv')
else:
    stimuli_set = pd.read_csv('RMT_rot3_18-11-20_revised.csv')



#TRAIEND STEM + UNTRAINED ENDING selection of items

for ts1 in range(len(ts_ue)):
    
    
    #how many rows is for each ending?
    n_row1 = 12
    
    #create random indices for the 4 endings
    indE1 = np.random.randint(0, n_row1)
    indE2 = np.random.randint(n_row1, 2*n_row1)
    indE3 = np.random.randint(2*n_row1, 3*n_row1)
    indE4 = np.random.randint(3*n_row1, 4*n_row1)
    
    indsE1 = [indE1, indE2, indE3, indE4]
    
    #first select 4 items with suffix
    ts_ue_suffDf = ts_ue[['id_suff','nonword_suff']]
    
    
    ts_ue_Suff = ts_ue_suffDf.iloc[indsE1, :]
    ts_ue_Suff.columns = ['id_rmt','target']
    
    while ts_ue_Suff['id_rmt'].str.contains('x').any(): # if the id_rmt column contains 'x', do the loop again
        break
    
    else:
        ts_ue_suff_items = copy.deepcopy(ts_ue_Suff) # if the id_rmt column doesn't contain 'x', save this combination of 4 items

    
for ts2 in range(len(ts_ue)):
    
    
    #how many rows is for each ending?
    n_row1 = 12
    
    #create random indices for the 4 endings
    indE12 = np.random.randint(0, n_row1)
    indE22 = np.random.randint(n_row1, 2*n_row1)
    indE32 = np.random.randint(2*n_row1, 3*n_row1)
    indE42 = np.random.randint(3*n_row1, 4*n_row1)
    
    indsE12 = [indE12, indE22, indE32, indE42]
    #second select 4 items with high frequency
    ts_ue_hfDf = ts_ue[['id_hf','nonword_hf']]
    
    ts_ue_Hf = ts_ue_hfDf.iloc[indsE1, :]
    ts_ue_Hf.columns = ['id_rmt','target']
    while ts_ue_Hf['id_rmt'].str.contains('x').any(): # if the id_rmt column contains 'x', do the loop again
        break
    
    else:
        ts_ue_hf_items = copy.deepcopy(ts_ue_Hf) # if the id_rmt column doesn't contain 'x', save this combination of 4 items

    
#third select 4 items with low frequency; there is no id == 'x', so no need for the while loop
ts_ue_lfDf = ts_ue[['id_lf','nonword_lf']]

ts_ue_lf_items = ts_ue_lfDf.iloc[indsE1, :]
ts_ue_lf_items.columns = ['id_rmt','target']

#UNTRAINED STEM + TRAINED ENDING selection of items
#I have to pick 4 items from suff, hf and lf which all have different endings and different stems, and have id_rmt! = 'x'

# getting the suffix items

us_te_suffDf = us_te[['id_suff','nonword_suff']]
n_row2 = 4 # because there are 4 same stems


for s1 in range(len(us_te_suffDf)):

    indword1 = [] # this will contain indices of chosen items
    
    stemind1 = np.random.permutation(12) # randomize the 12 stems
    stemind1 = stemind1[0:4] # get 4 stems
    
    suffind1 = np.random.permutation(4) # randomize endings
    
    
    for w1 in range(4): # we need 4 items, so range = 4
        indwordT1 = n_row2*stemind1[w1]+suffind1[w1] # get 4 indices which combine a stem from stemind and suffix from suffind, 
                                                #but none of them are repeated
        indword1.append(indwordT1)

        # get the items with ilocs == indword
        us_te_Suff = us_te_suffDf.iloc[indword1, :] # use the generated indices to select items from the df
        us_te_Suff.columns = ['id_rmt','target']

    while us_te_Suff['id_rmt'].str.contains('x').any(): # if the id_rmt column contains 'x', do the loop again
        break
    
    else:
        us_te_suff_items = copy.deepcopy(us_te_Suff) # if the id_rmt column doesn't contain 'x', save this combination of 4 items

        
   

# getting the high frequency items
us_te_hfDf = us_te[['id_hf','nonword_hf']]


for s2 in range(len(us_te_hfDf)):

    indword2 = []
    
    stemind2 = np.random.permutation(12)
    stemind2 = stemind2[0:4]
    
    hfind2 = np.random.permutation(4)
    
    
    for w2 in range(4): # we need 4 items, so range = 4
        indwordT2 = n_row2*stemind2[w2]+hfind2[w2]
        indword2.append(indwordT2)

        # get the items with ilocs == indword
        us_te_Hf = us_te_hfDf.iloc[indword2, :] 
        us_te_Hf.columns = ['id_rmt','target']

    while us_te_Hf['id_rmt'].str.contains('x').any():
        break
    
    else:
        us_te_hf_items = copy.deepcopy(us_te_Hf)



# getting the low frequency items
us_te_lfDf = us_te[['id_lf','nonword_lf']]


for s3 in range(len(us_te_lfDf)):

    indword3 = []
    
    stemind3 = np.random.permutation(12)
    stemind3 = stemind3[0:4]
    
    lfind3 = np.random.permutation(4)
    
    
    for w3 in range(4): # we need 4 items, so range = 4
        indwordT3 = n_row2*stemind3[w3]+lfind3[w3]
        indword3.append(indwordT3)

        # get the items with ilocs == indword
        us_te_Lf = us_te_lfDf.iloc[indword3, :] 
        us_te_Lf.columns = ['id_rmt','target']

    while us_te_Lf['id_rmt'].str.contains('x').any():
        break
    
    else:
        us_te_lf_items = copy.deepcopy(us_te_Lf)



#merge the three endings DFs with "stimuli" DF (i.e. the correct and  recombinant items)
stimuli1 = pd.concat([stimuli_set,ts_ue_suff_items,ts_ue_hf_items,ts_ue_lf_items,us_te_suff_items,us_te_hf_items,us_te_lf_items],axis = 0)
stimuli = stimuli1.reset_index(drop=True) #drop the mixed up index that's result of randomization and concatenation

# create columns that I need for analysis AND get a simple id and save in a column (I don't want two loops with the same iterator so I do it together)

distractor_type = []
real_id = []

for id_item in stimuli['id_rmt']:
    real_id.append(re.findall(r'\d+', id_item))
    last_2 = id_item[-2:]
    if last_2 == "Te":
        distractor_type.append("uste")
    elif last_2 == "rr":
        distractor_type.append("corr")
    elif last_2 == "ec":
        distractor_type.append("rec")
    else:
        distractor_type.append("tsue")
        
# add this column to stimuli df
stimuli['distractor_type'] = distractor_type
# flatten the list of lists
flat_id = [item for sublist in real_id for item in sublist]
stimuli['id'] = flat_id

    
    

# randomize stimuli
num_stimuli = len(stimuli['target'])

num_stimuliRand = stimuli.reindex(rn.sample(range(num_stimuli),num_stimuli))
num_stimuliRand.index = range(num_stimuli)


# register responses and times
response=list()
responseP=list()

#record the IDs of words that have already been shown to a participant
shown_word_id =[]

#current word ID
curr_word_id = []

# define output files
outputFileName = 'out_' + 'sbj' + expInfo['ID'] + '_' + 'rot' + expInfo['Rot'] + '_' + str(timeStamp) + '.csv'

# create window 
win = visual.Window(fullscr=False, color=[-1,-1,-1], units='pix', size = (800,600))

# instructions, goodbyes, messages, feedback
instr_prac = visual.TextStim(win, text="In questa fase dell’esperimento, vedrai alcune parole apparire una alla volta sullo schermo.\n Il tuo compito è di dire se le hai viste durante la fase precedente dell’esperimento o meno. \nPuoi rispondere con SI (tasto verde) o NO (tasto rosso). Per passare alla parola seguente, premi la barra spaziatrice. \n Iniziamo con un po' di pratica. Nella pratica, rispondi SI se conosci la parola oppure NO se non la conosci.", \
                                        color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
instr_main = visual.TextStim(win, text='Ora passiamo al compito vero e proprio. Non avrai più il feedback sulla tua risposta. \nOra dovrai rispondere SI se ti ricordi la parola, o NO se non te la ricordi. \nSe hai qualche dubbio, puoi chiedere ora. Premi la barra quando sei pronto.', \
                                        color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
goodbye = visual.TextStim(win, text="L'esperimento è finito. \n Grazie!", color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
correct = visual.TextStim(win, text="Corretto!", color='green',pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
incorrect = visual.TextStim(win, text="Sbagliato!", color='red',pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
abort_mess = visual.TextStim(win, text="Experiment aborted.", color=[.8,.8,.8], pos=[0,0], ori=0,font='Arial', height=25, wrapWidth=2500)
blank = visual.TextStim(win, text='', color=[.8,.8,.8], pos=[0,0], ori=0)

# this allows to abort experiment whenever by pressing 'q'
if event.getKeys(keyList=['q']):
    abort_mess.draw(win=win)
    win.flip()
    core.wait(1)
    win.close()
    core.quit()
    

# EXPERIMENT STARTS

# show instructions
instr_prac.draw(win=win)
win.flip()
event.waitKeys(keyList=['space'])
win.flip()
core.wait(1)


# PRACTICE LOOP

for iPsent,psentence in enumerate(practice_sent['practice_sentence']):
    
    blank.draw()
    win.flip()
    core.wait(0.3)
    
    if event.getKeys(keyList=['q']):
        abort_mess.draw(win=win)
        win.flip()
        core.wait(1)
        win.close()
        core.quit()
        
    # define clock
    clock=core.Clock()
    
    responsePtemp=[]
    
    real_id_sentP = practice_sent['id_practice'][iPsent]
    pword = visual.TextStim(win, text=psentence, color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
    pword.draw(win=win)
    win.flip()

    responsePtemp = event.waitKeys(keyList=['l','s'],timeStamped=clock)
        
    win.flip()
    core.wait(0.3)

    # append responses and times one after the other        
    # responseP.extend(responsePtemp)
    

    if responsePtemp[0][0]=='s':
        if real_id_sentP not in ['1p', '3p', '5p']:         
            correct.draw(win=win)
            win.flip()
            core.wait(0.5)
            # event.waitKeys(keyList=['space'])
            # win.flip()
            # core.wait(0.5)
        else:    
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.5)
            # event.waitKeys(keyList=['space'])
            # win.flip()
            # core.wait(0.5)
    elif responsePtemp[0][0]=='l':
        if real_id_sentP in ['1p', '3p', '5p']:
            correct.draw(win=win)
            win.flip()
            core.wait(0.5)
            # event.waitKeys(keyList=['space'])
            # win.flip()
            # core.wait(0.5)
        else:
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.5)
            # event.waitKeys(keyList=['space'])
            # win.flip()
            # core.wait(0.5)
            
    win.flip()
    core.wait(0.3)



# instructions for the main trial
instr_main.draw(win=win)
win.flip()
event.waitKeys(keyList=['space'])
win.flip()
core.wait(1)


# MAIN LOOP
for trial_i,trial_num in enumerate(range(num_stimuli)):
    
    blank.draw(win=win)
    win.flip()
    core.wait(0.3)
    
    if event.getKeys(keyList=['q']):
        break
    
    # define clock
    clock=core.Clock()
    # temporary response info
    responseTemp=list()
    # resp_timesTemp=list()
    
    #stim_word=stimuli['target'][trial_num]
    stim_word=visual.TextStim(win, text=num_stimuliRand['target'][trial_num], color=[.8,.8,.8], pos=[0,0], ori=0)
    stim_word.draw(win=win)
    win.flip()
    
    # collect answers    
    responseTemp = event.waitKeys(keyList=['l','s'],timeStamped=clock)
    
    #remember which ID has been shown
    # shown_word_id.append(curr_word_id)
        
    win.flip()
    core.wait(0.2)

    # append responses and times one after the other        
    response.extend(responseTemp)
    
    # set directory
    os.chdir('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\Olga_experiment\Recognition_Memory_Task')
    
    # SAVE TO OUTPUT FILE
    # concatenate and write out
    sbj_id_df = pd.DataFrame({'sbj_id':[expInfo['ID']] * len(num_stimuliRand)})
    # rot_df = pd.DataFrame({'rot':[rot_no] * len(num_stimuliRand)})
    response_df = pd.DataFrame(response)
    randomizationMapping = pd.DataFrame(num_stimuliRand)
    together = pd.concat([sbj_id_df, randomizationMapping, response_df],axis=1)
    together.columns = ['sbj_id', 'id_rmt','rot','target_complexity', 'simple_id','target','distractor_type','id','ans','rt']
    # together.columns = ['id_rmt','target','ans','rt']
    together.to_csv(outputFileName)


# goodbye message
goodbye.draw(win=win)
win.flip()
core.wait(1)

win.close()

# CLOSE EVERYTHING
core.quit()

