# -*- encoding: UTF-8 -*-

class BaseService(object):
    def __init__(self, host, sid=0):
        self.host = host
        self.sid = sid
        self.commandMap = {}

    def registCommand(self, cid, function):
        if isinstance(cid, int):
            cid = str(cid)
        self.commandMap[cid] = function

    def handle(self, msg, owner):
        if not msg.has_key('cid'):
            return
        cid = msg['cid']
        if isinstance(cid, int):
            cid = str(cid)
        if cid not in self.commandMap.keys():
            raise Exception('unregist cid ' + cid)
        f = self.commandMap[cid]
        # try:
        #     return f(msg, owner)
        # except:
        #     raise Exception('bad command ' + cid)
        return f(msg, owner)