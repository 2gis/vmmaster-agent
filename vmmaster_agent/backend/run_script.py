# coding: utf-8
import subprocess
import tempfile
import platform
import logging
import os
import sys
from threading import Lock, Timer

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


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
            self.flusher = Timer(self.flush_frequency, self.flush)
            self.flusher.start()

    def write(self, _buffer):
        with self.lock:
            self.buffer += _buffer

    def flush(self):
        self.flusher = Timer(self.flush_frequency, self.flush)
        with self.lock:
            if self.buffer:
                log.info("flushing: %s" % self.buffer)
                if isinstance(self.channel, str) or isinstance(self.channel, unicode):
                    self.channel += self.buffer
                else:
                    self.channel.sendMessage(bytes(self.buffer))
                self.buffer = ""

    def close(self):
        if self.buffer:
            self.flush()
        self.flusher.cancel()


def run_command(command, websocket):
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    log.info("Running command: %s" % str(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)

    channel = Channel(websocket, autoflush=True)
    while process.poll() is None:
        channel.write(process.stdout.read(1).decode(sys.stdout.encoding))

    channel.write(process.stdout.read().decode(sys.stdout.encoding))
    channel.close()

    if isinstance(channel.channel, str) or isinstance(channel.channel, unicode):
        output = channel.channel
    else:
        output = ""

    return process.returncode, output


def run_script(script, command=None, websocket=None):
    log.info("Got script: %s" % str(script))
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
        log.info("Writing script to: %s" % str(tmp_file_path))
        f.write(script)

    return run_command(command.split(" ") + [tmp_file_path], websocket)