### Olga
### 22-11-2020

### update 


#import packages
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import pylink
import os
from numpy.random import shuffle
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from psychopy import visual, core, event, monitors, gui
import random as rn
import pandas as pd
import numpy as np

# SET UP THE ENVIRONMENT

#clock
timeStamp = core.getAbsTime()

#specify working directory
os.chdir('D:\\OlgaSolaja\\Olga_experiment\\ET_Sentence_Congruency_Task')

#get subject info
expInfo = {'ID':'00', 'Rot':'TEST'}
dlg = gui.DlgFromDict(dictionary=expInfo, title="New Word Learning", order=['ID', 'Rot'])
if not dlg.OK: 
    core.quit()  # user pressed cancel

##################################################################################################################

# SET UP EYE TRACKER 

# open a connection to the tracker
# replace the IP address with None will open a simulated connection
tk = pylink.EyeLink('100.1.1.1')

# Open an EDF data file on the Host and write a file header
# The file name should not exceeds 8 characters
dataFileName = expInfo['ID'] + '_' + expInfo['Rot'] + '.EDF'
tk.openDataFile(dataFileName)
# add personalized data file header (preamble text)
tk.sendCommand("add_file_preamble_text 'my_exp'") 


#  Open a window for stimulus presentation, and configure options for 
# calibration/validation and drift-correction (target size, color, etc.)
scnWidth, scnHeight = (1920, 1080)


# we need to set monitor parameters to use the different PsychoPy screen "units"
mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0) ### to be updated
mon.setSizePix((scnWidth, scnHeight))

# open a window; set winType='pyglet' to prevent text display issues in PsychoPy2
win = visual.Window((scnWidth,scnHeight), fullscr = True, monitor=mon, color="black",
                    winType='pyglet', units='pix', allowStencil=True)


# set up a custom graphics envrionment (EyeLinkCoreGraphicsPsychopy) for calibration
genv = EyeLinkCoreGraphicsPsychoPy(tk, win)

# set background and foreground colors, (-1,-1,-1)=black, (1,1,1)=white
genv.backgroundColor = (-1,-1,-1) ### background should be black and circle white
genv.foregroundColor = (1,1,1)


# Configure the calibration target, could be a 'circle', 
# a movie clip ('movie'), a 'picture', or a 'spiral', the default is a circle
genv.calTarget = 'circle'


pylink.openGraphicsEx(genv)

# Set up the tracker
# put the tracker in idle mode before we change its parameters
tk.setOfflineMode()
pylink.pumpDelay(100)

# IMPORTANT: send screen resolution to the tracker
# see Eyelink Installation Guide, Section 8.4: Customizing Your PHYSICAL.INI Settings
tk.sendCommand("screen_pixel_coords = 0 0 %d %d" % (scnWidth-1, scnHeight-1))

# save screen resolution in EDF data, so Data Viewer can correctly load experimental graphics
# see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration
tk.sendMessage("DISPLAY_COORDS = 0 0 %d %d" % (scnWidth-1, scnHeight-1))

# sampling rate, 250, 500, 1000, or 2000; this command is not supported for EyeLInk II/I trackers
# tk.sendCommand("sample_rate 1000") 


# detect eye events based on "GAZE" (or "HREF") data
tk.sendCommand("recording_parse_type = GAZE")

# Saccade detection thresholds: 0-> standard/coginitve, 1-> sensitive/psychophysiological
# see Eyelink User Manual, Section 4.3: EyeLink Parser Configuration
tk.sendCommand("select_parser_configuration 0") 

# choose a calibration type, H3, HV3, HV5, HV13 (HV = horiztonal/vertical), 
# tk.setCalibrationType('HV9') also works, see the Pylink manual
tk.sendCommand("calibration_type = HV5") 

# tracker hardware, 1-EyeLink I, 2-EyeLink II, 3-Newer models (1000/1000Plus/Portable DUO)
hardware_ver = tk.getTrackerVersion()

