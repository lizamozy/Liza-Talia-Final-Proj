from pydub import AudioSegment 
from pydub.playback import play
from record import recordAudio
import RPi.GPIO as GPIO
import sqlite3
from sqlite3 import Error
import time
import pyaudio
from flask import Flask, render_template, request
import thing_file

#set up pins first
RoAPin = 11    # CLK Pin
RoBPin = 12    # DT Pin
RotPin = 13    # rotary Pin
BtnPin = 29    # btn pin
Gpin   = 22     #green
Rpin   = 16     #red

isRecording = False #will signal this from the flask app
wav_ctr= 0
output_file = None
input_file = 'recording22.wav'
edit = 0

globalCounter = 0.0  # Initialize as a float
isGreen = False
flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0
rec_ctr= 0

def connection(database):
    #get connection 
    conn = None 
    try: 
        conn = sqlite3.connect(database)
    except Error as e: 
        print(e)
    return conn
    
#set up
def setup():
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(RoAPin, GPIO.IN)    # input mode
    GPIO.setup(RoBPin, GPIO.IN)
    GPIO.setup(RotPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Gpin, GPIO.OUT)    
    GPIO.setup(Rpin, GPIO.OUT)     
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.remove_event_detect(BtnPin)
    GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=300)

def rotaryDeal():
    global flag
    global Last_RoB_Status
    global Current_RoB_Status
    global globalCounter
    Last_RoB_Status = GPIO.input(RoBPin)
    while(not GPIO.input(RoAPin)):
        Current_RoB_Status = GPIO.input(RoBPin)
        flag = 1
    if flag == 1:
        flag = 0
        if (Last_RoB_Status == 1) and (Current_RoB_Status == 0) and isGreen:
            #speed up 
            globalCounter = globalCounter + 0.1
        if (Last_RoB_Status == 0) and (Current_RoB_Status == 1) and isGreen:
            #slow down
            globalCounter = globalCounter - 0.1
def index_original():
    conn = connection("Recordings.db")
    index = 0
    with conn:
        sql = '''select count(*) from original;'''
        cur = conn.cursor()
        cur.execute(sql)
        index = cur.fetchone()
        conn.commit()
        

    return index[0]
def index_edit():
    conn = connection("Recordings.db")
    index = 0
    with conn:
        sql = '''select count(*) from edited;'''
        cur = conn.cursor()
        cur.execute(sql)
        index = cur.fetchone()
        conn.commit()
    return index[0]
    
def Led(x):
    global wav_ctr
    global output_file
    global isRecording
    #print("x: ", x)
    if x:
        GPIO.output(Rpin, GPIO.LOW)
        GPIO.output(Gpin, GPIO.HIGH)
    else:
        print(isRecording)
        GPIO.output(Rpin, GPIO.HIGH)
        GPIO.output(Gpin, GPIO.LOW)
        if edit == 1: 
            #used the globalcounter to pass in speed factor
            wav_ctr = index_edit() + 1 
            if globalCounter  == 0:
                save_edit(None, -1)
            elif globalCounter < 0: 
                output_file = "slowdown"+str(wav_ctr)+".wav"
            else:
                output_file = "speedup"+str(wav_ctr)+".wav"
                speed_up_wav(input_file, output_file, globalCounter)
                #reset button 
            
def speed_up_wav(input_file, output_file, speed_factor):
    global globalCounter
    speed_factor = speed_factor + 1.0
    if input_file == None:
        print ("no file inputted--destroying")
        destroy()
    # Load the audio file
    audio = AudioSegment.from_file(input_file, format="wav")

    # Speed up the audio
    sped_up = audio.speedup(playback_speed=speed_factor)

    # Save the modified audio
    sped_up.export(output_file, format="wav")
    save_edit(output_file, 1)
    globalCounter = 0.0
    
def slow_down_wav(input_file, output_file, speed_factor):
    speed_factor = speed_factor + 1.0
    # Load the audio file
    audio = AudioSegment.from_file(input_file, format="wav")

    # Slow down the audio
    slowed_down = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate / speed_factor)
    })

    # Export the modified audio
    slowed_down.export(output_file, format="wav")
    # Save the modified audio
    sped_up.export(output_file, format="wav")
    save_edit(output_file, 0)
    globalCounter = 0.0

def save_edit(file, flag):
    conn = connection("Recordings.db")
    with conn:
        if file == None: #no change save the recording as is
            edit_name = input_file[-4]
            edit_path = input_file
            flag = -1
            sql = '''INSERT INTO edited(flag, edit_name, edit_path)values(?,?,?)'''
            cur = conn.cursor()
            cur.execute(sql, (flag,edit_name, edit_path))
            conn.commit()
        elif not flag: 
            edit_name = file[-4]
            edit_path = file
            flag = 0
            sql = '''INSERT INTO edited(flag, edit_name, edit_path)values(?,?,?)'''
            cur = conn.cursor()
            cur.execute(sql, (flag,edit_name, edit_path))
            conn.commit()
        else:
            edit_name = file[-4]
            edit_path = file
            flag = 1
            sql = '''INSERT INTO edited(flag, edit_name, edit_path)values(?,?,?)'''
            cur = conn.cursor()
            cur.execute(sql, (flag,edit_name, edit_path))
            conn.commit()

    
#press button to record
def detect(chn):
    global isGreen
    global isRecording
    isGreen = not isGreen  # Toggle the state
    if isRecording:
        Led(isGreen)
        record()
        if isRecording:
            print("here")
            isRecording = False
    else:
        Led(isGreen)

   
    
def record():
    global rec_ctr
    #pyaudio set up variables 
    # Constants for the recording
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 10
    rec_ctr = index_original() + 1
    WAVE_OUTPUT_FILENAME = "recording" + str(rec_ctr)+ ".wav"

    p = pyaudio.PyAudio()
    recordAudio(CHUNK, FORMAT,CHANNELS, RATE, RECORD_SECONDS, WAVE_OUTPUT_FILENAME, p)
    #then send to db
    
    

def btnISR(channel):
    global globalCounter
    globalCounter = 0.0  # Reset to 0.0 instead of 0
    
def loop(x):
    global globalCounter
    global isRecording
    isRecording = x
    print("IN LOOP ISRECORDING IS: " + str(isRecording) +  "\n\n\n\n")
    tmp = 0.0  # Initialize as a float to store the temporary count
    GPIO.add_event_detect(RotPin, GPIO.FALLING, callback=btnISR)
    while True:
        rotaryDeal()
        if tmp != globalCounter:
            print('globalCounter = %.1f' % globalCounter)
            tmp = globalCounter
            
                  
def destroy():
    GPIO.cleanup()             # Release resource
    GPIO.output(Gpin, GPIO.HIGH)       # Green led off
    GPIO.output(Rpin, GPIO.HIGH)       # Red led off
    GPIO.cleanup()  

#main
if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  
        destroy()
    
   

