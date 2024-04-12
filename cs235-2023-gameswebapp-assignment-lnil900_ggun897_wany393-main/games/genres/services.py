from games.adapters.repository import AbstractRepository


def get_genres(repo: AbstractRepository):
    return repo.get_all_genres()
