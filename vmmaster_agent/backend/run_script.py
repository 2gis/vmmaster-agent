# coding: utf-8
import subprocess
import tempfile
import platform
import logging
import os
import locale
import time

from threading import Lock, Thread

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


ENCODING = locale.getpreferredencoding()


class Flusher(Thread):
    def __init__(self, interval, callback):
        Thread.__init__(self)
        self.running = True
        self.daemon = True
        self.interval = interval
        self.callback = callback

    def run(self):
        while self.running:
            self.callback()
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        self.join()


class Channel(object):
    flush_frequency = 1
    buffer = ""

    def __init__(self, websocket=None, autoflush=True):
        if websocket:
            self.channel = websocket
        else:
            self.channel = ''

        self.lock = Lock()
        if autoflush:
            self.flusher = Flusher(self.flush_frequency, self.flush)
            self.flusher.start()

    def write(self, _buffer):
        with self.lock:
            self.buffer += _buffer

    def flush(self):
        with self.lock:
            if self.buffer:
                log.info("flushing: %s" % self.buffer)
                if isinstance(self.channel, str) or isinstance(self.channel, unicode):
                    self.channel += self.buffer
                else:
                    self.channel.sendMessage(self.buffer.encode('utf-8'))
                self.buffer = ""

    def close(self):
        if self.buffer:
            self.flush()
        self.flusher.stop()


def run_command(command, websocket):
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    log.info("Running command: %s" % str(command))
    with tempfile.NamedTemporaryFile(delete=True) as f:
        with open(f.name, 'rb') as stdout:
            process = subprocess.Popen(command, stdout=stdout, stderr=stdout, env=env)

            channel = Channel(websocket, autoflush=True)
            while process.poll() is None:
                channel.write(process.stdout.read(1).decode(ENCODING))

            channel.write(process.stdout.read().decode(ENCODING))
            channel.close()

    if isinstance(channel.channel, str) or isinstance(channel.channel, unicode):
        output = channel.channel
    else:
        output = ""

    return process.returncode, output


def run_script(script, command=None, websocket=None):
    log.info("Got script: %s" % script.encode(ENCODING))
    tmp_file_path = None
    if command is None:
        if platform.system() == "Windows":
            tmp_file_path = tempfile.mktemp(suffix=".bat")
            command = "cmd.exe /c"
        else:
            command = "/bin/bash"

    if tmp_file_path is None:
        tmp_file_path = tempfile.mktemp()

    with open(tmp_file_path, "w") as f:
        log.info("Writing script to: %s" % tmp_file_path)
        f.write(script.encode(ENCODING))

    return run_command(command.split(" ") + [tmp_file_path], websocket)
