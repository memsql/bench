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


import _mysql

from base_database import BaseDatabase
from config import MYSQL_FLAGS, MEMSQL_FLAGS

class SqlConnection(object):
    '''A barebones wrapper around _mysql.'''
    def __init__(self, **flags):
        '''Open a _mysql connection, passing through all flags.'''
        self.connection = _mysql.connect(**flags)

    def execute(self, query):
        '''Execute a given query (returning no results.'''
        self.connection.query(query)

    def query(self, query):
        '''Execute a given query, returning a tuple of dicts.'''
        self.connection.query(query)
        result = self.connection.use_result()
        return result.fetch_row(100, 1)

class SqlDatabase(BaseDatabase):
    '''An implementation of BaseDatabase using _mysql.'''
    def __init__(self, **flags):
        self.db = SqlConnection(**flags)
        try:
            self.db.execute('USE game')
        except:
            pass

    def setup(self):
        self.db.execute('DROP DATABASE IF EXISTS game')
        self.db.execute('/*!90618 set global default_partitions_per_leaf=1*/')
        self.db.execute('CREATE DATABASE game')
        self.db.execute('USE game')
        self.db.execute('CREATE TABLE games (id BIGINT AUTO_INCREMENT, turn INT NOT NULL, player1 INT NOT NULL, player2 INT NOT NULL, INDEX (player1), INDEX (player2), PRIMARY KEY (id))')
        self.db.execute('CREATE TABLE players (id BIGINT PRIMARY KEY, games_started INT NOT NULL, games_won INT NOT NULL)')
        self.db.execute('CREATE TABLE game_lengths (length INT PRIMARY KEY, num INT NOT NULL)')
        self.db.execute('CREATE TABLE events (id BIGINT AUTO_INCREMENT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP, user_id INT, description CHAR(32), INDEX (user_id), INDEX (ts DESC), PRIMARY KEY(id))')

    def get_stats(self):
        return {
            'total_games_started': self.db.query("SELECT SUM(games_started) FROM players")[0], 
            'game_length_distr': self.db.query("SELECT * FROM game_lengths ORDER BY num DESC"),
            'last_5_events': self.db.query("SELECT * FROM events ORDER BY ts DESC LIMIT 5"),
            'events_from_random_user': self.db.query("SELECT * FROM events WHERE user_id = %s" % 20)
        }

    def get_games(self, me):
        return (self.db.query("SELECT * FROM games WHERE player1 = " + str(me)) + 
                self.db.query("SELECT * FROM games WHERE player2 = " + str(me)))

    def start_game(self, me, other):
        self.db.execute("INSERT INTO games (turn, player1, player2) VALUES (0, " + str(me) + ", " + str(other) + ")")
        self.db.execute("UPDATE players SET games_started=games_started+1 WHERE id = " + str(me) + " OR id = " + str(other))

    def make_move(self, me, game):
        self.db.execute("UPDATE games SET turn=turn+1 WHERE id = " + str(game['id']))

    def end_game(self, me, game):
        self.db.execute("DELETE FROM games WHERE id = " + str(game['id']))
        self.db.execute("UPDATE players SET games_won=games_won+1 WHERE id = " + str(me))
        self.db.execute("INSERT INTO game_lengths VALUES (" + str(game['turn']) + ", 1) ON DUPLICATE KEY UPDATE num=num+1")

    def log(self, me, event):
        self.db.execute("INSERT INTO events (user_id, description) VALUES (" + str(me) + ", '" + str(event) + "')")

    def add_player(self, me):
        self.db.execute('INSERT INTO players VALUES (' + str(me) + ', 0, 0)')

class MySqlDatabase(SqlDatabase):
    def __init__(self):
        super(MySqlDatabase, self).__init__(**MYSQL_FLAGS)

class MemSqlDatabase(SqlDatabase):
    def __init__(self):
        super(MemSqlDatabase, self).__init__(**MEMSQL_FLAGS)

