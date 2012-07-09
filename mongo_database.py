#  Copyright 2012 MemSQL, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import pymongo

from base_database import BaseDatabase
from config import MONGO_FLAGS, MONGO_USER, MONGO_PWD, MONGO_DROP_DATABASE

class MongoDatabase(BaseDatabase):
    '''An implementation of BaseDatabase using pymongo.'''
    def __init__(self):
        self.connection = pymongo.Connection(**MONGO_FLAGS)
        self.db = self.connection.game
        if MONGO_USER != '': 
            try:
                self.db.authenticate(MONGO_USER,MONGO_PWD)
            except Exception, e:
                print e

    def setup(self):
        if MONGO_DROP_DATABASE:
            self.connection.drop_database('game')
        self.db.players.ensure_index([('id', pymongo.ASCENDING)])
        self.db.games.ensure_index([('players', pymongo.ASCENDING)])
        self.db.events.ensure_index([('user_id', pymongo.ASCENDING)])
        self.db.game_lengths.ensure_index([('length', pymongo.ASCENDING)])

    def get_stats(self):
        return {
            'game_length_distr': list(self.db.game_lengths.find().sort('num', -1)),
            'last_5_events': list(self.db.events.find().sort('$natural', -1).limit(5)),
            'events_from_random_user': list(self.db.events.find({'user_id': 20}))
        }

    def get_games(self, me):
        return [game for game in self.db.games.find({'players': me}) if game['turn'] % 2 == game['players'].index(me)]

    def start_game(self, me, other):
        game_id = self.db.games.save({'turn': 0, 'players': [me, other]})
        self.db.players.update({'id': {'$in': [me, other]}}, {'$inc': {'games_started': 1}})

    def make_move(self, me, game):
        self.db.games.update(game, {'$inc': {'turn': 1}})

    def end_game(self, me, game):
        self.db.games.remove(game)
        self.db.players.update({'id': me}, {'$inc': {'games_won': 1}})
        self.db.game_lengths.update({'length': game['turn']}, {'$inc': {'num': 1}}, upsert=True)

    def log(self, me, event):
        self.db.events.insert({'user_id': me, 'description': event})

    def add_player(self, me):
        self.db.players.save({'id': me, 'total_games': 0, 'games_won': 0,'games': []})

