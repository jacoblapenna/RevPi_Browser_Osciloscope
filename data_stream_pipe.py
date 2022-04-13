# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:16:40 2022

@author: jlapenna
"""
import eventlet
eventlet.monkey_patch(thread=False)

import numpy as np
from multiprocessing import Pipe, Process
import multiprocessing as mp
import random
import time
from collections import deque
import redis
import socket
from collections import deque

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
    def __init__(self, max_buffer_len):
        self._freq = 2.0
        self._dt = 0.001
        self._time = 0
        self._max_len = max_buffer_len;
        self._buffer = deque([], maxlen=self._max_len)
        self._buffer_len = 0
        self._consumer, self._producer = Pipe(False)
        self._socket = SocketIO(message_queue="redis://", async_mode="eventlet")

    def produce(self):
        print("Producing...")
        while True:
            point = (self._time, np.sin(self._freq*2*np.pi*self._time))
            self._producer.send(point)
            self._time += 0.001

    def consume(self):
        print("Consuming...")
        detector = ExtremaDetector()
        while True:
            try:
                point = self._consumer.recv()
                self._buffer.append(point)
                if self._buffer_len < self._max_len:
                    self._buffer_len += 1
                if detector.check_value(point):
                    pass # emit current control event here
                self._socket.emit("data", {"data" : list(self._buffer)})
            except EOFError:
                self._consumer.close()

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on("start_stream")
def start_stream():
    streamer = DataStreamer(10000)

    producer_process = Process(target=streamer.produce, name="producer_process")
    consumer_process = Process(target=streamer.consume, name="consumer_process")

    producer_process.start()
    consumer_process.start()

@socketio.on("stop_stream")
def stop_stream():
    # print("Terminating processes...")
    # consumer.close()
    # producer.close()
    for p in mp.active_children():
        if p.name == "producer_process" or p.name == "consumer_process":
            print(dir(p))
            # p.close()
            # p.terminate()

if __name__ == "__main__":

    r = redis.Redis()
    try:
        r.ping()
    except ConnectionRefusedError:
        raise(Exception("Please start the redis server via $ redis-server command!"))

    # socketio.run(app, use_reloader=True, debug=True, extra_files=['/templates/index.html'])
    ip = get_ip_address()
    socketio.run(app,
                 host=ip,
                 port=8080,
                 use_reloader=True,
                 debug=True,
                 extra_files=["templates/index.html"])
