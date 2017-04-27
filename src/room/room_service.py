#-*- encoding: UTF-8 -*-

from base_service import BaseService


class RoomService(BaseService):
    def __init__(self, host, sid):
        BaseService.__init__(self, host, sid)
        self.registCommand('0', self.createRoomHandler)
        self.rooms = []

    # 新建房间 cid=0
    def createRoomHandler(self, data, hid):
        pass