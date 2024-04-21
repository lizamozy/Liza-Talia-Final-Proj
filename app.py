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
# ======== Initialize flask app ===========
app = Flask(__name__)


@app.route('/'+thing_file.thing_name)
def show_home():
    return render_template('main_page.html')


#create main route
    #record new audio
    #view stored audio
    #edit audio

#record route
    #api call to press button to record sound
    #need to signal the global vairable to chnage recording=True
#route to see recordings
    #database call to display all of recordings stored in orginal and edited database
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

#speed up

#slow down

if __name__ == '__main__':

    # If you have debug=True and receive the error "OSError: [Errno 8] Exec format error", then:
    # remove the execuition bit on this file from a Terminal, ie:
    # chmod -x flask_api_server.py
    #
    # Flask GitHub Issue: https://github.com/pallets/flask/issues/3189

    app.run(host="0.0.0.0", port=8080, debug=True) 