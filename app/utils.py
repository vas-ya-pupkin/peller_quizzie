import hashlib
from typing import Dict, List, Any, Tuple

from jinja2 import Environment, PackageLoader
from peewee import DatabaseError, DoesNotExist
from playhouse.shortcuts import model_to_dict
from sanic.log import logger
from sanic.response import html

from .models import Quiz, Question, Option, User, database

env = Environment(
    loader=PackageLoader('app', 'templates'),
    trim_blocks=True,
    lstrip_blocks=True,
)  # загружаем шаблоны


def render_template(name, **kwargs):
    """
    Возвращает HTML собранного шаблона с параметрами
    :param name: Имя файла
    :param kwargs: Переменные шаблона
    :return:
    """
    template = env.get_template(name)
    return html(template.render(**kwargs))


def to_sha256(string: str) -> str:
    """
    Хеширование строки в sha256
    :param string:
    :return:
    """
    return hashlib.sha256(string.encode()).hexdigest()


def get_quiz_data(quiz_id: int) -> Dict[str, Any]:
    """
    Возвращает вопросы и варианты ответов для выбранного опроса
    :param quiz_id:
    :return:
    """
    res = dict()
    try:
        quiz_title = Quiz.get(Quiz.id == quiz_id).quiz_name

        questions = [
            {
                'question_text': x.title,
                'id': x.id
            } for x in Question.select().join(Quiz).where(Quiz.id == quiz_id)
        ]

        for q in questions:
            q['options'] = [
                {
                    'title': o.title,
                    'id': o.id
                } for o in Option.select().join(Question).where(Question.id == q['id'])
            ]

        res['quiz_title'] = quiz_title
        res['questions'] = questions

    except Exception as e:
        logger.exception(e)

    finally:
        return res


def get_quizzes_list() -> List[Dict[str, Any]]:
    """
    Возвращает список доступных опросов
    :return:
    """
    return [model_to_dict(x) for x in Quiz.select()]


def is_quiz_info_valid(json_info: Dict[str, Any]) -> bool:
    """
    Валидация теста в формате JSON
    :param json_info:
    :return:
    """
    if not all([json_info.get('title', ''), json_info.get('questions', '')]):
        return False

    if not all(
            [q.get('question_title', '') for q in json_info['questions']] +
            [q.get('options', '') for q in json_info['questions']]
    ):
        return False

    for question in json_info['questions']:
        if not all(
                [o for o in question['options']]
        ) or not all(
            [o['correct'] in [True, False] for o in question['options']]
        ):
            return False
    return True


def add_quiz_to_db(quiz_info: Dict[str, Any]) -> bool:
    """
    Добавление нового теста в БД
    :param quiz_info:
    :return:
    """
    quiz_row = Quiz(quiz_name=quiz_info['title'])

    with database.atomic():
        try:
            quiz_row.save()
        except DatabaseError as e:
            logger.exception(e)
            return False

        for question in quiz_info['questions']:
            question_row = Question(title=question['question_title'], quiz=quiz_row.id)

            try:
                question_row.save()
            except DatabaseError as e:
                logger.exception(e)
                return False

            prepared_options = [
                (
                    o['option_title'],
                    o['correct'],
                    question_row.id,
                )
                for o in question['options']
            ]

            try:
                Option.insert_many(
                    rows=prepared_options,
                    fields=[
                        Option.title,
                        Option.is_correct,
                        Option.question,
                    ]
                ).execute()
            except DatabaseError as e:
                logger.exception(e)
                return False
    return True


def count_correct_answers(data: Dict[str, List[str]]) -> Tuple[int, int]:
    """
    Подсчет правильных ответов и общего количества вопросов
    :param data:
    :return:
    """
    answers = [data[x][0] for x in data]
    correct = len([
        uid for uid in answers if
        Option.get_by_id(uid).is_correct
    ])

    return correct, len(answers)


def signup(email: str, password: str, gender: str, is_admin=False) -> bool:
    """
    Регистрирует нового пользователя
    :param email:
    :param password:
    :param gender:
    :param is_admin:
    :return:
    """
    password_hash = to_sha256(password)
    user = User(
        email=email,
        password_hash=password_hash,
        gender=gender,
        is_admin=is_admin,
    )
    try:
        with database.atomic():
            user.save()
        return True
    except DatabaseError as e:
        logger.exception(e)
    return False


def get_user_id(email: str, password: str) -> int:
    """
    Возвращает id пользователя с таким email и паролем
    :param email:
    :param password:
    :return:
    """
    password_hash = to_sha256(password)
    try:
        user = User.get(
            User.email == email,
            User.password_hash == password_hash
        )
        return user.id
    except (DoesNotExist, DatabaseError):
        return 0
