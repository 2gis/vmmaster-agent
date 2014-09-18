import json

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet.threads import deferToThread
from twisted.web.server import NOT_DONE_YET

from .backend import take_screenshot, run_script


def json_response(data, request):
    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    request.responseHeaders.addRawHeader(b"connection", b"close")
    request.write(json.dumps(data))
    request.finish()


class TakeScreenshot(Resource):
    isLeaf = True

    def render_GET(self, request):
        d = deferToThread(take_screenshot)
        d.addCallback(lambda screenshot: json_response({'screenshot': screenshot}, request))
        return NOT_DONE_YET


class RunScript(Resource):
    isLeaf = True

    def render_POST(self, request):
        data = json.loads(request.content.read())
        d = deferToThread(run_script, data.get("script"), data.get("command", None))
        d.addCallback(lambda r: json_response({'status': r[0], 'output': r[1]}, request))
        return NOT_DONE_YET


class ApiServer(Site):
    root = Resource()

    def setup_root(self):
        self.root.server = self
        self.root.putChild('takeScreenshot', TakeScreenshot())
        self.root.putChild('runScript', RunScript())

    def __init__(self):
        Site.__init__(self, self.root)
        self.setup_root()
