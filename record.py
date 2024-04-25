import wave
import time
import sqlite3
import sys
from sqlite3 import Error

import pyaudio

# # Constants for the recording
# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 2
# RATE = 44100
# RECORD_SECONDS = 5
# WAVE_OUTPUT_FILENAME = "record.wav"
frames = []
# p = pyaudio.PyAudio()
def connection(database):
    #get connection 
    conn = None 
    try: 
        conn = sqlite3.connect(database)
    except Error as e: 
        print(e)
    return conn

# Define the callback for recording
def callback(in_data, frame_count, time_info, status):
    global frames
    frames.append(in_data)
    return (in_data, pyaudio.paContinue)

def recordAudio(CHUNK:int, FORMAT: int, CHANNELS: int, RATE: int, RECORD_SECONDS:int, WAVE_OUTPUT_FILENAME: str, p: object):
    # Open stream using callback
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    

    # Start recording
    print("Recording...")
    stream.start_stream()

    while stream.is_active():
        time.sleep(0.1)
        if len(frames) * CHUNK >= RATE * RECORD_SECONDS:
            stream.stop_stream()

    print("Finished recording.")

    # Stop and close the stream
    stream.close()

    # Terminate the PortAudio interface
    p.terminate()

    # Save recorded data to a wave file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    #name = WAVE_OUTPUT_FILENAME
    conn = connection("Recordings.db")
    with conn:
        
        sql = '''INSERT INTO original(rec_name, rec_path)values(?,?)'''
        cur = conn.cursor()
        cur.execute(sql, (WAVE_OUTPUT_FILENAME[6:-4], WAVE_OUTPUT_FILENAME))
        conn.commit()
    conn.close()
