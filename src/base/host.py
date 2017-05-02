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
        self.userService = user_service.UserService(self, sid='1000')
        self.roomService = room_service.RoomService(self, sid='1001')

        self.dispatcher.registService('1000', self.userService)
        self.dispatcher.registService('1001', self.roomService)

    def __startLoop(self):
        while not self.shutdown:
            self.host.process()
            if len(self.host.queue) > 0:
                logging.debug(self.host.queue)
            msg = self.host.read()
            event, hid, tag, data = msg
            if event != -1 and self.clientLastMsgMap.has_key(str(hid)) \
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
                    self.__handleData(hid, data)
                elif event == netstream.NET_TIMER:
                    pass

    def __handleNew(self, hid):
        self.host.nodelay(hid, 1)

    def __handleData(self, hid, data):
        self.dispatcher.dispatch(hid, data)

    def findUserByUid(self, uid):
        try:
            for idx, user in enumerate(self.users):
                if uid == user['uid']:
                    return user
            return None
        except:
            logging.warning('find user error')
            return None

    def findRoomByRid(self, rid):
        try:
            for idx, room in enumerate(self.rooms):
                if rid == room['rid']:
                    return room
            return None
        except:
            logging.warning('find room error')
            return None
