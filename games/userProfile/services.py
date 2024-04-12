from games.adapters.repository import AbstractRepository
from games.domainmodel.model import User


def get_user_from_username(repo: AbstractRepository, username: str):
    return repo.get_user(username)


def get_user_history(repo: AbstractRepository, user: User, entries: int = 10):
    user_history = repo.get_user_history(user)
    user_history = [(history.datetimestamp, history.entry) for history in user_history]
    return user_history[-entries:]
