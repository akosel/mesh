from flask import render_template,flash,redirect,session,url_for,request,g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_oauth import OAuth
from mongoengine import Q
from app import app,db,lm,oid
from forms import LoginForm,GoalForm,TaskForm,AddNewBrainstormForm, AddBrainstormCommentForm, AddIncentivesForm
from models import User,ROLE_USER,ROLE_ADMIN,Goal,FeedItem,GoalRequest,Task,TaskCreate,Brainstorm,Comment,BrainstormRequest,Incentive
from sets import Set
from bson.objectid import ObjectId
import config
import urllib
import requests
import datetime
from dateutil import parser


def datetimeformat(value,format='%Y-%m-%d'):
    #TODO add some error handling if value is not a datetime object
    if value:
        return value.strftime('%B %d, %Y')
app.jinja_env.filters['datetimeformat'] = datetimeformat


@lm.user_loader
def load_user(id):
    return User.objects(id=id).first()

# Login handlers

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

        if not user:
            user = User(username = r.json()['email'], picture = r.json()['picture'], role = ROLE_USER, name = r.json()['name']) 
            user.save()
        else:
	    user['picture'] = r.json()['picture']
            user['first_name'] = r.json()['given_name']
            user['last_name'] = r.json()['family_name']
            user.save()
        login_user(user)
        return redirect(url_for('index'))
    else:
        return 'Oops, looks like the login failed.'

 
@app.route('/login')
def login():
    return render_template('login.html')

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.FACEBOOK_APP_ID,
    consumer_secret=config.FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)


@app.route('/fb_login')
def fblogin():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/fb_login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    picture = "http://graph.facebook.com/"+me.data['id']+"/picture?type=large"

    user = User.objects(username = me.data['email']).first()

    if not user:
        user = User(username = me.data['email'], picture = picture, role = ROLE_USER, name = me.data['first_name'] + me.data['last_name']) 
        user.save()
    else:
        user['picture'] = picture
        user['name'] = me.data['first_name'] + " " + me.data['last_name']
        user['first_name'] = me.data['first_name']
        user['last_name'] = me.data['last_name']
        user.save()
            
    login_user(user)

    return redirect(url_for('index'))
    #return 'Logged in as id=%s name=%s redirect=%s' % \
      #  (me.data, me.data['id'], request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.before_request
def before_request():
    g.user = current_user

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

####################################
#Begin defining page handlers
@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=["GET","POST"])
@login_required
def index():
    user = User.objects(id = g.user.id).first()
    tasks = Task.objects(people=g.user.id)
    return render_template('dashboard.html',
        title = 'Home',user=user,todo=tasks)


@app.route('/goals')
@login_required
def goals():

    requests = User.objects(id = g.user.id).first().goalrequest
    myGoals = Goal.objects(people=g.user.id)
    completedGoals = Goal.objects(completed=g.user.id)
    missedGoals = Goal.objects(missed=g.user.id)

    return render_template('goals.html', goals = myGoals, completedGoals = completedGoals, missedGoals = missedGoals, requests = requests)

@app.route('/newgoal',methods=["GET","POST"])
@login_required
def newgoal():
    form = GoalForm()
    if form.validate_on_submit():

        me = User.objects(id = g.user.id).first()

        goal = Goal(name = form.name.data, description = form.description.data, start = form.start.data, end = form.end.data, people = [me] )
        goal.save()

        feeditem = GoalRequest(user=me,goal=goal,message='Your friend invited you to join their goal')
        

        people = []
        for email in form.people.data:
            friend = User.objects(username = email).first() 
            friend.feed.append(feeditem)
            friend.goalrequest.append(goal)
            friend.save()

        flash ('Goal added!')
        return redirect(url_for('goals'))
    else:
        print "Nope"

    return render_template('newgoal.html',form=form)
    
@app.route('/goals/<goalid>',methods=['GET','POST'])
@login_required
def goaltree(goalid):

    me = User.objects(id = g.user.id).first()
    goal = Goal.objects(id = goalid).first()
    tasks = Task.objects(goal = goalid).order_by('-end')

    form = TaskForm()
    if form.validate_on_submit():
        task = Task(goal=goal,name = form.name.data, description = form.description.data, end = form.end.data, people = [me])
        task.save()
    
        feeditem = TaskCreate(message='A task was added to a goal you are working on',user=me,task=task) 

        for person in goal.people:
            person.feed.append(feeditem)
            person.save()

        return redirect(url_for('goaltree',goalid=goalid))

    return render_template('goaltree.html',me = me, goal = goal, tasks = tasks, today = datetime.datetime.now(), form = form) 

