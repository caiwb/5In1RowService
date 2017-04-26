#-*- encoding: UTF-8 -*-

class ServiceDispather(object):
    def __init__(self, host):
        self.service = host
        self.__serviceMap = {}

    def registService(self, sid, svc):
        if isinstance(sid, int):
            sid = str(sid)
        self.__serviceMap[sid] = svc

    def dispatch(self, msg, owner):
        if not msg.has_key('sid'):
            return
        sid = msg['sid']
        if isinstance(sid, int):
            sid = str(sid)
        if sid not in self.__serviceMap.keys():
            raise Exception('unregist sid ' + sid)
        svc = self.__serviceMap[sid]
        # try:
        #     return svc.handle(msg, owner)
        # except:
        #     raise Exception('bad service ' + sid)
        return svc.handle(msg, owner)