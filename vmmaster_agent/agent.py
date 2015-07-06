from twisted.internet import reactor as twisted_reactor
from twisted.internet.endpoints import TCP4ServerEndpoint

from api import ApiServer


class VMMasterAgent(object):
    def __init__(self, reactor):
        self.reactor = reactor
        self.endpoint_api = TCP4ServerEndpoint(self.reactor, 9000)
        self.endpoint_api.listen(ApiServer())

    def run(self):
        self.reactor.run()

    def stop(self):
        self.reactor.stop()


def main():
    VMMasterAgent(twisted_reactor).run()


if __name__ == "__main__":
    main()
