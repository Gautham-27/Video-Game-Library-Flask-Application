from flask import Blueprint, render_template, url_for, request, session

import games.adapters.repository as repo
import games.search.services as search_services
import games.gamesList.services as services

from games.genres.services import get_genres

from games.authentication.authentication import login_required

# Configure Blueprint.
gamesList_blueprint = Blueprint('gamesList_bp', __name__)


@gamesList_blueprint.route('/gamesList', methods=['GET', 'POST'])
def games_list():
    user = None
    if session.get('user_name'):
        user = session['user_name']

    number_to_show = 6

    genres_list = get_genres(repo.repo_instance)
    publishers = services.get_publishers(repo.repo_instance)


    search_handler = search_services.process_url()
    max_page = services.get_number_of_pages(search_handler["games_to_show"], number_to_show)
    games_to_show = services.get_page_of_games(search_handler["games_to_show"], search_handler["search_page"],
                                               number_to_show)

    if request.method == "POST":
        # Ready in case jump-to-page is implemented
        jump_page = int(request.form.get('page_jump'))
        if jump_page:
            search_handler["search_page"] = max(1, min(jump_page, max_page))

    pagination_urls = {}
    pagination_urls["next"] = url_for('gamesList_bp.games_list', page=min(search_handler["search_page"] + 1,
                                                                          max_page),
                                      genre_filter=[genre.genre_name for genre in search_handler["search_genres"]],
                                      search=search_handler["search_query"])

    pagination_urls["prev"] = url_for('gamesList_bp.games_list', page=max(search_handler["search_page"] - 1, 1),
                                      genre_filter=[genre.genre_name for genre in search_handler["search_genres"]],
                                      search=search_handler["search_query"])

    pagination_urls["first"] = url_for('gamesList_bp.games_list', page=1,
                                       genre_filter=[genre.genre_name for genre in search_handler["search_genres"]],
                                       search=search_handler["search_query"])

    pagination_urls["last"] = url_for('gamesList_bp.games_list',
                                      page=max_page,
                                      genre_filter=[genre.genre_name for genre in search_handler["search_genres"]],
                                      search=search_handler["search_query"])

    return render_template('gameList/gameList.html', games_list=games_to_show,
                           genres_list=genres_list, pagination_urls=pagination_urls,
                           page_number=search_handler["search_page"], user=user, publishers=publishers)
