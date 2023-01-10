"""
functional tests for the 'main' blueprint
"""


def test_home_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """

    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Referral Service' in response.data
    assert b'Hello from Referral Service' in response.data
    assert bytes('Андрюха', encoding='utf-8') in response.data
    assert bytes('Логин', encoding='utf-8') in response.data
    assert bytes('Регистрация', encoding='utf-8') in response.data
    assert bytes('Компании', encoding='utf-8') in response.data


def test_home_page_post(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.post('/')
    assert response.status_code == 405
    assert b"Referral Service" not in response.data