# tracking software version
software_ver = 0
if hardware_ver == 3:
    tvstr = tk.getTrackerVersionString()
    vindex = tvstr.find("EYELINK CL")
    software_ver = float(tvstr.split()[-1])

# sample and event data saved in EDF data file
# see sectin 4.6 of the EyeLink user manual, software version > 4 adds remote tracking (and thus HTARGET)
tk.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT")
if software_ver >= 4:
    tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,GAZERES,PUPIL,HREF,AREA,STATUS,HTARGET,INPUT")
else:
    tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,GAZERES,PUPIL,HREF,AREA,STATUS,INPUT")

# sample and event data available over the link    
tk.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,FIXUPDATE,SACCADE,BLINK,BUTTON,INPUT")
if software_ver >= 4:
    tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,PUPIL,HREF,AREA,STATUS,HTARGET,INPUT")
else:
    tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,PUPIL,HREF,AREA,STATUS,INPUT")
    
# instruct the experimenter to calibrate the tracker
msg = visual.TextStim(win, text='Press ENTER twice to calibrate the tracker')
msg.draw()
win.flip()
event.waitKeys()

# set up the camera and calibrate the tracker
tk.doTrackerSetup()
    
##################################################################################################################
# SET UP EXPERIMENT

#read in stimuli and practice files
rot_no = int(expInfo['Rot'])

if rot_no==1:
    stimuli=pd.read_csv('sct_stim_rot1_revised.csv')
else:
    stimuli=pd.read_csv('sct_stim_rot2_revised.csv')
practice_sent = pd.read_csv('sct_practice.csv')

# define output files
outputFileNameResp = 'output_' + 'sbj_' + expInfo['ID'] + '_' + 'rot_' + expInfo['Rot'] + '_' + str(timeStamp) + '.csv'

# #randomize stimuli
# NumStimuli = len(Stimuli)
# trial_numbers = list(range(NumStimuli))
# shuffle(trial_numbers)

# randomize stimuli
num_stimuli = len(stimuli['target'])

num_stimuliRand = stimuli.reindex(rn.sample(range(num_stimuli),num_stimuli)) #reindex keeps the original association between indexes and targets
num_stimuliRand.index = range(num_stimuli)

#set seed
seed = int(expInfo['ID'])
rn.seed(seed) # this way, the seed changes for each participant automatically, I can't forget to do it
np.random.seed(seed)

#list of all sentences through which MAIN loop should go
sent_num = range(len(num_stimuliRand))


# instructions, goodbyes, etc
instr_pract = visual.TextStim(win, text="In questa fase dell’esperimento vedrai alcune frasi apparire sullo schermo. \nPrima di ogni frase vedrai una crocetta che segna la posizione della lettera iniziale della frase che seguirà.  \n Il tuo compito è di leggere la frase, comprenderla e rispondere alla domanda che seguirà. \n Come all’inizio dell’esperimento, le frasi potranno contenere parole che non hai mai visto; tu fai comunque del tuo meglio per capire la frase. \n Per passare alla domanda, premi la barra spaziatrice. \n Per rispondere SI, premi il tasto verde, e invece per rispondere NO, premi il tasto rosso.\n Dopo il feedback, premi la barra per leggere la frase seguente. \n Iniziamo con alcune frasi di pratica. Premi la barra spaziatrice per iniziare.", \
                              color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=1720)
instr_main = visual.TextStim(win, text="Ora inizia l'esperimento vero e proprio. Non avrai più il feedback. \nSe hai qualche domanda, falla pure ora. \nAltrimenti, premi la barra spaziatrice per iniziare.", \
                             color=[.8,.8,.8], pos=[0,0], ori=0, font='Arial', height=25, wrapWidth=1720)
