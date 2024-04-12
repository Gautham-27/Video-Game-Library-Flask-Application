from games.adapters.repository import AbstractRepository
from math import ceil


def get_all_games(repo: AbstractRepository):
    return repo.get_all_games()


def get_number_of_pages(items, items_per_page):
    return ceil(len(items) / items_per_page)


def get_page_of_games(games, page_number, per_page):
    # Make sure page number isn't too high or too low, fix if it is.
    page_number = max(1, min(page_number, get_number_of_pages(games, per_page)))
    start_point = (page_number - 1) * per_page

    return games[start_point:start_point+per_page]


def get_publishers(repo: AbstractRepository):
    return repo.get_all_publishers()
