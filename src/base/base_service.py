# -*- encoding: UTF-8 -*-

import logging, json

class BaseService(object):
    def __init__(self, main, sid=0):
        self.main = main
        self.sid = sid
        self.commandMap = {}

    def registCommand(self, cid, function):
        if isinstance(cid, int):
            cid = str(cid)
        self.commandMap[cid] = function

    def handle(self, data, hid):
        if not data.has_key('cid'):
            return
        cid = data['cid']
        if isinstance(cid, int):
            cid = str(cid)
        if cid not in self.commandMap.keys():
            logging.warning('unregist cid ' + cid)
        f = self.commandMap[cid]
        try:
            return f(data, hid)
        except:
            logging.warning('bad command ' + self.sid + '_' + cid)