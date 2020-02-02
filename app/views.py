from sanic.exceptions import abort
from sanic.response import redirect, json
from sanic_auth import User, Auth
from sanic_session import Session, InMemorySessionInterface

from app import app
from .utils import get_quiz_data, get_quizzes_list, is_quiz_info_valid, add_quiz_to_db, count_correct_answers, signup, \
    get_user_id, render_template

app.config.AUTH_LOGIN_ENDPOINT = 'signin'
auth = Auth(app)

Session(app, interface=InMemorySessionInterface())


@app.route("/")
async def index(request):
    return redirect('/quiz/list')


@app.route('/signup', methods=['GET', 'POST'])
async def signup_handler(request):
    if request.method == 'GET':
        return render_template('signup.html')

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
    return render_template('signin.html')


@app.route('/quiz/add', methods=['GET', 'POST'])
@auth.login_required
async def add_quiz_handler(request):
    if request.method == 'GET':
        return render_template('new_quiz.html', questions=1, options=4, logged=True)
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
    return render_template('quizzes_list.html', quizzes=quizzes, logged=True)


@app.route('/quiz/<quiz_id:int>', methods=['GET', 'POST'])
@auth.login_required
async def quiz_handler(request, quiz_id):
    if request.method == 'GET':
        data = get_quiz_data(quiz_id)  # информация об опросе
        if not data:
            abort(404)
        return render_template('quiz.html', data=data, logged=True)

    elif request.method == 'POST':
        correct, total = count_correct_answers(request.form)
        return render_template('results.html', correct=correct, total=total,
                               logged=True)  # счетчик правильных ответов/всего


@app.route('/signout')
@auth.login_required
async def logout(request):
    auth.logout_user(request)
    return redirect('/signin')
