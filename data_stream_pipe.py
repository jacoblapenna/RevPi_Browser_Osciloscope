# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:16:40 2022

@author: jlapenna
"""

import numpy as np
from multiprocessing import Pipe, Process
import multiprocessing as mp
import random
import time
from collections import deque
import socket
from collections import deque

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
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
                return True
        else:
            if val > self._mn + self._threshold:
                self._mx = val
                self._look_for_maxima = True
                # print(f"Local minima detected at {(self._mn_t, self._mn)}")
                return True

        return None


class DataStreamer:

    """
    pull from AIO on revpi here when ready
    """
    def __init__(self):
        self._freq = 2.0
        self._dt = 0.001
        self._time = 0
        self._consumer, self._producer = Pipe()
        self._extrema_detector = ExtremaDetector()
        self._stop_stream = False

    def produce(self):
        """
        This method is ran in another process, and, to be thread safe, all
        class attributes used here cannot be used in any other method other
        than __init__.
        """
        buffer = []
        while True:
            buffer.append([self._time, np.sin(self._freq*2*np.pi*self._time)])
            self._time += 0.001
            if self._producer.poll():
                consumer_instruction = self._producer.recv()
                if consumer_instruction == "get_new_data":
                    self._producer.send(buffer)
                    buffer = []
                elif consumer_instruction == "stop_producer":
                    break
                else:
                    raise Exception(f"Invalid instruction: consumer_instruction=={consumer_instruction}")
        # close this connection here so process can be stopped

    def consume(self, socket):
        buffer = None
        self._consumer.send("get_new_data")
        if self._consumer.poll(1000):
            buffer = self._consumer.recv()
            if buffer:
                socket.emit("new_data", {"data" : buffer})

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("start_stream")
def start_stream():
    producer_process = Process(target=data_streamer.produce, name="producer_process")
    producer_process.start()
    socketio.emit("stream_started")

@socketio.on("stop_stream")
def stop_stream():
    for p in mp.active_children():
        if p.name == "producer_process":
            print(dir(p))
            # p.close()
            # p.terminate()

@socketio.on("get_new_data")
def get_and_send_new_data():
    data_streamer.consume(socketio)

if __name__ == "__main__":

    data_streamer = DataStreamer()

    ip = get_ip_address()
    socketio.run(app,
                 host=ip,
                 port=8080,
                 use_reloader=True,
                 debug=True,
                 extra_files=["templates/index.html"])
