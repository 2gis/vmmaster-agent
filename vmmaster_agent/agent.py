from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint

from api import ApiServer


class VMMasterAgent(object):
    def __init__(self):
        self.endpoint_api = TCP4ServerEndpoint(reactor, 9000)
        self.endpoint_api.listen(ApiServer())

    def run(self):
        reactor.run()