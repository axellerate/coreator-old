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
	def create_user(cls, user_obj):
		user = cls(email = user_obj.email, password_hash = user_obj.password_hash,
			first_name = user_obj.first_name, last_name = user_obj.last_name)
		user.put()
		return True