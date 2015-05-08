# coding: utf-8
import subprocess
import sys
import tempfile
import platform
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


def run_command(command):
    log.info("Running command: %s" % str(command))
    stdout = tempfile.TemporaryFile()
    process = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=stdout)
    process.wait()
    stdout.flush()
    stdout.seek(0)
    output = stdout.read().decode(sys.stdout.encoding)
    stdout.close()
    sys.stdout.write(output)
    log.info("Command ended with returncode %s" % process.returncode)
    return process.returncode, output


def run_script(script, command=None):
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

    return run_command(command.split(" ") + [tmp_file_path])
