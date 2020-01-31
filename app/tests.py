import pytest
from .models import Quiz, Question, Option, User, database
from .utils import is_quiz_info_valid
from app import app
import random


@pytest.fixture
def client():
    """
    Основная фикстура
    :return:
    """
    app.testing = True
    test_db_name = 'test'
    database.init(test_db_name)
    database.create_tables([Quiz, Question, Option, User], safe=True)

    yield app.test_client

    database.drop_tables([Quiz, Question, Option, User])
    app.testing = False


def test_user_creation(client):
    """
    Тест создания нового пользователя
    :param client:
    """
    _, response = client.post('/signup', data={'email': 'a@a.com', 'password': '123', 'gender': 'f'})
    assert response.status == 200

    _, response = client.post('/signup', data={'password': '123', 'gender': 'f'})
    assert response.status == 400

    _, response = client.post('/signup', data={'email': 'a@a.com'})
    assert response.status == 400


def test_auth(client):
    """
    Тест авторизации
    :param client:
    :return:
    """
    email = 'a@a.com'
    password = '123'

    _, response = client.post('/signup', data={'email': email, 'password': password, 'gender': 'f'})
    assert response.status == 200

    _, response = client.post('/signin', data={'email': email, 'password': password, 'gender': 'f'})
    assert response.status == 200

    _, response = client.post('/signin', data={'email': 'completelywrongemail', 'password': password, 'gender': 'f'})
    assert response.status == 401


def test_auth_requiring(client):
    """
    Тест на проверку авторизации при попытке доступа
    :param client:
    :return:
    """
    _, response = client.get('/quiz/add', allow_redirects=False)
    assert response.status == 302

    _, response = client.get('/quiz/list', allow_redirects=False)
    assert response.status == 302

    _, response = client.get('/quiz/1', allow_redirects=False)
    assert response.status == 302


def test_quiz_adding(client):
    """
    Тест создания опроса
    :param client:
    :return:
    """
    email = 'a@a.com'
    password = '123'

    _, response = client.post('/signup', data={'email': email, 'password': password, 'gender': 'f'})
    assert response.status == 200
    _, response = client.post('/signin', data={'email': email, 'password': password, 'gender': 'f'})
    assert response.status == 200

    quiz_name = str(random.randint(111111, 999999))
    quiz = {
        'title': quiz_name,
        'questions': [
            {
                'question_title': 'test_title',
                'options': [
                    {
                        'option_title': 'op_title',
                        'correct': True,
                    }
                ]
            }
        ]
    }

    assert is_quiz_info_valid(quiz)

    _, response = client.post('/quiz/add', data=quiz)
    assert response.status == 200
