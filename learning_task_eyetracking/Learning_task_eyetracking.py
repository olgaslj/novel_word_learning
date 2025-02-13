### Novel word learning eyetracking experiment
### 1-9-2020


#import packages
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import pylink
import os
import random
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from psychopy import visual, core, event, monitors, sound, gui, data, logging, clock, locale_setup, prefs
from PIL import Image  # for preparing the Host backdrop image
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import sys  # to get file system encoding

from psychopy.hardware import keyboard

import pandas as pd

# SET UP THE ENVIRONMENT

# #specify working directory
# os.chdir('my_directory')

#get subject info
expInfo = {'ID':'00', 'Rot':'TEST'}
dlg = gui.DlgFromDict(dictionary=expInfo, title="New Word Learning", order=['ID', 'Rot'])
if not dlg.OK: 
    core.quit()  # user pressed cancel

# SET UP THE ENVIRONMENT

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
scnWidth, scnHeight = (1920, 1080) ### to be updated


# we need to set monitor parameters to use the different PsychoPy screen "units"
mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0) ### to be updated
mon.setSizePix((scnWidth, scnHeight))

# open a window; set winType='pyglet' to prevent text display issues in PsychoPy2
win = visual.Window((scnWidth, scnHeight), fullscr=True, monitor=mon, color="black",
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
    
# SET UP EXPERIMENT

#read in stimuli and practice files
practice_sent = pd.read_csv('practice_sentencesSentence.csv')
#select the correct rotation, the same as it was in the Learning Task
rot_no = int(expInfo['Rot'])

if rot_no==1:
    Stimuli = pd.read_csv('rot1.csv')
elif rot_no==2:
    Stimuli = pd.read_csv('rot2.csv')
else:
    Stimuli = pd.read_csv('rot3.csv')

#randomize stimuli
NumStimuli = len(Stimuli)
trial_numbers = list(range(NumStimuli))
shuffle(trial_numbers)

# instructions, goodbyes, etc
instr_pract = visual.TextStim(win, text="Benvenuta/o, e grazie mille per la tua disponibilità. \nIn questo esperimento vedrai delle frasi apparire sullo schermo. \nPrima di ogni frase vedrai una crocetta che segna la posizione della lettera iniziale della frase che seguirà.  \n Il tuo compito è di leggere e capire le frasi. Non sarà sempre facile, dato che le frasi contengono alcune parole sconosciute; \ntu fai comunque del tuo meglio. \nPer passare alla frase seguente, premi la barra spaziatrice. Iniziamo con alcune frasi di pratica.\nPremi la barra spaziatrice per iniziare.",\
                              color=[.8,.8,.8], pos=[0,0], ori=0,font='Arial', height=25, wrapWidth=1720)
instr_main = visual.TextStim(win, text="Ora inizia l'esperimento vero e proprio. Se hai qualche domanda, questo è il momento di farla. \nAvrai tre pause durante l'esperimento. Premi la barra spaziatrice quando sei pronto.", \
                                        color=[.8,.8,.8], pos=[0,0], ori=0,font='Arial', height=25, wrapWidth=1720)
cross = visual.TextStim(win, text='+', color=[.8,.8,.8], alignText = 'left', pos=[0,0], ori=0, font='Courier New', height=25, wrapWidth=1720)
goodbye = visual.TextStim(win, text="L'esperimento è finito. \n Grazie!", color=[.8,.8,.8], pos=[0,0], ori=0)

#define breaks
break_frequency = 60

# EXPERIMENT STARTS

# practice trial instructions
instr_pract.draw(win=win)
win.flip()
event.waitKeys(keyList=['space'])
win.flip()
core.wait(1)


# PRACTICE TRIAL LOOP

for iPsentenceP, psentence in enumerate(practice_sent['practice_sentence']):
    nsentenceP = practice_sent['id_practice'][iPsentenceP]
   
    tk.setOfflineMode()
    pylink.msecDelay(100)
    
    # send the standard "TRIALID" message to mark the start of a trial
    # see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration
    tk.sendMessage('TRIALID %s' % psentence)
    
    
    # record_status_message : show some info on the Host PC - OPTIONAL
    # here we show how many trial has been tested
    tk.sendCommand("record_status_message 'Trial number %s'"% nsentenceP)


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
    tk.sendMessage("!V TRIAL_VAR word %s" % (psentence))
    tk.sendMessage('TRIAL_RESULT 0')
    
    
    # blank screen
    blank_screen = visual.TextStim(win, text='', color=[.8,.8,.8], pos=[0,0], ori=0)
    blank_screen.draw(win=win)
    win.flip()
    core.wait(0.2)
    
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

for trial_i, trial_num in enumerate(trial_numbers):
    
    nsentenceMT = Stimuli['id_learning_sen'][trial_num]
    
    tk.setOfflineMode()
    pylink.msecDelay(100)
    
    # send the standard "TRIALID" message to mark the start of a trial
    # see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration
    tk.sendMessage('TRIALID %s' % Stimuli['id_learning_sen'][trial_i])
    
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
    sentence = Stimuli['learning_sentence'][trial_num]
    ### decide on font and size, do we want monospaced or not?
    word = visual.TextStim(win, text=sentence, color=[.8,.8,.8], alignText = 'left',pos=[0,0],ori=0, font='Courier New', height=25, wrapWidth=1720)
    
    word.draw(win=win)
    
    # save a screenshot so we can use it in Data Viewer to overlay the gaze
    # taking a screenshot can be time consuming, not recommended for timing critical tasks

    if not os.path.exists('screenshots'): 
        os.mkdir('screenshots')
    screenshot = 'screenshots' + os.sep + 'trial_' + nsentenceMT +'_' + expInfo['ID'] + '_' + expInfo['Rot']+ '.jpg' 
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
    
    # exit the loop to abort the experiment
    if event.getKeys(keyList=["q"]):
        break

    # defines breaks
    if (trial_i+1) % break_frequency == 0:
        brk = visual.TextStim(win, text='break', color=[.8,.8,.8], pos=[0,0], ori=0)
        brk.draw(win=win)
        win.flip()
        event.waitKeys(keyList=['space'])
        
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

# CLOSE EVERYTHING
core.quit()
