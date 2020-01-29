from sanic import Sanic

app = Sanic(name="Quiz")

from app import views
