from google.appengine.ext import ndb

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
		print Users.get_by_id(uid)
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