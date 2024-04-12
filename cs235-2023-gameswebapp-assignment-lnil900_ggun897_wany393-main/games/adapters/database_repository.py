from typing import List, Union

from pathlib import Path

from sqlalchemy import desc, asc
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound

import csv

from games.domainmodel.model import *
from games.adapters.repository import AbstractRepository
from games.adapters.datareader.csvdatareader import GameFileCSVReader


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if self.__session is not None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, user_name: str) -> User:
        # Assume usernames will be modified as they are when set under User constructor
        # For safety, bail if the username isn't a string before trying to format.
        if not isinstance(user_name, str):
            return None
        user_name = user_name.lower().strip()

        user = None
        try:
            user = self._session_cm.session.query(User).filter(User._User__username == user_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user

    def get_all_users(self):
        return self._session_cm.session.query(User).all()

    def add_game(self, game: Game):
        with self._session_cm as scm:
            scm.session.merge(game)
            scm.commit()

    def get_number_of_games(self):
        return len(self.get_all_games())

    def get_all_games(self):
        games =  self._session_cm.session.query(Game).order_by(Game._Game__release_date).all()

        # Sort by date and reverse order to show newest games first
        games = list(reversed(sorted(games, key=lambda x: datetime.strptime(x.release_date, "%b %d, %Y"))))

        return games

    def get_games_by_genres(self, genres: List[Genre]):
        games = None
        genre_names = [genre.genre_name for genre in genres]
        try:
            # Here we are building a query that has a chain of .filter().filter().filter()... for every Genre..
            # This progressively thins the output list until only games with ALL genres desired remain.
            query = self._session_cm.session.query(Game)
            for genre_name in genre_names:
                query = query.filter(Game._Game__genres.any(Genre._Genre__genre_name == genre_name))
            games = query.order_by(Game._Game__release_date).all()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        # Sort by date and reverse order to show newest games first
        games = list(reversed(sorted(games, key=lambda x: datetime.strptime(x.release_date, "%b %d, %Y"))))

        return games

    def get_games_by_name_query(self, query: str):
        games = None
        try:
            games = self._session_cm.session.query(Game).filter(Game._Game__game_title.like(query)).order_by(Game._Game__release_date).all()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        # Sort by date and reverse order to show newest games first
        games = list(reversed(sorted(games, key=lambda x: datetime.strptime(x.release_date, "%b %d, %Y"))))

        return games

    def get_game_by_id(self, game_id: int) -> Union[None, Game]:
        game = None
        try:
            game = self._session_cm.session.query(Game).filter(Game._Game__game_id == game_id).one()
        except NoResultFound:
            print("Couldn't find game")
            # Ignore any exception and return None.
            pass

        return game

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.merge(genre)
            scm.commit()

    def get_genre(self, name: str):
        game = None
        try:
            game = self._session_cm.session.query(Genre).filter(Genre._Genre__genre_name == name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return game

    def get_all_genres(self):
        return self._session_cm.session.query(Genre).order_by(Genre._Genre__genre_name).all()

    def add_publisher(self, publisher: Publisher):
        with self._session_cm as scm:
            scm.session.merge(publisher)
            scm.commit()

    def get_all_publishers(self):
        return self._session_cm.session.query(Publisher).all()

    def sort_games(self):
        # Depreciated
        return NotImplementedError

    def sort_genres(self):
        # Depreciated
        return NotImplementedError

    def sort_publishers(self):
        # Depreciated
        return NotImplementedError

    def sort_self(self):
        # Depreciated
        return NotImplementedError

    def add_review(self, review: Review):
        with self._session_cm as scm:
            scm.session.merge(review)

            scm.commit()

    def remove_review(self, review: Review):
        with self._session_cm as scm:
            scm.session.delete(review)
            scm.commit()

    def get_reviews(self) -> List[Review]:
        return self._session_cm.session.query(Review).all()

    def add_game_to_wishlist(self, user: User, game: Game):
        with self._session_cm as scm:
            user.add_to_wishlist(game)
            scm.commit()

    def remove_game_from_wishlist(self, user: User, game: Game):
        with self._session_cm as scm:
            user.remove_from_wishlist(game)
            scm.commit()

    def get_all_games_in_wishlist(self, user: User):
        with self._session_cm as scm:
            wishlist = scm.session.query(Wishlist).filter(Wishlist._Wishlist__user == user).one()
            return wishlist.list_of_games()

    def get_user_history(self, user: User):
        with self._session_cm as scm:
            history = scm.session.query(History).filter(History._History__user == user).all()
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


def populate(repo: AbstractRepository, data_path: Path):
    load_games(repo, data_path)
