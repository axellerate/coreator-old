from models import *

import endpoints

from protorpc import messages
from protorpc import message_types
from protorpc import remote

class DisplayImage(webapp2.RequestHandler):
    def get(self):
        image_id = self.request.get('id')
        image = Images.get_by_id(int(image_id))
        if image:
            self.response.headers['Content-Type'] = "image/png"
            return self.response.out.write(image.image)
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
    
    professions = Professions.query().order(Professions.name)
    errors = {}

    def get(self):
        return self.render('register.html', errors = self.errors, professions = self.professions)

    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')
        retype_password = self.request.get('retype_password')
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        profession = self.request.get('profession')
        form_errors = False
        if(password != retype_password):
            form_errors = True
            errors.update({"passwords_mismatch": "Passwords do not match."})

        if(Users.query(Users.email == email).count() > 0):
            form_errors = True
            self.errors.update({"email_error":"That email is already in use."})

        if(first_name == "" or last_name == "" or email == "" or password == "" or profession == ""):
            form_errors = True
            self.errors.update({"missing_fields": "You're missing some information."})

        if form_errors == True:
            return self.render('register.html', professions = self.professions, 
                errors = self.errors, email = email, first_name = first_name, 
                last_name = last_name)
        profession = Professions.query(Professions.slug == profession).get()
        user = Users.register(email, password, first_name, last_name, profession.key)
        user.put()
        self.login(user)
        return self.redirect(('/profile?id=%s') %user.key.id())

class Logout(MainHandler):
    def get(self):
        self.logout()
        return self.redirect('/')

class Profile(MainHandler):
    def get(self):
        # user1 = Users.get_by_id(5865619656278016)
        # FriendsPending.send_request(user1, self.user)
        # Friends.remove_friend(user1, self.user)
        # FriendsPending.accept_request(user1, self.user)

        profile_id = int(self.request.get('id'))
        profile_user = Users.get_by_id(profile_id)
        profile_profession = Professions.query(Professions.key == profile_user.profession).get()
        if self.user:
            return self.render('profile.html', profession = profile_profession, user = self.user, profile_user = profile_user)
        else:
            return self.render('profile.html', profession = profile_profession, profile_user = profile_user)

class EditUser(MainHandler):

    professions = Professions.query()

    def get(self):
        user = self.user
        if user:
            self.render('edit-user.html', user = user, professions = self.professions)
        else:
            self.redirect('/register')

    def post(self):
        user = self.user
        old_password = self.request.get('old_password')
        new_password = self.request.get('new_password')
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        profession = self.request.get('profession')
        profession = Professions.query(Professions.slug == profession).get()
        profile_image = self.request.get('profile_image')
        print "profile image"
        print profile_image
        profile_cover_image = self.request.get('profile_cover_image')

        if old_password != "" and new_password > 6:
            if valid_pw(user.email, old_password, user.password_hash):
                pw_hash = make_pw_hash(user.email, new_password)
                user.password_hash = pw_hash
                user.put()
            else:
                return self.redirect('/edit-user')
        if first_name != user.first_name:
            user.first_name = first_name
            user.put()
        if last_name != user.last_name:
            user.last_name = last_name
            user.put()
        if profession.key != user.profession:
            user.profession = profession.key
            user.put()
        if profile_image:
            # if user.profile_image:
            #     img = Images.query(Images.key == user.profile_image).get()
            #     img.key.delete()
            profile_image = Images(image = profile_image)
            profile_image.put()
            user.profile_image = profile_image.key
            user.put()
        if profile_cover_image:
            # if user.profile_cover_image:
            #     img = Images.query(Images.key == user.profile_cover_image).get()
            #     img.key.delete()
            profile_cover_image = Images(image = profile_cover_image)
            profile_cover_image.put()
            user.profile_cover_image = profile_cover_image.key
            user.put()
        return self.redirect('/profile?id=%s' %user.key.id())

class ProjectsPage(MainHandler):
    def get(self):
        page_of_projects = Projects.query().order(Projects.created).fetch(16)
        if self.user:
            return self.render('projects.html', user = self.user, page_of_projects = page_of_projects)
        else:
            return self.render('projects.html', page_of_projects = page_of_projects)

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

class ProjectPage(MainHandler):

    def get(self):
        project_id = self.request.get('id')
        project = Projects.get_by_id(int(project_id))
        field = Fields.query(Fields.key == project.field).get()
        if project == None:
            return self.redirect('/')
        if self.user:
            return self.render('project.html', user = self.user, project = project, field = field)
        else:
            return self.render('project.html', project = project, field = field)

