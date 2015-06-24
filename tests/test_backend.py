# coding: utf-8
import unittest
from ddt import ddt, data
from vmmaster_agent.backend import run_script


class WebsocketLikeObject(object):
    def __init__(self):
        self.data = ""

    def sendMessage(self, data):
        self.data += data


@ddt
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

    @data('hello world', 'Привет, мир!')
    def test_output_with_websocket(self, message):
        websocket = WebsocketLikeObject()
        output = run_script("echo '%s'" % message, websocket=websocket)
        self.assertEqual((0, ""), output)
        self.assertEqual(message, websocket.data[:-1])