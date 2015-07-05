from website import *
from models import *

import endpoints

from protorpc import messages
from protorpc import message_types
from protorpc import remote


class Home(MainHandler):
    def get(self):
        self.render('index.html')

class Register(MainHandler):
    def get(self):
        self.render('register.html')

class UserObject(messages.Message):
    email = messages.StringField(1, required = True)
    first_name = messages.StringField(2)
    last_name = messages.StringField(3)
    password_hash = messages.StringField(4)

class Response(messages.Message):
    message = messages.StringField(1)
    success = messages.BooleanField(2)

@endpoints.api(name = 'users', version = 'v1.00',
               description = 'User Management Resources')
class UsersApi(remote.Service):


    @endpoints.method(UserObject, Response,
                        name = 'create_user',
                        path = 'create_user',
                        http_method = 'POST')
    def create_user(self, request):
        Users.create_user(request)
        return Response(message = "User created successfully", success = True)

    @endpoints.method(UserObject, UserObject,
                        name = 'get_user',
                        path = 'get_user',
                        http_method = 'GET')
    def get_user(self, request):
        user = Users.query(Users.email == request.email).fetch(1)
        return UserObject(email = user[0].email, first_name = user[0].first_name, last_name = user[0].last_name)

@endpoints.api(name = 'projects', version = 'v1',
               description = 'Project Management Resources')
class ProjectsApi(remote.Service):
    pass


application = endpoints.api_server([UsersApi, ProjectsApi])

app = webapp2.WSGIApplication([
    ('/', Home),
    ('/register', Register)
], debug=True)