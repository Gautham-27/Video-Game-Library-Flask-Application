from typing import List, Union
from datetime import datetime

from pathlib import Path

from games.adapters.repository import AbstractRepository
from games.adapters.datareader.csvdatareader import GameFileCSVReader
from games.domainmodel.model import Game, Genre, Publisher, User, Review

import csv
from werkzeug.security import generate_password_hash


class MemoryRepository(AbstractRepository):
    def __init__(self):
        self.__games = list()
        self.__genres = list()
        self.__publishers = list()
        self.__users = list()
        self.__reviews = list()

    def add_user(self, user: User):
        if isinstance(user, User) and user not in self.__users:
            self.__users.append(user)

    def get_user(self, user_name: str):
        # Assume usernames will be modified as they are when set under User constructor
        # For security, bail if the username isn't a string before trying to format.
        if not isinstance(user_name, str):
            return None
        user_name = user_name.lower().strip()
        for user in self.__users:
            if user.username == user_name:
                return user
        return None

    def get_all_users(self):
        return self.__users

    def add_game(self, game: Game):
        if game not in self.__games:
            self.__games.append(game)
        self.sort_games()

    def get_game(self, app_id: int) -> Union[None, Game]:
        # Check each game's id field for specified
        for game in self.__games:
            if game.game_id == app_id:
                return game

        # If for we reach this point, the game isn't in the repository and we return None.
        return None

    def get_number_of_games(self):
        return len(self.__games)

    def get_all_games(self):
        return self.__games

    def get_games_by_genres(self, genres: List[Genre]):
        hits = []
        for game in self.__games:
            for genre in genres:
                if genre in game.genres:
                    hits.append(game)
                    continue

        return hits

    def get_games_by_name_query(self, query: str):
        hits = []
        for game in self.__games:
            if query in game.title:
                hits.append(game)

        return hits

    def get_game_by_id(self, game_id: int) -> Union[None, Game]:
        hits = [game for game in self.__games if game.game_id == game_id]
        if hits:
            return hits[0]
        else:
            return None

    def add_genre(self, genre: Genre):
        if genre not in self.__genres:
            self.__genres.append(genre)
        self.sort_genres()

    def get_genre(self, name: str):
        hits = [genre for genre in self.__genres if genre.genre_name == name]
        if hits:
            return hits[0]
        else:
            return None

    def get_all_genres(self):
        return self.__genres

    def add_publisher(self, publisher: Publisher):
        if publisher not in self.__publishers:
            self.__publishers.append(publisher)
        self.sort_publishers()

    def get_all_publishers(self):
        return self.__publishers

    def sort_games(self):
        # Sort by newest games first
        self.__games = list(reversed(sorted(self.__games, key=lambda x: datetime.strptime(x.release_date, "%b %d, %Y"))))

    def sort_genres(self):
        self.__genres = sorted(self.__genres)

    def sort_publishers(self):
        self.__publishers = sorted(self.__publishers)

    def sort_self(self):
        self.sort_games()
        self.sort_genres()
        self.sort_publishers()

    def add_review(self, review: Review):
        if isinstance(review, Review) and review not in self.__reviews:
            super().add_review(review)
            self.__reviews.append(review)

    def remove_review(self, review: Review):
        if isinstance(review, Review) and review in self.__reviews:
            super().remove_review(review)
            self.__reviews.remove(review)

    def get_reviews(self) -> List[Review]:
        return self.__reviews

    def add_game_to_wishlist(self, user: User, game: Game):
        user.add_to_wishlist(game)

    def remove_game_from_wishlist(self, user: User, game: Game):
        user.remove_from_wishlist(game)

    def get_all_games_in_wishlist(self, user: User):
        return user.wishlist.list_of_games()

    def get_user_history(self, user: User):
        history = user.history
        history = list(sorted(history, key=lambda x: datetime.strptime(x.datetimestamp, "%d/%m/%Y %I:%M %p")))
        return history


def read_csv_simple(file_path: str):
    with open(file_path, encoding='utf-8-sig') as file:
        reader = csv.reader(file)

        headers = next(reader)

        rows = []
        for row in reader:
            row = [item.strip() for item in row]
            rows.append(row)

        return rows


def load_games(repo: AbstractRepository, data_path: Path):
    path = str(Path(data_path) / "games.csv")
    reader = GameFileCSVReader(path)
    reader.read_csv_file()

    # Add everything from the CSV file to the repo for use on the website. Might be slow, but only needs to run once
    for game in reader.dataset_of_games:
        repo.add_game(game)

    for genre in reader.dataset_of_genres:
        repo.add_genre(genre)

    for publisher in reader.dataset_of_publishers:
        repo.add_publisher(publisher)

    repo.sort_self()


def load_users(repo: AbstractRepository, data_path: Path):
    path = str(Path(data_path) / "users.csv")
    rows = read_csv_simple(path)

    for row in rows:
        repo.add_user(User(row[1], generate_password_hash(row[2])))


def populate(repo: AbstractRepository, data_path: Path):
    load_games(repo, data_path)
