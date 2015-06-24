# coding: utf-8
import subprocess
import platform
import base64
import tempfile

import pyscreenshot
try:
    from PIL import ImageGrab
except ImportError:
    pass

from run_script import run_command


## Blocking code that record a desktop and saves to file
def take_screenshot():
    tmp_file_path = tempfile.mktemp(suffix='.png')

    if platform.system() == "Windows":
        ImageGrab.grab().save(tmp_file_path)
    if platform.system() == "Darwin":
        run_command(["screencapture", tmp_file_path], None)
    else:
        pyscreenshot.grab_to_file(tmp_file_path)

    try:
        with open(tmp_file_path, "rb") as image_file:
            img = base64.b64encode(image_file.read())
        return img
    except:
        return None