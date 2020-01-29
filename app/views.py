from app import app


@app.route("/")
async def index(request):
    ...


@app.route('/signup')
async def signup_handler(request):
    ...


@app.route('/signin')
async def signin_handler(request):
    ...


@app.route('/quiz/add')
async def quiz_add_handler(request):
    ...


@app.route('/quiz/list')
async def quiz_list_handler(request):
    ...


@app.route('/quiz/<quiz_id:int>')
async def quiz_handler(request, quiz_id):
    ...


@app.route('/quiz/results')
async def quiz_results_handler(request):
    ...
