from flask import Blueprint, render_template, url_for, request, session

import games.adapters.repository as repo
import games.userProfile.services as services

from games.authentication.authentication import login_required
from games.domainmodel.model import User
from games.gamesList.services import get_publishers
from games.genres.services import get_genres

# Configure Blueprint.
userProfile_blueprint = Blueprint('userProfile_bp', __name__)


@userProfile_blueprint.route('/userProfile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = services.get_user_from_username(repo.repo_instance, session['user_name'])
    publishers = get_publishers(repo.repo_instance)
    genres_list = get_genres(repo.repo_instance)

    wishlist = user.wishlist
    user_history = services.get_user_history(repo.repo_instance, user, 6)
    if len(user_history) < 6:
        history = user_history + [("N/A", "Nothing Found")] * (6 - len(user_history))
    else:
        history = user_history

    return render_template('userProfile/userProfile.html',
                           user=user.username, wishlist=wishlist, history=history, user_obj=user, genres_list=genres_list, publishers=publishers)
