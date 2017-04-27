#-*- encoding: UTF-8 -*-

import logging
import time
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
            if len(self.host.queue) > 0:
                logging.debug(self.host.queue)
            event, hid, tag, data = self.host.read()
            if event != -1:
                print event
                if event == netstream.NET_NEW:
                    self.__handleNew(hid)
                elif event == netstream.NET_LEAVE:
                    pass
                elif event == netstream.NET_DATA:
                    self.__handleData(data, hid)
                elif event == netstream.NET_TIMER:
                    pass

    def __handleNew(self, wparam):
        # self.host.settag(wparam, wparam)
        self.host.nodelay(wparam, 1)

    def __handleData(self, data, hid):
        print data
        self.dispatcher.dispatch(data, hid)



