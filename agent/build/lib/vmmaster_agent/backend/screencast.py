# coding: utf-8

import os
import errno
import logging
import subprocess
from threading import Timer

from vmmaster_agent.backend import adb


log = logging.getLogger(__name__)


class ScreencastRecorder:
    url = None
    process = None
    screencast_file_abspath = None

    def __init__(self):
        self.screencast_dir_abspath = os.path.join(os.path.dirname(os.path.abspath(self.__module__)), "screencast")

    def convert_images_to_video(self):
        log.info("Start converting images to video...")
        input_file = "{}/input.txt".format(self.screencast_dir_abspath)

        if not os.path.exists(input_file):
            raise Exception("Screencast file was not created because input.txt file for ffmpeg not found.")

        self.screencast_file_abspath = os.path.join(self.screencast_dir_abspath, "video.webm")
        args = [
            "ffmpeg",
            "-loglevel", "panic",
            "-f", "concat",
            "-i", input_file,
            self.screencast_file_abspath
        ]
        try:
            converter = subprocess.Popen(args, stdout=subprocess.PIPE)
            if converter.pid:
                converter.communicate()
        except OSError as e:
            if e.errno == errno.ENOENT:
                log.exception("ffmpeg is not installed, screenshots won't be converted to video")
            else:
                raise Exception("Error while running ffmpeg. Screencast file was not created")

        if os.path.exists(self.screencast_file_abspath):
            log.info("Screencast file was successfully created: {}".format(self.screencast_file_abspath))
            return self.screencast_file_abspath
        else:
            raise Exception("Screencast file was not created for an unknown reason")

    @property
    def pid(self):
        if self.is_alive():
            return self.process.pid

    def start(self, url=None):
        self.url = url if url else adb.get_device_name()

        log.info(
            "Starting recorder for current session on {} to {} ...".format(self.url, self.screencast_dir_abspath))
        args = [
            "stf-record",
            "--adb-connect-url", self.url,
            "--log-level", "INFO",
            "--dir", self.screencast_dir_abspath
        ]
        try:
            self.process = subprocess.Popen(args, stdout=subprocess.PIPE)
        except:
            raise Exception("Failed to start stf-record")

        log.info("Record process(PID:{}) has been started...".format(self.pid))
        return self.pid

    def stop(self):
        def kill(process):
            log.warn("Timeout expired while waiting for process to terminate. Killing...")
            process.kill()
        if self.process and not self.process.returncode:
            timer = Timer(15, kill, [self.process])
            try:
                timer.start()
                self.process.terminate()
                self.process.wait()
            finally:
                timer.cancel()
        log.info("Stopped recoder for current session on {}...".format(self.url))

    def stop_and_convert(self):
        self.stop()
        self.convert_images_to_video()

    def is_alive(self):
        if self.process and not self.process.returncode:
            log.debug("Screencast process is alive!")
            return True
