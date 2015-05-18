# coding: utf-8

import unittest
import json
from functools import partial

import requests
from nose.twistedtools import reactor

from vmmaster_agent.agent import VMMasterAgent

take_screenshot_request = partial(requests.get, "http://localhost:9000/takeScreenshot")
script = {
    'script': "echo 'hello world'"
}
script_with_command = {
    "command": "python",
    "script": "print 'hello world'"
}
run_script_request = partial(requests.post,
                             "http://localhost:9000/runScript",
                             data=json.dumps(script))
run_script_request_with_command = partial(requests.post,
                                          "http://localhost:9000/runScript",
                                          data=json.dumps(script_with_command))


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = VMMasterAgent(reactor)

    @classmethod
    def tearDownClass(cls):
        cls.agent.stop()

    def test_take_screenshot(self):
        result = take_screenshot_request()
        self.assertEqual(200, result.status_code)
        self.assertTrue("screenshot" in result.content)

    def test_run_script(self):
        response = run_script_request()
        result = {
            "status": 0,
            "output": "hello world\n"
        }
        self.assertEqual(200, response.status_code)
        self.assertEqual(result, json.loads(response.content))

    def test_run_script_with_command(self):
        response = run_script_request_with_command()
        result = {
            "status": 0,
            "output": "hello world\n"
        }
        self.assertEqual(200, response.status_code)
        self.assertEqual(result, json.loads(response.content))