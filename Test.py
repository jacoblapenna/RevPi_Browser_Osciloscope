from multiprocessing import Pipe, Process
import revpimodio2

def process_target(conn):
    class DAQ:
        def __init__(self, conn):
            self._conn = conn
            self._revpi = revpimodio2.RevPiModIO(autorefresh=True)

        def _produce_data(self, ct):
            new_data = self._revpi.io.InputValue_1.value/1000
            self._conn.send(new_data)

        def produce(self):
            self._revpi.cycleloop(self._produce_data, cycletime=25)

        daq = DAQ(conn)
        daq.produce()

conn1, conn2 = Pipe()
p = Process(target=process_target, args=(conn2,))
p.start()

while True:
    if conn1.poll():
        print(conn1.recv())
