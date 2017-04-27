#-*- encoding: UTF-8 -*-

import json
import logging

class ServiceDispather(object):
    def __init__(self, host):
        self.service = host
        self.__serviceMap = {}

    def registService(self, sid, svc):
        if isinstance(sid, int):
            sid = str(sid)
        self.__serviceMap[sid] = svc

    def dispatch(self, data, hid):
        logging.debug('recv' + data)
        try:
            data = json.loads(data)
        except:
            logging.warning('msg format error')
        if not data.has_key('sid'):
            logging.warning('data has not sid key')
            return -1
        sid = data['sid']
        if isinstance(sid, int):
            sid = str(sid)
        if sid not in self.__serviceMap.keys():
            logging.warning('unregist sid ' + sid)
            return -1
        svc = self.__serviceMap[sid]
        try:
            return svc.handle(data, hid)
        except:
            logging.warning('bad service ' + sid)