cross = visual.TextStim(win, text='+', color=[.8,.8,.8], alignText = 'left', pos=[0,0], ori=0, font='Courier New', height=25, wrapWidth=1720)
goodbye = visual.TextStim(win, text="L'esperimento è finito. \n Grazie!", color=[.8,.8,.8], pos=[0,0], ori=0)
question = visual.TextStim(win, text="Ha senso quello che hai letto?", color=[.8,.8,.8], pos=[0,0], ori=0, font='Courier New', height=25, wrapWidth=1720)
correct = visual.TextStim(win, text="Corretto!", color='green',pos=[0,0], ori=0, font='Courier New', height=25, wrapWidth=1720)
incorrect = visual.TextStim(win, text="Sbagliato!", color='red',pos=[0,0], ori=0, font='Courier New', height=25, wrapWidth=1720)


#get responses
responseQ = []

#collect real IDs
real_id_sent = []

# EXPERIMENT STARTS

# practice trial instructions
instr_pract.draw(win=win)
win.flip()
event.waitKeys(keyList=['space'])
win.flip()
core.wait(1)


# PRACTICE TRIAL LOOP

for iPsentenceP, psentence in enumerate(practice_sent['target']):
    nsentenceP = practice_sent['sentID'][iPsentenceP]
   
    responseTempP = []


    # define clock
    clock=core.Clock()

    tk.setOfflineMode()
    pylink.msecDelay(100)
    
    # send the standard "TRIALID" message to mark the start of a trial
    # see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration
    tk.sendMessage('TRIALID %s' % psentence)
    
    
    # record_status_message : show some info on the Host PC - OPTIONAL
    # here we show how many trial has been tested
    tk.sendCommand("record_status_message 'Trial number %s'"% psentence)


    tk.setOfflineMode()
    pylink.pumpDelay(100)
    
    
    # fixation cross
    cross.draw(win=win)
    win.flip()
    event.waitKeys(keyList=['space'])
    
    #drift correction
    # do we need to recalibrate?
    if event.getKeys(keyList=['t']):
        tk.doTrackerSetup()
       
    ### decide on font and size, do we want monospaced or not?
    pword = visual.TextStim(win, text=psentence, color=[.8,.8,.8], alignText = 'left',pos=[0,0], ori=0, font='Courier New', height=25, wrapWidth=1720)

    # start recording    
    # arguments: sample_to_file, events_to_file, sample_over_link, event_over_link (1-yes, 0-no)
    err = tk.startRecording(1, 1, 1, 1)
    pylink.pumpDelay(100)  # wait for 100 ms to cache some samples
    
    # Clear bufferred keyboard events (in Psychopy) if there are any
    event.clearEvents(eventType='keyboard')
    
    pword.draw(win=win)
    

    # save a screenshot so we can use it in Data Viewer to overlay the gaze
    # taking a screenshot can be time consuming, not recommended for timing critical tasks

    if not os.path.exists('screenshots'): 
        os.mkdir('screenshots')
    screenshot = 'screenshots' + os.sep + 'trial'+nsentenceP +'_' + expInfo['ID'] + expInfo['Rot']+ '.jpg' 
    win.getMovieFrame('back')
    win.saveMovieFrames(screenshot)

    win.flip()
    
    tk.sendMessage("stim_onset")
    # send a Data Viewer integration message here, so DV knows which screenshot to load
    tk.sendMessage('!V IMGLOAD CENTER %s %d %d' % ('..' + os.sep + screenshot, scnWidth/2, scnHeight/2))
    
    event.waitKeys(keyList=['space'])

    # clear the subject display
    win.color=[0, 0, 0]
    win.flip()
    tk.sendMessage('blank_screen')
    
    # stop recording
    tk.stopRecording()
    tk.sendMessage("!V TRIAL_VAR pword %s" % (psentence))
    tk.sendMessage('TRIAL_RESULT 0')
    
    
    # blank screen
    blank_screen = visual.TextStim(win, text='', color=[.8,.8,.8], pos=[0,0], ori=0)
    blank_screen.draw(win=win)
    win.flip()
    core.wait(0.2)
    
    # question
    question.draw()
    win.flip()
   
    if len(responseTempP)==0:
        responseTempP = event.waitKeys(keyList=['l','s'],timeStamped=clock)
        
    win.flip()
    core.wait(0.2)

    if responseTempP[0][0]=='s':
        if nsentenceP not in ['1p', '2p', '5p']:
            correct.draw(win=win)
            win.flip()
            core.wait(0.5)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.5)
        else:    
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.5)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.5)
    elif responseTempP[0][0]=='l':
        if nsentenceP in ['1p', '2p', '5p']:
            correct.draw(win=win)
            win.flip()
            core.wait(0.5)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.5)
        else:
            incorrect.draw(win=win)
            win.flip()
            core.wait(0.5)
            event.waitKeys(keyList=['space'])
            win.flip()
            core.wait(0.5)
            
    win.flip()
    core.wait(0.5)
   
    
    
    # this allows to abort experiment whenever
    if event.getKeys(keyList=["q"]):
        break
    

