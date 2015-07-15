from google.appengine.ext import ndb

import os
import webapp2
from string import letters
import hashlib
import random
import hmac
import jinja2
from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), 'website/templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'ID44fmkf458FDHhfJIJ9j%^77RRF76gb22s2'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(email, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(email + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(email, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(email, password, salt)

def users_key(group = 'default'):
    return ndb.key.from_path('users', group)


class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        print str(user.key.id())
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and Users.by_id(int(uid))

class BaseModel(ndb.Model):
	created = ndb.DateTimeProperty(auto_now_add = True)
	updated = ndb.DateTimeProperty(auto_now = True)

class Users(BaseModel):
    email = ndb.StringProperty(required = True)
    password_hash = ndb.StringProperty(required = True)
    first_name = ndb.StringProperty(required = True)
    last_name = ndb.StringProperty(required = True)
    profession = ndb.KeyProperty(kind = 'Professions', required = True)
    active = ndb.BooleanProperty(default = True)
    profile_image = ndb.KeyProperty(kind = 'Images')
    profile_cover_image = ndb.KeyProperty(kind = 'Images')

    @classmethod
    def by_id(cls, uid):
        return Users.get_by_id(uid)
    
    @classmethod
    def by_email(cls, email):
        e = Users.query(Users.email == email).get()
        return e

    @classmethod
    def register(cls, email, password, first_name, last_name, profession):
        pw_hash = make_pw_hash(email, password)
        check = cls.query(cls.email == email)
        if check.count() > 0:
            return
        return cls( email = email.lower(),
            password_hash = pw_hash,
            first_name = first_name,
            last_name = last_name,
            profession = profession)
    
    @classmethod
    def login(cls, email, pw):
        u = cls.by_email(email)
        if u and valid_pw(email, pw, u.password_hash):
            return u

class Images(BaseModel):
    image = ndb.BlobProperty(required = True)

class Fields(BaseModel):
    name = ndb.StringProperty(required = True)
    slug = ndb.StringProperty(required = True)
    icon = ndb.StringProperty(required = True)  

class Professions(BaseModel):
    name = ndb.StringProperty(required = True)
    slug = ndb.StringProperty(required = True)
    field = ndb.KeyProperty(kind = 'Fields')

class Projects(BaseModel):
    title = ndb.StringProperty(required = True)
    description = ndb.TextProperty(required = True)
    founder = ndb.KeyProperty(kind = 'Users', required = True)
    contributors = ndb.KeyProperty(kind = 'Users', repeated = True)
    moderators = ndb.KeyProperty(kind = 'Users', repeated = True)
    field = ndb.KeyProperty(kind = 'Fields')
    professions = ndb.KeyProperty(kind = 'Professions', repeated = True)
    card = ndb.KeyProperty(kind = 'Images')
    votes = ndb.IntegerProperty(default = 0)

class Messages(BaseModel):
    message = ndb.StringProperty(required = True)
    to_user = ndb.KeyProperty(kind = 'Users')
    from_user = ndb.KeyProperty(kind = 'Users')
    read = ndb.BooleanProperty(default = False)

class UserCommends(BaseModel):
    message = ndb.StringProperty()
    user = ndb.KeyProperty(kind = 'Users')
    commender = ndb.KeyProperty(kind = 'Users')

    @classmethod
    def commend(cls, user, commender, message):
        check = cls.query(cls.user == user.key, cls.commender == commender.key)
        if check.count() > 0:
            return False
        cls(message = message, user = user.key, commender = commender.key)
        cls.put()
        return True

class Friends(BaseModel):
    user = ndb.KeyProperty(kind = 'Users')
    friend = ndb.KeyProperty(kind = 'Users')

    @classmethod
    def add_friend(cls, requester, reciever):
        f1 = cls.query(cls.user == requester.key, cls.friend == reciever.key)
        f2 = cls.query(cls.user == reciever.key, cls.friend == requester.key)
        print f1.count()
        print f2.count()
        if f1.count() > 0 or f2.count() > 0:
            return False
        f1 = Friends(user = requester.key, friend = reciever.key)
        f2 = Friends(user = reciever.key, friend = requester.key)
        f1.put()
        f2.put()
        return True

    @classmethod
    def remove_friend(cls, user, friend):
        f1 = cls.query(cls.user == user.key, cls.friend == friend.key)
        f2 = cls.query(cls.user == friend.key, cls.friend == user.key)
        if f1 > 0 and f2 > 0:
            f1.get().key.delete()
            f2.get().key.delete()
            return True
        return False

class FriendsPending(BaseModel):
    requester = ndb.KeyProperty(kind = 'Users')
    reciever = ndb.KeyProperty(kind = 'Users')

    @classmethod
    def send_request(cls, requester, reciever):
        check = cls.query(cls.requester == requester.key, cls.reciever == reciever.key)
        if check.count() > 0:
            return False
        f = cls(requester = requester.key, reciever = reciever.key)
        f.put()
        m = Messages(message = "Friend Request", to_user = reciever.key, from_user = null)
        m.put()

    @classmethod
    def accept_request(cls, requester, reciever):
        check = cls.query(cls.requester == requester.key, cls.reciever == reciever.key)
        print check.count()
        if check.count() > 0:
            if Friends.add_friend(reciever, requester) == False:
                return False
            check.get().key.delete()
            return True
        return False


