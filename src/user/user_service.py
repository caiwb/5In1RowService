#-*- encoding: UTF-8 -*-

import json
import logging

from base_service import BaseService


class UserService(BaseService):
    def __init__(self, host, sid):
        BaseService.__init__(self, host, sid)
        self.registCommand('0', self.loginHandler)
        self.users = []

    # 登录 cid=0
    def loginHandler(self, data, hid):
        respData = {'sid': 0,
                    'cid': 0}
        if not data.has_key('user'):
            logging.debug('login data has not user key')
            return
        user = data['user']
        respData['user'] = user
        if user in self.users:
            respData['result'] = 0
            respData['code'] = 1001
            respData['reason'] = 'this user is online'
            respJson = json.dumps(respData)
            self.host.send(hid, respJson)
        else:
            respData['result'] = 1
            respData['code'] = 0
            respData['reason'] = 'login success'
            respJson = json.dumps(respData)
            self.users.append((hid, user))
            self.host.send(hid, respJson)
        logging.debug('send' + respJson)
