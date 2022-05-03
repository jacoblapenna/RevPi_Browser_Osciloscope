from multiprocessing import Pipe, Process
import revpimodio2

from random import randint
from time import sleep

from flask_socketio import SocketIO

class DataStreamer:
    """
    pull from AIO on revpi here when ready
    """
    def __init__(self):
        self._produce_stream = False # TEMP
        self._producer_socketio = SocketIO(message_queue='redis://')
        self._controller_conn, self._producer_conn = Pipe()
        self._producer_process = Process(target=self._produce, name="producer_process")
        self._producer_process.start()

    def _produce(self):
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
        class DAQ:
            def __init__(self, socketio, conn):
                self._produce_stream = False
                self.buffer = []
                self._socketio = socketio
                self._conn = conn
                self._revpi = revpimodio2.RevPiModIO(autorefresh=True)

            def _cycle_handler(self, ct):
                if self._produce_stream:
                    new_data = randint(-500, 500)/100
                    self._socketio.emit("new_data", {"data" : new_data})
                if self._conn.poll():
                    instruction = self._conn.recv()
                    if instruction == "start_stream":
                        self._produce_stream = True
                        self._socketio.emit("stream_started")
                    elif instruction == "stop_stream":
                        self._produce_stream = False
                        self._socketio.emit("stream_stopped")
                    else:
                        raise Exception(f"Producer received invalid instruction: instruction={instruction}")

            def produce(self):
                self._revpi.cycleloop(self._cycle_handler, cycletime=25)
                # while True:
                #     self._cycle_handler(1)
                #     sleep(0.025)

        daq = DAQ(self._producer_socketio, self._producer_conn)
        daq.produce()

    def control_stream(self, instruction):
        if instruction == "start_stream":
            self._controller_conn.send(instruction)
        elif instruction == "stop_stream":
            self._controller_conn.send(instruction)
        else:
            raise Exception(f"Attempt to send invalid instruction to producer: instruction={instruction}")
