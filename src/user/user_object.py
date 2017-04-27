#-*- encoding: UTF-8 -*-

import time

class UserObject(object):
    def __init__(self, user):
        self.uid = user
        self.account = user
        self.password = ''
        self.score = 0
