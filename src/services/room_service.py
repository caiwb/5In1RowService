#-*- encoding: UTF-8 -*-

from src.base.base_service import BaseService
import logging, json

#cid
CREATE_ROOM_HANDLER_ID  = 1000
POST_LIST_HANDLER_ID    = 1001
ENTER_ROOM_HANDLER_ID   = 1002
LEAVE_ROOM_HANDLER_ID   = 1003
CHAT_IN_ROOM_HANDLER_ID = 1004

class RoomService(BaseService):
    def __init__(self, main, sid, db=None):
        BaseService.__init__(self, main, sid, db)
        self.registCommand(CREATE_ROOM_HANDLER_ID, self.createRoomHandler)
        self.registCommand(POST_LIST_HANDLER_ID, self.postListHandler)
        self.registCommand(ENTER_ROOM_HANDLER_ID, self.enterRoomHandler)
        self.registCommand(LEAVE_ROOM_HANDLER_ID, self.leaveRoomHandler)
        self.registCommand(CHAT_IN_ROOM_HANDLER_ID, self.chatInRoomHandler)

    # 新建房间 cid=0
    def createRoomHandler(self, hid, data):
        respData = {'sid': self.sid,
                    'cid': CREATE_ROOM_HANDLER_ID}
        if 'uid' not in data:
            logging.warning('create room data has not uid key')
            return

        uid = data['uid']
        user = self.main.findUserByUid(uid)
        if user:
            room = {
                'rid': len(self.main.rooms) + 1,
                'users': [user]
            }
            user['rid'] = room['rid']
            self.main.rooms.append(room)
            respData['result'] = 1
            respData['room'] = room
            respData['code'] = 0
        else:
            respData['result'] = 0
            respData['room'] = None
            respData['code'] = 1100
        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1001 c=1000 ' + respJson)
        if respData['result'] == 1:
            self.postAllListHandler()

    # 房间列表 cid=1
    def postListHandler(self, hid, data=''):
        respData = {'sid': self.sid,
                    'cid': POST_LIST_HANDLER_ID,
                    'result': 1,
                    'code': 0,
                    'rooms': self.main.rooms}
        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1001 c=1001 ' + respJson)

    def postAllListHandler(self):
        for client in self.main.host.clients:
            if client:
                self.postListHandler(client.hid)


    # 进入房间 cid=2
    def enterRoomHandler(self, hid, data):
        respData = {'sid': self.sid,
                    'cid': ENTER_ROOM_HANDLER_ID}
        if 'uid' not in data or 'rid' not in data:
            logging.warning('enter room data key err')
            return

        uid = data['uid']
        rid = data['rid']
        user = self.main.findUserByUid(uid)
        user['rid'] = rid
        room = self.main.findRoomByRid(rid)
        users = room['users']
        users.append(user)

        if user and room:
            respData['result'] = 1
            respData['code'] = 0
            respData['room'] = room
            respJson = json.dumps(respData)
            for user in room['users']:
                h = self.main.userHid[user['uid']]
                self.main.host.send(h, respJson)
            self.postAllListHandler()

        else:
            respData['result'] = 0
            respData['code'] = 1001
            respData['room'] = None
            respJson = json.dumps(respData)
            self.main.host.send(hid, respJson)

        logging.debug('send s=1001 c=1002 ' + respJson)

    # 退出房间 cid=3
    def leaveRoomHandler(self, hid, data):
        respData = {'sid': self.sid,
                    'cid': LEAVE_ROOM_HANDLER_ID}
        if 'uid' not in data or 'rid' not in data:
            logging.warning('leave room data key err')
            return

        uid = str(data['uid'])
        rid = data['rid']
        respData['uid'] = uid
        user = self.main.findUserByUid(uid)
        room = self.main.findRoomByRid(rid)
        user['rid'] = None
        hids = []
        result = 1
        try:
            for user in room['users']:
                if user['uid'] in self.main.userHid:
                    hids.append(self.main.userHid[user['uid']])
                if user['uid'] == uid:
                    room['users'].remove(user)
            if not len(room['users']):
                self.main.rooms.remove(room)
                room = None
        except Exception as e:
            logging.warning(e.message)
            result = 0

        if uid and result:
            respData['result'] = 1
            respData['code'] = 0

        else:
            respData['result'] = 0
            respData['code'] = 1001

        respData['room'] = room

        respJson = json.dumps(respData)
        for h in hids:
            self.main.host.send(h, respJson)
        logging.debug('send s=1001 c=1003 ' + respJson)
        self.postAllListHandler()

    # 聊天 cid=4
    def chatInRoomHandler(self, hid, data):
        respData = {'sid': self.sid,
                    'cid': CHAT_IN_ROOM_HANDLER_ID}
        if 'uid' not in data or 'rid' not in data \
                or 'text' not in data:
            logging.warning('room chat data key err')
            return
        respData.update(data)
        respJson = json.dumps(respData)
        room = self.main.findRoomByRid(data['rid'])
        for user in room['users']:
            if user['uid'] in self.main.userHid:
                self.main.host.send(self.main.userHid[user['uid']], respJson)
        logging.debug('send s=1001 c=1004 ' + respJson)
