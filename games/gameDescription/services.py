from games.adapters.repository import AbstractRepository
from games.domainmodel.model import Game, User, create_review


class NonExistentGameException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def get_game_by_id(repo: AbstractRepository, game_id: int):
    return repo.get_game_by_id(game_id)


def add_review(repo: AbstractRepository, username: str, game_id: int,  rating: int, review_text: str):
    # Make sure the game is real
    game = repo.get_game_by_id(game_id)
    if game is None:
        raise NonExistentGameException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    review = create_review(user, game, rating, review_text)

    user.update_history(f"Created a {review.rating}/5 review for '{review.game.title}'")

    repo.add_review(review)


def get_game_reviews(repo: AbstractRepository, game_id: int):
    return [review for review in repo.get_reviews() if review.game.game_id == game_id]


def get_average_rating(repo: AbstractRepository, game_id: int):
    reviews = get_game_reviews(repo, game_id)
    ratings = [review.rating for review in reviews]

    if len(ratings) > 0:
        return round(sum(ratings) / len(ratings), 2)
    else:
        return 0


def get_user_from_username(repo: AbstractRepository, username: str):
    return repo.get_user(username)


def game_in_user_wishlist(repo: AbstractRepository, username: str, game_id: int):
    user = get_user_from_username(repo, username)
    if not user:
        return False

    return get_game_by_id(repo, game_id) in repo.get_all_games_in_wishlist(user)


def add_game_to_user_wishlist(repo: AbstractRepository, user: User, game: Game):
    repo.add_game_to_wishlist(user, game)


def remove_game_from_user_wishlist(repo: AbstractRepository, user: User, game: Game):
    repo.remove_game_from_wishlist(user, game)
