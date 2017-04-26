#-*- encoding: UTF-8 -*-

from base_service import BaseService
import json

class LoginService(BaseService):
    def __init__(self, host, sid):
        BaseService.__init__(self, host, sid)
        self.registCommand('0', self.loginHandler)
        self.users = []

    # 登录 cid=0
    def loginHandler(self, msg, owner):
        respData = {'sid': 0,
                    'cid': 0}
        if not msg.has_key('user'):
            return
        user = msg['user']
        if user in self.users:
            respData['result'] = 0
            respData['reason'] = 'this user is online'
            respJson = json.dumps(respData)
            self.host.send(owner, respJson)
        else:
            respData['result'] = 1
            respData['reason'] = ''
            respJson = json.dumps(respData)
            self.users.append(user)
            self.host.send(owner, respJson)
