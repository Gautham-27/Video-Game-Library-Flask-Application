from flask import Blueprint, render_template, request, redirect, url_for, session

from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length

import games.adapters.repository as repo
import games.gameDescription.services as services

from games.authentication.authentication import login_required
from games.genres.services import get_genres
from games.gamesList.services import get_publishers

# Configure Blueprint.
gameDescription_blueprint = Blueprint('gameDescription_bp', __name__)


@gameDescription_blueprint.route('/gameDescription')
def game_description():
    user = None
    if session.get('user_name'):
        user = session['user_name']

    genres_list = get_genres(repo.repo_instance)
    publishers = get_publishers(repo.repo_instance)

    game_id = int(request.args.get('id'))
    game_to_show = services.get_game_by_id(repo.repo_instance, game_id)
    reviews = services.get_game_reviews(repo.repo_instance, game_id)
    reviews = list(reversed(reviews))
    review_average = services.get_average_rating(repo.repo_instance, game_id)

    if 'user_name' not in session:
        on_wishlist = False
    else:
        on_wishlist = services.game_in_user_wishlist(repo.repo_instance, session['user_name'], game_id)

    return render_template('gameDescription/gameDescription.html', genres_list=genres_list,
                           game=game_to_show, reviews=reviews, review_count=len(reviews), review_average=review_average,
                           on_wishlist=on_wishlist, user=user, form=None, publishers=publishers)


@gameDescription_blueprint.route('/review', methods=['GET', 'POST'])
@login_required
def review_game():
    username = session['user_name']

    form = ReviewForm()
    if form.validate_on_submit():
        game_id = int(form.game_id.data)

        services.add_review(repo.repo_instance, username, game_id, int(form.rating.data), form.review_text.data)

        return redirect(url_for('gameDescription_bp.game_description', id=game_id))

    if request.method == 'GET':
        game_id = int(request.args.get('game_id'))

        form.game_id.data = game_id

    else:
        game_id = int(form.game_id.data)

    game = services.get_game_by_id(repo.repo_instance, game_id)
    return render_template('gameDescription/gameDescription.html', game=game, form=form,
                           handler_url=url_for('gameDescription_bp.review_game'), user=username)


class ReviewForm(FlaskForm):
    rating = SelectField('Rating',
                         choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                         validators=[DataRequired()])
    review_text = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='This review is too short!')])
    game_id = HiddenField("Game id")
    submit = SubmitField('Submit')


@gameDescription_blueprint.route('/gameDescription/wishlist', methods=['GET', 'POST'])
@login_required
def wishlist_request():
    username = session['user_name']
    user = services.get_user_from_username(repo.repo_instance, username)

    game_id = int(request.args.get('id'))
    game = services.get_game_by_id(repo.repo_instance, game_id)

    # We'll make things nice and simple by just handling this as a toggle. If the game is not in the users wishlist,
    # add it. If it is, remove it. Nice and simple.
    on_wishlist = services.game_in_user_wishlist(repo.repo_instance, session['user_name'], game_id)

    if not on_wishlist:
        services.add_game_to_user_wishlist(repo.repo_instance, user, game)
    else:
        services.remove_game_from_user_wishlist(repo.repo_instance, user, game)

    return redirect(url_for('gameDescription_bp.game_description', id=game_id))
