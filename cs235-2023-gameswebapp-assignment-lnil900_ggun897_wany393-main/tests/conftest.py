import pytest

from pathlib import Path

from games import create_app
from games.adapters import memory_repository
from games.adapters.memory_repository import MemoryRepository

# the csv files in the test folder are different from the csv files in the covid/adapters/data folder!
# tests are written against the csv files in tests, this data path is used to override default path for testing
FULL_DATA_PATH = Path(__file__).parents[1] / 'games' / 'adapters' / 'data'
TEST_DATA_PATH = Path(__file__).parents[1] / 'tests' / 'data'


@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository()
    memory_repository.populate(repo, FULL_DATA_PATH)
    return repo


@pytest.fixture
def in_memory_repo_shortened():
    repo = MemoryRepository()
    memory_repository.populate(repo, TEST_DATA_PATH)
    return repo


@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,                                # Set to True during testing.
        'REPOSITORY': 'memory',
        'TEST_DATA_PATH': TEST_DATA_PATH,               # Path for loading test data into the repository.
        'WTF_CSRF_ENABLED': False                       # test_client will not send a CSRF token, so disable validation.
    })

    return my_app.test_client()


class AuthenticationManager:
    def __init__(self, client):
        self.__client = client

    def login(self, user_name='tester', password='Testing&Checking12345'):
        return self.__client.post(
            'authentication/login',
            data={'user_name': user_name, 'password': password}
        )

    def logout(self):
        return self.__client.get('/authentication/logout')


@pytest.fixture
def auth(client):
    return AuthenticationManager(client)
