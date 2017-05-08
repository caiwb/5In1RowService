#-*- encoding: UTF-8 -*-

import json
import logging
from src.base.base_service import BaseService

#cid
LOGIN_HANDLER_ID        = 1000
POST_RANK_HANDLER_ID    = 1001
CHAT_IN_HALL_HANDLER_ID = 1002

class UserService(BaseService):
    def __init__(self, main, sid, db=None):
        BaseService.__init__(self, main, sid, db)
        self.registCommand(LOGIN_HANDLER_ID, self.loginHandler)
        self.registCommand(POST_RANK_HANDLER_ID, self.postRankHandler)
        self.registCommand(CHAT_IN_HALL_HANDLER_ID, self.chatInHallHandler)

    # 登录 cid=0
    def loginHandler(self, hid, data):
        respData = {'sid': self.sid,
                    'cid': LOGIN_HANDLER_ID}
        if not 'account' in data:
            logging.debug('login data has not account key')
            return
        account = data['account']

        user = {
            'uid': account,
            'account': account,
            'password': '',
            'score': 0
            }

        respData['user'] = user

        if account in self.main.userHid.keys():
            respData['result'] = 0
            respData['code'] = 1001
            respData['reason'] = 'this user is online'
        else:
            respData['result'] = 1
            respData['code'] = 0
            respData['reason'] = 'login success'
            u = self.main.findUserByUid(user['uid'])
            if not u:
                self.main.users.append(user)
            self.main.userHid[user['uid']] = hid

        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1000 c=1000 ' + respJson)

        self.main.postAllRank()

    # 排行榜 cid=1
    def postRankHandler(self, hid, data=''):
        respData = {'sid': self.sid,
                    'cid': POST_RANK_HANDLER_ID,
                    'users': self.main.users}
        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1000 c=1001 ' + respJson)

    # 大厅聊天 cid=2
    def chatInHallHandler(self, hid, data):
        respData = {'sid': self.sid,
                    'cid': CHAT_IN_HALL_HANDLER_ID}
        if 'uid' not in data or 'text' not in data:
            logging.warning('hall chat data key err')
            return
        respData.update(data)
        respJson = json.dumps(respData)
        for user in self.main.users:
            if user['uid'] in self.main.userHid:
                self.main.host.send(self.main.userHid[user['uid']], respJson)
        logging.debug('send s=1000 c=1002 ' + respJson)


