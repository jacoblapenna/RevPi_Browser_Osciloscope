# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:16:40 2022

@author: jlapenna
"""
import eventlet
eventlet.monkey_patch()

import redis

from Server import Server
from DataStreamer import DataStreamer

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, message_queue='redis://')

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("start_stream")
def start_stream():
    streamer.control_stream("start_stream")

@socketio.on("stop_stream")
def stop_stream():
    streamer.control_stream("stop_stream")

if __name__ == "__main__":
    if redis.Redis().ping():
        # make sure redis-server.service is running
        pass
    else:
        raise Exception("Check that redis-server.service is running!")
    server = Server()
    streamer = DataStreamer()
    socketio.run(app,
                 host=server.ip,
                 port=8080,
                 use_reloader=True,
                 debug=True,
                 extra_files=["templates/index.html"])
