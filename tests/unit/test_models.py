
def test_new_user(new_user):
    '''
    GIVEN a User model
    WHEN a new User is created
    THEN check fields are defined correctly
    '''

    assert new_user.first_name == 'Alex'
    assert new_user.second_name == 'Testov'
    assert new_user.email == 'test@test.ru'
    assert new_user.gender == 'Мужской'
    assert new_user.phone_number == '+5019015900'
    assert not new_user.confirmed


def test_set_password_user(new_user):
    """
    GIVEN a User model
    WHEN the user's password is changed
    THEN check the password has been changed
    """
    new_user.set_password('NewPas1')
    assert new_user.email == 'test@test.ru'
    assert new_user.hashed_psw != 'NewPas1'
    assert new_user.check_password('NewPas1')


def test_confirmation_token(new_user):
    """
    GIVEN a User model
    WHEN the user's email need verification
    THEN check the email is verification
    """
    token = new_user.generate_confirmation_token()
    assert new_user.email == 'test@test.ru'
    assert new_user.confirm_token(token) == 'test@test.ru'


def test_new_company(new_company):
    '''
    GIVEN a Company model
    WHEN a new Company is created
    THEN check fields are defined correctly
    '''
    assert new_company.title == 'First'
    assert new_company.email == 'company@test.ru'
    assert new_company.description == 'First test company'
    assert new_company.logo == 'name_photo.png'
    assert new_company.phone_number == '+4991951095'
    assert new_company.address == 'Somewhere in the world'
    assert new_company.hashed_psw != 'testPASS'
    assert new_company.check_password('testPASS')



