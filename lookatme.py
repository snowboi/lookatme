#-*- coding: utf-8 -*-
import os
import urllib
import logging

from models import Greeting
from models import Heart

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import images

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return db.Key.from_path('Guestbook', guestbook_name)

class MainPage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():            
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name',
                                          users.get_current_user().user_id() or DEFAULT_GUESTBOOK_NAME))
        else:
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME))
        '''
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        '''
        greetings = db.GqlQuery('SELECT * '
                                'FROM Greeting '
                                'WHERE ANCESTOR IS :1 '
                                'ORDER BY date DESC LIMIT 10',
                                guestbook_key(guestbook_name))


        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Image(webapp2.RequestHandler):
    def get(self):
        greeting = db.get(self.request.get('img_id'))
        if greeting.avatar:
            self.response.headers['Content-Type'] = 'imgage/png'
            self.response.out.write(greeting.avatar)
        else:
            self.error(404)

class Suggest(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():            
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name',
                                          users.get_current_user().user_id() or DEFAULT_GUESTBOOK_NAME))
        else:
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME))

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }        
        template = JINJA_ENVIRONMENT.get_template('list.html')
        self.response.write(template.render(template_values))

class Ranking(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():            
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name',
                                          users.get_current_user().user_id() or DEFAULT_GUESTBOOK_NAME))
        else:
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME))

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }        
        template = JINJA_ENVIRONMENT.get_template('ranking.html')
        self.response.write(template.render(template_values))

class Post(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():            
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name',
                                          users.get_current_user().user_id() or DEFAULT_GUESTBOOK_NAME))
        else:
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME))

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }        
        template = JINJA_ENVIRONMENT.get_template('post.html')
        self.response.write(template.render(template_values))
        
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        if users.get_current_user():            
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name',
                                          users.get_current_user().user_id() or DEFAULT_GUESTBOOK_NAME))
        else:
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME))

        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user().nickname()
            greeting.user_id = users.get_current_user().user_id()

        if self.request.get('img'):
            avatar = images.resize(self.request.get('img'),100,100)
            greeting.avatar = db.Blob(avatar)
        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class SendHeart(webapp2.RequestHandler):
    def post(self):
        sender = users.get_current_user()
        greeting = db.get(self.request.get('id'))

        if sender:
            logging.info(sender.user_id() + "##" + greeting.content)
        else:
            logging.info("No user" + "##" + greeting.content)

        if sender:
            if greeting:
                
                '''
                Add Heart Object
                '''
                hearts = db.GqlQuery('SELECT * '
                                'FROM Heart '
                                'WHERE ANCESTOR IS :1 '
                                'AND user_id = :2 '
                                'ORDER BY date DESC LIMIT 1',
                                greeting.key(),
                                sender.user_id())
                heart = hearts.get()
                if not heart:
                    heart = Heart(parent=greeting.key())
                    logging.info("log ## Create new Heart")
                heart.photo = greeting
                heart.user_id = sender.user_id()
                heart.value = True
                heart.put()

                '''
                Update Heart Count
                '''
                hearts = db.GqlQuery('SELECT * '
                                'FROM Heart '
                                'WHERE ANCESTOR IS :1 '
                                'ORDER BY date DESC',
                                greeting.key())
                greeting.heartCount = hearts.count()
                greeting.put()
                logging.info("count:"+str(greeting.heartCount))
                self.response.write("count:"+str(greeting.heartCount))

            else:
                self.response.write('Error:NoContent')
        else:
            self.response.write('Error:NoUser')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/post', Post),
    ('/image', Image),
    ('/sendHeart', SendHeart),
    ('/suggest', Suggest),
    ('/ranking', Ranking),
], debug=True)
