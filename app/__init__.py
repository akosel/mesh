from flask import Flask
from flask.ext.mongoengine import MongoEngine
from mongoengine import connect

db = connect('Mesh_DB',host='localhost', port=27017)

app = Flask(__name__)
app.config.from_object('config')

import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
import config

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(config.basedir, 'tmp'))

	
app.secret_key = config.SECRET_KEY


from app import views,models

