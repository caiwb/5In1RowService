# -*- encoding: UTF-8 -*-

import logging
import copy
import time
import netstream
import service_dispatcher
import user_service
import room_service

class MainService(object):
    def __init__(self):
        self.host = netstream.nethost()
        self.host.startup(7890, '127.0.0.1')
        self.shutdown = False
        self.dispatcher = service_dispatcher.ServiceDispather(self.host)
        self.__setupServices()
        self.clientLastMsgMap = {}

        #data
        self.users = []
        self.rooms = []
        self.userHid = {}

        self.__startLoop()

    def __setupServices(self):
        self.userService = user_service.UserService(self, sid='0')
        self.roomService = room_service.RoomService(self, sid='1')

        self.dispatcher.registService('0', self.userService)
        self.dispatcher.registService('1', self.roomService)

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

    def findUserByUid(self, uid):
        try:
            for idx, user in enumerate(self.users):
                if uid == user.uid:
                    return copy.deepcopy(user)
            return None
        except:
            logging.warning('find user error')
            return None
