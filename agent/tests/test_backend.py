# coding: utf-8
import unittest
import time
from mock import Mock

from vmmaster_agent.backend import run_script
from vmmaster_agent.backend.run_script import Flusher


class WebsocketLikeObject(object):
    def __init__(self):
        self.data = ""

    def sendMessage(self, data):
        self.data += data


class TestRunScript(unittest.TestCase):
    def test_singleline_run_script(self):
        output = run_script("echo 'hello world'")
        self.assertEqual((0, "hello world\n"), output)

    def test_multiline_run_script(self):
        output = run_script(
            "#!/usr/bin/env bash\n"
            "TEXT='hello world'\n"
            "echo $TEXT\n")
        self.assertEqual((0, "hello world\n"), output)

    def test_run_script_with_command(self):
        output = run_script(
            "print 'hello world'",
            command="python")
        self.assertEqual((0, "hello world\n"), output)

    def test_fail_run_script(self):
        output = run_script(
            "command_to_fail")
        self.assertEqual(127, output[0])
        self.assertTrue("line 1: command_to_fail: command not found\n" in output[1])

    def test_output_with_stderr(self):
        output = run_script(
            ">&2 echo 'error'")
        self.assertEqual(0, output[0])
        self.assertEqual("error\n", output[1])

    def test_output_with_websocket(self):
        websocket = WebsocketLikeObject()
        output = run_script("echo 'hello world'", websocket=websocket)
        self.assertEqual((0, ""), output)
        self.assertEqual("hello world\n", websocket.data)

    def test_websocket_flusher(self):
        mock = Mock()

        flusher = Flusher(interval=0.1, callback=mock)
        flusher.start()
        time.sleep(0.5)
        self.assertEqual(mock.call_count, 5)
        time.sleep(0.5)
        self.assertEqual(mock.call_count, 10)