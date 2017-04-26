#-*- encoding: UTF-8 -*-

import logging
import time
import json
import login_service
import netstream
import service_dispatcher

class MainService(object):
    def __init__(self):
        self.host = netstream.nethost()
        self.host.startup(7890, '127.0.0.1')
        self.shutdown = False
        self.dispatcher = service_dispatcher.ServiceDispather(self.host)
        self.__setupServices()
        self.__startLoop()

    def __setupServices(self):
        self.loginService = login_service.LoginService(self.host, '0')
        self.dispatcher.registService('0', self.loginService)

    def __startLoop(self):
        while not self.shutdown:
            self.host.process()
            logging.debug(self.host.queue)
            msg = self.host.read()
            if msg:
                event = msg[0]
                if event == netstream.NET_NEW:
                    pass
                elif event == netstream.NET_LEAVE:
                    pass
                elif event == netstream.NET_DATA:
                    self.dispatcher.dispatch(json.loads(msg[3]), msg[1])

                elif event == netstream.NET_TIMER:
                    pass




