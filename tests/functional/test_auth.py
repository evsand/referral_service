"""
functional tests for the 'auth' blueprint
"""
from app import mail


def test_get_register_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the 'auth/register' page is requested (GET)
    THEN check that the response is valid
    """

    response = test_client.get('auth/register')
    assert response.status_code == 200
    assert b'Referral Service' in response.data
    #assert bytes('Регистрация', encoding='utf-8') in response.data
    assert 'Имя' in response.data.decode('utf-8')
    assert 'Фамилия' in response.data.decode('utf-8')
    assert 'Email' in response.data.decode('utf-8')
    assert 'Пароль' in response.data.decode('utf-8')
    assert 'Повторите пароль' in response.data.decode('utf-8')
    assert 'Пол:' in response.data.decode('utf-8')
    assert 'Мужской' in response.data.decode('utf-8')
    assert 'Женский' in response.data.decode('utf-8')
    assert 'Номер телефона' in response.data.decode('utf-8')


def test_valid_registration(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/register' page is posted to (POST) with valid data
    THEN check the response is valid, the user is registered, and an email was queued up to send
    """
    with mail.record_messages() as outbox:

        response = test_client.post('/auth/register',
                                    data={'first_name': 'AlexI',
                                          'second_name': 'Testovoi',
                                          'email': 'test@test.ru',
                                          'password': 'Qwerty123',
                                          'password2': 'Qwerty123',
                                          'gender': 'Мужской',
                                          'phone_number': '+5019015900',
                                          },
                                    follow_redirects=True)

        assert response.status_code == 200
        assert response.request.path == "/auth/unconfirmed"
        assert 'Подтвердите свой email. На указанную почту отправлено письмо' in response.data.decode('utf-8')
        assert len(outbox) == 1
        assert outbox[0].subject == '[RS] Подтверждение регистрации'
        assert outbox[0].sender == 'referralservice.helper@gmail.com'
        assert outbox[0].recipients[0] == 'test@test.ru'
        assert 'http://localhost/auth/confirm/' in outbox[0].html


