from flask import Flask, render_template, request
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
import record
# ======== Initialize flask app ===========
app = Flask(__name__)


@app.route('/'+thing_file.thing_name)
def show_home():
    main.setup()
    return render_template('main_page.html')

#record route
@app.route('/'+thing_file.thing_name+'/record', methods=['POST'])
def start_record():
    #api call to press button to record sound
    #need to signal the global vairable to chnage recording=True
    try:
        main.loop()
    except KeyboardInterrupt:  
        main.destroy()
    result = main.record()
    render_template('main_page.html', result=result)

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
        print(recordings)
    conn.close()
    render_template('recordings.html', recordings=recordings)
    
    
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
    render_template('recordings.html', recordings=recordings)
    

    

   
    #next to orginal, have button that says edit
        #goes to edit route

#play recording
    #get the path from the database
    #wave_obj = sa.WaveObject.from_wave_file(file_path)
    #play_obj = wave_obj.play()
    #play_obj.wait_done()
    #except Exception as e:
    #print("Error:", e)

    #if __name__ == "__main__":
    #file_path = input("Enter the path of the .wav file: ")
    #play_wav(file_path)

#route to edit
@app.route('/'+thing_file.thing_name+'/edit')
def edit_sound():
    #what funcitons do i call to set up the edit audio??? talia needs to clarify
    main.rotaryDeal()
    

#speed up

#slow down

if __name__ == '__main__':

    # If you have debug=True and receive the error "OSError: [Errno 8] Exec format error", then:
    # remove the execuition bit on this file from a Terminal, ie:
    # chmod -x flask_api_server.py
    #
    # Flask GitHub Issue: https://github.com/pallets/flask/issues/3189
    app.run(host="0.0.0.0", port=8080, debug=True) 
    
   