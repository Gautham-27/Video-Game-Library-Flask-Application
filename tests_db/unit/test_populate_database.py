from sqlalchemy import select, inspect

from games.adapters.orm import metadata

def test_database_populate_correct_table_names(database_engine):

    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['game_genres', 'games', 'genres', 'history', 'publishers', 'reviews', 'users', 'wishlist_games', 'wishlists']

def test_database_populate_select_all_games(database_engine):
    inspector = inspect(database_engine)

    with database_engine.connect() as connection:
        select_statement = select([metadata.tables['games']])
        result = connection.execute(select_statement)

        games = []

        for row in result:
            games.append(row)

        assert len(games) == 29

def test_database_populate_select_all_genres(database_engine):
    inspector = inspect(database_engine)

    with database_engine.connect() as connection:
        select_statement = select([metadata.tables['genres']])
        result = connection.execute(select_statement)

        genres = []

        for row in result:
            genres.append(row)

        assert len(genres) == 3


def test_database_populate_select_all_publishers(database_engine):
    inspector = inspect(database_engine)

    with database_engine.connect() as connection:
        select_statement = select([metadata.tables['publishers']])
        result = connection.execute(select_statement)

        publishers = []

        for row in result:
            publishers.append(row)

        assert len(publishers) == 29


def test_database_populate_select_all_game_genres(database_engine):
    inspector = inspect(database_engine)

    with database_engine.connect() as connection:
        select_statement = select([metadata.tables['game_genres']])
        result = connection.execute(select_statement)

        genres = []

        for row in result:
            genres.append(row)

        assert len(genres) == 40