def test_invalid_registration(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/register' page is posted to (POST) with invalid data (missing password)
    THEN check an error message is returned to the user
    """
    response = test_client.post('/auth/register',
                                data={'first_name': 'AlexI',
                                      'second_name': 'Testovoi',
                                      'email': 'test@test.ru',
                                      'password': 'Qwerty123',
                                      'password2': 'Qwerty12',  # password != password2
                                      'gender': 'Мужской',
                                      'phone_number': '+5019015900',
                                      },
                                # Empty field is not allowed!
                                follow_redirects=True)
    assert response.status_code == 200
    assert 'Подтвердите свой email. На указанную почту отправлено письмо' not in response.data.decode('utf-8')
    assert len(response.history) == 0
    assert 'Пароли не совпадают' in response.data.decode('utf-8')


def test_duplicate_registration(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/register' page is posted to (POST) with the email address for an existing user
    THEN check an error message is returned to the user
    """

    response = test_client.post('/auth/register',
                                data={'first_name': 'Alex2',
                                      'second_name': 'Testov2',
                                      'email': 'test@test.ru',  # that email is taken (register_default_user)
                                      'password': 'Qwerty12',
                                      'password2': 'Qwerty12',
                                      'gender': 'Мужской',
                                      'phone_number': '+5019015901'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert 'Подтвердите свой email. На указанную почту отправлено письмо' not in response.data.decode('utf-8')
    assert 'Фамилия' in response.data.decode('utf-8')
    assert 'Email' in response.data.decode('utf-8')
    assert 'Выход' not in response.data.decode('utf-8')
    assert 'That email is taken. Please choose a different one' in response.data.decode('utf-8')
    assert len(response.history) == 0


def test_get_login_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/login' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/auth/login')
    assert response.status_code == 200
    assert b'Referral Service' in response.data
    assert 'Авторизация'in response.data.decode('utf-8')
    assert 'Email' in response.data.decode('utf-8')
    assert 'Пароль' in response.data.decode('utf-8')
    assert 'Запомнить' in response.data.decode('utf-8')
    assert 'Забыли пароль?' in response.data.decode('utf-8')


def test_valid_login_and_logout(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/login' page is posted to (POST) with valid credentials
    THEN check the response is valid
    """

    response = test_client.post('/auth/login',
                                data={'email': 'test@test.ru',
                                      'password': 'Qwerty123'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/"
    assert 'Выход' in response.data.decode('utf-8')
    assert 'Профиль' in response.data.decode('utf-8')
    assert 'Регистрация' not in response.data.decode('utf-8')

    """
    GIVEN a Flask application
    WHEN the '/auth/logout' page is requested (GET) for a logged in user
    THEN check the response is valid
    """
    response = test_client.get('auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert 'Выход' not in response.data.decode('utf-8')
    assert 'Профиль' not in response.data.decode('utf-8')
    assert 'Регистрация' in response.data.decode('utf-8')
    assert 'Логин' in response.data.decode('utf-8')
    assert 'До скорых встреч!' in response.data.decode('utf-8')


def test_invalid_login(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/login' page is posted to (POST) with invalid credentials (incorrect password)
    THEN check an error message is returned to the user
    """
    response = test_client.post('/auth/login',
                                data={'email': 'test@test.ru',
                                      'password': 'Qwerty12345'},  # Incorrect!
                                follow_redirects=True)
    assert response.status_code == 200
    assert 'Регистрация' in response.data.decode('utf-8')
    assert 'Логин' in response.data.decode('utf-8')
    assert 'Неправильный email или пароль. Попробуйте еще раз!' in response.data.decode('utf-8')
    assert 'Выход' not in response.data.decode('utf-8')
    assert 'Профиль' not in response.data.decode('utf-8')


def test_valid_login_when_logged_in_already(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing and the default user logged in
    WHEN the '/auth/login' page is posted to (POST) with value credentials for the default user
    THEN check a warning is returned to the user (already logged in)
    """
    response = test_client.post('/auth/login',
                                data={'email': 'test@test.ru',
                                      'password': 'Qwerty123'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/"
    assert 'Выход' in response.data.decode('utf-8')
    assert 'Вы уже авторизовались!' in response.data.decode('utf-8')


def test_invalid_logout(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/logout' page is posted to (POST)
    THEN check that a 405 error is returned
    """
    response = test_client.post('/auth/logout', follow_redirects=True)
    assert response.status_code == 405


def test_user_profile_logged_in(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing and the default user logged in
    WHEN the '/user/profile' page is requested (GET)
    THEN check that the profile for the current user is displayed
    """
    response = test_client.get('/user/profile')
    assert response.status_code == 200
    assert b'Referral Service' in response.data
    assert 'Емайл' in response.data.decode('utf-8')
    assert 'Обновить' in response.data.decode('utf-8')


def test_invalid_logout_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/logout' page is requested (GET) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    test_client.get('/auth/logout', follow_redirects=True)  # Double-check that there are no logged in users!
    response = test_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Referral Service' in response.data
    assert 'До скорых встреч!' not in response.data.decode('utf-8')
    assert 'Логин' in response.data.decode('utf-8')
    assert 'Выход' not in response.data.decode('utf-8')
    assert 'Авторизуйтесь для доступа к закрытым страницам' in response.data.decode('utf-8')
    assert len(response.history) == 1


def test_user_profile_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/user/profile' page is requested (GET) when the user is NOT logged in
    THEN check that the user is redirected to the login page
    """
    response = test_client.get('/user/profile', follow_redirects=True)
    assert response.status_code == 200
    assert 'Логин' in response.data.decode('utf-8')
    assert 'Выход' not in response.data.decode('utf-8')
    assert 'Авторизуйтесь для доступа к закрытым страницам' in response.data.decode('utf-8')
    assert len(response.history) == 1


def test_login_with_next_valid_path(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the 'auth/login?next=%2Fuser%2Fprofile' page is posted to (POST) with a valid user login
    THEN check that the user is redirected to the user profile page
    """
    response = test_client.post('auth/login?next=%2Fuser%2Fprofile',
                                data={'email': 'test@test.ru',
                                      'password': 'Qwerty123'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Referral Service' in response.data
    assert 'Емайл' in response.data.decode('utf-8')
    assert 'Обновить' in response.data.decode('utf-8')

    # Log out the user - Clean up!
    test_client.get('/users/logout', follow_redirects=True)


def test_login_with_next_invalid_path(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the 'auth/login?next=http://www.badsite.com' page is posted to (POST) with a valid user login
    THEN check that a 400 (Bad Request) error is returned
    """
    response = test_client.post('auth/login?next=http://www.badsite.com',
                                data={'email': 'test@test.ru',
                                      'password': 'Qwerty123'},
                                follow_redirects=True)
    assert response.status_code == 400
    assert b'Referral Service' not in response.data


