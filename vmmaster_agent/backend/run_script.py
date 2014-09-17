# coding: utf-8
import subprocess
import sys
import tempfile
import platform


def run_command(command, silent=False):
    process = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

    if not silent:
        output = ""
        while process.poll() is None:
            line = process.stdout.readline()
            sys.stdout.write(line)
            output += line

        sys.stdout.write('\n')
    else:
        process.wait()

    return process.returncode, process.communicate()[0]


def run_script(script, command=None):
    if command is None:
        if platform.system() == "Windows":
            tmp_file_path = tempfile.mktemp(suffix=".bat")
            command = "cmd.exe /c"
        else:
            tmp_file_path = tempfile.mktemp()
            command = "/bin/bash"

    with open(tmp_file_path, "w") as f:
        f.write(script)

    return run_command(command.split(" ") + [tmp_file_path], silent=True)
