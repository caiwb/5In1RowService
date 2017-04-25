#-*- encoding: UTF-8 -*-

from netstream import nethost

class service(object):
    def __init__(self):
        self.server = nethost()
        self.server.startup(8080, '127.0.0.1')
        while True:
            self.server.process()
            print self.server.queue

if __name__ == "__main__":
    service = service()

