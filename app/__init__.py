from sanic import Sanic
from sanic_auth import Auth
from .models import database, Quiz, Question, Option, User

database.create_tables([Quiz, Question, Option, User], safe=True)

app = Sanic(name="Quiz")

from app import views