@app.route('/friends')
@login_required
def friends():
    goals = Goal.objects(people = g.user.id)
    me = User.objects(id = g.user.id).first()

    friends = Set()
    for goal in goals:
        friends.update(goal.people)
        friends.update(goal.completed)

    if friends:
        friends.remove(me)

    return render_template('friends.html', friends = friends)

@app.route('/joingoal/<goalid>')
@login_required
def joingoal(goalid):
    goal = Goal.objects(id = goalid).first()
    me = User.objects(id = g.user.id).first()

    feeditem = FeedItem(message=g.user.name+" just joined a goal you are working on",user = me)
    
    for person in goal.people:
        person.feed.append(feeditem)
        person.save()

    goal.people.append(me)
    goal.save()

    User.objects(id = g.user.id).update_one(pull__feed__goal=ObjectId(goalid))
    User.objects(id = g.user.id).update_one(pull__goalrequest=ObjectId(goalid))
 
    return redirect(url_for('index'))

@app.route('/jointask/<taskid>')
@login_required
def jointask(taskid):
    task = Task.objects(id = taskid).first()
    me = User.objects(id = g.user.id).first()

    feeditem = FeedItem(message=g.user.name+" just joined a task you are working on",user = me)
    
    for person in task.people:
        person.feed.append(feeditem)
        person.save()

    if me not in task.people:
        task.people.append(me)
        task.save()
    else:
        flash( "Person in task already")
    print task.goal.id
 
    return redirect(url_for('goaltree',goalid = task.goal.id))

@app.route('/removefeeditem/<goalid>')
@login_required
def removefeeditem(goalid):
    User.objects(id = g.user.id).update_one(pull__feed__goal=ObjectId(goalid))
    return redirect(url_for('index'))

@app.route('/removebsfeeditem/<bsid>')
@login_required
def removebsfeeditem(bsid):
    User.objects(id = g.user.id).update_one(pull__feed__brainstorm=ObjectId(bsid))
    return redirect(url_for('index'))

@app.route('/removegoal/<goalid>')
@login_required
def removegoal(goalid):
    Goal.objects(id=goalid).delete()
    print goalid
 #   User.objects().update_one(pull__goalrequest=ObjectId(goalid))
    print User.objects(id = g.user.id).first().goalrequest
    return redirect(url_for('goals'))
    
@app.route('/removetask/<taskid>')
@login_required
def removetask(taskid):
    goalid = Task.objects(id=taskid).first().goal.id
    Task.objects(id=taskid).delete()
    return redirect(url_for('goaltree',goalid=goalid))

@app.route('/brainstorms',methods=["GET","POST"])
@login_required
def brainstorms():
    me = User.objects(id = g.user.id).first() 

    #TODO add ability to comment on brainstorms in here.
    
    return render_template('brainstorms.html',me = me)

@app.route('/brainstorms/<bsid>',methods=["GET","POST"])
@login_required
def conversation(bsid):

    brainstorm = Brainstorm.objects(id = bsid).first()
    #there should be a form here. actually, i think this should just replace the comment add page, which is too decontextualized.
    form = AddBrainstormCommentForm()
    me = User.objects(id = g.user.id).first()
    if form.validate_on_submit():
        if me not in brainstorm.people:
            brainstorm.people.append(me)
        if brainstorm not in me.brainstorms:
            me.brainstorms.append(brainstorm)
            me.save()
        c = Comment(message = form.comment.data, user = g.user.id)
        brainstorm.comments.append(c)
        brainstorm.save()
        return render_template('conversation.html',brainstorm = brainstorm,form=form)
    
    return render_template('conversation.html',brainstorm = brainstorm,form=form)

