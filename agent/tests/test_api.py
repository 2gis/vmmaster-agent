# coding: utf-8

import unittest
import json
from Queue import Queue
from StringIO import StringIO
from threading import Thread

import requests
from twisted.internet import reactor as twisted_reactor
from twisted.python.failure import Failure
from twisted.internet import defer
from twisted.internet.endpoints import TCP4ClientEndpoint
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketClientFactory

from vmmaster_agent.agent import VMMasterAgent

script = {
    'script': "echo 'hello world'"
}


def sleep(secs):
    d = defer.Deferred()
    twisted_reactor.callLater(secs, d.callback, None)
    return d


@defer.inlineCallbacks
def wait_for_output(output):
    while not output.getvalue():
        yield sleep(0)
    yield defer.succeed(True)


def block_on(d, timeout=None):
    q = Queue()
    d.addBoth(q.put)
    ret = q.get(timeout is not None, timeout)
    if isinstance(ret, Failure):
        ret.raiseException()
    else:
        return ret


class MyClientProtocol(WebSocketClientProtocol):

    def __init__(self, output):
        WebSocketClientProtocol.__init__(self)
        self.output = output

    def onOpen(self):
        self.sendMessage(u'{"script": "фыва"}'.encode('utf8'))

    def onMessage(self, payload, isBinary):
        self.output.write(payload)


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = VMMasterAgent(twisted_reactor)
        cls.agent_thread = Thread(target=cls.agent.run)
        cls.agent_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.agent.stop()
        cls.agent_thread.join()

    def test_take_screenshot(self):
        result = requests.get("http://localhost:9000/takeScreenshot")
        self.assertEqual(200, result.status_code)
        self.assertTrue("screenshot" in result.content)

    def test_run_script(self):
        response = requests.post(
            "http://localhost:9000/runScript",
            data=json.dumps(script)
        )
        result = {
            "status": 0,
            "output": "hello world\n"
        }
        self.assertEqual(200, response.status_code)
        self.assertEqual(result, json.loads(response.content))

    def test_run_script_with_command(self):
        script_with_command = {
            "command": "python",
            "script": "print('hello world')"
        }
        response = requests.post(
            "http://localhost:9000/runScript",
            data=json.dumps(script_with_command)
        )
        result = {
            "status": 0,
            "output": "hello world\n"
        }
        self.assertEqual(200, response.status_code)
        self.assertEqual(result, json.loads(response.content))

    def test_run_script_websocket(self):
        point = TCP4ClientEndpoint(twisted_reactor, "localhost", 9000)
        factory = WebSocketClientFactory("ws://localhost:9000/runScript")
        output = StringIO()
        factory.protocol = lambda: MyClientProtocol(output)
        point.connect(factory)
        block_on(wait_for_output(output), 5)
        self.assertIn("command not found", output.getvalue())