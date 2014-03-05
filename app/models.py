from app import db
from mongoengine import *
import datetime
from hashlib import md5

ROLE_USER=0
ROLE_ADMIN=1

class FeedItem(EmbeddedDocument):
    timestamp = DateTimeField(default=datetime.datetime.now())
    message = StringField(max_length=140)
    user = ReferenceField('User')
    
    @property
    def feed_item_type(self):
        return self.__class__.__name__

    meta = {'allow_inheritance':True}

class GoalRequest(FeedItem):
    goal = ReferenceField('Goal',unique=True)

class TaskCreate(FeedItem):
    task = ReferenceField('Task',unique=True)
    
class Brainstorm(Document):
    title = StringField(max_length=140,required=True)
    comments = ListField(StringField(max_length=140))

class User(Document):
    username = EmailField(max_length=120,required=True)
    role = IntField(default=ROLE_USER)
    feed = ListField(EmbeddedDocumentField(FeedItem))
    friends = ListField(ReferenceField('User'))
    goalrequest = ListField(ReferenceField('Goal'))
    brainstorms = ListField(ReferenceField(Brainstorm))
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
        return '<User %r>' % (self.name)


class Comment(EmbeddedDocument):
    user = ReferenceField(User)
    message = StringField(max_length=140)
    
class Incentive(EmbeddedDocument):
    penalties = ListField(StringField(max_length=50))    

class Goal(Document):
    name = StringField(max_length=120, required=True,unique_with=['people'])
    description = StringField(max_length=300) 
    start = DateTimeField(default=datetime.datetime.now())
    end = DateTimeField(required=True)
    people = ListField(ReferenceField(User),unique_with=['name','description'])
    completed = ListField(ReferenceField(User))
    comments = ListField(EmbeddedDocumentField(Comment))
    incentives = ListField(EmbeddedDocumentField(Incentive))

    @property
    def feed_item_type(self):
        return self.__class__.__name__

    @queryset_manager
    def objects(doc_cls, queryset): 
        print doc_cls
        return queryset.order_by('end')

    meta = {'allow_inheritance': True}
    
class Task(Goal):
    goal = ReferenceField(Goal,reverse_delete_rule=CASCADE, unique_with=['name','description'])

