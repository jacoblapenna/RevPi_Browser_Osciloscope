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
import revpimodio2

from flask import Flask, render_template
from flask_socketio import SocketIO

try:
    from daqhats import mcc118, OptionFlags, HatIDs, HatError
    from daqhats_utils import select_hat_device, enum_mask_to_string, chan_list_to_mask
    mcc_daqhat = True
except ImportError:
    # on revolution pi
    mcc_daqhat = False

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
        self._threshold = 0.01
        self._SNR = 100
        self._look_for_maxima = True

    def check_value(self, val):
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
                return True
        else:
            if val > self._mn + self._threshold:
                self._mx = val
                self._look_for_maxima = True
                return True

        return None


class DataStreamer:
    """
    pull from AIO on revpi here when ready
    """
    def __init__(self, hat):
        self._consumer, self._producer = Pipe()
        self._extrema_detector = ExtremaDetector()
        self._hat = hat
        if self._hat:
            self._address = select_hat_device(HatIDs.MCC_118)
            self._daq = mcc118(self._address)
            self._mcc_option = OptionFlags.CONTINUOUS
            self._stream_data = False

    def produce(self):
        """
        This method is ran in another process, and, to be thread safe, all
        class attributes used here cannot be used in any other method other
        than __init__.

        This process is always running and whether data is streamed or not is
        determined via duplex communication through the pipe.

        Eventually, an instruction will need to  be added to stop and restart
        the pipe and process. This should be done whenever control is taken
        and given up.
        """

        """ Revolution Pi """
        if not self._hat:
            class DAQ:
                def __init__(self, pipe_connection):
                    self.daq = revpimodio2.RevPiModIO(autorefresh=True)
                    self._conn = pipe_connection
                    self._stream_data = False
                    self._buffer = []

                def cycle_handler(self, ct):
                    if self._stream_data:
                        self._buffer.append(self.daq.io.InputValue_1.value/1000)
                    if self._conn.poll():
                        instruction = self._conn.recv()
                        if instruction == "start_stream":
                            self._stream_data = True
                        elif instruction == "stop_stream":
                            self._stream_data = False
                            self._conn.send(self._buffer)
                            self._buffer = []
                        elif instruction == "get_new_data":
                            self._conn.send(self._buffer)
                            self._buffer = []
                        else:
                            raise Exception(f"Invalid instruction at producer: instruction=={instruction}")

            daq = DAQ(self._producer)

            daq.daq.cycleloop(daq.cycle_handler, cycletime=25)

        """ MCC Daqhat """
        if self._hat:
            channels = [0]
            channel_mask = chan_list_to_mask(channels)
            options = self._mcc_option
            scan_rate = 30
            samples = round(scan_rate * 3600)
            stream_data = False
            buffer = []

            self._daq.a_in_scan_start(channel_mask, samples, scan_rate, options)

            while True:
                if self._stream_data:
                    buffer += self._daq.a_in_scan_read().data
                if self._producer.poll():
                    instruction = self._producer.recv()
                    if instruction == "start_stream":
                        self._stream_data = True
                    elif instruction == "stop_stream":
                        self._stream_data = False
                        self._producer.send(buffer)
                        buffer = []
                    elif instruction == "get_new_data":
                        self._producer.send(buffer)
                        buffer = []
                    else:
                        raise Exception(f"Invalid instruction at producer: instruction=={instruction}")

    def control_stream(self, instruction, socket):
        if instruction == "start_stream":
            self._consumer.send(instruction)
            socket.emit("stream_started")
        elif instruction == "stop_stream":
            self._consumer.send(instruction)
            self._consume(1, socket)
            socket.emit("stream_stopped")
        elif instruction == "get_new_data":
            self._consumer.send(instruction)
            self._consume(1, socket)
        else:
            raise Exception(f"Invalid instruction at consumer: instruction=={instruction}")

    def _consume(self, timeout, socket):
        buffer = None
        if self._consumer.poll(timeout):
            buffer = self._consumer.recv()
            if buffer:
                socket.emit("new_data", {"data" : buffer})


@app.route('/')
def index():
    return render_template("index.html")


@socketio.on("start_stream")
def start_stream():
    if not mp.active_children():
        producer_process = Process(target=data_streamer.produce, name="producer_process")
        producer_process.start()
    data_streamer.control_stream("start_stream", socketio)


@socketio.on("stop_stream")
def stop_stream():
    data_streamer.control_stream("stop_stream", socketio)


@socketio.on("get_new_data")
def get_new_data():
    data_streamer.control_stream("get_new_data", socketio)


if __name__ == "__main__":
    print(f"mcc_daqhat={mcc_daqhat}")
    data_streamer = DataStreamer(hat=mcc_daqhat)
    ip = get_ip_address()
    socketio.run(app,
                 host=ip,
                 port=8080,
                 use_reloader=True,
                 debug=True,
                 extra_files=["templates/index.html"])
