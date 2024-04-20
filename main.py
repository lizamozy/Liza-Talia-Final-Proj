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
                out_file = "slowdown"+str(wav_ctr)+".wav"
                wav_ctr= wav_ctr + 1
            else:
                out_file = "speedup"+str(wav_ctr)+".wav"
                wav_ctr= wav_ctr + 1
            
        
        
        
def speed_up_wav(input_file, output_file, speed_factor):
    if input_file == None:
        print ("no file inputted--destroying")
        destroy()
    # Load the audio file
    audio = AudioSegment.from_file(input_file, format="wav")

    # Speed up the audio
    sped_up = audio.speedup(playback_speed=speed_factor)

    # Save the modified audio
    sped_up.export(output_file, format="wav")
    
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
    WAVE_OUTPUT_FILENAME = "record.wav"

    p = pyaudio.PyAudio()
    recordAudio(CHUNK, FORMAT,CHANNELS, RATE, RECORD_SECONDS, WAVE_OUTPUT_FILENAME, p)

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
