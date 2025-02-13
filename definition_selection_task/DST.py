# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 15:02:15 2020

@author: olgas
"""

# Definition selection task for NWL
# Olga
# 14-11-20


#load packages
import pandas as pd
import random as rn
import numpy as np
from random import shuffle, sample
from psychopy import event, visual, core, gui
import os
import os.path

# SET WORKING DIRECTORY
os.chdir('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\Definition_Selection_Task')

# SET UP THE ENVIRONMENT
timeStamp = core.getAbsTime()


# get subject info
expInfo = {'ID':'', 'Rot_LT':''}
dlg = gui.DlgFromDict(dictionary=expInfo, title="DST", order=['ID', 'Rot_LT'])
if not dlg.OK: 
    core.quit()
    
#set window
win = visual.Window(fullscr=False, size = (800, 600), color=[-1,-1,-1], units='pix')

    
# use subj no to set seed
seed = int(expInfo['ID'])
rn.seed(seed) # I HAVE TO CHANGE THIS NUMBER FOR EACH PARTICIPANT
np.random.seed(seed)

#load stimuli and practice set
stimuli_set = pd.read_csv('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\Definition_Selection_Task\DST_stimuli_exp_revised.csv')
practice_stim = pd.read_csv('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\Definition_Selection_Task\\dst_practice.csv')


# randomize words to be tested
num_stimuli = len(stimuli_set['test_novel_word'])
num_stimuliRand = stimuli_set.reindex(rn.sample(range(num_stimuli),num_stimuli))
num_stimuliRand.index = range(num_stimuli)


# define output files
outputFileNameResp = 'out_resp_' + 'sbj' + expInfo['ID'] + '_' + '_' + str(timeStamp) + '.csv'

#instructions, goodbyes, question, feedback
instr_practice = visual.TextStim(win, text="In questa fase dell’esperimento il tuo compito consiste nel leggere la parola scritta in alto in rosso, \ne decidere quale definizione tra quelle proposte sotto è corretta. \nPer dare la risposta, premi i tasti 1, 2, 3 o 4 sulla tastiera; per passare alla parola successiva, premi invece la barra spaziatrice.\nIniziamo con un po' di esercizio. Premi la barra quando sei pronto.", \
                                            color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
instr_main = visual.TextStim(win, text="Ora inizia l'esperimento vero e proprio. Non avrai più il feedback sulla tua risposta. \nSe hai qualche dubbio, puoi chiedere ora. Premi la barra quando sei pronto.", \
                                        color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
goodbye = visual.TextStim(win, text="L'esperimento è finito. \n Grazie!", color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
question = visual.TextStim(win, text="Ha senso quello che hai letto?", color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
correct = visual.TextStim(win, text="Corretto!", color='green',pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
incorrect = visual.TextStim(win, text="Sbagliato!", color='red',pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=2500)
abort_mess = visual.TextStim(win, text="Experiment aborted.", color=[.8,.8,.8], pos=[0,0], ori=0,font='Arial', height=25, wrapWidth=2500)

# record responses and times for answers
response = list()

#list with correctness of answers
correct_choice=[]

# record which answer was chosen
chosen_option = []
button2Inf=[]
button3Inf=[]
button4Inf=[]

#define positions of answer choices
positions = [[0,100],[0,0],[0,-100],[0,-200]]

#positions of the choices
button1Pos= [] #correct
button2Pos= [] #incompatible
button3Pos= [] #overarching category
button4Pos= [] #meaning incompatible

#list of all words through which PRACTICE loop should go
pract_words = range(len(practice_stim['target']))

#list of all words through which MAIN loop should go
test_words = range(len(num_stimuliRand))

# this allows to abort experiment whenever by pressing 'q'
if event.getKeys(keyList=['q']):
    abort_mess.draw(win=win)
    win.flip()
    core.wait(1)
    win.close()
    core.quit()

#EXPERIMENT STARTS
instr_practice.draw()
win.flip()
event.waitKeys(keyList=['space'])
win.flip()
core.wait(0.5)

#PRACTICE LOOP TRIAL
for trialP in pract_words:
    # this allows to abort experiment whenever by pressing 'q'
    if event.getKeys(keyList=['q']):
        abort_mess.draw(win=win)
        win.flip()
        core.wait(1)
        win.close()
        core.quit()

    # define clock
    clock=core.Clock()    

    pword = practice_stim['target'][trialP]
    positionsRandP = rn.sample(positions,len(positions))

    showStimP = visual.TextStim(win, text=pword, color='red', pos=[0,200], ori=0, font='Arial', height=25, bold=True, wrapWidth=1720)
    showStimP.draw(win=win)  

    button1p = visual.TextStim(win, text=practice_stim['ans_correct'][trialP], color=[.8,.8,.8], pos=positionsRandP[0], ori=0, font='Arial', height=25, wrapWidth=1720)
    button2p = visual.TextStim(win, text=practice_stim['ans_incompatible'][trialP], color=[.8,.8,.8], pos=positionsRandP[1], ori=0, font='Arial', height=25, wrapWidth=1720)
    button3p = visual.TextStim(win, text=practice_stim['ans_overarching_cat'][trialP], color=[.8,.8,.8], pos=positionsRandP[2], ori=0, font='Arial', height=25, wrapWidth=1720)
    button4p = visual.TextStim(win, text= practice_stim['ans_meaning_swapped'][trialP], color=[.8,.8,.8], pos=positionsRandP[3], ori=0, font='Arial', height=25, wrapWidth=1720)

    #collect positions where button1(i.e. the correct choice) was
    button1PosTempP = positionsRandP[0] 

    button1p.draw(win=win) 
    button2p.draw(win=win)  
    button3p.draw(win=win)
    button4p.draw(win=win)
   
    win.flip()
    responseTempP = event.waitKeys(keyList=['1','2','3','4'], timeStamped = clock)
    
    # izbrisem vreme
    responseTempKeyP = responseTempP.pop(0)

    # feedback
    if button1PosTempP == [0,100]:
        if '1' in responseTempKeyP:
            chosen_ansTemp = practice_stim['ans_correct'][trialP]
            correct.draw(win=win)
            win.flip()
            core.wait(0.3)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.3)
        else:
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.3)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.3)
    elif button1PosTempP == [0,0]:
        if '2' in responseTempKeyP:
            correct.draw(win=win)
            win.flip()
            core.wait(0.3)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.3)
        else:
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.3)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.3)
    elif button1PosTempP == [0,-100]:
        if '3' in responseTempKeyP:
            correct.draw(win=win)
            win.flip()
            core.wait(0.3)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.3)
        else:
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.3)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.3)
    elif button1PosTempP == [0,-200]:
        if '4' in responseTempKeyP:
            correct.draw(win=win)
            win.flip()
            core.wait(0.3)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.3)
        else:
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.3)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.3)
    
    win.flip()
    core.wait(0.5   )
    
    
instr_main.draw()
win.flip()
event.waitKeys(keyList=['space'])
win.flip()
core.wait(0.5)

#MAIN TRIAL LOOP
for trial in test_words:
   # this allows to abort experiment whenever by pressing 'q'
   if event.getKeys(keyList=['q']):
       abort_mess.draw(win=win)
       win.flip()
       core.wait(1)
       win.close()
       core.quit()
   
   #randomize positions in which answers will appear
   positionsRand = rn.sample(positions,len(positions))
    
     
    
   tword = num_stimuliRand['test_novel_word'][trial]
    
   showStim = visual.TextStim(win, text=tword, color='red', pos=[0,200], ori=0, font='Arial', height=25, bold=True, wrapWidth=1720)
   showStim.draw(win=win)  
    
    
   button1 = visual.TextStim(win, text=num_stimuliRand['ans_correct'][trial], color=[.8,.8,.8], pos=positionsRand[0], ori=0, font='Arial', height=25, wrapWidth=1720)
   # box1 = visual.Rect(win, fillColor = 'yellow', lineColor = 'blue', width = 70, height = 30,pos=positionsRand[0])
   button2 = visual.TextStim(win, text=num_stimuliRand['ans_incompatible'][trial], color=[.8,.8,.8], pos=positionsRand[1], ori=0, font='Arial', height=25, wrapWidth=1720)
   # box2 = visual.Rect(win, fillColor = 'yellow', lineColor = 'blue', width = 70, height = 30,pos=[positionsRand[1]])
   button3 = visual.TextStim(win, text=num_stimuliRand['ans_overarching_cat'][trial], color=[.8,.8,.8], pos=positionsRand[2], ori=0, font='Arial', height=25, wrapWidth=1720)
   # box3 = visual.Rect(win, fillColor = 'yellow', lineColor = 'blue', width = 70, height = 30,pos=positionsRand[2])
   button4 = visual.TextStim(win, text= num_stimuliRand['ans_meaning_swapped'][trial], color=[.8,.8,.8], pos=positionsRand[3], ori=0, font='Arial', height=25, wrapWidth=1720)
   # box4 = visual.Rect(win, fillColor = 'yellow', lineColor = 'blue', width = 70, height = 30,pos=positionsRand[3])

   # button1 is always correct and all others are always the same choices, justs position changes

   #collect positions where button1(i.e. the correct choice) was
   button1PosTemp = positionsRand[0]

   #collect positions where other buttons were
   button2PosTemp = positionsRand[1]
   button3PosTemp = positionsRand[2]
   button4PosTemp = positionsRand[3]

   button1.draw(win=win) 
   # box1.draw()
   button2.draw(win=win)  
   # box2.draw()
   button3.draw(win=win)
   # box3.draw()
   button4.draw(win=win)
   # box4.draw()    
 
   # define clock
   clock=core.Clock()

   win.flip()
   responseTemp = event.waitKeys(keyList=['1','2','3','4'], timeStamped = clock)

   # izbrisem vreme
   responseTempKey = responseTemp[0][0]

   # accuracy
   if button1PosTemp == [0,100]:
       if '1' in responseTempKey:
           correct_choiceT = 'yes'
       else:
           correct_choiceT = 'no'
   elif button1PosTemp == [0,0]:
       if '2' in responseTempKey:
           correct_choiceT = 'yes'
       else:
           correct_choiceT = 'no'
   elif button1PosTemp == [0,-100]:
       if '3' in responseTempKey:
           correct_choiceT = 'yes'
       else:
           correct_choiceT = 'no'
   elif button1PosTemp == [0,-200]:
       if '4' in responseTempKey:
           correct_choiceT = 'yes'
       else:
           correct_choiceT = 'no'
    
   #collecting incorrectly chosen options 
    
   if button2PosTemp == [0,100]:
       if '1' in responseTempKey:
           button2InfT = num_stimuliRand['ans_incompatible'][trial]
       else:
           button2InfT = 'x'
   elif button2PosTemp == [0,0]:
       if '2' in responseTempKey:
           button2InfT = num_stimuliRand['ans_incompatible'][trial]
       else:
           button2InfT = 'x'
   elif button2PosTemp == [0,-100]:
       if '3' in responseTempKey:
           button2InfT = num_stimuliRand['ans_incompatible'][trial]
       else:
           button2InfT = 'x'
   elif button2PosTemp == [0,-200]:
       if '4' in responseTempKey:
           button2InfT = num_stimuliRand['ans_incompatible'][trial]
       else:
           button2InfT = 'x'
        
        
   if button3PosTemp == [0,100]:
       if '1' in responseTempKey:
           button3InfT = num_stimuliRand['ans_overarching_cat'][trial]
       else:
           button3InfT = 'x'
   elif button3PosTemp == [0,0]:
       if '2' in responseTempKey:
           button3InfT = num_stimuliRand['ans_overarching_cat'][trial]
       else:
           button3InfT = 'x'
   elif button3PosTemp == [0,-100]:
       if '3' in responseTempKey:
           button3InfT = num_stimuliRand['ans_overarching_cat'][trial]
       else:
           button3InfT = 'x'
   elif button3PosTemp == [0,-200]:
       if '4' in responseTempKey:
           button3InfT = num_stimuliRand['ans_overarching_cat'][trial]
       else:
           button3InfT = 'x'
        
        
   if button4PosTemp == [0,100]:
       if '1' in responseTempKey:
           button4InfT = num_stimuliRand['ans_meaning_swapped'][trial]
       else:
           button4InfT = 'x'
   elif button4PosTemp == [0,0]:
       if '2' in responseTempKey:
           button4InfT = num_stimuliRand['ans_meaning_swapped'][trial]
       else:
           button4InfT = 'x'
   elif button4PosTemp == [0,-100]:
       if '3' in responseTempKey:
           button4InfT = num_stimuliRand['ans_meaning_swapped'][trial]
       else:
           button4InfT = 'x'
   elif button4PosTemp == [0,-200]:
       if '4' in responseTempKey:
           button4InfT = num_stimuliRand['ans_meaning_swapped'][trial]
       else:
           button4InfT = 'x'
   # def accuracy(buttonNumPos):
   #     if buttonNumPos == [0,100]:
   #         if '1' in responseTempKey:
   #             correct_choiceT = 'yes'
   #         else:
   #             correct_choiceT = 'no'
   #     elif buttonNumPos == [0,0]:
   #         if '2' in responseTempKey:
   #             correct_choiceT = 'yes'
   #         else:
   #             correct_choiceT = 'no'
   #     elif buttonNumPos == [0,-100]:
   #         if '3' in responseTempKey:
   #             correct_choiceT = 'yes'
   #         else:
   #             correct_choiceT = 'no'
   #     elif buttonNumPos == [0,-200]:
   #         if '4' in responseTempKey:
   #             correct_choiceT = 'yes'
   #         else:
   #             correct_choiceT = 'no'
        
   # accuracy(button1PosTemp)
   # accuracy(button2PosTemp)
   # accuracy(button3PosTemp)
   # accuracy(button4PosTemp)
        
        
        
   win.flip()
   core.wait(0.2)
 
   #collect the choice participant made
   response.extend(responseTemp)

   #collect positions of buttons ie. choices
   button1Pos.append(button1PosTemp)
   button2Pos.append(button2PosTemp)
   button3Pos.append(button3PosTemp)
   button4Pos.append(button4PosTemp)

   #collect choice options
   button2Inf.append(button2InfT)
   button3Inf.append(button3InfT)
   button4Inf.append(button4InfT)

   #collect whether the participant chose correctly or not
   correct_choice.append(correct_choiceT)
   chosen_optionT = num_stimuliRand['ans_correct'][trial]

   chosen_option.extend(chosen_optionT)

   # SAVE TO OUTPUT FILE
   # set directory
   os.chdir('C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\Definition_Selection_Task')

   # concatenate and write out
   sbj_id_df = pd.DataFrame({'sbj_id':[expInfo['ID']] * len(num_stimuliRand)})
   rot_df = pd.DataFrame({'rot':[expInfo['Rot_LT']] * len(num_stimuliRand)})
   response_df = pd.DataFrame(response)
   correct_choice_df = pd.DataFrame(correct_choice)
   randomizationMapping = pd.DataFrame(num_stimuliRand)
   pos_corr_ans = pd.DataFrame({0:button1Pos})
   pos_incompat_ans = pd.DataFrame({0:button2Pos})
   pos_overCat_ans = pd.DataFrame({0:button3Pos})
   pos_meanIncCat_ans = pd.DataFrame({0:button4Pos})
   button2Inf_df = pd.DataFrame(button2Inf)
   button3Inf_df = pd.DataFrame(button3Inf)
   button4Inf_df = pd.DataFrame(button4Inf)
   response_out = pd.concat([sbj_id_df,rot_df,randomizationMapping,response_df,correct_choice_df,pos_corr_ans,pos_incompat_ans,pos_overCat_ans,pos_meanIncCat_ans,button2Inf_df,button3Inf_df,button4Inf_df],axis=1)
   response_out.columns = ['sbj_id','rot_LT','id', 'complexity_LT_rot_1', 'complexity_LT_rot_2','complexity_LT_rot_3', 'test_novel_word', 'ans_correct','ans_incompatible', 'ans_overarching_cat', 'ans_meaning_swapped','keypress','RT','accuracy','pos_corr_ans','pos_incompat_ans','pos_overCat_ans','pos_meanIncCat_ans','buttonIncom','buttonOverCat','buttonMeanInc'] 
   response_out.to_csv(outputFileNameResp)
    

   event.waitKeys(keyList=['space'])
   win.flip()
   core.wait(0.2)
   
# goodbye message
goodbye.draw(win=win)
win.flip()
core.wait(1)
   
   
win.close()

#close everything
core.quit()




