import pytest
import os
from pathlib import Path
from games.domainmodel.model import Publisher, Genre, Game, Review, User, Wishlist
from games.adapters.datareader.csvdatareader import GameFileCSVReader

from games.adapters.memory_repository import MemoryRepository, populate


def test_repository_add_game():
    repo = MemoryRepository()

    game1 = Game(1, "Test Game")
    repo.add_game(game1)

    # Check repo knows the game list length has increased
    assert repo.get_number_of_games() == 1

    # Check the right game object was added
    assert game1 in repo.get_all_games()

    # Check that adding another game works, and does not affect the first game
    game2 = Game(2, "Test Quest")
    repo.add_game(game2)

    assert repo.get_number_of_games() == 2
    assert game2 in repo.get_all_games()
    assert game1 in repo.get_all_games()

    # Check that adding a third game still works fine, and that adding it twice doesn't add a duplicate
    game3 = Game(3, "Unit Tests: The Game")
    repo.add_game(game3)
    repo.add_game(game3)
    assert repo.get_number_of_games() == 3
    assert game3 in repo.get_all_games()
    assert game2 in repo.get_all_games()
    assert game1 in repo.get_all_games()

    # Check once again that trying to add duplicates doesn't add the game again
    repo.add_game(game1)
    repo.add_game(game2)
    assert repo.get_number_of_games() == 3
    assert game3 in repo.get_all_games()
    assert game2 in repo.get_all_games()
    assert game1 in repo.get_all_games()


def test_get_game():
    repo = MemoryRepository()

    game1 = Game(1, "Test Game")
    repo.add_game(game1)
    game2 = Game(2, "Test Quest")
    repo.add_game(game2)
    game3 = Game(3, "Unit Tests: The Game")
    repo.add_game(game3)

    assert repo.get_game_by_id(1) == game1
    assert repo.get_game_by_id(2) == game2
    assert repo.get_game_by_id(3) == game3

    assert repo.get_game_by_id(-1) is None
    assert repo.get_game_by_id(4) is None


def test_repo_genres(in_memory_repo):
    repo = in_memory_repo

    initial_genres = repo.get_all_genres()

    # Ensure repo has number of unique genres in original data set
    assert len(repo.get_all_genres()) == 26

    # Check adding a genre works correctly, and nothing is lost
    genre1 = Genre("Test Genre")
    repo.add_genre(genre1)

    new_genres = repo.get_all_genres()

    assert genre1 in repo.get_all_genres()
    assert len(repo.get_all_genres()) == 27
    assert all(genre in new_genres for genre in initial_genres)


def test_genre_search(in_memory_repo):
    repo = in_memory_repo

    # A known game to check with
    game_callofduty = repo.get_game_by_id(7940)

    # Can the program handle no genres given?
    assert repo.get_games_by_genres([]) == []

    # Can it handle a genre that isn't real / has no games?
    assert repo.get_games_by_genres([Genre("Not a real genre")]) == []

    # Will it return the right number of games for a few single genres,
    # if the number of games of that sort in the repo is already known?
    genre1 = repo.get_genre("Action")
    genre2 = repo.get_genre("Simulation")
    genre3 = repo.get_genre("Violent")

    assert len(repo.get_games_by_genres([genre1])) == 405
    assert len(repo.get_games_by_genres([genre2])) == 189
    assert len(repo.get_games_by_genres([genre3])) == 6

    # Is a known game of the genre found?
    assert game_callofduty in repo.get_games_by_genres([genre1])

    # Does the repo handle multiple genres?
    assert len(repo.get_games_by_genres([genre1, genre2])) == 594
    assert len(repo.get_games_by_genres([genre1, genre3])) == 411
    assert len(repo.get_games_by_genres([genre1, genre2, genre3])) == 600


def test_text_search(in_memory_repo):
    repo = in_memory_repo

    # A known game to check with
    game_callofduty = repo.get_game_by_id(7940)

    # Try searching for a known franchise with only one title in the repo. Does it show up? Is it the right game?
    assert len(repo.get_games_by_name_query("Call of Duty")) == 1
    assert game_callofduty in repo.get_games_by_name_query("Call of Duty")

    # Try a more broad query, will it search the whole repo properly?
    assert len(repo.get_games_by_name_query("e")) == 739
    assert game_callofduty in repo.get_games_by_name_query("e")

    # Try searching for nonsense. Does it handle no games found?
    assert repo.get_games_by_name_query("857r6t2q378g78r1g282g8") == []
    assert repo.get_games_by_name_query("Test game please ignore") == []
    assert repo.get_games_by_name_query("Half-Life 3") == []

    # Does a blank search find all games as expected?
    assert repo.get_games_by_name_query("") == repo.get_all_games()


