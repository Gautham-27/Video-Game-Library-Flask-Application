from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Text, Float, ForeignKey
)

from sqlalchemy.orm import mapper, relationship

from games.domainmodel.model import *

metadata = MetaData()

publishers_table = Table(
    'publishers', metadata,
    # We only want to maintain those attributes that are in our domain model
    # For publisher, we only have name.
    Column('name', String(255), primary_key=True)  # nullable=False, unique=True)
)

games_table = Table(
    'games', metadata,
    Column('game_id', Integer, primary_key=True),
    Column('game_title', Text, nullable=False),
    Column('game_price', Float, nullable=False),
    Column('release_date', String(50), nullable=False),
    Column('game_description', String(255), nullable=True),
    Column('game_image_url', String(255), nullable=True),
    Column('game_website_url', String(255), nullable=True),
    Column('publisher_name', ForeignKey('publishers.name'))
)

genres_table = Table(
    'genres', metadata,
    # For genre again we only have name.
    Column('genre_name', String(64), primary_key=True, nullable=False)
)

game_genres_table = Table(
    'game_genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('game_id', ForeignKey('games.game_id')),
    Column('genre_name', ForeignKey('genres.genre_name'))
)

users_table = Table(
    'users', metadata,
    Column('username', String(255), primary_key=True),
    Column('password', String(255)),
)

reviews_table = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_name', String(255), ForeignKey('users.username')),
    Column('game_id', Integer, ForeignKey('games.game_id')),
    Column('comment', Text),
    Column('rating', Integer),
)

wishlists_table = Table(
    'wishlists', metadata,
    Column('wishlist_id', Integer, primary_key=True, autoincrement=True),
    Column('user', String(255), ForeignKey('users.username')),
)

wishlist_games_table = Table(
    'wishlist_games', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('wishlist_id', ForeignKey('wishlists.wishlist_id')),
    Column('game_id', ForeignKey('games.game_id'))
)

history_table = Table(
    'history', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_name', String(255), ForeignKey('users.username')),
    Column('datetime', Text),
    Column('entry', Text),
)


def map_model_to_tables():
    mapper(Publisher, publishers_table, properties={
        '_Publisher__publisher_name': publishers_table.c.name,
    })

    mapper(Game, games_table, properties={
        '_Game__game_id': games_table.c.game_id,
        '_Game__game_title': games_table.c.game_title,
        '_Game__price': games_table.c.game_price,
        '_Game__release_date': games_table.c.release_date,
        '_Game__description': games_table.c.game_description,
        '_Game__image_url': games_table.c.game_image_url,
        '_Game__website_url': games_table.c.game_website_url,
        '_Game__publisher': relationship(Publisher),
        '_Game__genres': relationship(Genre, secondary=game_genres_table),
        '_Game__reviews': relationship(Review, back_populates='_Review__game'),
    })

    mapper(Genre, genres_table, properties={
        '_Genre__genre_name': genres_table.c.genre_name,
    })

    mapper(User, users_table, properties={
        '_User__username': users_table.c.username,
        '_User__password': users_table.c.password,
        '_User__reviews': relationship(Review, back_populates='_Review__user'),
        '_User__wishlist': relationship(Wishlist, back_populates='_Wishlist__user', uselist=False),
        '_User__history': relationship(History, back_populates='_History__user'),
    })

    mapper(Review, reviews_table, properties={
        '_Review__user': relationship(User, back_populates='_User__reviews'),
        '_Review__game': relationship(Game, back_populates='_Game__reviews'),
        '_Review__comment': reviews_table.c.comment,
        '_Review__rating': reviews_table.c.rating,
    })

    mapper(Wishlist, wishlists_table, properties={
        '_Wishlist__user': relationship(User, back_populates='_User__wishlist'),
        '_Wishlist__list_of_games': relationship(Game, secondary=wishlist_games_table)
    })

    mapper(History, history_table, properties={
        '_History__user': relationship(User, back_populates='_User__history'),
        '_History__datetimestamp': history_table.c.datetime,
        '_History__entry': history_table.c.entry,
    })
