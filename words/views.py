import os
from pyramid.response import FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest, HTTPNoContent

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound

from .models import (
    DBSession,
    User
)


@view_config(route_name='home')
def home_view(request):
    directory = os.path.dirname(__file__)
    location = os.path.join(directory, 'static', 'index.html')
    return FileResponse(location)

# todo: class test
@view_defaults(route_name='user', renderer='json')
class UserView(object):
    S_ID = 'user_id'
    S_NAME = 'name'
    S_PASSWORD = 'password'
    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        user_id = self.request.matchdict[UserView.S_ID]
        try:
            # get the user name
            user_name = DBSession.query(User.name)\
            .filter(User.id==user_id)\
            .one()[0] # [0] returns first column
        except NoResultFound:
            # if no such a ID exits
            return HTTPNotFound()
        return dict(id=user_id, name=user_name)

    # since the url is only 'users/', post method itself has a route name
    @view_config(route_name='users', request_method='POST', accept='application/json')
    def post(self):
        try:
            request = self.request.json_body
        except ValueError:
            # unable to parse json
            return HTTPBadRequest()
        user_name = request.get(UserView.S_NAME)
        user_password = request.get(UserView.S_PASSWORD)
        # lacking mandatory arguments
        if not user_name or not user_password:
            return HTTPBadRequest()
        user = User(name=user_name, password=user_password)
        try:
            DBSession.add(user)
            DBSession.flush()
        # todo: more types of exception
        except DBAPIError:
            # if there is user with the same name
            DBSession.rollback()
            # this is a duplicate request
            return HTTPConflict()
        # http 201 created
        self.request.response.status_int = 201
        return dict(id=user.id, name=user.name)

    @view_config(request_method='PUT', accept='application/json')
    def put(self):
        user_id = self.request.matchdict[UserView.S_ID]
        try:
            request = self.request.json_body
        except ValueError:
            # unable to parse json
            return HTTPBadRequest()
        new_user_name = request.get(UserView.S_NAME)
        new_user_password = request.get(UserView.S_PASSWORD)
        # at least needs one argument
        if not new_user_name and not new_user_password:
            return HTTPBadRequest()
        try:
            # get user instance
            user = DBSession.query(User).filter(User.id==user_id).one()
            # update corresponding values
            if new_user_name:
                user.name = new_user_name
            if new_user_password:
                user.password = new_user_password
            # flush the new values
            DBSession.flush()
        except NoResultFound:
            # such a resource does not exist
            return HTTPNotFound()
        except DBAPIError:
            # there is already a same user name existing
            return HTTPConflict()
        # return the value
        return dict(id=user_id, name=user.name)

    @view_config(request_method='DELETE')
    def delete(self):
        user_id = self.request.matchdict[UserView.S_ID]
        try:
            user = DBSession.query(User).filter(User.id==user_id).one()
        except NoResultFound:
            return HTTPBadRequest()
        # remove it
        DBSession.delete(user)
        # 204 no content response
        return HTTPNoContent()