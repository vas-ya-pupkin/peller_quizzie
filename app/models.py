from peewee import Model, CharField, ForeignKeyField, BooleanField, PostgresqlDatabase
import os

database = PostgresqlDatabase(
    database=os.getenv('POSTGRES_DB', 'postgres'),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    host=os.getenv('POSTGRES_HOST', 'postgres'),
)


class BaseModel(Model):
    class Meta:
        database = database


class Quiz(BaseModel):
    quiz_name = CharField(null=False)


class Question(BaseModel):
    title = CharField(null=False)
    quiz = ForeignKeyField(Quiz, field='id')


class Option(BaseModel):
    title = CharField(null=False)
    is_correct = BooleanField(null=False, default=False)
    question = ForeignKeyField(Question, field='id')


class User(BaseModel):
    email = CharField(null=False, unique=True)
    password_hash = CharField(null=False)
    gender = CharField(null=False, default='m')
    is_admin = BooleanField(null=False, default=False)
