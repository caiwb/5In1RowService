# -*- encoding: UTF-8 -*-

import logging
import time

import netstream
import service_dispatcher
import user_service


class MainService(object):
    def __init__(self):
        self.host = netstream.nethost(8)
        self.host.startup(7890, '127.0.0.1')
        self.shutdown = False
        self.dispatcher = service_dispatcher.ServiceDispather(self.host)
        self.__setupServices()
        self.clientLastMsgMap = {}
        self.__startLoop()

    def __setupServices(self):
        self.userService = user_service.UserService(self.host, sid='0')

        self.dispatcher.registService('0', self.userService)

    def __startLoop(self):
        while not self.shutdown:
            self.host.process()
            if len(self.host.queue) > 0:
                logging.debug(self.host.queue)
            msg = self.host.read()
            event, hid, tag, data = msg
            if self.clientLastMsgMap.has_key(str(hid)) \
                    and msg == self.clientLastMsgMap[str(hid)][0] \
                    and time.time() - self.clientLastMsgMap[str(hid)][1] < 1:
                continue
            self.clientLastMsgMap[str(hid)] = (msg, time.time())
            if event != -1:
                if event == netstream.NET_NEW:
                    self.__handleNew(hid)
                elif event == netstream.NET_LEAVE:
                    pass
                elif event == netstream.NET_DATA:
                    self.__handleData(data, hid)
                elif event == netstream.NET_TIMER:
                    pass

    def __handleNew(self, hid):
        self.host.nodelay(hid, 1)

    def __handleData(self, data, hid):
        self.dispatcher.dispatch(data, hid)
