#-*- coding: utf-8 -*-
from google.appengine.ext import db

"""Models an individual Guestbook entry with author, content, and date."""
class Greeting(db.Model):
    author = db.StringProperty()
    user_id = db.StringProperty()
    content = db.StringProperty(multiline=True)
    avatar = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    heartCount = db.IntegerProperty(default=0)

class Heart(db.Model):
    photo = db.ReferenceProperty(Greeting)
    value = db.BooleanProperty(default=False)
    date = db.DateTimeProperty(auto_now_add=True)
    user_id = db.StringProperty()

class Profile(db.Model):
    name = db.StringProperty()
    birthday = db.DateProperty()
    img = db.BlobProperty()
    isDeleted = db.BooleanProperty(default=False)

class ProfilePermission(db.Model):
    profile = db.ReferenceProperty(Profile)
    user_id = db.StringProperty()
    isWritable = db.BooleanProperty(default=False)
    isDeleted = db.BooleanProperty(default=False)
    
class LAMUser(db.Model):
    user_id = db.StringProperty()
    name = db.StringProperty()
    birthday = db.DateProperty()
    area = db.StringProperty()
    company = db.StringProperty()
    profile_img = db.BlobProperty()
    '''
    follows = db.ListProperty()
    followers = db.ListProperty()
    '''
    heartspendtime = db.DateTimeProperty()
    remainheart = db.DateTimeProperty()
    preferredAgeStart = db.IntegerProperty()
    preferredAgeEnd = db.IntegerProperty()
    showMen = db.BooleanProperty()
    showWomen = db.BooleanProperty()
    'Follow, Follower, Phone, email, Facebook, SpendHeartTime, RemainHeart'

'''    
class Category(db.Model):
    category = db.ListProperty()

class company(db.Model):
    company = db.ListProperty()
'''