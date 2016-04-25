#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import RockPaperScissorsAPI

from models import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            subject = 'This is a reminder!'
            body = 'Hello {}, try out Guess A Number!'.format(user.name)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)
            
class UpdateUserScore(webapp2.RequestHandler):
    def post(self):
        RockPaperScissorsAPI._update_user_score(self.request.get('user_name'), self.request.get('result'))
        self.response.set_status(204)

class CacheTopTen(webapp2.RequestHandler):
    def post(self):
        RockPaperScissorsAPI._cache_top_ten(self.request.get('user_name'))
        self.response.set_status(204)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/update_user_score', UpdateUserScore),
    ('/tasks/cache_top_ten', CacheTopTen),
], debug=True)