def test_user_get_add():
    repo = MemoryRepository()

    user1 = User("Logan Nilson", "Password")
    user2 = User("Gautham Gunasheelan", "ACoolPassword")
    user3 = User("Yuqi Wang", "MyPassword123")

    assert repo.get_all_users() == []

    repo.add_user(user1)
    repo.add_user(user2)

    assert len(repo.get_all_users()) == 2
    assert repo.get_user("Logan Nilson") == user1
    assert repo.get_user("Gautham Gunasheelan") == user2
    assert repo.get_user("Yuqi Wang") is None

    repo.add_user(user1)
    repo.add_user(user2)
    repo.add_user(user3)
    assert len(repo.get_all_users()) == 3
    assert repo.get_user("Logan Nilson") == user1
    assert repo.get_user("Gautham Gunasheelan") == user2
    assert repo.get_user("Yuqi Wang") == user3

    assert repo.get_user("Shyamli") is None
    assert repo.get_user(300) is None
    assert repo.get_user(None) is None

    repo.add_user(None)
    repo.add_user("Definitely a real user")

    assert len(repo.get_all_users()) == 3
    assert repo.get_user("Logan Nilson") == user1
    assert repo.get_user("Gautham Gunasheelan") == user2
    assert repo.get_user("Yuqi Wang") == user3


def test_review_add_remove():
    repo = MemoryRepository()

    user = User("Shyamli", "pw12345")
    game = Game(1, "Domino Game")

    review1 = Review(user, game, 3, "Great game!")
    review2 = Review(user, game, 4, "Superb game!")
    review3 = Review(user, game, 2, "Boring game!")

    assert len(repo.get_reviews()) == 0

    user.add_review(review1)
    game.add_review(review1)

    repo.add_review(review1)
    assert len(repo.get_reviews()) == 1
    assert review1 in repo.get_reviews()
    assert review2 not in repo.get_reviews()
    assert review3 not in repo.get_reviews()

    user.add_review(review2)
    game.add_review(review2)

    repo.add_review(review2)
    assert len(repo.get_reviews()) == 2
    assert review1 in repo.get_reviews()
    assert review2 in repo.get_reviews()
    assert review3 not in repo.get_reviews()

    user.add_review(review3)
    game.add_review(review3)

    user.remove_review(review1)
    game.remove_review(review1)

    repo.add_review(review3)
    repo.remove_review(review1)
    assert len(repo.get_reviews()) == 2
    assert review1 not in repo.get_reviews()
    assert review2 in repo.get_reviews()
    assert review3 in repo.get_reviews()

    repo.remove_review(review1)
    repo.remove_review(review1)
    assert len(repo.get_reviews()) == 2
    assert review1 not in repo.get_reviews()
    assert review2 in repo.get_reviews()
    assert review3 in repo.get_reviews()

    repo.add_review("One of the games of all time")
    repo.add_review(1984)
    repo.add_review(None)
    assert len(repo.get_reviews()) == 2
    assert review1 not in repo.get_reviews()
    assert review2 in repo.get_reviews()
    assert review3 in repo.get_reviews()

    repo.remove_review("One of the games of all time")
    repo.remove_review(1984)
    repo.remove_review(None)

    user.add_review(review1)
    game.add_review(review1)

    repo.add_review(review1)
    assert len(repo.get_reviews()) == 3
    assert review1 in repo.get_reviews()
    assert review2 in repo.get_reviews()
    assert review3 in repo.get_reviews()

    user.remove_review(review1)
    game.remove_review(review1)

    user.remove_review(review2)
    game.remove_review(review2)

    user.remove_review(review3)
    game.remove_review(review3)

    repo.remove_review(review1)
    repo.remove_review(review2)
    repo.remove_review(review3)
    assert len(repo.get_reviews()) == 0
    assert review1 not in repo.get_reviews()
    assert review2 not in repo.get_reviews()
    assert review3 not in repo.get_reviews()
