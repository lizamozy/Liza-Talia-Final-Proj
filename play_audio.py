"""PyAudio Example: Play a wave file."""

import wave
import sys
import sqlite3
from sqlite3 import Error
import pyaudio

def connection(database):
    #get connection 
    conn = None 
    try: 
        conn = sqlite3.connect(database)
    except Error as e: 
        print(e)
    return conn

def get_wav(audio):
    conn = connection("Recordings.db")
    print(audio)
    with conn:
        sql = '''select rec_path from original where rec_name = ?'''
        cur = conn.cursor()
        cur.execute(sql, (audio,))
        conn.commit()
        ret = cur.fetchone()
        print(ret)
        return ret
    
def get_edit_wav(audio):
    conn = connection("Recordings.db")
    print(audio)
    with conn:
        sql = '''select edit_path from edited where edit_name = ?'''
        cur = conn.cursor()
        cur.execute(sql, (audio,))
        conn.commit()
        ret = cur.fetchone()
        print(ret)
        return ret
    
def play_recording(audio, flag):
    if not flag: 
        wav = get_wav(audio)[0]
    else:
        #wav = audio
        wav = get_edit_wav(audio)[0]
        
    print(wav)
    CHUNK = 1024

    #if len(sys.argv) < 2:
    #    print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
     #   sys.exit(-1)

    with wave.open(wav, 'rb') as wf:
        # Instantiate PyAudio and initialize PortAudio system resources (1)
        p = pyaudio.PyAudio()

        # Open stream (2)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Play samples from the wave file (3)
        while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
            stream.write(data)

        # Close stream (4)
        stream.close()

        # Release PortAudio system resources (5)
        #p.terminate()
