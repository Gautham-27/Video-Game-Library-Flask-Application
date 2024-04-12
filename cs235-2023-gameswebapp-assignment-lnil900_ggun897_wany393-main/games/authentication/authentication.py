from flask import Blueprint, render_template, redirect, url_for, session, request

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from password_validator import PasswordValidator

from functools import wraps

import games.authentication.services as services
import games.adapters.repository as repo

authentication_blueprint = Blueprint('authentication_bp', __name__, url_prefix='/authentication')


@authentication_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    not_unique_message = None

    # If successful POST then username and password are valid
    if form.validate_on_submit():
        # Try adding new user credentials to repo using service layer
        try:
            services.add_user(form.user_name.data, form.password.data, repo.repo_instance)
            # If successful redirect new user to login
            return redirect(url_for('authentication_bp.login'))
        # Handle exception if new user_name is not unique
        except services.UsernameNotUniqueException:
            not_unique_message = "This username is already taken. Please enter a different username"

    # For GET request or failed POST request return registration page
    return render_template(
        'authentication/auth.html',
        title='Register',
        form=form,
        user_name_error=not_unique_message,
        user=None,
        handler_url=url_for('authentication_bp.register')
    )


@authentication_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username_error = None
    password_error = None



    # If successful POST then username and password are valid
    if form.validate_on_submit():
        try:
            user = services.get_user(form.user_name.data, repo.repo_instance)

            # Authenticate user
            services.authenticate_user(user.username, form.password.data, repo.repo_instance)

            # Initialise start session and redirect user to homepage once logged in
            session.clear()
            session['user_name'] = user.username
            return redirect(url_for('home_bp.home'))
        except services.UnknownUserException:
            username_error = "Your username was not found - Please enter a different username"
        except services.AuthenticationException:
            password_error = "The password entered was incorrect - Please try again"



    # For GET request or failed POST request return registration page
    return render_template(
        'authentication/auth.html',
        title='Login',
        user_name_error=username_error,
        form=form,
        user=None,
        password_error=password_error

    )


@authentication_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_bp.home'))


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_name' not in session:
            return redirect(url_for('authentication_bp.login'))
        return view(**kwargs)
    return wrapped_view


class CheckPasswordValid:
    def __init__(self, message=None):
        if not message:
            message = "Your password must be at least 8 characters long and contain at least 1 uppercase letter,\
                        lowercase letter and a digit."
        self.message = message

    def __call__(self, form, field):
        schema = PasswordValidator()
        schema \
            .min(8)\
            .has().uppercase() \
            .has().lowercase() \
            .has().digits()
        if not schema.validate(field.data):
            raise ValidationError(self.message)


class RegistrationForm(FlaskForm):
    # Entry for username and validates username
    user_name = StringField("Username", [
        DataRequired(message="Entering a username is required"),
        Length(min=2, message="Your username must be more than 2 characters")])
    # Entry for password and calls CheckPasswordValid to validate password
    password = PasswordField("Password", [
        DataRequired(message="Entering a password is required"),
        CheckPasswordValid()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    user_name = StringField('Username', [
        DataRequired(message="Please enter a Username.")])
    password = PasswordField('Password', [
        DataRequired(message="Please enter a Password.")])
    submit = SubmitField('Login')

