from flask.ext.wtf import Form
from wtforms import DateTimeField,FieldList,StringField,TextField, BooleanField,TextAreaField,HiddenField,Field
from wtforms.widgets import TextInput
from wtforms.validators import Required, Length
from wtforms.ext.dateutil.fields import DateField
from app.models import User

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
    people = TagListField('people', validators = [Required()])    

class TaskForm(Form):
    name = TextField('name',validators = [Required()])
    description = TextField('description',validators = [Required()])
    end = DateField('end', validators = [Required()])

class AddNewBrainstormForm(Form):
    title = TextField('title',validators = [Required()])
    initialcomment = TextField('initialcomment',validators = [Required()])
    people = TagListField('people', validators = [Required()])

class AddBrainstormCommentForm(Form):
    comment = TextField('comment',validators = [Required()])

class AddIncentivesForm(Form):
    first = TextField('first',default='Donate $10 to the charity of your choice')
    second = TextField('second')
    third = TextField('third')
    beyond = TextField('beyond')
