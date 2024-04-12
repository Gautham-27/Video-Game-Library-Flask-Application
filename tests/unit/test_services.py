import pytest
import os

from pathlib import Path
from games.domainmodel.model import Publisher, Genre, Game, Review, User, Wishlist
from games.adapters.datareader.csvdatareader import GameFileCSVReader
from games.adapters.memory_repository import MemoryRepository, populate
from games.adapters.repository import AbstractRepository
from games.gameDescription.services import *
from games.gamesList.services import *
from games.genres.services import *
from games.search.services import *
import games.userProfile.services as userProfileServices
from games.authentication.services import *


def test_gamesDescription_services():
    repo = MemoryRepository()
    game1 = Game(1, "GGUN897s GAME")
    game2 = Game(2, "TEST GAME")
    game3 = Game(3, "CODING GAME")
    repo.add_game(game1)
    repo.add_game(game2)
    repo.add_game(game3)

    # Test gameDescription service layer returns an existing game object by ID
    assert get_game_by_id(repo, 2) == game2

    # Test add_review
    user1 = User("John Doe", "Password123!")
    repo.add_user(user1)
    review1 = Review(user1, game1, 5, "Good!")
    add_review(repo, "John Doe", 1, 5, "Good!")
    assert review1 in repo.get_reviews()

    # Test get_game_reviews
    assert get_game_reviews(repo, 1) == [review1]

    # Test get_average_rating
    add_review(repo, "John Doe", 1, 1, "Not Good!")
    assert get_average_rating(repo, 1) == 3.0

    # Test get_user_from_username
    assert get_user_from_username(repo, "John Doe") == user1

    # Test game_in_user_wishlist
    user1.add_to_wishlist(game2)
    assert not game_in_user_wishlist(repo, "John Doe", 1)
    assert game_in_user_wishlist(repo, "John Doe", 2)


def test_gamesList_services():
    repo = MemoryRepository()
    game1 = Game(1, "GGUN897s GAME")
    game2 = Game(2, "TEST GAME")
    game3 = Game(3, "CODING GAME")
    repo.add_game(game1)
    repo.add_game(game2)
    repo.add_game(game3)

    # Test service layer returns all games in repository
    assert (game1 and game2 and game3) in get_all_games(repo)

    # Test service layer returns correct number of games in repository
    assert len(get_all_games(repo)) == 3

    # Test service layer returns correct number of pages required to display certain amount of games
    num_games = [game1, game2, game3]
    games_per_page = 1
    assert get_number_of_pages(num_games, games_per_page) == 3

    #Test service layer retrieves correct number of games for pagination functionality
    games = get_all_games(repo)
    page_number = 2
    per_page = 1

    retrieved_games = get_page_of_games(games, page_number, per_page)

    assert len(retrieved_games) == 1


def test_genres_services():
    repo = MemoryRepository()
    action = Genre("Action")
    horror = Genre("Horror")
    repo.add_genre(horror)
    repo.add_genre(action)


    #Test genre service layer returns all genres belonging to games in the repo
    assert (action and horror) in get_genres(repo)


def test_search_services():
    repo = MemoryRepository()
    game1 = Game(1, "GGUN897s GAME")
    game2 = Game(2, "TEST GAME")
    game3 = Game(3, "GGUN897s GAME: THE SEQUEL")
    action = Genre("Action")
    horror = Genre("Horror")
    game1.add_genre(horror)
    game1.add_genre(action)
    game2.add_genre(action)
    game3.add_genre(action)
    repo.add_game(game1)
    repo.add_game(game2)
    repo.add_game(game3)

    # Test service layer retrieves all games associated with a specific genre
    horror_games = get_games_by_genre(repo, horror)
    assert (game1 in horror_games) and len(horror_games) == 1

    # Test service layer retrieves correct game based on a search query containing an exact name
    assert game2 in get_games_by_name(repo, "TEST GAME")

    # Test service layer retrieves all applicable games based on a search query containing a partial name
    assert (game1 and game3) in get_games_by_name(repo, "GGUN897s")

    # Test service layer can search for a game within a specific genre
    assert game2 in get_games_by_cascade(repo, [action], None, "TEST")

    # Test service layer returns an empty list if it searchs for a game which does exist in the repo but does not belong to the given genre
    assert get_games_by_cascade(repo, [horror], None, "TEST") == []


def test_userProfile_services():
    repo = MemoryRepository()
    user1 = User("John Doe", "Password123!")
    repo.add_user(user1)

    # Test get_user_from_username
    assert userProfileServices.get_user_from_username(repo, "John Doe") == user1

    # Test get_user_history
    history_messages = [item[1] for item in userProfileServices.get_user_history(repo, user1)]
    assert history_messages == ["Created their account"]

    game1 = Game(1, "GGUN897s GAME")
    user1.add_to_wishlist(game1)
    history_messages = [item[1] for item in userProfileServices.get_user_history(repo, user1)]
    assert history_messages == ["Created their account", "Added 'GGUN897s GAME' to wishlist"]


def test_authentication_services():
    repo = MemoryRepository()

    # Testing add_user
    add_user("John Doe", "Password123!", repo)
    assert len(repo.get_all_users()) == 1
    user1 = repo.get_user("John Doe")
    assert user1 is not None
    assert isinstance(user1, User)

    # User already in repo, should raise UsernameNotUniqueException
    with pytest.raises(UsernameNotUniqueException):
        add_user("John Doe", "Password123!", repo)

    # Testing get_user
    user2 = get_user("John Doe", repo)
    assert user2 == user1

    # Not a real user, should raise UnknownUserException
    with pytest.raises(UnknownUserException):
        get_user("Logan Nilson", repo)

    # Testing authenticate_user
    # Should pass without issue; valid authentication
    authenticate_user("John Doe", "Password123!", repo)

    # Wrong password, should fail authentication, so raise an AuthenticationException
    with pytest.raises(AuthenticationException):
        authenticate_user("John Doe", "NotThePassword", repo)

    # Not a real user, should raise UnknownUserException from calling get_user BEFORE failing authentication
    with pytest.raises(UnknownUserException):
        authenticate_user("Logan Nilson", "Password", repo)
