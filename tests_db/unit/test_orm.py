import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from games.domainmodel.model import *


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT username from users'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_games(empty_session, values: list[Game]):
    for value in values:
        empty_session.execute('INSERT INTO games (game_id, game_title, game_price, release_date) VALUES (:game_id, :game_title, :game_price, :release_date)',
                              {'game_id': value.game_id, 'game_title': value.title, 'game_price': value.price, 'release_date': value.release_date})
    rows = list(empty_session.execute('SELECT game_id from games'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_genres(empty_session, values: list[Genre]):
    for value in values:
        empty_session.execute('INSERT INTO genres (genre_name) VALUES (:genre_name)',
                              {'genre_name': value.genre_name})
    rows = list(empty_session.execute('SELECT genre_name from genres'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_game_genre_associations(empty_session, game_key, genre_keys):
    stmt = 'INSERT INTO game_genres (game_id, genre_name) VALUES (:game_id, :genre_name)'
    for genre_key in genre_keys:
        empty_session.execute(stmt, {'game_id': game_key, 'genre_name': genre_key})


def insert_reviewed_game(empty_session):
    user_key = insert_users(empty_session, ["lnil900", "Password123!"])[0]

    game = Game(1, "Test Game")
    game.price = 5.99

    game_key = insert_games(empty_session, [game])[0]

    empty_session.execute(
        'INSERT INTO reviews (user_name, game_id, comment, rating) VALUES '
        '(:user_name, :game_id, "Review 1", 1),'
        '(:user_name, :game_id, "Review 2", 5)',
        {'user_name': user_key, 'game_id': game_key,}
    )


def test_loading_of_users(empty_session):
    users = []
    users.append(("lnil900", "Password123!"))
    users.append(("ggun897", "54321##A"))
    insert_users(empty_session, users)

    expected = [
        User("lnil900", "Password123!"),
        User("ggun897", "54321##A")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = User("lil900", "Password123!")
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT * FROM users'))
    assert rows == [("lil900", "Password123!")]


def test_saving_duplicate_users(empty_session):
    users = []
    users.append(("lnil900", "Password123!"))
    users.append(("ggun897", "54321##A"))
    insert_users(empty_session, users)
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("lnil900", "Password123!")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_games(empty_session):
    game1 = Game(1, "Test Game")
    game1.price = 5.99

    game2 = Game(2, "Test Quest")
    game2.price = 15.99

    game3 = Game(3, "Unit Tests: The Game")
    game3.price = 10.49

    games = [game1, game2, game3]
    insert_games(empty_session, games)

    assert empty_session.query(Game).all() == games


def test_saving_of_games(empty_session):
    game1 = Game(1, "Test Game")
    game1.price = 5.99

    empty_session.add(game1)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT game_id, game_title, game_price FROM games'))
    assert rows == [(1, "Test Game", 5.99)]


def test_saving_duplicate_games(empty_session):
    game1 = Game(1, "Test Game")
    game1.price = 5.99

    game2 = Game(2, "Test Quest")
    game2.price = 15.99

    game3 = Game(3, "Unit Tests: The Game")
    game3.price = 10.49

    games = [game1, game2, game3]
    insert_games(empty_session, games)

    empty_session.commit()

    with pytest.raises(IntegrityError):
        empty_session.add(game1)
        empty_session.commit()


def test_user_reviewing(empty_session):
    insert_reviewed_game(empty_session)

    rows = empty_session.query(Game).all()
    game = rows[0]

    for review in game.reviews:
        assert review.game is game


def test_saving_of_comment(empty_session):
    user_key = insert_users(empty_session, [("lnil900", "Password123!")])[0]

    game = Game(1, "Test Game")
    game.price = 5.99

    game_key = insert_games(empty_session, [game])[0]

    user = empty_session.query(User).all()[0]
    game = empty_session.query(Game).get(1)

    review_text = "GOOD GAME!!!"
    review = Review(user, game, 5, review_text)

    empty_session.merge(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_name, game_id, comment FROM reviews'))

    assert rows == [(user_key, game_key, review_text)]


def test_genres_for_game(empty_session):
    game = Game(1, "Test Game")
    game.price = 5.99
    game_key = insert_games(empty_session, [game])[0]

    genres = [Genre("Action"), Genre("Simulation"), Genre("Racing")]
    genre_keys = insert_genres(empty_session, genres)

    insert_game_genre_associations(empty_session, game_key, genre_keys)

    game = empty_session.query(Game).get(1)
    genres = [empty_session.query(Genre).get(key) for key in genre_keys]

    for genre in genres:
        assert genre in game.genres
