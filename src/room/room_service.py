#-*- encoding: UTF-8 -*-

from base_service import BaseService
import logging, json, copy
from room_object import RoomObject

class RoomService(BaseService):
    def __init__(self, main, sid):
        BaseService.__init__(self, main, sid)
        self.registCommand('0', self.createRoomHandler)
        self.registCommand('1', self.roomListHandler)
        self.cout = 0
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
        self.cout += 1
        return list

    # 新建房间 cid=0
    def createRoomHandler(self, data, hid):
        if self.cout == 1:
            self.cout
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
            respData['rooms'] = self.roomListData
            if not len(respData['rooms']):
                respData['result'] = 0
        else:
            respData['result'] = 0
            respData['rooms'] = []
        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1 c=0 ' + respJson)

    # 房间列表 cid=1
    def roomListHandler(self, data, hid):
        respData = {'sid': 1,
                    'cid': 0}


    # 退出房间 cid=2

