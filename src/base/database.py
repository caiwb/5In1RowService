# -*- encoding: UTF-8 -*-

import pymongo, logging
from pymongo import MongoClient

class DataManager(object):
    def __init__(self):
        client = MongoClient("localhost", 27017)
        self.db = client.test_db
        self.collection = self.db.test_collection
        self.users = []

    def findAllUser(self):
        return self.collection.find()

    def insertMany(self, users):
        if not isinstance(users, list):
            return
        self.collection.insert_many(users)

    def insert(self, user):
        if not isinstance(user, dict):
            return
        self.collection.insert(user)