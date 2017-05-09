#-*- encoding: UTF-8 -*-

from src.base.base_service import BaseService
import logging, json

#confirm type
CONFIRM_START     = 0
CONFIRM_REDO      = 1
CONFIRM_GIVE_UP   = 2
CONFIRM_FORBIDDEN = 3

#confirm side
CONFIRM_REQUEST  = 0
CONFIRM_RESPONSE = 1

#chess
NONE_CHESS  = 0
WHITE_CHESS = 1
BLACK_CHESS = 2

#cid
CHESS_CONFIRM_HANDLER_ID = 1000
DO_CHESS_HANDLER_ID      = 1001

class ChessService(BaseService):
    def __init__(self, main, sid, db=None):
        BaseService.__init__(self, main, sid, db)
        self.registCommand(CHESS_CONFIRM_HANDLER_ID, self.confirmHandler)
        self.registCommand(DO_CHESS_HANDLER_ID, self.chessHandler)

    # 确认 cid=0
    def confirmHandler(self, hid, data):
        respData = {'sid': self.sid,
                    'cid': CHESS_CONFIRM_HANDLER_ID}
        if 'rid' not in data or 'uid' not in data \
                or 'type' not in data \
                or 'side' not in data:
            logging.debug('chess data has error key')
            return
        room = self.main.findRoomByRid(data['rid'])
        uid = data['uid']
        rival = None
        users = []
        for user in room['users']:
            users.append(user)
            if user['uid'] != uid:
                rival = user['uid']

        if not rival:
            return
        rHid = self.main.userHid[rival]
        hids = [hid, rHid]

        # side
        if data['side'] == CONFIRM_REQUEST:
            if data['type'] == CONFIRM_FORBIDDEN and \
                            str(data['rid']) in self.main.chessDataMap \
                    and len(self.main.chessDataMap[str(data['rid'])]) > 2:
                return
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
            elif confirmType == CONFIRM_REDO and 'chess_type' in data:
                redoStep = self.redo(str(room['rid']), data['chess_type'])
                respData['step'] = redoStep
                respData['chess_type'] = data['chess_type']
            elif confirmType == CONFIRM_GIVE_UP and 'chess_type' in data:
                self.giveup(str(room['rid']), 3 - data['chess_type'])
                return
            elif confirmType == CONFIRM_FORBIDDEN:
                self.forbidden(str(room['rid']))

            respData['result'] = 1
            for index, h in enumerate(hids):
                respData['chess'] = index + 1
                if index < len(users):
                    users[index]['chess_type'] = index + 1
                respJson = json.dumps(respData)
                self.main.host.send(h, respJson)

    # 下棋 cid=1
    def chessHandler(self, hid, data):
        respData = {'sid': self.sid,
                    'cid': DO_CHESS_HANDLER_ID}
        if 'x' not in data and 'y' not in data and \
                'type' not in data:
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
            self.main.forbiddenMap[rid] = False
            self.postResult(rid, type)
            self.main.postAllRank()
        elif str(rid) in self.main.forbiddenMap and \
                self.main.forbiddenMap[str(rid)]:
            rslt = self.isForbidden(x, y, type, str(rid))
            if rslt:
                self.postResult(rid, 3 - type)
                self.main.postAllRank()


    # 输赢 cid=2
    def postResult(self, rid, type):
        respData = {'sid': 1002,
                    'cid': 1002,
                    'type': type}
        hids = []
        room = self.main.findRoomByRid(int(rid))
        for user in room['users']:
            user['score'] = user['score'] - 30 \
                if type == user['chess_type'] else user['score'] + 30
        respData['room'] = room
        respJson = json.dumps(respData)
        for user in room['users']:
            self.main.host.send(self.main.userHid[user['uid']], respJson)

    def start(self, rid):
        self.main.chessDataMap[rid] = []
        self.main.chessMap[rid] = [[0] * 15 for i in range(15)]

    def redo(self, rid, type):
        x, y, t = self.main.chessDataMap[rid].pop()
        self.main.chessMap[rid][x][y] = NONE_CHESS
        if t == type:
            return 1
        x, y, t = self.main.chessDataMap[rid].pop()
        self.main.chessMap[rid][x][y] = NONE_CHESS
        return 2

    def giveup(self, rid, type):
        self.postResult(rid, type)

    def forbidden(self, rid):
        self.main.forbiddenMap[rid] = True

    # 判断输赢 type为当前棋子颜色
    def isWin(self, x, y, type, rid):
        chessboard = self.main.chessMap[rid]
        # 竖直方向
        i = x
        j = y
        count = 1
        for loop in range(1, 6):
            if j - loop < 0:
                break
            if chessboard[i][j - loop] != type:
                break
            count += 1
        j = y
        for loop in range(1, 6):
            if j + loop > 14:
                break
            if chessboard[i][j + loop] != type:
                break
            count += 1
        if count == 5:
            return True
        elif count > 5 and type == WHITE_CHESS:
            return True
        elif count > 5 and rid in self.main.forbiddenMap and \
                not self.main.forbiddenMap[rid] \
                and self.type == BLACK_CHESS:
            return True

        # 水平方向
        i = x
        j = y
        count = 1
        for loop in range(1, 6):
            if i - loop < 0:
                break
            if chessboard[i - loop][j] != type:
                break
            count += 1
        i = x
        for loop in range(1, 6):
            if i + loop > 14:
                break
            if chessboard[i + loop][j] != type:
                break
            count += 1
        if count == 5:
            return True
        elif count > 5 and \
                (type == WHITE_CHESS or rid not in self.main.forbiddenMap):
            return True
        elif count > 5 and rid in self.main.forbiddenMap and \
                not self.main.forbiddenMap[rid] and type == BLACK_CHESS:
            return True

        # 左下右上方向
        i = x
        j = y
        count = 1
        for loop in range(1, 6):
            if j + loop > 14 or i - loop < 0:
                break
            if chessboard[i - loop][j + loop] != type:
                break
            count += 1
        i = x
        j = y
        for loop in range(1, 6):
            if i + loop > 14 or j - loop < 0:
                break
            if chessboard[i + loop][j - loop] != type:
                break
            count += 1
        if count == 5:
            return True
        elif count > 5 and type == WHITE_CHESS:
            return True
        elif count > 5 and rid in self.main.forbiddenMap and \
                not self.main.forbiddenMap[rid] \
                and self.type == BLACK_CHESS:
            return True

        # 右下左上方向
        i = x
        j = y
        count = 1
        for loop in range(1, 6):
            if chessboard[i - loop][j - loop] != type:
                break
            count += 1
        i = x
        j = y
        for loop in range(1, 6):
            if i + loop > 14 or j + loop > 14:
                break
            if chessboard[i + loop][j + loop] != type:
                break
            count += 1
        if count == 5:
            return True
        elif count > 5 and type == WHITE_CHESS:
            return True
        elif count > 5 and rid in self.main.forbiddenMap and \
                not self.main.forbiddenMap[rid] \
                and self.type == BLACK_CHESS:
            return True

        return False

    # 判断禁手
    # 1．三、三禁手
    # 黑方一子落下同时形成两个或两个以上的活三（或嵌四），此步为三三禁手。 注意：这里一定要两个都是 “活”三才能算。
    # 2．四、四禁手
    # 黑方一子落下同时形成两个或两个以上的四，活四、冲四、嵌五之四，包括在此四之内。此步为四四禁手。注意：只要是两个“四”即为禁手，无
    # 论是哪种四，活四，跳四，冲四都算。
    # 3．四、三、三禁手
    # 黑方一步使一个四，两个活三同时形成。
    # 4．四、四、三禁手
    # 黑方一步使两个四，一个活三同时形成。
    # 5．长连禁手
    # 黑方一子落下形成连续六子或六子以上相连
    def isForbidden(self, x, y, type, rid):
        chessboard = self.main.chessMap[rid]
        if type == WHITE_CHESS:
            return False

        # 竖直方向
        tCount = 0 # 活三个数
        fCount = 0 # 四子个数
        count = 1 # 棋子个数
        emptyCount = 0
        i = x
        j = y
        for loop in range(1, 6):
            if j - loop < 0:
                break
            if not chessboard[i][j - loop] and not emptyCount:
                emptyCount += 1
            elif chessboard[i][j - loop] == type:
                count += 1
            else:
                break
        j = y
        for loop in range(1, 6):
            if j + loop > 14:
                break
            if not chessboard[i][j + loop] and not emptyCount:
                emptyCount += 1
            elif chessboard[i][j + loop] == type:
                count += 1
            else:
                break
        if count == 3:
            tCount += 1
        elif count == 4:
            fCount += 1
        elif count > 5:
            return True

        # 水平方向
        count = 1 # 棋子个数
        emptyCount = 0
        i = x
        j = y
        for loop in range(1, 6):
            if i - loop < 0:
                break
            if not chessboard[i - loop][j] and not emptyCount:
                emptyCount += 1
            elif chessboard[i - loop][j] == type:
                count += 1
            else:
                break
        i = x
        for loop in range(1, 6):
            if i + loop > 14:
                break
            if not chessboard[i + loop][j] and not emptyCount:
                emptyCount += 1
            elif chessboard[i + loop][j] == type:
                count += 1
            else:
                break
        if count == 3:
            tCount += 1
        elif count == 4:
            fCount += 1
        elif count > 5:
            return True

        # 左下右上方向
        count = 1 # 棋子个数
        emptyCount = 0
        i = x
        j = y
        for loop in range(1, 6):
            if j + loop > 14 or i - loop < 0:
                break
            if not chessboard[i - loop][j + loop] and not emptyCount:
                emptyCount += 1
            elif chessboard[i - loop][j + loop] == type:
                count += 1
            else:
                break
        i = x
        j = y
        for loop in range(1, 6):
            if i + loop > 14 or j - loop < 0:
                break
            if not chessboard[i + loop][j - loop] and not emptyCount:
                emptyCount += 1
            elif chessboard[i + loop][j - loop] == type:
                count += 1
            else:
                break
        if count == 3:
            tCount += 1
        elif count == 4:
            fCount += 1
        elif count > 5:
            return True

        # 左上右下方向
        count = 1 # 棋子个数
        emptyCount = 0
        i = x
        j = y
        for loop in range(1, 6):
            if j - loop < 0 or j - loop < 0:
                break
            if not chessboard[i - loop][j - loop] and not emptyCount:
                emptyCount += 1
            elif chessboard[i - loop][j - loop] == type:
                count += 1
            else:
                break
        i = x
        j = y
        for loop in range(1, 6):
            if i + loop > 14 or j + loop > 14:
                break
            if not chessboard[i + loop][j + loop] and not emptyCount:
                emptyCount += 1
            elif chessboard[i + loop][j + loop] == type:
                count += 1
            else:
                break
        if count == 3:
            tCount += 1
        elif count == 4:
            fCount += 1
        elif count > 5:
            return True

        # 结果判断
        if tCount == 2 and not fCount:
            return True
        elif tCount == 2 and fCount == 1:
            return True
        elif tCount == 1 and fCount == 2:
            return True
        elif not tCount and fCount == 2:
            return True
        return False