class People(MainHandler):
    def get(self):
        if self.user:
            return self.render('people.html', user = self.user)
        else:
            return self.render('people.html')

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

class UserProjects(MainHandler):
    def get(self):
        user_id = int(self.request.get('id'))
        projects_user = Users.get_by_id(user_id)
        projects = Projects.query(Projects.founder == projects_user.key)
        if projects.count() == 0:
            projects = ''
        if self.user:
            return self.render('user-projects.html', user = self.user, 
                projects_user = projects_user, projects = projects)
        else:
            return self.render('user-projects.html', projects_user = projects_user,
                projects = projects)

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

class NewProject(MainHandler):

    fields = Fields.query().order(Fields.name)
    professions = Professions.query().order(Professions.name)
    project_types = ProjectTypes.query().order(ProjectTypes.name)

    def get(self):
        if self.user:
            return self.render('new-project.html', user = self.user,
                fields = self.fields, professions = self.professions,
                project_types = self.project_types)
        else:
            return self.redirect('/register')

    def post(self):
        title = self.request.get('title')
        description = self.request.get('description')
        field = self.request.get('field')
        professions = self.request.get_all('professions')
        card = self.request.get('card')
        project_type = self.request.get('type')

        if not title or not description or not field or not professions or not project_type or not card:
            return self.render('new-project.html', user = self.user, fields = self.fields, 
                professions = self.professions, title = title, description = description)

        field = Fields.query(Fields.slug == field).get()
        profession_keys = []
        for p in professions:
            profession = Professions.query(Professions.slug == p).get()
            profession_keys.append(profession.key)

        project_type = ProjectTypes.query(ProjectTypes.slug == project_type).get()


        card = Images(image = card)
        card.put()       
        project = Projects(title = title, description = description, field = field.key,
            professions = profession_keys, card = card.key, founder = self.user.key,
            project_type = project_type.key)
        project.put()
        return self.redirect('/')


class EditProject(MainHandler):

    fields = Fields.query().order(Fields.name)
    professions = Professions.query().order(Professions.name)
    project_types = ProjectTypes.query().order(ProjectTypes.name)

    def get(self):

        project_id = self.request.get('id')
        project = Projects.get_by_id(int(project_id))
        if project == None:
            return self.redirect('/')

        if self.user.key == project.founder:
            return self.render('edit-project.html', user = self.user, project = project,
                fields = self.fields, professions = self.professions, 
                project_types = self.project_types)
        elif self.user:
            return self.redirect('/')
        else:
            return self.redirect('/register')


    def post(self):

        project_id = self.request.get('id')
        project = Projects.get_by_id(int(project_id))

        title = self.request.get("title")
        description = self.request.get("description")
        field = self.request.get("field")
        project_type = self.request.get("type")
        professions = self.request.get_all("professions")
        card_image = self.request.get("card")

        project.title = title
        project.description = description
        field = Fields.query(Fields.slug == field).get()
        project.field = field.key

        project_type = ProjectTypes.query(ProjectTypes.slug == project_type).get()

        project.project_type = project_type.key

        profession_keys = []
        for p in professions:
            profession = Professions.query(Professions.slug == p).get()
            profession_keys.append(profession.key)
        if card_image != "":
            card = Images(image = card_image)
            card.put()
            project.card = card.key

        project.professions = profession_keys
        project.put()
        return self.redirect('/edit-project?id=%s' %str(project.key.id()))
        






'''
    Coreator API
    This will be implemented as needed!
'''






class UserObject(messages.Message):
    email = messages.StringField(1, required = True)
    first_name = messages.StringField(2)
    last_name = messages.StringField(3)
    password_hash = messages.StringField(4)
    profession = messages.StringField(5)

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
        profession = Professions.query(Professions.slug == request.profession).get()
        u = Users.register(request.email, request.password_hash,
            request.first_name, request.last_name, profession.key)
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

    @endpoints.method(UserObject, Response,
                        name = 'check_if_exists',
                        path = 'check_if_exists',
                        http_method = 'GET')
    def check_if_exists(self, request):
        user = Users.query(Users.email == request.email.lower())
        if user.count() > 0:
            return Response(message = "That email is already in use.", success = False)
        return Response(message = "That email is not in use.", success = True)


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
        f = Fields.query(Fields.slug == request.field_slug).get()
        p = Professions(name = request.name, slug = request.slug, field = f.key)
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
    ('/project', ProjectPage),
    ('/people', People),
    ('/new-project', NewProject),
    ('/edit-project', EditProject),
    ('/image', DisplayImage),
    ('/edit-user', EditUser)

], debug=True)