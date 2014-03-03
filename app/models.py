from app import db
from mongoengine import *
import datetime
from hashlib import md5

ROLE_USER=0
ROLE_ADMIN=1

class User(Document):
    username = EmailField(max_length=120,required=True)
    role = IntField(default=ROLE_USER)
    #feed = EmbeddedDocument()
    #friends = EmbeddedDocument()
    #goalrequest = EmbeddedDocument()
    #friendrequests = EmbeddedDocument()
    #brainstorms = EmbeddedDocument()
    picture = StringField()
    name = StringField()
    last_seen = DateTimeField(default=datetime.datetime.now())

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def avatar(self,size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.objects(nickname = nickname).first() == None:
            return nickname
        
        version = 2

        while True:
            new_nickname = nickname + str(version)
            
            if User.objects(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

class Goal(Document):
    name = StringField(max_length=120, required=True)
    description = StringField(max_length=300) 
    
class Task(Document):
    goal = ReferenceField(Goal, required=True)
    name = StringField(max_length=120, required=True)
    description = StringField(max_length=300)
    end = DateTimeField(required=True)
