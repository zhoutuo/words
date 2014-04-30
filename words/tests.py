import unittest

from pyramid import testing
import pyramid.httpexceptions as httpexc
from .views import UserView
from .models import User

def initTestDB():
    from sqlalchemy import create_engine
    from .models import (
        DBSession,
        Base
    )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession


class UserViewTests(unittest.TestCase):
    def setUp(self):
        self.session = initTestDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _createDummyUser(self,
                         dummy_id=10000,
                         dummy_name='my_name',
                         dummy_password='my_password'):
        # create a dummy user
        return User(id=dummy_id, name=dummy_name, password=dummy_password)

    def test_get_non_exist(self):
        request = testing.DummyRequest()
        # user with id of 1 does not exist
        # since it is a temporary in-memory database
        request.matchdict[UserView.S_PATH_ID] = 1
        view = UserView(request)
        response = view.get()
        # should return not found exception
        self.assertIsInstance(response, httpexc.HTTPNotFound)

    def test_get_exist(self):
        # create a dummy user
        user = self._createDummyUser()
        self.session.add(user)
        # query this user
        request = testing.DummyRequest()
        request.matchdict[UserView.S_PATH_ID] = user.id
        view = UserView(request)
        # response will be a dict this time
        response = view.get()
        self.assertEqual(response, {
            UserView.S_ID: user.id,
            UserView.S_NAME: user.name
        })

    def test_post_bad_request(self):
        # create a dummy
        user = self._createDummyUser()
        ############################## missing name
        request = testing.DummyRequest(json_body={
            UserView.S_PASSWORD: user.password
        })
        # get response
        response = UserView(request).post()
        self.assertIsInstance(response, httpexc.HTTPBadRequest)
        ############################## missing password
        request = testing.DummyRequest(json_body={
            UserView.S_NAME: user.name,
        })
        # get response
        response = UserView(request).post()
        self.assertIsInstance(response, httpexc.HTTPBadRequest)

    def test_post_create(self):
        # create a dummy user
        user = self._createDummyUser()
        # populate json body
        request = testing.DummyRequest(json_body={
            UserView.S_NAME: user.name,
            UserView.S_PASSWORD: user.password
        })
        # get response
        view = UserView(request)
        # in the form of dict
        response = view.post()
        # should have the same name in the response
        self.assertEqual(response[UserView.S_NAME], user.name)

    def test_post_confict(self):
        # create a dummy user
        user = self._createDummyUser()
        # add to database
        self.session.add(user)
        # populate json body
        request = testing.DummyRequest(json_body={
            UserView.S_NAME: user.name,
            UserView.S_PASSWORD: user.password
        })
        # repeat user creation with the same name and get the response
        response = UserView(request).post()
        # should return the conflict exception
        self.assertIsInstance(response, httpexc.HTTPConflict)

    def test_put_bad_request(self):
        # send an empty body
        request = testing.DummyRequest(json_body={
        })
        # set up the id, in this case it is not used
        request.matchdict[UserView.S_PATH_ID] = 1
        response = UserView(request).put()
        # should be a bad request
        self.assertIsInstance(response, httpexc.HTTPBadRequest)

    def test_put_not_found(self):
        # create a dummy
        user = self._createDummyUser()
        # send an empty body
        request = testing.DummyRequest(json_body={
            UserView.S_NAME: user.name,
            UserView.S_PASSWORD: user.password
        })
        # set up the id, this user does not exist
        request.matchdict[UserView.S_PATH_ID] = 1
        response = UserView(request).put()
        # should be a not found exception
        self.assertIsInstance(response, httpexc.HTTPNotFound)

    def test_put_update(self):
        # create a dummy
        user = self._createDummyUser(dummy_id=3000)
        # add to database
        self.session.add(user)
        # update new info
        user.name = 'new_hah'
        user.password = 'bad)password'
        # update this user through put method
        request = testing.DummyRequest(json_body={
            UserView.S_NAME: user.name,
            UserView.S_PASSWORD: user.password
        })
        request.matchdict[UserView.S_PATH_ID] = user.id
        response = UserView(request).put()
        # the response should be 204 no content
        self.assertIsInstance(response, httpexc.HTTPNoContent)
        # check the DB as well
        updated_user = self.session.query(User).filter(User.id==user.id).one()
        self.assertIs(user, updated_user)

    def test_delete_bad_request(self):
        # send an empty body
        request = testing.DummyRequest()
        # set up the id, in this case this does not exist
        request.matchdict[UserView.S_PATH_ID] = 1
        response = UserView(request).delete()
        # should be a bad request
        self.assertIsInstance(response, httpexc.HTTPBadRequest)

    def test_delete_remove(self):
        # create a dummy
        user = self._createDummyUser(dummy_id=200)
        self.session.add(user)
        # create the request
        request = testing.DummyRequest()
        request.matchdict[UserView.S_PATH_ID] = user.id
        response = UserView(request).delete()
        # should be a no content
        self.assertIsInstance(response, httpexc.HTTPNoContent)
        # DB checking, 0 remains
        self.assertEqual(self.session.query(User).filter(User.id==user.id).count(), 0)
