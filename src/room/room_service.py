#-*- encoding: UTF-8 -*-

from base_service import BaseService
import logging, json, copy
from room_object import RoomObject

class RoomService(BaseService):
    def __init__(self, main, sid):
        BaseService.__init__(self, main, sid)
        self.__needsPostRoomList = False
        self.registCommand('0', self.createRoomHandler)
        self.registCommand('1', self.postListHandler)

    # 新建房间 cid=0
    def createRoomHandler(self, hid, data):
        respData = {'sid': 1,
                    'cid': 0}
        if not data.has_key('uid'):
            logging.warning('create room data has not uid key')
            return

        uid = data['uid']
        user = self.main.findUserByUid(uid)
        if user:
            room = RoomObject(len(self.main.rooms), user)
            self.main.rooms.append(room)
            respData['result'] = 1
            respData['rid'] = room.roomId
            respData['code'] = 0
        else:
            respData['result'] = 0
            respData['rid'] = -1
            respData['code'] = 1100
        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1 c=0 ' + respJson)
        if respData['result'] == 1:
            self.needsPostRoomList = True

    # 房间列表 cid=1
    def postListHandler(self, hid, data=''):
        try:
            respData = {'sid': 1,
                        'cid': 1,
                        'result': 1,
                        'code': 0,
                        'rooms': self.roomListData}
            respJson = json.dumps(respData)
        except:
            respData = {'sid': 1,
                        'cid': 1,
                        'result': 0,
                        'code': 1101,
                        'rooms': []}
            respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1 c=1 ' + respJson)

    def postAllListHandler(self):
        for client in self.main.host.clients:
            self.postListHandler(client.hid)


    # 进入房间 cid=2

    # 退出房间 cid=3

    @property
    def needsPostRoomList(self):
        return self.__needsPostRoomList

    @needsPostRoomList.setter
    def needsPostRoomList(self, value):
        if value:
            self.__needsPostRoomList = True
            self.postAllListHandler()
            self.__needsPostRoomList = False

    @property
    def roomListData(self):
        list = []
        try:
            for idx, room in enumerate(self.main.rooms):
                room = copy.deepcopy(room)
                roomDict = room.__dict__
                userList = []
                for user in room.users:
                    userList.append(user.__dict__)
                roomDict['users'] = userList
                list.append(roomDict)
        except Exception as e:
            logging.warning('roomlist return error - ' + e.message)
        return list
