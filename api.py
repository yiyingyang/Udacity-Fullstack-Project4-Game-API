# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import User, Game
from models import StringMessage, NewGameForm, GameForm, GameForms, UserForm, UserForms, RankForm, RankForms
from utils import get_by_urlsafe

import heapq

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
GET_USER_GAMES = endpoints.ResourceContainer(
        user_name=messages.StringField(1),)
GET_ALL_USERS = endpoints.ResourceContainer()
GET_USER_RANKINGS = endpoints.ResourceContainer()
GET_ALL_GAMES = endpoints.ResourceContainer()
GET_TOP_TEN= endpoints.ResourceContainer()
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_TOP_TEN = 'USER_RANKINGS'

Top_ten = []

@endpoints.api(name='rock_paper_scissors', version='v1')
class RockPaperScissorsAPI(remote.Service):
    """Game API"""
    
    def _returnResult(self, game):
        if game.result == 'draw':
            return game.to_form('You played Rock, Scissors and Paper! You choose {}, your opponent chooses {}. You reach a draw!'.format(game.player_choice, game.pc_choice))
        elif game.result == 'win':
            return game.to_form('You played Rock, Scissors and Paper! You choose {}, your opponent chooses {}. You win!'.format(game.player_choice, game.pc_choice))
        else:
            return game.to_form('You played Rock, Scissors and Paper! You choose {}, your opponent chooses {}. You Lose!'.format(game.player_choice, game.pc_choice))
        
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key, request.player_choice)
        except ValueError:
            raise endpoints.BadRequestException('Please make a valid choice from rock, scissors and paper')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(params={'user_name': user.name,
                              'result': game.result},
            url='/tasks/update_user_score')
        taskqueue.add(params={'user_name': user.name},
            url='/tasks/cache_top_ten')
        return self._returnResult(game)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return self._returnResult(game)
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_ALL_USERS,
                      response_message=UserForms,
                      path='allusers',
                      name='get_all_users',
                      http_method='GET')
    def get_all_users(self, request):
        """Return all the user records."""
        return UserForms(items=[user.to_form() for user in User.query()])
        
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=UserForm,
                      path='record/{user_name}',
                      name='get_user_record',
                      http_method='GET')
    def get_user_record(self, request):
        """Return the record of one user."""
        user = User.query(User.name==request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with {} does not exist!'.format(request.user_name))
        return user.to_form()
        
    @endpoints.method(request_message=GET_ALL_GAMES,
                      response_message=GameForms,
                      path='allgames',
                      name='get_all_games',
                      http_method='GET')
    
    def get_all_games(self, request):
        """Return all the game history for all users."""
        return GameForms(items=[game.to_form('') for game in Game.query()])
    
    @endpoints.method(request_message=GET_USER_GAMES,
                      response_message=GameForms,
                      path='games/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all the game history of one user."""
        user = User.query(User.name==request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with {} does not exist!'.format(request.user_name))
        games = Game.query(Game.user==user.key)
        return GameForms(items=[game.to_form('') for game in games])
    
    @endpoints.method(request_message=GET_USER_RANKINGS,
                      response_message=RankForms,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns RankForms of all users ordered by win_ratio."""
        return RankForms(items=[user.to_rank_form() for user in User.query().order(-User.win_ratio)])
    
    @endpoints.method(request_message=GET_TOP_TEN,
                      response_message=StringMessage,
                      path='topten',
                      name='get_top_ten',
                      http_method='GET')
    def get_top_ten(self, request):
        """Return top ten ranking."""
        return StringMessage(message=memcache.get(MEMCACHE_TOP_TEN) or "")
        #list = [p[1] for p in sorted(Top_ten)]
        #return StringMessage(message = ','.join(list[::-1]))

    @staticmethod
    def _update_user_score(user_name, result):
        """Update User Score"""
        user = User.query(User.name==user_name).get()
        user.games += 1
        if result == 'win':
            user.wins += 1
        elif result == 'lose':
            user.loses += 1
        user.win_ratio = float(user.wins)/user.games
        user.put()
    
    @staticmethod
    def _cache_top_ten(user_name):
        user = User.query(User.name==user_name).get()
        if not Top_ten:
            heapq.heappush(Top_ten, [user.win_ratio, user_name])
        else:
            change = False
            for index in range(len(Top_ten)):
                p_score, p_user = Top_ten[index]
                if p_user == user.name:
                    Top_ten[index][0] = user.win_ratio
                    change = True
                    break
            if not change:
                if len(Top_ten) < 10:
                    heapq.heappush(Top_ten, [user.win_ratio, user.name])
                elif Top_ten[0][0] < user.win_ratio:
                    heapq.heappop(Top_ten)
                    heapq.heappush(Top_ten, [user.win_ratio, user.name])
        output = ''
        for p in sorted(Top_ten)[::-1]:
            output += p[1] + '('+ str(p[0]*100) + '%) -- '
        memcache.set(MEMCACHE_TOP_TEN, output)
        
api = endpoints.api_server([RockPaperScissorsAPI])
