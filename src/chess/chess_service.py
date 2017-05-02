#-*- encoding: UTF-8 -*-

from base_service import BaseService
import logging, json, copy
from room_object import RoomObject

#confirm type
CONFIRM_START   = 0
CONFIRM_REDO    = 1
CONFIRM_GIVE_UP = 2
CONFIRM_NO      = 3

#confirm side
CONFIRM_REQUEST  = 0
CONFIRM_RESPONSE = 1

#chess
NONE_CHESS  = 0
WHITE_CHESS = 1
BLACK_CHESS = 2

class ChessService(BaseService):
    def __init__(self, main, sid):
        BaseService.__init__(self, main, sid)
        self.registCommand('1000', self.confirmHandler)
        self.registCommand('1001', self.chessHandler)

    # 确认 cid=0
    def confirmHandler(self, hid, data):
        respData = {'sid': 1002,
                    'cid': 1000}
        if not data.has_key('rid') or not data.has_key('uid') \
                or not data.has_key('type') \
                or not data.has_key('side'):
            logging.debug('chess data has error key')
            return
        room = self.main.findRoomByRid(data['rid'])
        uid = data['uid']
        rival = None
        for user in room['users']:
            if user['uid'] != uid:
                rival = user['uid']

        if not rival:
            return
        rHid = self.main.userHid[rival]
        hids = [hid, rHid]

        # side
        if data['side'] == CONFIRM_REQUEST:
            respData['side'] = CONFIRM_REQUEST
            respData['type'] = data['type']
            respData['result'] = 1
            respJson = json.dumps(respData)
            self.main.host.send(rHid, respJson)
            logging.debug('send s=1002 c=1000 ' + respJson)

        elif data['side'] == CONFIRM_RESPONSE:
            respData['side'] = CONFIRM_RESPONSE
            confirmType = data['type']
            respData['type'] = confirmType

            if confirmType == CONFIRM_START:
                self.start(str(room['rid']))
            elif confirmType == CONFIRM_REDO:
                self.redo()
            elif confirmType == CONFIRM_GIVE_UP:
                self.redo()
            elif confirmType == CONFIRM_NO:
                pass

            respData['result'] = 1
            for index, h in enumerate(hids):
                respData['chess'] = index + 1
                respJson = json.dumps(respData)
                self.main.host.send(h, respJson)



    # 下棋 cid=1
    def chessHandler(self, hid, data):
        respData = {'sid': 1002,
                    'cid': 1001}
        if not data.has_key('x') and not data.has_key('y') and\
                not data.has_key('type'):
            logging.debug('chess data has error key')
            return

        room = self.main.findRoomByRid(data['rid'])
        hids = []
        for user in room['users']:
            hids.append(self.main.userHid[user['uid']])
        x = int(data['x'])
        y = int(data['y'])
        type = data['type']
        rid = data['rid']

        try:
            if self.main.chessMap[str(rid)][x][y] == NONE_CHESS:
                self.main.chessMap[str(rid)][x][y] = type
                self.main.chessDataMap[str(rid)].append((x, y, type))
                respData['result'] = 1
            else:
                respData['result'] = 0
        except Exception as e:
            logging.warning(e.message)

        respData['x'] = x
        respData['y'] = y
        respData['type'] = type
        respJson = json.dumps(respData)
        for h in hids:
            self.main.host.send(h, respJson)
        rslt = self.isWin(x, y, type, str(rid))
        if rslt:
            logging.debug("win!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


    def start(self, rid):
        self.main.chessDataMap[rid] = []
        self.main.chessMap[rid] = [[0] * 15 for i in range(15)]

    def isWin(self, x, y, type, rid):
        chessboard = self.main.chessMap[rid]

        # 竖直方向
        i = x
        j = y
        count = 0
        for loop in range(1, 6):
            j -= loop
            t = chessboard[i][j]
            if chessboard[i][j] != type:
                break
            count += 1
        if count == 5:
            return True
        j = y
        for loop in range(1, 6):
            j += loop
            t = chessboard[i][j]
            if chessboard[i][j] != type:
                break
            count += 1
        if count == 5:
            return True

        # 水平方向
        j = y
        count = 0
        for loop in range(1, 6):
            i -= loop
            t = chessboard[i][j]
            if chessboard[i][j] != type:
                break
            count += 1
        if count == 5:
            return True
        i = x
        for loop in range(1, 6):
            i += loop
            t = chessboard[i][j]
            if chessboard[i][j] != type:
                break
            count += 1
        if count == 5:
            return True

        # 左下右上方向
        i = x
        count = 0
        for loop in range(1, 6):
            i -= loop
            j += loop
            t = chessboard[i][j]
            if chessboard[i][j] != type:
                break
            count += 1
        if count == 5:
            return True
        i = x
        j = y
        for loop in range(1, 6):
            i += loop
            j -= loop
            t = chessboard[i][j]
            if chessboard[i][j] != type:
                break
            count += 1
        if count == 5:
            return True

        # 右下左上方向
        i = x
        j = y
        count = 0
        for loop in range(1, 6):
            i -= loop
            j -= loop
            t = chessboard[i][j]
            if chessboard[i][j] != type:
                break
            count += 1
        if count == 5:
            return True
        i = x
        j = y
        for loop in range(1, 6):
            i += loop
            j += loop
            t = chessboard[i][j]
            if chessboard[i][j] != type:
                break
            count += 1
        if count == 5:
            return True

        return False




