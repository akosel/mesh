from flask.ext.wtf import Form
from wtforms import DateTimeField,FieldList,StringField,TextField, BooleanField,TextAreaField,HiddenField,Field
from wtforms.widgets import TextInput
from wtforms.validators import Required, Length,ValidationError
from wtforms.ext.dateutil.fields import DateField
from app.models import User
from app import db


def emptinessCheck(form,field):
    if not field.data[0]:
        raise ValidationError('You need to add at least one other person to your goal')

def validUserCheck(form,field):
    for user in field.data:
        print user
        if not User.objects(username = user):
            print 'Bad user'
            raise ValidationError('The e-mail ' + user +  ' is not in our system.')

class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []





class LoginForm(Form):
    openid = TextField('openid',validators = [Required()])
    remember_me = BooleanField('remember_me',default=False)

class GoalForm(Form):
    name = TextField('name',validators = [Required()])
    description = TextField('description',validators = [Required()])
    start = DateField('start',validators = [Required()])
    end = DateField('end', validators = [Required()])
    people = TagListField('people', validators = [validUserCheck,emptinessCheck])    

class TaskForm(Form):
    name = TextField('name',validators = [Length(max=20),Required()])
    description = TextField('description')
    end = DateField('end', validators = [Required()])

class AddNewBrainstormForm(Form):
    title = TextField('title',validators = [Required()])
    initialcomment = TextField('initialcomment',validators = [Required()])
    people = TagListField('people', validators = [Required()])

class AddBrainstormCommentForm(Form):
    comment = TextField('comment',validators = [Required()])

class AddIncentivesForm(Form):
    first = TextField('first',default='Donate $10 to the charity of your choice')
    second = TextField('second',default='Donate $20 to the charity of your choice')
    third = TextField('third',default='Donate $40 to the charity of your choice')
    beyond = TextField('beyond',default='Donate $80 to the charity of your choice')
