
from flask import Blueprint, render_template, redirect, url_for, session, request

import games.adapters.repository as repo

from games.genres.services import get_genres
from games.gamesList.services import get_publishers

home_blueprint = Blueprint('home_bp', __name__)


@home_blueprint.route('/')
def home():
    genres_list = get_genres(repo.repo_instance)
    publishers = get_publishers(repo.repo_instance)
    user = None
    if session.get('user_name'):
        user = session['user_name']

    return render_template("home/home.html", genres_list=genres_list, user=user, publishers=publishers)