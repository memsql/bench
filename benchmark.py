import random, time, sys
from multiprocessing import Pool, Process, Pipe, JoinableQueue
from config import (NUM_WORKERS, PLAYERS_PER_WORKER, NUM_PLAYERS, DATABASE, 
                   SHOW_GAME_STATISTICS, GAME_ENABLE_LOG, TOTAL_TIME, 
                   SAMPLE_INTERVAL)
from mongo_database import MongoDatabase
from sql_database import MySqlDatabase, MemSqlDatabase
from utils import Reporter

Database = eval(DATABASE)

def simulate_play(db, me):
    '''Simulate one action for player. This can be either starting a game,
    making a move or winning a game, and is determined randomly.'''

    # First, get a list of games for the current player.
    games = db.get_games(me)

    # If the number of games is small, consider starting a new game.
    if len(games) == 0 or (len(games) < 10 and random.random() > .3):
        other = random.randint(0, NUM_PLAYERS - 1)
        if other >= me:
            other += 1
        
        db.start_game(me, other)
        if GAME_ENABLE_LOG:
            db.log(me, 'challenged ' + str(other))
    elif len(games) > 0:
        # Otherwise, we will make a move in some game.
        game = random.choice(games)

        # The longer the game, the higher the chance that we win a game.
        if random.random() < min((float(game['turn']) / 50) ** 3, .8):
            db.end_game(me, game)
            if GAME_ENABLE_LOG:
                db.log(me, 'won')
        else:
            # Otherwise, we advance the game by one step.
            db.make_move(me, game)
            if GAME_ENABLE_LOG:
                db.log(me, 'moved')

def worker_main(creation_queue, pipe, worker_id):
    '''The code for a worker. First the worker helps fill the database with
    players. Then the worker will simulate its players.'''
    # We need a try block to cleanly exit when ctrl-c is pressed.
    try:
        # Setup our reporting
        db = Database()
        reporter = Reporter(pipe)

        # We are responsible for the following range of players.
        players = range(worker_id * PLAYERS_PER_WORKER, (worker_id + 1) * PLAYERS_PER_WORKER)

        # Add all our players to the db.
        for player in players:
            db.add_player(player)

        # Mark our worker as done initializing.
        creation_queue.get()
        creation_queue.task_done()
        # Wait for all workers to be done.
        creation_queue.join()

        # Now simulate actions.
        while True:
            simulate_play(db, random.choice(players))
            reporter.mark_event()
    except KeyboardInterrupt:
        pass

class WorkerInfo(object):
    '''Utility class to store some information per process.'''
    def __init__(self, pipe, process):
        self.pipe = pipe
        self.process = process
        self.qps = 0

def main():
    print >>sys.stderr, "Using", DATABASE

    # Setup the database.
    db = Database()
    db.setup()

    # Create a synchronizing queue to coordinate the creation of players. Use
    # it as a semaphore, where we start simulating once each thread has popped
    # and marked one item as done.
    creation_queue = JoinableQueue()
    for i in range(NUM_WORKERS):
        creation_queue.put(i)

    # Create our worker processes and let them start.
    print >>sys.stderr, "Spawning %s workers" % NUM_WORKERS
    workers = []
    for i in range(NUM_WORKERS):
        left, right = Pipe()
        process = Process(target=worker_main, args=(creation_queue, right, i))
        process.start()
        workers.append(WorkerInfo(left, process))

    # Catch KeyboardInterrupt so we can cleanly exit all workers.
    try:
        sum_qps = 0
        total_samples = 0

        print >>sys.stderr, "Setting up %s players" % NUM_PLAYERS
        creation_queue.join()

        print >>sys.stderr, "Simulating!"
        # Store last reporting time so we can print qps once per second.
        last_qps = last_stats = last_sample = time.time()
        samples = []

        start_time = time.time()
        while TOTAL_TIME is None or time.time() - start_time < TOTAL_TIME:
            # Poll each worker to see if qps information has been updated.
            for worker in workers:
                while worker.pipe.poll():
                    worker.qps = worker.pipe.recv()

            qps = sum(worker.qps for worker in workers)

            # Report qps and statistics.
            if time.time() - last_qps > 1:
                last_qps = time.time()
                print >>sys.stderr, "%s actions per second" % qps

                # Additionally, compute a running average over the qps.
                sum_qps += qps
                total_samples += 1

            if SHOW_GAME_STATISTICS and time.time() - last_stats > 2.5:
                last_stats = time.time()
                print >>sys.stderr, "Statistics:", db.get_stats()

            if SAMPLE_INTERVAL is not None and time.time() - last_sample > SAMPLE_INTERVAL:
                samples.append(qps)
                last_sample = time.time()
            time.sleep(0.01)

    except KeyboardInterrupt:
        # Shut down each worker.
        pass
    finally:
        for worker in workers:
            worker.pipe.close()
            worker.process.terminate()
        
    print >>sys.stderr, "Average actions per second", sum_qps / total_samples

    if SAMPLE_INTERVAL is not None:
        # For javascript output
        print "sample_interval = %s;" % SAMPLE_INTERVAL
        print "samples = %s;" % samples

if __name__ == '__main__':
    main()