# instructions for main trial
instr_main.draw(win=win)
win.flip()
event.waitKeys(keyList=['space'])
win.flip()
core.wait(1)

# MAIN TRIAL LOOP

for trial_i, trial_num in enumerate(sent_num):
    

    real_id_sentT = num_stimuliRand['sentID'][trial_i]
    
    
    # define clock
    clock=core.Clock()
    
    # temporary responses
    responseQTemp = []
    
    nsentenceMT = stimuli['sentID'][trial_num]
    
    tk.setOfflineMode()
    pylink.msecDelay(100)
    
    # send the standard "TRIALID" message to mark the start of a trial
    # see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration
    tk.sendMessage('TRIALID %s' % stimuli['sentID'][trial_i])
    
    # record_status_message : show some info on the Host PC - OPTIONAL
    # here we show how many trial has been tested
    tk.sendCommand("record_status_message 'Trial number %s'"% trial_i)
    

    # put the tracker in idle mode before we start recording
    tk.setOfflineMode()
    pylink.pumpDelay(100)
    
    
    # fixation cross
    
    cross = visual.TextStim(win, text='+', color=[.8,.8,.8], alignText = 'left', pos=[0,0], ori=0, font='Courier New', height=25, wrapWidth=1720)
    cross.draw(win=win)
    win.flip()
    event.waitKeys(keyList=['space'])
    
    #drift correction
    # do we need to recalibrate?
    if event.getKeys(keyList=['t']):
        tk.doTrackerSetup()

    # start recording    
    # arguments: sample_to_file, events_to_file, sample_over_link, event_over_link (1-yes, 0-no)
    err = tk.startRecording(1, 1, 1, 1)
    pylink.pumpDelay(100)  # wait for 100 ms to cache some samples
    
    # Clear bufferred keyboard events (in Psychopy) if there are any
    event.clearEvents(eventType='keyboard')
    
    
    
    # stimuli def
    sentence = num_stimuliRand['target'][trial_num]
    ### decide on font and size, do we want monospaced or not?
    word = visual.TextStim(win, text=sentence, color=[.8,.8,.8], alignText = 'left',pos=[0,0],ori=0, font='Courier New', height=25, wrapWidth=1720)
    
    word.draw(win=win)
    
    # save a screenshot so we can use it in Data Viewer to overlay the gaze
    # taking a screenshot can be time consuming, not recommended for timing critical tasks

    if not os.path.exists('screenshots'): 
        os.mkdir('screenshots')
    screenshot = 'screenshots' + os.sep + 'trial_' + str(nsentenceMT) +'_' + expInfo['ID'] + '_' + expInfo['Rot']+ '.jpg' 
    win.getMovieFrame('back')
    win.saveMovieFrames(screenshot)
    
    
    win.flip()
    
    tk.sendMessage("stim_onset")
    # send a Data Viewer integration message here, so DV knows which screenshot to load
    tk.sendMessage('!V IMGLOAD CENTER %s %d %d' % ('..' + os.sep + screenshot, scnWidth/2, scnHeight/2))
    
    event.waitKeys(keyList=['space'])

    # clear the subject display
    win.color=[0, 0, 0]
    win.flip()
    tk.sendMessage('blank_screen')
    
    # stop recording
    tk.stopRecording()
    tk.sendMessage("!V TRIAL_VAR word %s" % (sentence))
    tk.sendMessage('TRIAL_RESULT 0')
    
    
    # blank screen
    blank_screen = visual.TextStim(win, text='', color=[.8,.8,.8], pos=[0,0], ori=0)
    blank_screen.draw(win=win)
    win.flip()
    core.wait(0.5)
    
    #ask the comprehension question after each sentence
    question.draw(win=win)
    # collect answers
    # if len(responseQTemp)==0:
    #         responseQTemp = event.getKeys(keyList=['l','s'],timeStamped=clock)

    win.flip()
    
    # tell it to wait until something is pressed??
    # if len(responseQTemp)==0:
    responseQTemp = event.waitKeys(keyList=['l','s'],timeStamped=clock)
    win.flip()
    core.wait(0.5)

    # append responses and times one after the other        
    responseQ.extend(responseQTemp)
    
    #append real IDs
    real_id_sent.append(real_id_sentT)
    
    # SAVE RESPONSE OUTPUT

    # set directory #this puts also .edf and screenshots in this folder for some reason but nevermind
    os.chdir('D:\\OlgaSolaja\\Olga_experiment\\ET_Sentence_Congruency_Task\\outputETSCT')
    
    # concatenate and write out
    rot_df = pd.DataFrame({'rot':[rot_no] * len(num_stimuliRand)})
    responseQ_df = pd.DataFrame(responseQ)
    randomizationMapping = pd.DataFrame(num_stimuliRand)
    responseQ_out = pd.concat([randomizationMapping,responseQ_df, rot_df],axis=1)
    responseQ_out.columns = ['id_sct','congruency','sent','answ','rt', 'rot']
    responseQ_out.to_csv(outputFileNameResp)
    
    
    # exit the loop to abort the experiment
    if event.getKeys(keyList=["q"]):
        break

        
