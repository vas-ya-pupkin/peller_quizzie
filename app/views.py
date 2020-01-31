from jinja2 import Environment, PackageLoader
from sanic.exceptions import abort
from sanic_auth import User, Auth
from sanic_session import Session, InMemorySessionInterface
from sanic.response import html, redirect, json

from app import app
from .utils import get_quiz_data, get_quizzes_list, is_quiz_info_valid, add_quiz_to_db, count_correct_answers, signup, \
    get_user_id

app.config.AUTH_LOGIN_ENDPOINT = 'signin'
auth = Auth(app)

Session(app, interface=InMemorySessionInterface())

env = Environment(
    loader=PackageLoader('app', 'templates'),
    trim_blocks=True,
    lstrip_blocks=True,
)  # загружаем шаблоны


@app.route("/")
async def index(request):
    return redirect('/quiz/list')


@app.route('/signup', methods=['GET', 'POST'])
async def signup_handler(request):
    if request.method == 'GET':
        template = env.get_template('signup.html')
        return html(template.render())

    elif request.method == 'POST':
        params = dict(
            gender=request.form.get('gender'),
            email=request.form.get('email'),
            password=request.form.get('password'),
        )

        if not all(params.values()):
            abort(400)

        success = signup(**params)
        if not success:
            return redirect('/signup')

        return redirect('/signin')


@app.route('/signin', methods=['GET', 'POST'])
async def signin(request):
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        uid = get_user_id(email=email, password=password)

        if uid:
            user = User(id=uid, name=email)
            auth.login_user(request, user)

            return redirect('/quiz/list')
        else:
            abort(401)
    template = env.get_template('signin.html')
    return html(template.render())


@app.route('/quiz/add', methods=['GET', 'POST'])
@auth.login_required
async def add_quiz_handler(request):
    if request.method == 'GET':
        template = env.get_template('new_quiz.html')
        return html(template.render(questions=1, options=4, logged=True))
    elif request.method == 'POST':
        quiz_info = request.json

        if is_quiz_info_valid(quiz_info):
            add_quiz_to_db(quiz_info)
            return json({'success': True})
        abort(400)


@app.route('/quiz/list', methods=['GET'])
@auth.login_required
async def quiz_list_handler(request):
    quizzes = get_quizzes_list()
    template = env.get_template('quizzes_list.html')
    return html(template.render(quizzes=quizzes, logged=True))


@app.route('/quiz/<quiz_id:int>', methods=['GET', 'POST'])
@auth.login_required
async def quiz_handler(request, quiz_id):
    if request.method == 'GET':
        data = get_quiz_data(quiz_id)  # информация об опросе
        if not data:
            abort(404)

        template = env.get_template('quiz.html')
        return html(template.render(data=data, logged=True))

    elif request.method == 'POST':
        correct, total = count_correct_answers(request.form)
        template = env.get_template('results.html')
        return html(template.render(correct=correct, total=total, logged=True))  # счетчик правильных ответов/всего


@app.route('/signout')
@auth.login_required
async def logout(request):
    auth.logout_user(request)
    return redirect('/signin')