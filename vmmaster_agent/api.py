import json

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet.threads import deferToThread
from twisted.web.server import NOT_DONE_YET
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

from backend import take_screenshot, run_script, screencast


def json_response(data, request):
    j = json.dumps(data)
    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    request.responseHeaders.addRawHeader(b"connection", b"close")
    request.responseHeaders.addRawHeader(b"content-length", str(len(j)))
    request.write(j)
    request.finish()


class TakeScreenshot(Resource):
    isLeaf = True

    def render_GET(self, request):
        d = deferToThread(take_screenshot)
        d.addCallback(lambda screenshot: json_response({'screenshot': screenshot}, request))
        return NOT_DONE_YET


class Screencast(Resource):
    isLeaf = True

    def __init__(self):
        Resource.__init__(self)
        self.screencast_recorder = screencast.ScreencastRecorder()
        self.putChild('/start', startScreencast(self.screencast_recorder))
        self.putChild('/stop', stopScreencast(self.screencast_recorder))

    def render_GET(self, request):
        if "/start" in request.path:
            self.getStaticEntity('/start').render_GET(request)
            return NOT_DONE_YET
        if "/stop" in request.path:
            self.getStaticEntity('/stop').render_GET(request)
            return NOT_DONE_YET
        return


class BaseScreencastCommand(Resource):
    def __init__(self, recorder):
        Resource.__init__(self)
        self.recorder = recorder


class startScreencast(BaseScreencastCommand):
    def render_GET(self, request):
        d = deferToThread(lambda: self.recorder.start())
        d.addCallback(lambda r: json_response(
            {'status': 0, 'output': "Screencast was started with PID #{}".format(self.recorder.pid)}, request)
        )
        d.addErrback(lambda f: json_response(
            {'status': 127, 'output': "Screencast starting was failed: {}".format(f)}, request)
        )
        return NOT_DONE_YET


class stopScreencast(BaseScreencastCommand):
    def render_GET(self, request):
        d = deferToThread(self.recorder.stop_and_convert)
        d.addCallback(lambda r: json_response(
            {'status': 0, 'output': "Screencast(PID:{}) was stopped and saved artifact to {}".format(
                self.recorder.pid, self.recorder.screencast_file_abspath
            )}, request)
        )
        d.addErrback(lambda f: json_response(
            {'status': 127, 'output': "Screencast stopping was failed: {}".format(f)}, request)
        )
        return NOT_DONE_YET


class RunScript(Resource):
    isLeaf = True

    def __init__(self):
        Resource.__init__(self)
        self.putChild('/websocket', RunScriptWebSocket())
        self.putChild('/http', RunScriptHTTP())

    def render(self, request):
        if request.requestHeaders.hasHeader('Upgrade'):
            self.getStaticEntity('/websocket').render(request)
        else:
            self.getStaticEntity('/http').render_POST(request)
        return NOT_DONE_YET


class RunScriptHTTP(Resource):
    def render_POST(self, request):
        data = json.loads(request.content.read())
        d = deferToThread(run_script, data.get("script"), data.get("command", None))
        d.addCallback(lambda r: json_response({'status': r[0], 'output': r[1]}, request))
        d.addErrback(lambda f: json_response({'status': 127, 'output': str(f)}, request))
        return NOT_DONE_YET


class RunScriptWebSocketProtocol(WebSocketServerProtocol):
    def onMessage(self, payload, isBinary):
        data = json.loads(payload)
        d = deferToThread(run_script, data.get("script"), data.get("command", None), self)
        d.addCallback(lambda r: self.endConnection(r))
        d.addErrback(lambda f: self.endConnection(f))

    def endConnection(self, result):
        if isinstance(result, tuple) and result[0] == 0:
            self.sendClose(code=WebSocketServerProtocol.CLOSE_STATUS_CODE_NORMAL,
                           reason=unicode(result[1])[:120])
        else:
            self.sendClose(code=3001, reason=unicode(result)[:120])


class RunScriptWebSocket(WebSocketResource):
    isLeaf = True

    def __init__(self):
        wsfactory = WebSocketServerFactory()
        wsfactory.protocol = RunScriptWebSocketProtocol
        wsfactory.setProtocolOptions(echoCloseCodeReason=True)
        super(RunScriptWebSocket, self).__init__(wsfactory)


class ApiServer(Site):
    root = Resource()

    def __init__(self):
        Site.__init__(self, self.root)
        self.root.server = self
        self.root.putChild('takeScreenshot', TakeScreenshot())
        self.root.putChild('runScript', RunScript())
        self.root.putChild('screencast', Screencast())
