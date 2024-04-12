import abc
from typing import List
from games.domainmodel.model import Game, Genre, Publisher, User, Review

repo_instance = None


class RepositoryException(Exception):
    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: User):
        """Adds a new user to the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, user_name) -> User:
        """Returns existing user from repository based on unique user_name"""
        raise NotImplementedError

    @abc.abstractmethod
    def add_game(self, game: Game):
        """ Add a game to the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_users(self):
        """ Returns a list of every user in the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_games(self):
        """ Return the number of games in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_games(self):
        """ Returns a list of every game in the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_games_by_genres(self, genres: List[Genre]):
        """ Returns a list of all games in the repository which are associated with at least one of the input genres """
        raise NotImplementedError

    @abc.abstractmethod
    def get_games_by_name_query(self, query: str):
        """ Returns a list of all games in the repository where the title of the game contains the input string """
        raise NotImplementedError

    @abc.abstractmethod
    def get_game_by_id(self, id: int):
        """ Returns a single game from the repository, where the id of the game matches the input exactly.
         If multiple exist, which should not happen, the first is given. If none are found, return None."""
        raise NotImplementedError

    @abc.abstractmethod
    def add_genre(self, genre: Genre):
        """ Add a genre to the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_genres(self):
        """ Returns a list of every genre in the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def add_publisher(self, publisher: Publisher):
        """ Add a publisher to the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_publishers(self):
        """ Returns a list of every publisher in the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def sort_games(self):
        """ Updates the list of games in the repo to be sorted """
        raise NotImplementedError

    @abc.abstractmethod
    def sort_genres(self):
        """ Updates the list of genres in the repo to be sorted """
        raise NotImplementedError

    @abc.abstractmethod
    def sort_publishers(self):
        """ Updates the list of publishers in the repo to be sorted """
        raise NotImplementedError

    @abc.abstractmethod
    def sort_self(self):
        """ Sorts the full repository """
        raise NotImplementedError

    @abc.abstractmethod
    def add_review(self, review: Review):
        """ Add a review to the repository.
        If the review has not been properly attached to the user AND game first, a RepositoryError will be raised. """

        if review.user is None or review not in review.user.reviews:
            raise RepositoryException('Review not correctly attached to a User')
        if review.game is None or review not in review.game.reviews:
            raise RepositoryException('Review not correctly attached to a Game')

    @abc.abstractmethod
    def remove_review(self, review: Review):
        """ Remove a review from the repository.
        If the review has not been properly detached from the user AND game first, a RepositoryError will be raised. """

        if review.user is None or review in review.user.reviews:
            raise RepositoryException('Review is still attached to a User')
        if review.game is None or review in review.game.reviews:
            raise RepositoryException('Review is still attached to a Game')

    @abc.abstractmethod
    def get_reviews(self) -> List[Review]:
        """ Fetch all reviews from the repository """
        raise NotImplementedError

    @abc.abstractmethod
    def add_game_to_wishlist(self, user: User, game: Game):
        """ Add a game to the given user's wishlist """
        raise NotImplementedError

    @abc.abstractmethod
    def remove_game_from_wishlist(self, user: User, game: Game):
        """ Remove a game to the given user's wishlist """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_games_in_wishlist(self, user: User):
        """ Return the given user's wishlist """
        raise NotImplementedError

    def get_user_history(self, user: User):
        """ Return the given user's history """
        raise NotImplementedError