# abort experiment option
if event.getKeys(keyList=["q"]):
    abort_mess = visual.TextStim(win, text = "Experiment aborted.", color = [.8,.8,.8], pos = [0,0], ori = 0)
    abort_mess.draw(win=win)
    win.flip()
    core.wait(1)
    win.close()
    core.quit()
    
# GOODBYE
goodbye.draw(win=win)
win.flip()
event.waitKeys(keyList=['space'])

# CLOSING EYETRACKER RELATED THINGS AND WRITING OUTPUT
# close the EDF data file and put the tracker in idle mode
tk.setOfflineMode()
pylink.pumpDelay(100)
tk.closeDataFile()

# download EDF file to Display PC and put it in local folder ('edfData')
msg = 'EDF data is transfering from EyeLink Host PC...'
edfTransfer = visual.TextStim(win, text=msg, color='white')
edfTransfer.draw()
win.flip()
pylink.pumpDelay(500)

# make sure the 'edfData' folder is there, create one if not
dataFolder = os.getcwd() + '/edfData/'
if not os.path.exists(dataFolder): 
    os.makedirs(dataFolder)
tk.receiveDataFile(dataFileName, 'edfData' + os.sep + dataFileName)

# close the connection to tracker
tk.close()

# SAVE REPONSE OUTPUT

# set directory
os.chdir('D:\\OlgaSolaja\\Olga_experiment\\ET_Sentence_Congruency_Task\\outputETSCT')

# concatenate and write out
sbj_id_df = pd.DataFrame({'sbj_id':[expInfo['ID']] * len(num_stimuliRand)})
rot_df = pd.DataFrame({'rot':[rot_no] * len(num_stimuliRand)})
responseQ_df = pd.DataFrame(responseQ)
randomizationMapping = pd.DataFrame(num_stimuliRand)
responseQ_out = pd.concat([sbj_id_df, rot_df, randomizationMapping,responseQ_df, rot_df],axis=1)
responseQ_out.columns = ['sbj_id','rot','id_sct','complexity_LT_rot_1', 'complexity_LT_rot_2','complexity_LT_rot_3','congruency','sent','answ','rt']
responseQ_out.to_csv(outputFileNameResp)



# CLOSE EVERYTHING
core.quit()