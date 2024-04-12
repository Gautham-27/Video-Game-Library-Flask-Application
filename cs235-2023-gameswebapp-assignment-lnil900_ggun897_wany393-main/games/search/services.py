from typing import List, Union

from flask import request

from games.adapters.repository import AbstractRepository
from games.domainmodel.model import Genre, Publisher
import games.adapters.repository as repo
import games.genres.services as genre_services


def get_games_by_genre(repo: AbstractRepository, genres: Union[Genre, List[Genre]]):
    # Contingency case for easier cascade sorting
    if not genres:
        return repo.get_all_games()

    else:
        # Ensure input is a list
        if type(genres) == Genre:
            genres = [genres]
        return repo.get_games_by_genres(genres)


def get_games_by_name(repo: AbstractRepository, query: str):
    return repo.get_games_by_name_query(query)


def get_games_by_cascade(repo: AbstractRepository, genres: Union[None, Genre, List[Genre]],
                         publishers: Union[None, Publisher, List[Publisher]], search_query: str):
    # Get games which match genre(s). get_games_by_genre() will handle instance of genres == None.
    valid_games = get_games_by_genre(repo, genres)

    # Remove games which are not by a desired publisher
    if publishers:
        # Ensure input is a list
        if type(publishers) == Publisher:
            publishers = [publishers]

        valid_games = [game for game in valid_games if game.publisher.publisher_name in publishers]

    # Searching for a query is likely the most resource-intensive operation, so we perform it last on the least games
    if search_query:
        valid_games = [game for game in valid_games if search_query in game.title]

    return valid_games


def process_url() -> dict:
    output_data = {}

    output_data["search_query"] = None
    output_data["search_genres"] = None
    output_data["search_publishers"] = None
    output_data["search_page"] = 1

    page_arg = request.args.get("page")
    if page_arg:
        output_data["search_page"] = int(page_arg)

    output_data["genres_in_dataset"] = genre_services.get_genres(repo.repo_instance)

    output_data["search_query"] = request.args.get('search')
    output_data["search_genres"] = [genre for genre in output_data["genres_in_dataset"] if genre.genre_name
                                    in request.args.getlist('genre_filter')]
    output_data["search_publishers"] = request.args.get("selectPublisher")


    output_data["games_to_show"] = get_games_by_cascade(repo.repo_instance, output_data["search_genres"],
                                                         output_data["search_publishers"], output_data["search_query"])

    return output_data

