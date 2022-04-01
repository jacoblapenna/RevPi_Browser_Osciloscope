# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:16:40 2022

@author: jlapenna
"""
import eventlet
eventlet.monkey_patch(thread=False)

import numpy as np
from multiprocessing import Pipe, Process
import random
import time
from collections import deque
import redis
import socket

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, message_queue="redis://", async_mode="eventlet")
# socketio = SocketIO(app)

def get_ip_address():
    # get the server's IP on which to serve app
    # client can navigate to IP

    ip_address = '127.0.0.1'  # Default to localhost
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # setup a socket object
    try:
        s.connect(('1.1.1.1', 1))  # does not have to be reachable
        ip_address = s.getsockname()[0]
    finally:
	    s.close()
    return ip_address

class ExtremaDetector:

    def __init__(self):
        self._mn, self._mx = float("inf"), -float("inf")
        self._mn_t, self._mx_t = 0, 0
        self._abs_mx = -float("inf")
        self._threshold = 0.01
        self._SNR = 100
        self._look_for_maxima = True

    def check_value(self, point):

        val = point[1]
        time = point[0]

        if val < self._mn:
            self._mn = val
            self._mn_t = time

        if val > self._mx:
            self._mx = val
            self._mx_t = time

        if self._look_for_maxima:
            if val < self._mx - self._threshold:
                self._mn = val
                self._look_for_maxima = False
                # print(f"Local maxima detected at {(self._mx_t, self._mx)}")
                return (self._mx_t, self._mx)
        else:
            if val > self._mn + self._threshold:
                self._mx = val
                self._look_for_maxima = True
                # print(f"Local minima detected at {(self._mn_t, self._mn)}")
                return (self._mn_t, self._mn)

        return None


class DataStreamer:

    """
    pull from AIO on revpi here when ready
    """
    def __init__(self):
        self._freq = 0.1
        self._dt = 0.001
        self._time = 0

    def produce(self, conn):
        print("Producing...")
        while True:
            buffer = []
            for _ in range(random.randint(7, 30)):
                buffer.append((self._time, np.sin(self._freq*2*np.pi*self._time)))
                self._time += 0.001
            conn.send(buffer)

def consume(conn):
    print("Consuming...")
    ed = ExtremaDetector()
    # consumer_socketio = SocketIO(message_queue="redis://")
    while True:
        buffer = conn.recv()
        # consumer_socketio.emit("data", {"buffer" : buffer})
        for point in buffer:
            if ed.check_value(point):
                pass

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("start_stream")
def stream_data():
    streamer = DataStreamer()
    consumer, producer = Pipe(False)

    producer_process = Process(target=streamer.produce, args=(producer,))
    consumer_process = Process(target=consume, args=(consumer,))

    producer_process.start()
    consumer_process.start()

if __name__ == "__main__":

    # redis.Redis()
    # socketio.run(app, use_reloader=True, debug=True, extra_files=['/templates/index.html'])
    ip = get_ip_address()
    socketio.run(app,
                 host=ip,
                 port=8080,
                 use_reloader=True,
                 debug=True,
                 extra_files=["templates/index.html"])
