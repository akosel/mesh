from flask.ext.wtf import Form
from wtforms import TextField, BooleanField,TextAreaField,HiddenField
from wtforms.validators import Required, Length
from app.models import User

class LoginForm(Form):
    openid = TextField('openid',validators = [Required()])
    remember_me = BooleanField('remember_me',default=False)

