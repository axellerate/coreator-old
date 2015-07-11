from models import *

import endpoints

from protorpc import messages
from protorpc import message_types
from protorpc import remote


class Home(MainHandler):
    def get(self):
        if self.user:
            self.render('index.html', user = self.user)
        else:
            self.render('index.html')

    def post(self):
        email = self.request.get('email').lower()
        password = self.request.get('password')

        u = Users.login(email, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid username or password.'
            self.render('index.html', error = msg)

class Register(MainHandler):
    def get(self):
        self.render('register.html')

class Logout(MainHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class Profile(MainHandler):
    def get(self):
        profile_id = int(self.request.get('id'))
        profile_user = Users.get_by_id(profile_id)
        if self.user:
            self.render('profile.html', user = self.user, profile_user = profile_user)
        else:
            self.render('profile.html', profile_user = profile_user)

class Projects(MainHandler):
    def get(self):
        if self.user:
            self.render('projects.html', user = self.user)
        else:
            self.render('projects.html')

class People(MainHandler):
    def get(self):
        if self.user:
            self.render('people.html', user = self.user)
        else:
            self.render('people.html')

class UserProjects(MainHandler):
    def get(self):
        user_id = int(self.request.get('id'))
        projects_user = Users.get_by_id(user_id)
        if self.user:
            self.render('user-projects.html', user = self.user, projects_user = projects_user)
        else:
            self.render('user-projects.html', projects_user = projects_user)

class NewProject(MainHandler):
    def get(self):
        if self.user:
            self.render('new-project.html', user = self.user)
        else:
            self.render('new-project.html')













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
        u = Users.register(request.email, request.password_hash,
            request.first_name, request.last_name)
        u.put()
        return Response(message = "User created successfully", success = True)

    @endpoints.method(UserObject, UserObject,
                        name = 'get_user',
                        path = 'get_user',
                        http_method = 'GET')
    def get_user(self, request):
        user = Users.query(Users.email == request.email).fetch(1)
        return UserObject(email = user[0].email, first_name = user[0].first_name, 
                          last_name = user[0].last_name)


@endpoints.api(name = 'projects', version = 'v1',
               description = 'Project Management Resources')
class ProjectsApi(remote.Service):
    pass


application = endpoints.api_server([UsersApi, ProjectsApi])

app = webapp2.WSGIApplication([
    ('/', Home),
    ('/register', Register),
    ('/logout', Logout),
    ('/profile', Profile),
    ('/user-projects', UserProjects),
    ('/projects', Projects),
    ('/people', People),
    ('/new-project', NewProject)

], debug=True)