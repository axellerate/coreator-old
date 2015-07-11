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
	email = ndb.StringProperty()
	password_hash = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()

	@classmethod
	def by_id(cls, uid):
		return Users.get_by_id(uid)
	
	@classmethod
	def by_email(cls, email):
		e = Users.query(Users.email == email).get()
		return e

	@classmethod
	def register(cls, email, password, first_name, last_name):
		pw_hash = make_pw_hash(email, password)
		return cls( email = email,
					password_hash = pw_hash,
					first_name = first_name,
					last_name = last_name)
	
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


