from models import *

import endpoints

from protorpc import messages
from protorpc import message_types
from protorpc import remote

class DisplayImage(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        image = Images.get(key)
        if image:
            self.response.headers['Content-Type'] = "image/png"
            return self.response.out.write(images.image)
        else:
            self.response.headers['Content-Type'] = "image/png"
            return self.response.out.write("/static/unknown.gif")


class Home(MainHandler):
    def get(self):
        if self.user:
            return self.render('index.html', user = self.user)
        else:
            return self.render('index.html')

    def post(self):
        email = self.request.get('email').lower()
        password = self.request.get('password')

        u = Users.login(email, password)
        if u:
            self.login(u)
            return self.redirect('/')
        else:
            msg = 'Invalid username or password.'
            return self.render('index.html', error = msg)

class Register(MainHandler):
    def get(self):
        return self.render('register.html')

class Logout(MainHandler):
    def get(self):
        self.logout()
        return self.redirect('/')

class Profile(MainHandler):
    def get(self):
        profile_id = int(self.request.get('id'))
        profile_user = Users.get_by_id(profile_id)
        if self.user:
            return self.render('profile.html', user = self.user, profile_user = profile_user)
        else:
            return self.render('profile.html', profile_user = profile_user)

class ProjectsPage(MainHandler):
    def get(self):
        if self.user:
            return self.render('projects.html', user = self.user)
        else:
            return self.render('projects.html')

class People(MainHandler):
    def get(self):
        if self.user:
            return self.render('people.html', user = self.user)
        else:
            return self.render('people.html')

class UserProjects(MainHandler):
    def get(self):
        user_id = int(self.request.get('id'))
        projects_user = Users.get_by_id(user_id)
        projects = Projects.query(Projects.founder == projects_user.key)
        if self.user:
            return self.render('user-projects.html', user = self.user, 
                projects_user = projects_user, projects = projects)
        else:
            return self.render('user-projects.html', projects_user = projects_user,
                projects = projects)

class NewProject(MainHandler):

    fields = Fields.query().order(Fields.name)
    professions = Professions.query().order(Professions.name)

    def get(self):
        if self.user:
            return self.render('new-project.html', user = self.user,
                fields = self.fields, professions = self.professions)
        else:
            return self.redirect('/register')

    def post(self):
        title = self.request.get('title')
        description = self.request.get('description')
        field = self.request.get('field')
        professions = self.request.get_all('professions')
        project_type = self.request.get('type')
        card = self.request.get('card')

        if not title or not description or not field or not professions or not project_type or not card:
            return self.render('new-project.html', user = self.user, fields = self.fields, 
                professions = self.professions, title = title, description = description)

        field = Fields.query(Fields.slug == field).get()
        profession_keys = []
        print professions
        for p in professions:
            print p
            profession = Professions.query(Professions.slug == p).get()
            profession_keys.append(profession.key)

        card = Images(image = card)
        card.put()       
        project = Projects(title = title, description = description, field = field.key,
            professions = profession_keys, card = card.key, founder = self.user.key)
        project.put()
        return self.redirect('/')



'''
    Coreator API
    This will be implemented as needed!
'''




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


class FieldObject(messages.Message):
    name = messages.StringField(1)
    slug = messages.StringField(2)
    icon = messages.StringField(3)

class FieldObjects(messages.Message):
    fields = messages.MessageField(FieldObject, 1, repeated = True)

@endpoints.api(name = 'fields', version = 'v1',
               description = 'Field Management Resources')
class FieldsApi(remote.Service):

    @endpoints.method(FieldObject, Response,
                        name = 'create_field',
                        path = 'create_field',
                        http_method = 'POST')
    def create_field(self, request):
        f = Fields(name = request.name, slug = request.slug, icon = request.icon)
        f.put()
        return Response(message = "Field created successfully", success = True)

    @endpoints.method(message_types.VoidMessage, FieldObjects,
                        name = 'get_fields',
                        path = 'get_fields',
                        http_method = 'GET')
    def get_fields(self, request):
        fields = Fields.query().order(Fields.name)
        all_fields = [FieldObject(name = f.name, slug = f.slug, icon = f.icon) for f in fields]
        return FieldObjects(fields = all_fields)

class ProfessionObject(messages.Message):
    name = messages.StringField(1)
    slug = messages.StringField(2)
    field_slug = messages.StringField(3)

class ProfessionObjects(messages.Message):
    professions = messages.MessageField(ProfessionObject, 1, repeated = True)

@endpoints.api(name = 'professions', version = 'v1',
               description = 'Profession Management Resources')
class ProfessionsApi(remote.Service):

    @endpoints.method(ProfessionObject, Response,
                        name = 'create_profession',
                        path = 'create_profession',
                        http_method = 'POST')
    def create_profession(self, request):
        f = Fields.query(slug = request.field_slug).get(1)
        p = Professions(name = request.name, slug = request.slug, field = k.Key())
        p.put()
        return Response(message = "Profession created successfully", success = True)

    @endpoints.method(message_types.VoidMessage, ProfessionObjects,
                        name = 'get_professions',
                        path = 'get_professions',
                        http_method = 'GET')
    def get_professions(self, request):
        professions = Professions.query().order(Professions.name)
        all_professions = [ProfessionObject(name = p.name, slug = p.slug) for p in professions]
        return ProfessionObjects(professions = all_professions)


application = endpoints.api_server([UsersApi, ProjectsApi, ProfessionsApi, FieldsApi])

app = webapp2.WSGIApplication([
    ('/', Home),
    ('/register', Register),
    ('/logout', Logout),
    ('/profile', Profile),
    ('/user-projects', UserProjects),
    ('/projects', ProjectsPage),
    ('/people', People),
    ('/new-project', NewProject),
    ('/image', DisplayImage)

], debug=True)