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

class TaskRequest(GoalRequest):
    task = ReferenceField('Task',unique=True)

class BrainstormRequest(FeedItem):
    brainstorm = ReferenceField('Brainstorm',unique=True)
    
class Brainstorm(Document):
    title = StringField(max_length=140,required=True)
    comments = ListField(EmbeddedDocumentField('Comment'))
    people = ListField(ReferenceField('User'))
    timestamp = DateTimeField(default=datetime.datetime.now())

class Goal(Document):
    name = StringField(max_length=120, required=True,unique_with=['people'])
    description = StringField(max_length=300) 
    isActive = BooleanField()

    start = DateTimeField(default=datetime.datetime.now())
    end = DateTimeField(required=True)
    #keep track of people's completion
    people = ListField(ReferenceField('User'),unique_with=['name','description'])
    completed = ListField(ReferenceField('User'))
    missed = ListField(ReferenceField('User'))

    comments = ListField(EmbeddedDocumentField('Comment'))
    incentives = ListField(EmbeddedDocumentField('Incentive'))
    incentivesActive = BooleanField()

    @property
    def feed_item_type(self):
        return self.__class__.__name__

    @queryset_manager
    def objects(doc_cls, queryset): 
        return queryset.order_by('end')

    meta = {'allow_inheritance': True}

class User(Document):
    username = EmailField(max_length=120,required=True)
    role = IntField(default=ROLE_USER)
    feed = ListField(EmbeddedDocumentField(FeedItem))
    friends = ListField(ReferenceField('User'))
    goalrequest = ListField(ReferenceField('Goal', reverse_delete_rule=PULL))
    brainstorms = ListField(ReferenceField(Brainstorm,reverse_delete_rule=PULL))
    picture = StringField()
    name = StringField()
    first_name = StringField()
    last_name = StringField()
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
    message = StringField(max_length=300)
    timestamp = ComplexDateTimeField(default=datetime.datetime.now())
    
class Incentive(EmbeddedDocument):
    penalties = ListField(StringField(max_length=50))    
    number = IntField(min_value=1)

    
class Task(Goal):
    goal = ReferenceField(Goal,reverse_delete_rule=CASCADE, unique_with=['name','description'])


