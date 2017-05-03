#-*- encoding: UTF-8 -*-

import json
import logging
from base_service import BaseService

class UserService(BaseService):
    def __init__(self, main, sid):
        BaseService.__init__(self, main, sid)
        self.registCommand('1000', self.loginHandler)

    # 登录 cid=0
    def loginHandler(self, hid, data):
        respData = {'sid': 1000,
                    'cid': 1000}
        if not data.has_key('account'):
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
            self.main.users.append(user)
            self.main.userHid[user['uid']] = hid

        respJson = json.dumps(respData)
        self.main.host.send(hid, respJson)
        logging.debug('send s=1000 c=1000 ' + respJson)
