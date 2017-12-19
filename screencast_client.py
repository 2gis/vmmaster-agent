from threading import Thread
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS, WebSocketServerProtocol


class FrameBasedHashClientProtocol(WebSocketClientProtocol):

    """
    Frame-based WebSockets server that computes a running SHA-256 for message
    data received. It will respond after every frame received with the digest
    computed up to that point. It can receive messages of unlimited number
    of frames. Digest is reset upon new message.
    """

    def onMessageBegin(self, isBinary):
        WebSocketClientProtocol.onMessageBegin(self, isBinary)
        self.screencast_file = open('./screencast.ogv', 'w')

        from twisted.internet.threads import deferToThread

        def df():
            import time
            time.sleep(15)
            self.sendMessage('stop')
            print 'send stop'

        d = deferToThread(df)
        d.addBoth(lambda r: self.sendClose(code=WebSocketServerProtocol.CLOSE_STATUS_CODE_NORMAL,
                                           reason=unicode("successful")))
        print 'begin'

    def onMessageFrame(self, payload):
        for data in payload:
            self.screencast_file.write(data)

    def onMessageEnd(self):
        self.screencast_file.close()
        self.sendClose(code=WebSocketServerProtocol.CLOSE_STATUS_CODE_NORMAL,
                       reason=unicode("successful"))


if __name__ == '__main__':

    factory = WebSocketClientFactory(u"ws://10.54.28.10:9000/takeScreencast")
    factory.protocol = FrameBasedHashClientProtocol

    enableCompression = False
    if enableCompression:
        from autobahn.websocket.compress import PerMessageDeflateOffer, \
            PerMessageDeflateResponse, \
            PerMessageDeflateResponseAccept

        # The extensions offered to the server ..
        offers = [PerMessageDeflateOffer()]
        factory.setProtocolOptions(perMessageCompressionOffers=offers)

        # Function to accept responses from the server ..
        def accept(response):
            if isinstance(response, PerMessageDeflateResponse):
                return PerMessageDeflateResponseAccept(response)

        factory.setProtocolOptions(perMessageCompressionAccept=accept)

    connectWS(factory)
    reactor.run()