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


# The benchmark uses several worker processes, each simulating several players.
# The exact numbers can be configured here.
NUM_WORKERS = 140
PLAYERS_PER_WORKER = 4000
NUM_PLAYERS = NUM_WORKERS * PLAYERS_PER_WORKER

# Flags used to connect to the various databases. The *SQL_FLAGS are used for 
# _mysql.connect; MONGO_FLAGS is used for pymongo.Connection.
MEMSQL_FLAGS = {'host': '127.0.0.1', 'port': 3306, 'user': 'root'} 
MYSQL_FLAGS = {'host': '127.0.0.1', 'port': 3307, 'user': 'root'}
MONGO_FLAGS = {}

# The database class to use for the benchmark. Options are 'MemSqlDatabase',
# 'MySqlDatabase' and 'MongoDatabase'.
DATABASE = 'MemSqlDatabase'

# Enable or disable printing of various statistics, such as the distribution
# of game lengths and recent events.
SHOW_GAME_STATISTICS = False

# Enable or disable the game simulation logging every action in the database.
GAME_ENABLE_LOG = True

# Run the benchmark for a given period in seconds or None to run forever.
TOTAL_TIME = None

# Number of seconds to wait between sampling QPS for the output file.
SAMPLE_INTERVAL = None
