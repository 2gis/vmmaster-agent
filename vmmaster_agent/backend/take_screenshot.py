# coding: utf-8
import platform
import base64
import tempfile

try:
    from PIL import ImageGrab
except ImportError:
    pass

from run_script import run_command


def take_screenshot():
    """
    Blocking code that takes screenshot of a desktop
    :return: base64 string
    """
    tmp_file_path = tempfile.mktemp(suffix='.png')
    if platform.system() == "Windows":
        ImageGrab.grab().save(tmp_file_path)
    elif platform.system() == "Darwin":
        run_command(["screencapture", tmp_file_path], None)
    else:
        run_command(["gnome-screenshot", "-f", tmp_file_path], None)

    try:
        with open(tmp_file_path, "rb") as image_file:
            img = base64.b64encode(image_file.read())
        return img
    except Exception as e:
        return str(type(e)) + e.message
