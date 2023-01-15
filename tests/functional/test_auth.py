"""
functional tests for the 'auth' blueprint
"""
from app.models import User
from app import mail
from flask import session


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


def test_confirm_email_valid(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/confirm/<token>' page is requested (GET) with valid data
    THEN check that the user's email address is marked as confirmed
    """
    # Create the unique token for confirming a user's email address
    user = User.query.filter_by(email='test@test.ru').first()
    token = user.generate_confirmation_token()
    response = test_client.get('/auth/confirm/'+token, follow_redirects=True)
    user = User.query.filter_by(email='test@test.ru').first()
    assert response.status_code == 200
    assert response.request.path == "/user/profile"
    assert 'Аккаунт подтвержден. Спасибо!' in response.data.decode('utf-8')
    assert user.confirm_token(token) == 'test@test.ru'
    assert user.confirm_token(token) != 'test@test.com'
    assert user.email_confirmed


def test_confirm_email_already_confirmed(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/confirm/<token>' page is requested (GET) with valid data
         but the user's email is already confirmed
    THEN check that the user's email address is marked as confirmed
    """
    # Create the unique token for confirming a user's email address
    user = User.query.filter_by(email='test@test.ru').first()
    token = user.generate_confirmation_token()

    # Confirm the user's email address
    test_client.get('/auth/confirm/'+token, follow_redirects=True)

    # Process a valid confirmation link for a user that has their email address already confirmed
    response = test_client.get('/auth/confirm/'+token, follow_redirects=True)
    user = User.query.filter_by(email='test@test.ru').first()
    assert response.status_code == 200
    assert 'Ваш аккаунт уже подтвержден!' in response.data.decode('utf-8')
    assert user.email_confirmed == 1


def test_confirm_email_invalid(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/confirm/<token>' page is is requested (GET) with invalid data
    THEN check that the link was not accepted
    """
    response = test_client.get('/auth/confirm/bad_confirmation_link', follow_redirects=True)
    assert response.status_code == 200
    assert 'Подтверждающая ссылка просрочена или повреждена' in response.data.decode('utf-8')


def test_get_password_reset_email_page(test_client, confirm_email_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the 'auth/reset_password_request' page is requested (GET)
    THEN check that the page is successfully returned
    """
    test_client.get('/auth/logout', follow_redirects=True)
    response = test_client.get('auth/reset_password_request', follow_redirects=True)
    assert response.status_code == 200
    assert 'Сброс пароля' in response.data.decode('utf-8')
    assert 'Емайл' in response.data.decode('utf-8')
    assert 'Сбросить пароль' in response.data.decode('utf-8')


def test_post_password_reset_email_page_valid(test_client, confirm_email_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/reset_password_request' page is posted to (POST) with a valid email address
    THEN check that an email was queued up to send
    """
    test_client.get('/auth/logout', follow_redirects=True)
    with mail.record_messages() as outbox:
        response = test_client.post('/auth/reset_password_request',
                                    data={'email': 'test@test.ru'},
                                    follow_redirects=True)

        assert response.status_code == 200
        assert response.request.path == "/auth/login"
        assert 'На указанный email были отправлены инструкции по восстановлению пароля' in response.data.decode('utf-8')
        assert len(outbox) == 1
        assert outbox[0].subject == '[RS] Запрос на смену пароля'
        assert outbox[0].sender == 'referralservice.helper@gmail.com'
        assert outbox[0].recipients[0] == 'test@test.ru'
        assert 'http://localhost/auth/reset_password/' in outbox[0].html


def test_post_password_reset_email_page_not_confirmed(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/reset_password_request' page is posted to (POST) with a email address that has not been confirmed
    THEN check that an error message is flashed
    """
    test_client.get('/auth/logout', follow_redirects=True)
    with mail.record_messages() as outbox:
        response = test_client.post('/auth/reset_password_request',
                                    data={'email': 'test@test.ru'},
                                    follow_redirects=True)

        assert response.status_code == 200
        assert len(response.history) == 0
        assert 'Пользователя с таким подтвержденным email не существует!' in response.data.decode('utf-8')
        assert len(outbox) == 0


def test_get_password_reset_valid_token(test_client, confirm_email_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/reset_password/<token>/' page is requested (GET) with a valid token
    THEN check that the page is successfully returned
    """
    test_client.get('/auth/logout', follow_redirects=True)
    user = User.query.filter_by(email='test@test.ru').first()
    token = user.get_reset_password_token()

    response = test_client.get('/auth/reset_password/' + token, follow_redirects=True)
    assert response.status_code == 200
    assert 'Новый пароль' in response.data.decode('utf-8')
    assert 'Подтвердите пароль' in response.data.decode('utf-8')
    assert 'Изменить пароль' in response.data.decode('utf-8')


def test_get_password_reset_invalid_token(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/reset_password/<token>' page is requested (GET) with an invalid token
    THEN check that an error message is displayed
    """
    token = 'invalid_token'
    response = test_client.get('/auth/reset_password/' + token, follow_redirects=True)
    assert response.status_code == 200
    assert 'Подтверждающая ссылка просрочена или повреждена' in response.data.decode('utf-8')
    assert len(response.history) == 1


def test_post_password_reset_valid_token(test_client, confirm_email_default_user, afterwards_reset_default_user_password):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/reset_password/<token>' page is posted to (POST) with a valid token
    THEN check that the password provided is processed
    """
    test_client.get('/auth/logout', follow_redirects=True)
    user = User.query.filter_by(email='test@test.ru').first()
    token = user.get_reset_password_token()

    response = test_client.post('/auth/reset_password/' + token,
                                data={'password': 'qwertY987',
                                      'confirm_password': 'qwertY987'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert 'Ваш пароль был обновлён!' in response.data.decode('utf-8')
    assert response.request.path == "/auth/login"


def test_post_password_reset_invalid_token(test_client, confirm_email_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/reset_password/<token>' page is posted to (POST) with an invalid token
    THEN check that the password provided is processed
    """
    test_client.get('/auth/logout', follow_redirects=True)
    token = 'invalid_token'

    response = test_client.post('/auth/reset_password/' + token,
                                data={'password': 'qwertY987',
                                      'confirm_password': 'qwertY987'},
                                follow_redirects=True)

    assert response.status_code == 200
    assert 'Ваш пароль был обновлён!'  not in response.data.decode('utf-8')
    assert 'Подтверждающая ссылка просрочена или повреждена' in response.data.decode('utf-8')
    assert len(response.history) == 1