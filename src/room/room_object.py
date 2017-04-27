#-*- encoding: UTF-8 -*-

import time

class RoomObject(object):
    def __init__(self, roomId, creater):
        self.roomId = roomId
        self.createTime = time.time()
        self.users = [creater]