from pydub import AudioSegment 
from pydub.playback import play
from record import recordAudio
import RPi.GPIO as GPIO
import sqlite3
from sqlite3 import Error
import time
import pyaudio

#set up pins first
RoAPin = 11    # CLK Pin
RoBPin = 12    # DT Pin
RotPin = 13    # rotary Pin
BtnPin = 29    # btn pin
Gpin   = 22     #green
Rpin   = 16     #red

record = True #will signal this from the flask app
wav_ctr= 0
output_file = None
input_file = None

globalCounter = 0.0  # Initialize as a float
isGreen = True
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

def Led(x):
    global output_file
    if x:
        GPIO.output(Rpin, GPIO.LOW)
        GPIO.output(Gpin, GPIO.HIGH)
    else:
        GPIO.output(Rpin, GPIO.HIGH)
        GPIO.output(Gpin, GPIO.LOW)
        if not record:
           
            #used the globalcounter to pass in speed factor
            if globalCounter  == 0:
                wav_ctr = wav_ctr
            elif globalCounter < 0: 
                output_file = "Desktop/slowdown"+str(wav_ctr)+".wav"
                wav_ctr= wav_ctr + 1
            else:
                output_file = "Desktop/speedup"+str(wav_ctr)+".wav"
                wav_ctr= wav_ctr + 1
                speed_up_wav(input_file, output_file, globalCounter)
                #reset button 

            
        
        
        
def speed_up_wav(input_file, output_file, speed_factor):
    if input_file == None:
        print ("no file inputted--destroying")
        destroy()
    # Load the audio file
    audio = AudioSegment.from_file(input_file, format="wav")

    # Speed up the audio
    sped_up = audio.speedup(playback_speed=speed_factor)

    # Save the modified audio
    edited = sped_up.export(output_file, format="wav")
    save_edit(edited, 1)

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
    global record
    isGreen = not isGreen  # Toggle the state
    if record:
        Led(isGreen)
        record()
    else:
        Led(isGreen)

    record = not record
    
def record():
    #pyaudio set up variables 
    # Constants for the recording
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 10
    WAVE_OUTPUT_FILENAME = "Desktop/recording" + str(rec_ctr)+ ".wav"

    p = pyaudio.PyAudio()
    recordAudio(CHUNK, FORMAT,CHANNELS, RATE, RECORD_SECONDS, WAVE_OUTPUT_FILENAME, p)
    rec_ctr = rec_ctr + 1; # update record
    #then send to db
    
    

def btnISR(channel):
    global globalCounter
    globalCounter = 0.0  # Reset to 0.0 instead of 0
    
def loop():
    global globalCounter
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
