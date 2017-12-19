import os
import subprocess
from threading import Thread
import time


def wait_for(condition, timeout=5):
    start = time.time()
    while not condition() and time.time() - start < timeout:
        time.sleep(0.1)

    return condition()


class Screencast(Thread):
    def __init__(self, websocket):
        super(Screencast, self).__init__()
        self.websocket = websocket
        self.process = None

    def run(self):
        filename = './video.ogv'
        env = os.environ.copy()
        # env['PYTHONUNBUFFERED'] = '1'
        env['DISPLAY'] = ':0'
        self.process = subprocess.Popen(["/usr/bin/recordmydesktop",
                                        "--fps=5",
                                        "--no-sound",
                                        "--on-the-fly-encoding",
                                        "--output=%s" % filename,
                                        "--overwrite"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        env=env)

        wait_for(lambda: os.path.isfile(filename)
                 and os.access(filename, os.R_OK))

        screencast_file = open(filename, 'r')
        self.websocket.beginMessage(isBinary=True)

        while self.process.poll() is None:
            data = screencast_file.read(1024)
            if data:
                print 'send'
                self.websocket.sendMessageFrame(data)

        import time
        time.sleep(10)
        data = screencast_file.read()
        # while data != "":
        #     data += screencast_file.read()

        self.websocket.sendMessageFrame(data)
        self.websocket.endMessage()
        print 'stopped'

    def stop(self):
        self.process.terminate()
