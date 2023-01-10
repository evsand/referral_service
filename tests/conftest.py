import pytest
from app import create_app, db
from app.models import User, Company
import flask
from flask.testing import FlaskClient as BaseFlaskClient
from flask_wtf.csrf import generate_csrf


class RequestShim(object):
    """
    A fake request that proxies cookie-related methods to a Flask test client.
    """

    def __init__(self, client):
        self.client = client
        self.vary = set({})

    def set_cookie(self, key, value='', *args, **kwargs):
        """Set the cookie on the Flask test client."""
        server_name = flask.current_app.config['SERVER_NAME'] or 'localhost'
        return self.client.set_cookie(
            server_name, key=key, value=value, *args, **kwargs
        )

    def delete_cookie(self, key, *args, **kwargs):
        """Delete the cookie on the Flask test client."""
        server_name = flask.current_app.config['SERVER_NAME'] or 'localhost'
        return self.client.delete_cookie(
            server_name, key=key, *args, **kwargs
        )


# We're going to extend Flask's built-in test client class, so that it knows
# how to look up CSRF tokens for you!
class FlaskClient(BaseFlaskClient):
    @property
    def csrf_token(self):
        # First, we'll wrap our request shim around the test client, so that
        # it will work correctly when Flask asks it to set a cookie.
        request = RequestShim(self)
        # Next, we need to look up any cookies that might already exist on
        # this test client, such as the secure cookie that powers `flask.session`,
        # and make a test request context that has those cookies in it.
        environ_overrides = {}
        self.cookie_jar.inject_wsgi(environ_overrides)
        with flask.current_app.test_request_context(
                '/auth/login', environ_overrides=environ_overrides,
        ):
            # Now, we call Flask-WTF's method of generating a CSRF token...
            csrf_token = generate_csrf()
            # ...which also sets a value in `flask.session`, so we need to
            # ask Flask to save that value to the cookie jar in the test
            # client. This is where we actually use that request shim we made!
            flask.current_app.session_interface.save_session(flask.current_app, flask.session, request)
            # And finally, return that CSRF token we got from Flask-WTF.
            return csrf_token

    # Feel free to define other methods on this test client. You can even
    # use the `csrf_token` property we just defined, like we're doing here!
    def login(self, username='test', password='test'):
        # use post_csrf instead of code of linked gist
        return self.post_csrf('/auth/login', username=username, password=password, remember_me=False)

    def logout(self):
        return self.get('/auth/logout', follow_redirects=True)


def post_csrf(self, url, **kwargs):
    """Generic post with csrf_token to test all form submissions of my flask app"""
    data = kwargs.pop("data", {})
    data["csrf_token"] = self.csrf_token
    follow_redirects = kwargs.pop("follow_redirects", True)

    return self.post(url, data=data, follow_redirects=follow_redirects, **kwargs)


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.test_client_class = FlaskClient
    app.config.from_object('config.TestingConfig')
    app.extensions['mail'].suppress = True
    yield app


@pytest.fixture
def test_client(app):
    with app.test_client() as testing_client:
        # Establish an application context before accessing the logger and database
        with app.app_context():
            #app.logger.info('Creating database tables in test_client fixture...')

            # Create the database and the database table(s)
            db.create_all()

        yield testing_client  # this is where the testing happens!

        with app.app_context():
            db.drop_all()


@pytest.fixture(scope='function')
def new_user(app):

    with app.app_context():
        user = User(
            first_name='Alex',
            second_name='Testov',
            email='test@test.ru',
            password='qwerty',
            gender='Мужской',
            phone_number='+5019015900',
        )
        yield user


@pytest.fixture(scope='function')
def register_default_user(test_client):
    # Register the default user
    test_client.post('/auth/register',
                     data={'first_name': 'Alex',
                           'second_name': 'Testov',
                           'email': 'test@test.ru',
                           'password': 'Qwerty123',
                           'password2': 'Qwerty123',
                           'gender': 'Мужской',
                           'phone_number': '+5019015900'},
                     follow_redirects=True)
    test_client.get('/auth/logout', follow_redirects=True)
    return


@pytest.fixture(scope='function')
def log_in_default_user(test_client, register_default_user):
    # Log in the default user
    test_client.post('/auth/login',
                     data={'email': 'test@test.ru',
                           'password': 'Qwerty123'},
                     follow_redirects=True)

    yield   # this is where the testing happens!

    # Log out the default user
    test_client.get('/auth/logout', follow_redirects=True)


@pytest.fixture(scope='module')
def new_company():
    company = Company(
        title='First',
        email='company@test.ru',
        description='First test company',
        logo='name_photo.png',
        phone_number='+4991951095',
        address='Somewhere in the world',
    )
    company.set_password('testPASS')
    return company
