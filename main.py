import webapp2

import endpoints

from protorpc import messages
from protorpc import message_types
from protorpc import remote

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('The app works')


class UserObject(messages.Message):
    # required signifies that the email is needed
    email = messages.StringField(1, required = True)
    firstName = messages.StringField(2, required = True)
    lastName = messages.StringField(3)

@endpoints.api(name = 'users', version = 'v1',
               description = 'API For User Management')
class Users(remote.Service):

    @endpoints.method(UserObject, UserObject,
                        name = 'getUserByEmail',
                        path = 'get_user_by_email',
                        http_method = 'GET')
    def getUser(self, request):
        user = UserObject(email = "email", firstName = "firstName",
                            lastName = "lastName")
        return user

@endpoints.api(name = 'projects', version = 'v1',
               description = 'API For Project Management')
class Projects(remote.Service):
    pass

@endpoints.api(name = 'messaging', version = 'v1',
               description = 'API For Message Management')
class Messaging(remote.Service):
    pass

@endpoints.api(name = 'authentication', version = 'v1',
               description = 'API For Authenticating Users')
class Authentication(remote.Service):
    pass


application = endpoints.api_server([Users, Projects, Messaging, Authentication])

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)