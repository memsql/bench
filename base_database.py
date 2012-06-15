class BaseDatabase(object):
    '''The API that should be implemented by every database.'''
    def setup(self):
        '''Configure the database. Will be called exactly once.'''
        raise NotImplemented
    def get_stats(self):
        '''Display various statistics.'''
        raise NotImplemented
    def get_games(self, me):
        '''Show games where user with ID me is next to move. Each game should
        support querying game['turn'].'''
        raise NotImplemented
    def start_game(self, me, other):
        '''Start a game between me and other. Increase the number of started
        games for both players by one.'''
        raise NotImplemented
    def make_move(self, me, game):
        '''Advance game by one turn.'''
        raise NotImplemented
    def end_game(self, me, game):
        '''End the game. Increase the number of wins for me by one.'''
        raise NotImplemented
    def log(self, me, event):
        '''Log an event, associated with user ID me.'''
        raise NotImplemented
    def add_player(self, me):
        '''Add player with ID me.'''
        raise NotImplemented
