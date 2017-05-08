# -*- encoding: UTF-8 -*-

import logging

class BaseService(object):
    def __init__(self, main, sid=0, db=None):
        self.main = main
        self.sid = sid
        self.commandMap = {}
        self.db = db

    def registCommand(self, cid, function):
        if isinstance(cid, int):
            cid = str(cid)
        self.commandMap[cid] = function

    def handle(self, hid, data):
        if 'cid' not in data:
            return
        cid = data['cid']
        if isinstance(cid, int):
            cid = str(cid)
        if cid not in self.commandMap.keys():
            logging.warning('unregist cid ' + cid)
        f = self.commandMap[cid]
        try:
            return f(hid, data)
        except:
            logging.warning('bad command ' + self.sid + '_' + cid)