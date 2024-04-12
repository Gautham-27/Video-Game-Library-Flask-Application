import pytest

from flask import session


def test_register(client):
    # Check that we retrieve the register page.
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid username and password.
    response = client.post(
        '/authentication/register',
        data={'user_name': 'Logan Nilson', 'password': 'Password123!'}
    )
    assert response.headers['Location'] == '/authentication/login'


@pytest.mark.parametrize(('user_name', 'password', 'message'), (
        ('', '', b'Entering a username is required'),
        ('a', '', b'Your username must be more than 2 characters'),
        ('test', '', b'Entering a password is required'),
        ('test', 'test', b'Your password must be at least 8 characters long and contain at least 1 uppercase letter,\
                        lowercase letter and a digit.'),
))
def test_register_with_invalid_input(client, user_name, password, message):
    # Check that attempting to register with invalid combinations of username and password generate appropriate error
    # messages.
    response = client.post(
        '/authentication/register',
        data={'user_name': user_name, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    # Check that we can retrieve the login page.
    status_code = client.get('/authentication/login').status_code
    assert status_code == 200

    # Check that a successful login generates a redirect to the homepage.
    response = auth.login()
    assert response.headers['Location'] == '/'

    # Check that a session has been created for the logged-in user.
    with client:
        client.get('/')
        assert session['user_name'] == 'tester'


def test_logout(client, auth):
    # Login first
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        response = auth.logout()
        assert 'user_id' not in session

        # Make sure user is redirected back to home after logging out.
        assert response.headers['Location'] == '/'


def test_homepage(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200
    assert b'This is a game library you can use to access information on video games.' in response.data


def test_login_required_to_make_review(client):
    # Check the user is sent to log in if trying to access review without being logged in
    response = client.post('/review')
    assert response.headers['Location'] == '/authentication/login'


def test_make_review(client, auth):
    # Login a user.
    auth.login()

    # Go to the review page for Call of Duty
    client.get('/review?game_id=7940')

    # Are we properly returned to the game's description after posting a review? Is the review there?
    response = client.post('/review', data={'game_id': 7940, 'rating': '5', 'review_text': 'I like this game!'})
    assert response.headers['Location'] == '/gameDescription?id=7940'

    # Check our new review is on the game's description page
    response = client.get('/gameDescription?id=7940')
    assert response.status_code == 200
    assert b'I like this game!' in response.data


def test_games_list(client):
    # Check that we can reach the game list.
    response = client.get('/gamesList')
    assert response.status_code == 200

    # Check that the three most recent games in the test data are present, since we sort by release date.
    assert b'Arcadia' in response.data
    assert b'MagicShop3D' in response.data
    assert b'Ninjas Against the Machines' in response.data


def test_articles_with_search_query(client):
    # Check that we can reach the game list.
    response = client.get('/gamesList?search=Call+of+Duty')
    assert response.status_code == 200

    # Check that the only game this query should return is here.
    assert b'Call of Duty' in response.data


def test_articles_with_genre_query(client):
    # Check that we can reach the game list.
    response = client.get('/gamesList?genre_filter=Casual')
    assert response.status_code == 200

    # Check that the only game in our test data that this query should return is here.
    assert b'Space Ace' in response.data


def test_login_required_to_view_profile(client):
    # Check the user is sent to log in if trying to access their profile without being logged in
    response = client.post('/userProfile')
    assert response.headers['Location'] == '/authentication/login'


def test_view_profile(client, auth):
    auth.login()

    # Check the first history entry is in the user's profile
    response = client.post('/userProfile')
    assert response.status_code == 200
    assert b'Created their account' in response.data


def test_login_required_to_add_wishlist(client):
    # Check the user is sent to log in if trying to add something to their wishlist without being logged in
    response = client.post('/gameDescription/wishlist')
    assert response.headers['Location'] == '/authentication/login'


def test_add__remove_wishlist(client, auth):
    auth.login()

    # First we try adding to wishlist
    response = client.post('/gameDescription/wishlist?id=7940')

    # Check if it's on our profile now
    response = client.post('/userProfile')
    assert response.status_code == 200

    formatted_response = response.data.decode('utf-8')
    assert 'Added' in formatted_response and 'Call of Duty' in formatted_response

    # Now let's see if we can remove it the same way, which should work since wishlist requests are a toggle.
    response = client.post('/gameDescription/wishlist?id=7940')
    response = client.post('/userProfile')
    assert response.status_code == 200

    formatted_response = response.data.decode('utf-8')
    assert 'Removed' in formatted_response and 'Call of Duty' in formatted_response
