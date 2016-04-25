"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""
import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

CHOICES = ['rock','scissors','paper']
POSSIBILITIES = [['rock', 'scissors'],
           ['paper', 'rock'],
           ['scissors', 'paper']
           ]
RESULTS = ['win', 'lose', 'draw'
           ]

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    wins = ndb.IntegerProperty(default=0)
    loses = ndb.IntegerProperty(default=0)
    games = ndb.IntegerProperty(default=0)
    draws = ndb.IntegerProperty(default=0)
    win_ratio = ndb.FloatProperty(default=0.0)
    
    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = UserForm()
        form.user_name = self.name
        form.win_ratio = str(self.win_ratio)
        form.wins = str(self.wins)
        form.loses = str(self.loses)
        form.games = str(self.games)
        form.draws = str(self.draws)
        return form
    def to_rank_form(self):
        form = RankForm()
        form.user_name = self.name
        form.win_ratio = str(self.win_ratio)
        return form
    
class Game(ndb.Model):
    """Game object"""
    
    player_choice = ndb.StringProperty(required=True)
    pc_choice = ndb.StringProperty(required=True)
    result = ndb.StringProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')
    

    @classmethod
    def new_game(cls, user, player_choice):
        """Creates and returns a new game"""
        if player_choice not in CHOICES:
            raise endpoints.BadRequestException('You need to enter a valid choice!')
        pc_choice = random.choice(CHOICES)
        result = None
        
        if player_choice == pc_choice:
            result = RESULTS[2]
        else:
            for p in POSSIBILITIES:
                if player_choice == p[0] and pc_choice == p[1]:
                    result = RESULTS[0]; break
                elif player_choice == p[1] and pc_choice == p[0]:
                    result = RESULTS[1]; break
        game = Game(user=user,
                    player_choice = player_choice,
                    pc_choice = pc_choice,
                    result = result
                    )
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.player_choice = self.player_choice
        form.pc_choice = self.pc_choice
        form.result = self.result
        form.message = message
        return form

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    player_choice = messages.StringField(2, required=True)
    pc_choice = messages.StringField(3, required=True)
    result = messages.StringField(4,required=True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True, default = 'sherry0419')
    player_choice = messages.StringField(2, required=True, default = 'paper')
    
class UserForm(messages.Message):
    """Representation of a User's record"""
    user_name = messages.StringField(1, required=True)
    win_ratio = messages.StringField(2, required=True)
    games = messages.StringField(3, required=True)
    wins = messages.StringField(4, required=True)
    loses = messages.StringField(5, required=True)
    draws = messages.StringField(6, required=True)

class RankForm(messages.Message):
    """Representation of a User's ranking record"""
    user_name = messages.StringField(1, required=True)
    win_ratio = messages.StringField(2, required=True)
    
class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class GameForms(messages.Message):
    """Multiple GameForm container"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class UserForms(messages.Message):
    """Multiple UserForm container"""
    items = messages.MessageField(UserForm, 1, repeated=True)
    
class RankForms(messages.Message):
    """Multiple RankForm container"""
    items = messages.MessageField(RankForm, 1, repeated=True)
