from flask import render_template,flash,redirect,session,url_for,request,g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app,db,lm,oid
from forms import LoginForm
from models import User,ROLE_USER,ROLE_ADMIN
import config
import urllib
import requests
import datetime

@lm.user_loader
def load_user(id):
    return User.objects.get(id=id)

@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=["GET","POST"])
@login_required
def index():

    return render_template('index.html',
        title = 'Home')

@app.route('/loginner')
def loginner():
    # Step 1
    params = dict(response_type='code',
                  scope=' '.join(config.scope),
                  client_id=config.client_id,
                  approval_prompt='force',  # or 'auto'
                  redirect_uri=config.redirect_uri)
    url = config.auth_uri + '?' + urllib.urlencode(params)
    return redirect(url)
 
 
@app.route('/callback')
def callback():
    if 'code' in request.args:
        # Step 2
        code = request.args.get('code')
        data = dict(code=code,
                    client_id=config.client_id,
                    client_secret=config.client_secret,
                    redirect_uri=config.redirect_uri,
                    grant_type='authorization_code')
        r = requests.post(config.token_uri, data=data)
        # Step 3
        access_token = r.json()['access_token']
        r = requests.get(config.profile_uri, params={'access_token': access_token})
        print r.json()
        user = User.objects(username = r.json()['email']).first()
        pic = ' ';
        if('picture' in r.json()):
            pic = r.json()['picture']
            session['picture'] = pic    
         #   if tryuser['picture'] != pic:
         #      tryuser['picture'] = pic
         #     db.users.save(tryuser)
        if not user:
            user = User(username = r.json()['email'], picture = r.json()['picture'], role = ROLE_USER, name = r.json()['name']) 
            user.save()
            
        session['email'] = r.json()['email']
        session['name'] = r.json()['name']
        login_user(user)
        return redirect(url_for('index'))
    else:
        return 'ERROR'
 
@app.route('/login')
def login():
    return render_template('login.html')

#@app.route('/login',methods=['GET','POST'])
#@oid.loginhandler
#def login():
#    if g.user is not None and g.user.is_authenticated():
#        return redirect(url_for('index'))
#    form = LoginForm()
#    if form.validate_on_submit():
#        print "--------------------"
#        session['remember_me'] = form.remember_me.data
#        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
#    return render_template('login.html',title='Sign In',form=form,providers = app.config['OPENID_PROVIDERS'])
#
#@oid.after_login
#def after_login(resp):
#    if resp.email is None or resp.email == "":
#        flash('Invalid login. Try again')
#        return redirect(url_for('login'))
#    user = User.objects(email = resp.email).first()
#
#    if user is None:
#        nickname = resp.nickname
#
#        if nickname is None or nickname =="":
#            nickname = resp.email.split('@')[0]
#        nickname = User.make_unique_nickname(nickname)
#        
#        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
#        user.save()
#
#    remember_me = False
#
#    if 'remember_me' in session:
#        remember_me = session['remember_me']
#        session.pop('remember_me',None)
#    login_user(user, remember = remember_me)
#    return redirect(request.args.get('next') or url_for('index'))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/test')
@login_required
def test():
    return render_template('test.html')
