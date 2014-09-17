import json

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet.threads import deferToThread
from twisted.web.server import NOT_DONE_YET

from .backend import take_screenshot, run_script


class TakeScreenshot(Resource):
    isLeaf = True

    def do_something_with_screenshot(self, screenshot, request):
        request.write(json.dumps({'screenshot': screenshot}))
        request.finish()

    def render_GET(self, request):
        d = deferToThread(take_screenshot)
        d.addCallback(lambda screenshot: TakeScreenshot.do_something_with_screenshot(self, screenshot, request))
        return NOT_DONE_YET


class RunScript(Resource):
    isLeaf = True

    def form_response(self, return_code, output, request):
        request.write(json.dumps({'status': return_code, 'output': output}))
        request.finish()

    def render_POST(self, request):
        data = json.loads(request.content.read())
        d = deferToThread(run_script, data.get("script"), data.get("command", None))
        d.addCallback(lambda r: self.form_response(r[0], r[1], request))
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
