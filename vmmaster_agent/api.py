from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet.threads import deferToThread
from twisted.web.server import NOT_DONE_YET

import base64
import json

import tempfile
import autopy


## Blocking code that record a desktop and saves to file
def take_screenshot():
    tmp_file_path = tempfile.mktemp(suffix='.png')

    autopy.bitmap.capture_screen().save(tmp_file_path)

    try:
        with open(tmp_file_path, "rb") as image_file:
            img = base64.b64encode(image_file.read())
        return img
    except:
        return None


class TakeScreenshot(Resource):
    isLeaf = True

    def do_something_with_screenshot(self, screenshot, request):
        request.write(json.dumps({'screenshot': screenshot}))
        request.finish()

    def render_GET(self, request):
        d = deferToThread(take_screenshot)
        d.addCallback(lambda screenshot: TakeScreenshot.do_something_with_screenshot(self, screenshot, request))
        return NOT_DONE_YET


class ApiServer(Site):
    root = Resource()

    def setup_root(self):
        self.root.server = self
        self.root.putChild('takeScreenshot', TakeScreenshot())

    def __init__(self):
        Site.__init__(self, self.root)
        self.setup_root()
