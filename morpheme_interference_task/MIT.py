# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 09:28:30 2020

@author: olgas
"""


# Morpheme Intereference Task for NWL
# Olga
# 30-11-2020


# import packages
from psychopy import visual, core, event, gui
import pandas as pd
import random as rn
import os
import os.path
import numpy as np
import copy

# SET WORKING DIRECTORY
os.chdir('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\\Morpheme_Interference_Task')


# SET UP THE ENVIRONMENT

timeStamp = core.getAbsTime()

# get subject info
expInfo = {'ID':'', 'Rot':''}
dlg = gui.DlgFromDict(dictionary=expInfo, title="MIT", order=['ID', 'Rot'])
if not dlg.OK: 
    core.quit() 


# use subj no to set seed
seed = int(expInfo['ID'])
rn.seed(seed) # I HAVE TO CHANGE THIS NUMBER FOR EACH PARTICIPANT
np.random.seed(seed)


#load the practice and stimulus set
practice_sent = pd.read_csv('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\\Morpheme_Interference_Task\\practice_sentences.csv')
stimuli_set = pd.read_csv('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\\Morpheme_Interference_Task\\mit_stim_new_version.csv')


## create the 2 rotations

# split targets into 2 sets of 30
first_30_tar = stimuli_set.loc[:29,'id':'target']
second_30_tar = stimuli_set.loc[30:,'id':'target']

# split distractors into 2 sets of 30
first_30_dist = stimuli_set.loc[:29,'id.1':'distractor']
second_30_dist = stimuli_set.loc[30:,'id.1':'distractor']
first_30_dist.columns = ['id','complexity','lexicality','target']
second_30_dist.columns = ['id','complexity','lexicality','target']


# create two sets of stimuli, each for one rotation
rot1 = pd.concat([first_30_tar,second_30_dist],axis = 0)
rot2 = pd.concat([second_30_tar,first_30_dist],axis = 0)

## create a unique stim set depending on the participants rotation

# prepare simple filler words
Swords = stimuli_set.loc[:23,'id.2':'filler_Sword']
Swords.columns = ['id','complexity','lexicality','target']

# prepare complex filler words
Cwords = stimuli_set.loc[:23,'id.3':'filler_Cword']
Cwords.columns = ['id','complexity','lexicality','target']

# create final stimuli
rot_no = int(expInfo['Rot'])

if rot_no==1:
    stimuli1 = pd.concat([rot1,Swords,Cwords],axis = 0)
    stimuli = stimuli1.reset_index(drop=True)
else:
    stimuli1 = pd.concat([rot2,Swords,Cwords],axis = 0)
    stimuli = stimuli1.reset_index(drop=True)

    
    
# randomize stimuli
num_stimuli = len(stimuli['target'])

num_stimuliRand = stimuli.reindex(rn.sample(range(num_stimuli),num_stimuli))
num_stimuliRand.index = range(num_stimuli)


# register responses and times
response=list()
responseP=list()

# define output files
outputFileName = 'output_PROBA' + 'sbj_' + expInfo['ID'] + '_' + 'rot_' + expInfo['Rot'] + '_' + str(timeStamp) + '.csv'

# create window 
win = visual.Window(size=[1920, 1080], fullscr=True, color=[-1,-1,-1], units='pix')

# instructions, goodbyes, messages, feedback
instr_prac = visual.TextStim(win, text="In questa fase dell’esperimento, vedrai alcune parole apparire una alla volta sullo schermo.\n Il tuo compito è di dire se sono le parole veramente esistenti in italiano o no. \nPuoi rispondere con SI (tasto verde) o NO (tasto rosso). Per passare alla parola seguente, premi la barra spaziatrice. \n Iniziamo con un po' di pratica. Rispondi SI se pensi che parola esiste in italiano oppure NO se pensi che non esiste.", \
                                        color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
instr_main = visual.TextStim(win, text='Ora passiamo al compito vero e proprio. Non avrai più il feedback sulla tua risposta. \nRicordati, rispondi SI se pensi che la parola esiste in italiano o NO se non esiste. \nSe hai qualche dubbio, puoi chiedere ora. Premi la barra quando sei pronto.', \
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

    if responsePtemp[0][0]=='s':
        if real_id_sentP not in ['1p', '3p', '5p']:         
            correct.draw(win=win)
            win.flip()
            core.wait(0.5)
        else:    
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.5)
    elif responsePtemp[0][0]=='l':
        if real_id_sentP in ['1p', '3p', '5p']:
            correct.draw(win=win)
            win.flip()
            core.wait(0.5)
        else:
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.5)

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
    
    stim_word=visual.TextStim(win, text=num_stimuliRand['target'][trial_num], color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial',height=25,wrapWidth=2500)
    stim_word.draw(win=win)
    win.flip()
    
    # collect answers    
    responseTemp = event.waitKeys(keyList=['l','s'],timeStamped=clock)
        
    win.flip()
    core.wait(0.3)

    # append responses and times one after the other        
    response.extend(responseTemp)
    
    # set directory
    os.chdir('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment')
    
    # SAVE TO OUTPUT FILE
    # concatenate and write out
    sbj_id_df = pd.DataFrame({'sbj_id':[expInfo['ID']] * len(num_stimuliRand)})
    rot_df = pd.DataFrame({'rot':[expInfo['Rot']] * len(num_stimuliRand)})
    response_df = pd.DataFrame(response)
    randomizationMapping = pd.DataFrame(num_stimuliRand)
    together = pd.concat([sbj_id_df, rot_df, randomizationMapping, response_df],axis=1)
    together.columns = ['sbj_id','rot','id','complexity','lexicality','target','ans','rt']
    together.to_csv(outputFileName)


# goodbye message
goodbye.draw(win=win)
win.flip()
core.wait(1)

win.close()

# CLOSE EVERYTHING
core.quit()

