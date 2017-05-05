#-*- encoding: UTF-8 -*-

class RoomObject(object):
    def __init__(self, roomId, creater):
        self.roomId = roomId
        self.users = [creater]

    def coverToDict(self):
        try:
            roomDict = self.__dict__
            userList = []
            for user in self.users:
                userList.append(user.__dict__)
            roomDict['users'] = userList
            return roomDict
        except:
            return {}