import pytest

from games.adapters.database_repository import SqlAlchemyRepository
from games.domainmodel.model import *
from games.adapters.repository import RepositoryException



def test_repo_can_add_retrieve_game(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    game = Game(30, "Test Game")
    game.price = 20
    repo.add_game(game)
    game2 = repo.get_game_by_id(30)

    assert game.game_id == game2.game_id


def test_repo_can_add_retrieve_publisher(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    publisher = Publisher("publisher name")
    repo.add_publisher(publisher)

    publishers = repo.get_all_publishers()

    assert publisher in publishers
def test_repo_can_add_retrieve_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre = Genre("genre name")
    repo.add_genre(genre)

    genre2 = repo.get_genre("genre name")

    assert genre.genre_name == genre2.genre_name

def test_repo_can_add_retrieve_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User("username", "password")
    repo.add_user(user)

    user2 = repo.get_user("username")

    assert user == user2 and user is user2

def test_repo_can_add_retrieve_review(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    user = User("username", "password")
    game = Game(31, "Test Game")
    game.price = 20

    review = Review(user, game, 5, "test comment")

    repo.add_review(review)

    reviews = repo.get_reviews()

    assert review in reviews and reviews[0].comment == review.comment

def test_get_number_of_games(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    num = repo.get_number_of_games()

    assert num == 29;

def test_get_games_by_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    genre = Genre("Adventure")
    genres = [genre]
    games = repo.get_games_by_genres(genres)

    adventure_game = repo.get_game_by_id(316260)
    action_game = repo.get_game_by_id(7940)

    assert adventure_game in games and action_game not in games

def test_get_games_by_search_query(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    games = repo.get_games_by_name_query("muri")

    game = repo.get_game_by_id(267360)

    assert game in games

def test_get_all_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre1 = Genre("Adventure")
    genre2 = Genre("Action")

    genres = repo.get_all_genres()

    assert (genre1 and genre2) in genres and len(genres) == 3


