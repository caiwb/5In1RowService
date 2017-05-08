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

    def dispatch(self, hid, data):
        logging.debug('recv' + data)
        try:
            data = json.loads(data)
        except:
            logging.warning('msg format error')
        if not 'sid' in data:
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
            return svc.handle(hid, data)
        except:
            logging.warning('bad service ' + sid)
