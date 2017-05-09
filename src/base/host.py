# -*- encoding: UTF-8 -*-

import logging
import time
from lib import netstream
import service_dispatcher
from src.services import user_service, room_service, chess_service

#sid
USER_SERVICE_ID  = 1000
ROOM_SERVICE_ID  = 1001
CHESS_SERVICE_ID = 1002

class MainService(object):
    def __init__(self):
        self.host = netstream.nethost(8)
        self.host.startup(7890, '127.0.0.1')
        self.host.settimer(20000)
        self.shutdown = False
        self.dispatcher = service_dispatcher.ServiceDispather(self.host)
        self.__setupServices()
        self.clientLastMsgMap = {}

        #data
        self.users = []
        self.rooms = []
        self.userHid = {}
        self.chessMap = {}
        self.chessDataMap = {}
        self.forbiddenMap = {}
        self.lastBlack = None
        self.lastWhite = None
        self.__startLoop()
        self.hbMap = {}
        self.hbTime = 30

    def __setupServices(self):
        self.userService = user_service.UserService(self, USER_SERVICE_ID)
        self.roomService = room_service.RoomService(self, ROOM_SERVICE_ID)
        self.chessService = chess_service.ChessService(self, CHESS_SERVICE_ID)

        self.dispatcher.registService(USER_SERVICE_ID, self.userService)
        self.dispatcher.registService(ROOM_SERVICE_ID, self.roomService)
        self.dispatcher.registService(CHESS_SERVICE_ID, self.chessService)

    def __startLoop(self):
        while not self.shutdown:
            self.host.process()
            if len(self.host.queue) > 0:
                logging.debug(self.host.queue)
            msg = self.host.read()
            event, hid, tag, data = msg
            t = time.time()
            if event != -1 and str(hid) in self.clientLastMsgMap \
                    and msg == self.clientLastMsgMap[str(hid)][0] \
                    and t - self.clientLastMsgMap[str(hid)][1] < 1:

                continue
            self.clientLastMsgMap[str(hid)] = (msg, time.time())
            if event != -1:
                if event == netstream.NET_NEW:
                    self.__handleNew(hid)

                elif event == netstream.NET_LEAVE:
                    for idx, uid in enumerate(self.userHid.keys()):
                        if hid == self.userHid[uid]:
                            user = self.findUserByUid(uid)
                            if 'rid' in user and user['rid']:
                                self.host.queue.append((netstream.NET_DATA, hid, 0,
                                                        '{"rid": %d, "cid": 1003, '
                                                        '"uid": %s, "sid": 1001}'
                                                        % (user['rid'], user['uid'])))
                            self.userHid.pop(uid)
                            continue

                elif event == netstream.NET_DATA:
                    if data == 'hb':
                        continue
                    self.__handleData(hid, data)

                elif event == netstream.NET_TIMER:
                    for client in self.host.clients:
                        if client:
                            self.host.send(client.hid, 'hb')
                    logging.debug('send heart beat')

    def postAllRank(self):
        for client in self.host.clients:
            if client:
                self.userService.postRankHandler(client.hid)

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