@app.route('/newbrainstorm',methods=['GET','POST'])
@login_required
def newbrainstorm():
    me = User.objects(id = g.user.id).first()
    
    form = AddNewBrainstormForm()
    if form.validate_on_submit():
        people = [me]
        c = Comment(message = form.initialcomment.data, user = me)

        b = Brainstorm(title = form.title.data, comments = [c], people = [me])
        b.save()

        me.brainstorms.append(b)
        me.save()

        feeditem = BrainstormRequest(brainstorm=b,message=g.user.name+" started a brainstorm with you.",user = me)

        for person in form.data['people']:
            friend = User.objects(username = person).first()
            friend.feed.append(feeditem)
            friend.save()

        return redirect(url_for('brainstorms'))
    else:
        print 'nope'

    return render_template('newbrainstorm.html',form=form)

@app.route('/joinbrainstorm/<bsid>')
@login_required
def joinbrainstorm(bsid):
    brainstorm = Brainstorm.objects(id = bsid).first()
    me = User.objects(id = g.user.id).first()

    feeditem = FeedItem(message=g.user.name+" just joined your brainstorm",user = me)
    
    for person in brainstorm.people:
        person.feed.append(feeditem)
        person.save()

    if me not in brainstorm.people:
        brainstorm.people.append(me)
        brainstorm.save()
        me.brainstorms.append(brainstorm)
        me.save()
        User.objects(id = g.user.id).update_one(pull__feed__brainstorm=ObjectId(bsid))
    else:
        flash( "Person in task already")
 
    return redirect(url_for('brainstorms'))

@app.route('/addincentives/<goalid>',methods=["POST","GET"])
@login_required
def addincentives(goalid):
    goal = Goal.objects(id = goalid).first()

    form = AddIncentivesForm()

    if form.validate_on_submit():
        #TODO will want to prepopulate fields if incentives already exist
        if form.first.data:
            first = Incentive(penalties = [ form.first.data ], number = 1)
            Goal.objects(id = goalid).update_one(add_to_set__incentives=first)
        if form.second.data:
            second = Incentive(penalties = [ form.second.data ], number = 2)
            Goal.objects(id = goalid).update_one(add_to_set__incentives=second)
        if form.third.data:
            third = Incentive(penalties = [ form.third.data ], number = 3)
            Goal.objects(id = goalid).update_one(add_to_set__incentives=third)
        if form.beyond.data:
            beyond = Incentive(penalties = [ form.beyond.data ], number = 4)
            Goal.objects(id = goalid).update_one(add_to_set__incentives=beyond)
        return redirect(url_for('goaltree', goalid=goalid))



    return render_template('addincentives.html',form = form)

@app.route('/removecomment/<bsid>/<timestamp>')
@login_required
def removecomment(bsid, timestamp):
    Brainstorm.objects(id = bsid).update_one(pull__comments__timestamp=parser.parse(timestamp))
    return redirect(url_for('conversation', bsid=bsid))

@app.route('/removebrainstorm/<bsid>')
@login_required
def removebrainstorm(bsid):
    Brainstorm.objects(id = bsid).delete()
    #remove any newsfeed references to this goal now.
    #User.objects().update(pull__feed__brainstorm=ObjectId(bsid))
    return redirect(url_for('brainstorms'))
    
@app.route('/approveincentives/<goalid>',methods=['GET','POST'])
@login_required
def approveincentives(goalid):
    goal = Goal.objects(id = goalid).first()
    return render_template('approveincentives.html', goal = goal)

@app.route('/completegoal/<goalid>')
@login_required
def completegoal(goalid):
    Goal.objects(id = goalid).update_one(pull__people = ObjectId(g.user.id))
    Goal.objects(id = goalid).update_one(push__completed = ObjectId(g.user.id))

    return redirect(url_for('goaltree',goalid=goalid))

@app.route('/completetask/<taskid>')
@login_required
def completetask(taskid):
    Task.objects(id = taskid).update_one(pull__people = ObjectId(g.user.id))
    Task.objects(id = taskid).update_one(add_to_set__completed = ObjectId(g.user.id))
    
    task = Task.objects(id = taskid).first()
    return redirect(url_for('goaltree',goalid=task.goal.id))

#TODO editgoal
#TODO edittask
#TODO addtask
#TODO addfriendtogoal
#TODO not a function, maybe, but add a place to see missed tasks and associated penalties
#TODO change width in conversation page
#TODO facebook login
#TODO repeating tasks



