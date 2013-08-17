#-*- coding: utf-8 -*-
import os
import urllib
import logging

from models import Greeting
from models import Heart
from models import Profile
from models import ProfilePermission

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import images

from datetime import datetime

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

        template = JINJA_ENVIRONMENT.get_template('html/index.html')
        self.response.write(template.render(template_values))

class Image(webapp2.RequestHandler):
    def get(self):
        greeting = db.get(self.request.get('img_id'))
        if greeting.avatar:
            self.response.headers['Content-Type'] = 'imgage/png'
            self.response.out.write(greeting.avatar)
        else:
            self.error(404)

class ProfileImage(webapp2.RequestHandler):
    def get(self):
        profile = db.get(self.request.get('img_id'))
        if profile.img:
            self.response.headers['Content-Type'] = 'imgage/png'
            self.response.out.write(profile.img)
        else:
            self.error(404)

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
        template = JINJA_ENVIRONMENT.get_template('html/post.html')
        self.response.write(template.render(template_values))
        
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        sender = users.get_current_user()
        if sender:            
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name',
                                          users.get_current_user().user_id() or DEFAULT_GUESTBOOK_NAME))
            greeting = Greeting(parent=guestbook_key(guestbook_name))
            greeting.author = users.get_current_user().nickname()
            greeting.user_id = users.get_current_user().user_id()
        else:
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME))
            greeting = Greeting(parent=guestbook_key(guestbook_name))



        if self.request.get('img'):
            avatar = images.resize(self.request.get('img'),300,300)
            greeting.avatar = db.Blob(avatar)
        greeting.content = self.request.get('content')
        greeting.date = datetime.now()
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
                    heart.date = datetime.now()
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

class ProfileManager(webapp2.RequestHandler):
    def get(self):
        sender = users.get_current_user()
        if sender:            
            guestbook_name = urllib.unquote_plus(self.request.get('guestbook_name',
                                          users.get_current_user().user_id() or DEFAULT_GUESTBOOK_NAME))
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            template_values = {
               'guestbook_name': urllib.quote_plus(guestbook_name),
               'url': url,
               'url_linktext': url_linktext,
            }
            action_type = self.request.get("action", "list")
            if action_type == "add":
                template = JINJA_ENVIRONMENT.get_template('html/profile_edit.html')
                self.response.write(template.render(template_values))
            elif action_type == "edit":
                profile_id = self.request.get("profile_id")
                if profile_id:
                    profile = db.get(profile_id)
                if profile:
                    template_values.update({'profile':profile})
                    template = JINJA_ENVIRONMENT.get_template('html/profile_edit.html')
                    self.response.write(template.render(template_values))                                
                else:
                    self.redirect('/profile')
            else:
                pfperms = db.GqlQuery('SELECT profile '
                    'FROM ProfilePermission '
                    'WHERE user_id = :1 '
                    'AND isWritable = True',
                    sender.user_id())
                profiles = []
                for pfperm in pfperms:
                    if pfperm:
                        if pfperm.profile:
                            if not pfperm.profile.isDeleted: 
                                profiles.append(pfperm.profile)
                                logging.info(profiles)

                template_values.update({'profiles':profiles})

                template = JINJA_ENVIRONMENT.get_template('html/profile_list.html')
                self.response.write(template.render(template_values))                
        else:
            self.redirect('/')
    def post(self):
        sender = users.get_current_user()
        profile_id = self.request.get("profile_id")
        if sender:
            if profile_id:
                profile = db.get(profile_id)
            else:
                profile = Profile()
            profile.name = self.request.get("name")
            if self.request.get('img'):
                avatar = images.resize(self.request.get('img'),300,300)
                profile.img = db.Blob(avatar)
            profile.put()
            if not profile_id:
                profilePermission = ProfilePermission()
                profilePermission.profile = profile
                profilePermission.user_id = sender.user_id()
                profilePermission.isWritable = True
                profilePermission.put()

        self.redirect('/profile')
        
    def delete(self):
        sender = users.get_current_user()
        profile_id = self.request.get("profile_id")
        if profile_id:
            logging.info("delete request : " + profile_id)
        else:
            logging.info("delete request error")
        if sender :
            if profile_id:
                profile = db.get(profile_id)
                logging.info(profile)
                if profile:
                    profile.isDeleted = True
                    profile.put()
                    logging.info("delete result : " + profile_id)
                    pfperms = db.GqlQuery('SELECT profile '
                        'FROM ProfilePermission '
                        'WHERE profile = :1 '
                        'AND isWritable = True',
                        profile)
                    logging.info(pfperms)
                    for pfperm in pfperms:
                        if pfperm:
                            if pfperm.profile:
                                if pfperm.profile.isDeleted: 
                                    pfperm.isDeleted = True
                                    pfperm.put()
                                    logging.info(pfperm)
        
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
        template = JINJA_ENVIRONMENT.get_template('html/list.html')
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
        template = JINJA_ENVIRONMENT.get_template('html/ranking.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/post', Post),
    ('/image', Image),
    ('/pfimg', ProfileImage),
    ('/sendHeart', SendHeart),
    ('/suggest', Suggest),
    ('/ranking', Ranking),
    ('/profile', ProfileManager),
], debug=True)
