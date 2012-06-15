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
