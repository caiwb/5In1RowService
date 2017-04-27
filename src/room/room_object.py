#-*- encoding: UTF-8 -*-

class RoomObject(object):
    def __init__(self, roomId, creater):
        self.roomId = roomId
        self.users = [creater]