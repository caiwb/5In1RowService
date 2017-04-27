#-*- encoding: UTF-8 -*-

import json
import logging
from user_object import UserObject
from base_service import BaseService


class UserService(BaseService):
    def __init__(self, main, sid):
        BaseService.__init__(self, main, sid)
        self.registCommand('0', self.loginHandler)

    # 登录 cid=0
    def loginHandler(self, data, hid):
        respData = {'sid': 0,
                    'cid': 0}
        if not data.has_key('account'):
            logging.debug('login data has not account key')
            return
        account = data['account']

        user = UserObject(account)

        respData['user'] = user.__dict__

        if self.main.findUserByUid(account):
            respData['result'] = 0
            respData['code'] = 1001
            respData['reason'] = 'this user is online'
        else:
            respData['result'] = 1
            respData['code'] = 0
            respData['reason'] = 'login success'
            self.main.users.append(user)
            self.main.userHid[user.account] = hid

        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=0 c=0 ' + respJson)
