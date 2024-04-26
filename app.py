from flask import Flask, render_template, request, send_file
import pandas as pd
import json
import plotly
import plotly.subplots
import plotly.express as px
import random
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime


#all important imports
    #other py files in this folder, simple audio, blah blah
import thing_file
import main
#from main import isRecording
import record
import play_audio

# ======== Initialize flask app ===========
app = Flask(__name__)


@app.route('/'+thing_file.thing_name)
def show_home():
    main.setup()
    return render_template('main_page.html')

#record route
@app.route('/'+thing_file.thing_name+'/gorecord', methods=['GET'])
def start_record():
    
    #api call to press button to record sound
    #need to signal the global vairable to chnage recording=True
    #isRecording = True
    try:
        main.setup()
        #global isRecording
        #isRecording = True
        main.loop(True, 0, None)
    except KeyboardInterrupt:  
        main.destroy()
    result = main.record()
    return render_template('main_page.html', result=result)

#route to see recordings
@app.route('/'+thing_file.thing_name+'/view-original')
def view_original():
    conn = record.connection("Recordings.db")
    with conn:
        sql = '''Select * from original'''
        cur = conn.cursor()
        # Execute the select statement
        cur.execute(sql)
        # Fetch all the rows from the result set
        recordings = cur.fetchall()
        sql = '''select count(*)from original'''
        cur = conn.cursor()
        # Execute the select statement
        cur.execute(sql)
        size = cur.fetchone()
        print(recordings)
    conn.close()
    return render_template('orig_recordings.html', recordings=recordings)

@app.route('/'+thing_file.thing_name+'/play-audio', methods=['GET'],)
def play():
    audioId = request.args.get('audioId')
    print(audioId)
    play_audio.play_recording(audioId, 0)
    return render_template('orig_recordings.html')

@app.route('/'+thing_file.thing_name+'/play-edit-audio', methods=['GET'],)
def edit_play():
    audioId = request.args.get('audioId')
    print("in edit play:")
    print(audioId)
    play_audio.play_recording(audioId, 1)
    return render_template('edit_recordings.html')


@app.route('/'+thing_file.thing_name+'/view-edited')
def view_edited():
    conn = record.connection("Recordings.db")
    with conn:
        sql = '''Select * from edited'''
        cur = conn.cursor()
        # Execute the select statement
        cur.execute(sql)
        # Fetch all the rows from the result set
        recordings = cur.fetchall()
        print(recordings)
    conn.close()
    return render_template('edit_recordings.html', recordings=recordings)

#play recording
    #get the path from the database
    #wave_obj = sa.WaveObject.from_wave_file(file_path)
    #play_obj = wave_obj.play()
    #play_obj.wait_done()
    #except Exception as e:
    #print("Error:", e)

#route to edit
@app.route('/'+thing_file.thing_name+'/edit',  methods=['GET'],)
def edit_sound():
    audioId = request.args.get('audioId')
    path = 'Audio/' + audioId + '.wav'
    #what funcitons do i call to set up the edit audio??? talia needs to clarify
    try:
        main.setup()
        #global isRecording
        #isRecording = True
        main.loop(False, 1, path)
    except KeyboardInterrupt:  
        main.destroy()

    

if __name__ == '__main__':

    # If you have debug=True and receive the error "OSError: [Errno 8] Exec format error", then:
    # remove the execuition bit on this file from a Terminal, ie:
    # chmod -x flask_api_server.py
    #
    # Flask GitHub Issue: https://github.com/pallets/flask/issues/3189
    app.run(host="0.0.0.0", port=5000, debug=True) 
    
   