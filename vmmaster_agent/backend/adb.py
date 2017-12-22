# coding: utf-8

import os
import logging
import tempfile
import subprocess


log = logging.getLogger(__name__)


class AdbProcess(object):
    def __init__(self, args):
        self.returncode = None

        self._out_tempfile = tempfile.NamedTemporaryFile(delete=True)
        self._err_tempfile = tempfile.NamedTemporaryFile(delete=True)

        self.stdout = open(self._out_tempfile.name, 'rb')
        self.stderr = open(self._err_tempfile.name, 'rb')

        self._process = subprocess.Popen(
            args,
            stdout=self._out_tempfile,
            stderr=self._err_tempfile,
            env=os.environ.copy()
        )

    def __del__(self):
        self.stdout.close()
        self.stderr.close()
        self._out_tempfile.close()
        self._err_tempfile.close()

    def wait(self):
        self.returncode = self._process.wait()
        return self.returncode

    def poll(self):
        self.returncode = self._process.poll()
        return self.returncode

    def terminate(self):
        self._process.terminate()


def _exec_adb(device_name, params):
    command = ["adb"] + params
    if device_name:
        command.extend(['-s', device_name])
    log.debug('ADB :{}: {}'.format(device_name, ' '.join(command)))
    return AdbProcess(command)


def get_device_name():
    adbp = _exec_adb(None, ['devices'])
    adbp.wait()
    stdout = adbp.stdout.readlines()
    if len(stdout) >= 2:
        stdout = stdout[1].split()[0]
    log.debug('Connected devices: {}'.format(stdout))
    return stdout
