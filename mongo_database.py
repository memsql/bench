import pymongo

from base_database import BaseDatabase
from config import MONGO_FLAGS

class MongoDatabase(BaseDatabase):
    '''An implementation of BaseDatabase using pymongo.'''
    def __init__(self):
        self.connection = pymongo.Connection(**MONGO_FLAGS)
        self.db = self.connection.game

    def setup(self):
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

