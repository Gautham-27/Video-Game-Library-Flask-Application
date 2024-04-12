from werkzeug.security import generate_password_hash, check_password_hash
from games.adapters.repository import AbstractRepository
from games.domainmodel.model import User


class UsernameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


def add_user(user_name: str, password: str, repo: AbstractRepository):
    # Check if user_name for new user is unique
    if repo.get_user(user_name) is not None:
        raise UsernameNotUniqueException

    # Encrypting given password before storage
    password_hash = generate_password_hash(password)

    # Create and storing new user with username and hashed password
    user = User(user_name, password_hash)
    repo.add_user(user)


def get_user(user_name: str, repo: AbstractRepository):
    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException
    return user


def authenticate_user(user_name: str, password: str, repo: AbstractRepository):
    authenticated = False
    user = get_user(user_name, repo)
    if user is not None:
        # Compares hashed password to given password to authenticate user
        authenticated = check_password_hash(user.password, password)
    if not authenticated:
        raise AuthenticationException



















