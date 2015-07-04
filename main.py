from website import *
from models import *

import endpoints

from protorpc import messages
from protorpc import message_types
from protorpc import remote


class Home(MainHandler):
    def get(self):
        self.render('index.html')


class UserObject(messages.Message):
    email = messages.StringField(1, required = True)
    firstName = messages.StringField(2, repeated = True)
    lastName = messages.StringField(3)

@endpoints.api(name = 'users', version = 'v1',
               description = 'User Management Resources')
class Users(remote.Service):

    @endpoints.method(UserObject, UserObject,
                        name = 'getUserByEmail',
                        path = 'get_user_by_email',
                        http_method = 'GET')
    def getUser(self, request):
        user = UserObject(email = "email", firstName = ['name1','name2','name3'],
                            lastName = "lastName")
        return user

@endpoints.api(name = 'projects', version = 'v1',
               description = 'Project Management Resources')
class Projects(remote.Service):
    pass


application = endpoints.api_server([Users, Projects])

app = webapp2.WSGIApplication([
    ('/', Home)
], debug=True)